# SMA Crossover with Polars and Baostock

基于双移动平均线交叉策略的回测，使用 `baostock` 获取A股数据，`polars` 进行数据处理。

## 功能

- 获取股票历史数据
- 计算移动平均线和交易信号
- 模拟交易执行
- 计算绩效指标
- 生成交易记录和图表
- 配置文件管理

## 环境要求

- baostock
- polars
- matplotlib
- 在一些Linux发行版中，为确保图像正确显示，需要安装python3-tk(如`sudo apt install python3-tk`)，并使用对应版本的Python解释器，如`python3-tk/noble,now 3.12.3-0ubuntu1 amd64`对应`Python 3.12.3`(其他系统未经测试)

## 使用

### 基本使用

建议使用`uv`管理环境

```bash
uv sync
uv run main.py
```

### 配置文件
程序会自动读取 `config.json` 配置文件。如果文件不存在，会自动创建默认配置。

配置文件示例：
```json
{
  "stock_code": "sh.600000",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "short_window": 20,
  "long_window": 60,
  "initial_capital": 100000,
  "trading_fees": {
    "commission_rate": 0.0003,
    "stamp_tax_rate": 0.001,
    "transfer_fee_rate": 0.001,
    "min_commission": 5.0
  }
}
```

## 输出

- 绩效指标：总收益率、年化收益率、夏普比率、最大回撤
- 交易记录：CSV文件
- 图表：资产净值、价格和信号

## 注意事项

- 仅供学习研究使用
- 使用前复权数据

## 许可证

MIT License
