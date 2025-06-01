# SMA Crossover Strategy Backtest System

这是一个基于双移动平均线（SMA）交叉策略的量化回测系统。该系统使用 `baostock` 获取中国A股市场的历史数据，并使用 `polars` 进行高效的数据处理和计算。

## 功能特点

- 从 baostock 获取股票历史数据
- 计算短期和长期移动平均线
- 基于均线交叉生成交易信号
- 模拟交易执行和资金管理
- 计算关键绩效指标（总收益率、年化收益率、夏普比率、最大回撤）
- 生成交易记录和可视化图表

## 数据说明

本系统使用前复权数据进行回测，原因如下：
1. 前复权价格更接近实际交易价格，更适合资金量较小的投资者
2. 回测区间较短，前复权对近期价格的影响较小
3. 更符合实际交易决策习惯

注意：前复权数据已经考虑了历史分红的影响，使得价格序列具有连续性，适合技术分析。

## 环境要求

- Python 3.12
- baostock >= 0.8.9
- polars >= 1.30.0
- matplotlib >= 3.10.3

## 安装

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/sma-crossover-with-polars-and-baostock.git
cd sma-crossover-with-polars-and-baostock
```

2. 创建并激活虚拟环境（可选但推荐）：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 修改 `main.py` 中的参数：
   - `stock_code`: 股票代码（例如：'sh.600000'）
   - `start_date`: 回测开始日期
   - `end_date`: 回测结束日期
   - `short_window`: 短期均线周期
   - `long_window`: 长期均线周期
   - `initial_capital`: 初始资金

2. 运行回测：
```bash
python main.py
```

## 输出结果

- 控制台输出：
  - 总收益率
  - 年化收益率
  - 夏普比率
  - 最大回撤

- 生成文件：
  - `{stock_code}_data.csv`: 股票历史数据
  - `{stock_code}_trades.csv`: 交易记录

- 可视化图表：
  - 资产净值曲线
  - 价格、均线和交易信号图

## 项目结构

- `data_handler.py`: 数据获取和处理
- `strategy.py`: 策略实现和信号生成
- `backtester.py`: 回测引擎
- `performance.py`: 绩效指标计算
- `visualizer.py`: 结果可视化
- `main.py`: 主程序

## 注意事项

- 本系统仅用于学习和研究目的
- 回测结果不代表未来表现
- 未考虑交易成本和滑点
- 使用前请确保已正确安装所有依赖

## 许可证

MIT License
