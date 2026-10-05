# expensetrack

终端记账小工具：记一笔、看明细、按分类汇总。纯标准库，纯本地，数据就是一个 JSON 文件。

## 安装

零依赖，Python 3.10+：

```bash
cd expensetrack
python3 -m expensetrack add 25.5 --category 餐饮 --note "午饭"
```

数据默认存在 `~/.config/expenses.json`，可用 `--data` 指向别处。

## 用法

```bash
# 记一笔（日期默认今天）
expensetrack add 25.5 --category 餐饮 --note "午饭"
expensetrack add 120 --category 交通 --date 2026-10-01

# 看明细（按日期排序）
expensetrack list
expensetrack list --month 2026-10

# 按分类汇总（带比例条）
expensetrack summary
expensetrack summary --month 2026-10

# 删除一条
expensetrack rm 3
```

汇总示例：

```
===== 分类汇总（2026-10）=====
  餐饮       68.50  ████████████████████
  交通       32.00  █████████
  其他       12.00  ████

总计       112.50  （4 笔）
```

## 设计取舍

- 金额必须大于 0（退款/收入请记负数？不支持——这是支出账本，收入另记）。
- 金额保留 2 位小数；分类默认"其他"。
- 写文件是原子的（写临时文件 + `os.replace`），中途断电不会写坏一半。
- 按 `(日期, 编号)` 排序；编号是自增整数，删掉的编号不复用。

## 诚实说明

- 这是一个**简单的流水账本**，不是会计软件：没有复式记账、没有预算告警、没有多币种。
- 数据是本地 JSON 明文；多设备同步、加密都不在范围内。
- 月份过滤只认 `YYYY-MM`；日期只认 `YYYY-MM-DD`。

## 已知局限

- 不做汇率换算；所有金额视为同一货币。
- `rm` 直接删除，不进回收站。
- 统计口径就是加总，没有去重/对账逻辑。

## License

MIT，Copyright (c) 2026 ljiang9。
