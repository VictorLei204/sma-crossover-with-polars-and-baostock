# SMA Crossover Strategy Backtest System

基于双移动平均线交叉策略的回测，使用 `baostock` 获取A股数据，`polars` 进行数据处理。

## 功能

- 获取股票历史数据
- 计算移动平均线和交易信号
- 模拟交易执行
- 计算绩效指标
- 生成交易记录和图表

## 环境要求

- baostock
- polars
- matplotlib

## 使用

1. 配置 `main.py` 参数：
   - 股票代码（如：'sh.600000'）
   - 回测起止日期
   - 均线周期
   - 初始资金
2. 交易费用在`backtester.py`中配置
3. 运行回测

## 输出

- 绩效指标：总收益率、年化收益率、夏普比率、最大回撤
- 交易记录：CSV文件
- 图表：资产净值、价格和信号

## 注意事项

- 仅供学习研究使用
- 使用前复权数据

## 许可证

MIT License
