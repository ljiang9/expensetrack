"""expensetrack —— 终端记账小工具：记一笔、看明细、按分类汇总。

数据存在 ~/.config/expenses.json（可用 --data 覆盖），纯标准库，纯本地。
"""
import argparse
import collections
import datetime
import json
import os
import sys

VERSION = "0.1.0"
DEFAULT_DATA = os.path.expanduser("~/.config/expenses.json")
BAR_WIDTH = 20


def err(msg, code=2):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def data_path(args):
    return getattr(args, "data", None) or DEFAULT_DATA


def load(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        err(f"数据文件损坏或无法读取：{path}（{e}）")
    if not isinstance(data, list):
        err(f"数据文件格式错误：{path}")
    return data


def save(path, entries):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def parse_date(s):
    try:
        datetime.date.fromisoformat(s)
    except ValueError:
        err(f"日期格式错误，应为 YYYY-MM-DD：{s}")
    return s


def parse_amount(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        err(f"金额必须是数字：{s}")
    if v <= 0:
        err(f"金额必须大于 0：{s}")
    return round(v, 2)


def fmt_amount(v):
    return f"{v:.2f}"


def cmd_add(args):
    entries = load(data_path(args))
    amount = parse_amount(args.amount)
    date = parse_date(args.date) if args.date else datetime.date.today().isoformat()
    category = args.category or "其他"
    note = args.note or ""
    new_id = max((e["id"] for e in entries), default=0) + 1
    entries.append({
        "id": new_id, "amount": amount, "category": category,
        "note": note, "date": date,
    })
    save(data_path(args), entries)
    print(f"已记账 #{new_id}：{date} {category} {fmt_amount(amount)}"
          + (f"（{note}）" if note else ""))


def filter_month(entries, month):
    if not month:
        return entries
    if not __import__("re").fullmatch(r"\d{4}-\d{2}", month):
        err(f"月份格式错误，应为 YYYY-MM：{month}")
    return [e for e in entries if e["date"].startswith(month)]


def sorted_entries(entries):
    return sorted(entries, key=lambda e: (e["date"], e["id"]))


def cmd_list(args):
    entries = sorted_entries(filter_month(load(data_path(args)), args.month))
    if not entries:
        print("暂无记账记录。")
        return
    title = f"记账明细（{args.month}）" if args.month else "记账明细"
    print(f"===== {title} =====")
    for e in entries:
        note = f" 备注：{e['note']}" if e["note"] else ""
        print(f"  #{e['id']}  {e['date']}  [{e['category']}]  {fmt_amount(e['amount'])}" + note)
    total = sum(e["amount"] for e in entries)
    print(f"\n共 {len(entries)} 笔，合计 {fmt_amount(total)}")


def cmd_summary(args):
    entries = filter_month(load(data_path(args)), args.month)
    if not entries:
        print("暂无记账记录。")
        return
    totals = collections.defaultdict(float)
    for e in entries:
        totals[e["category"]] += e["amount"]
    grand = sum(totals.values())
    title = f"分类汇总（{args.month}）" if args.month else "分类汇总"
    print(f"===== {title} =====")
    width = max(len(c) for c in totals)
    peak = max(totals.values())
    for cat in sorted(totals, key=lambda c: -totals[c]):
        v = totals[cat]
        bar = "█" * max(1, round(v / peak * BAR_WIDTH)) if peak > 0 else ""
        print(f"  {cat:<{width}}  {fmt_amount(v):>10}  {bar}")
    print(f"\n{'总计':<{width}}  {fmt_amount(grand):>10}  （{len(entries)} 笔）")


def cmd_rm(args):
    path = data_path(args)
    entries = load(path)
    rid = args.id
    if not any(e["id"] == rid for e in entries):
        err(f"没有这条记录：#{rid}", code=1)
    entries = [e for e in entries if e["id"] != rid]
    save(path, entries)
    print(f"已删除记录 #{rid}")


def add_common(p):
    p.add_argument("--data", default=None, help="数据文件路径（默认 ~/.config/expenses.json）")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="expensetrack", description="终端记账小工具：记一笔、看明细、按分类汇总。")
    ap.add_argument("--version", action="version", version=f"expensetrack {VERSION}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="记一笔支出")
    p.add_argument("amount", help="金额（数字，大于 0）")
    p.add_argument("--category", default="其他", help="分类（默认：其他）")
    p.add_argument("--note", default="", help="备注")
    p.add_argument("--date", default=None, help="日期 YYYY-MM-DD（默认今天）")
    add_common(p)
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="列出记账明细")
    p.add_argument("--month", default=None, help="只看某月 YYYY-MM")
    add_common(p)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("summary", help="按分类汇总")
    p.add_argument("--month", default=None, help="只汇总某月 YYYY-MM")
    add_common(p)
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("rm", help="删除一条记录")
    p.add_argument("id", type=int, help="记录编号")
    add_common(p)
    p.set_defaults(func=cmd_rm)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
