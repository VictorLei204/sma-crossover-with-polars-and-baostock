import matplotlib.pyplot as plt
import polars as pl


def plot_equity_curve(portfolio_history: pl.DataFrame, title: str = "Equity Curve") -> None:
    """
    绘制资产净值曲线
    
    Args:
        portfolio_history: 包含每日资产价值的DataFrame
        title: 图表标题
    """
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_history['date'], portfolio_history['total_value'])
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.grid(True)
    plt.show()

def plot_signals_on_price(stock_data: pl.DataFrame, short_window: int, long_window: int, title: str = "Price, SMAs, and Signals") -> None:
    """
    绘制价格、均线和交易信号
    
    Args:
        stock_data: 包含价格和信号的DataFrame
        short_window: 短期均线周期
        long_window: 长期均线周期
        title: 图表标题
    """
    plt.figure(figsize=(12, 6))
    
    # 绘制收盘价
    plt.plot(stock_data['date'], stock_data['close'], label='Close Price', alpha=0.5)
    
    # 绘制均线
    plt.plot(stock_data['date'], stock_data[f'sma_{short_window}'], 
             label=f'{short_window}-day SMA', alpha=0.7)
    plt.plot(stock_data['date'], stock_data[f'sma_{long_window}'], 
             label=f'{long_window}-day SMA', alpha=0.7)
    
    # 绘制买入信号
    buy_signals = stock_data.filter(pl.col('signal') == 1)
    plt.scatter(buy_signals['date'], buy_signals['close'], 
                marker='^', color='g', label='Buy Signal', alpha=1)
    
    # 绘制卖出信号
    sell_signals = stock_data.filter(pl.col('signal') == -1)
    plt.scatter(sell_signals['date'], sell_signals['close'], 
                marker='v', color='r', label='Sell Signal', alpha=1)
    
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show() 