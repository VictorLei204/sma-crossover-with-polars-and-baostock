import data_handler as dh
import strategy as st
import backtester as bt
import performance as pf
import visualizer as vis

def main():
    # 设置参数
    stock_code = "sh.600000"  # 浦发银行
    start_date = "2020-01-01"
    end_date = "2024-12-31"
    short_window = 20
    long_window = 60
    initial_capital = 100000
    
    # 获取数据
    print("获取股票数据...")
    df = dh.fetch_stock_data(stock_code, start_date, end_date)
    
    # 保存数据到CSV（可选）
    dh.save_data_to_csv(df, f"{stock_code.replace('.', '_')}_data.csv")
    
    # 计算均线和信号
    print("计算技术指标和交易信号...")
    df_with_signals = st.add_sma_signals(df, short_window, long_window)
    
    # 执行回测
    print("执行回测...")
    backtester = bt.SMABacktester(initial_capital, df_with_signals)
    backtester.run_backtest()
    
    # 获取回测结果
    portfolio_history = backtester.get_portfolio_history()
    trade_log = backtester.get_trade_log()
    
    # 计算绩效指标
    print("\n=== 回测结果 ===")
    total_return = pf.calculate_total_return(portfolio_history)
    annual_return = pf.calculate_annualized_return(portfolio_history)
    sharpe_ratio = pf.calculate_sharpe_ratio(portfolio_history)
    max_drawdown = pf.calculate_max_drawdown(portfolio_history)
    
    print(f"总收益率: {total_return:.2%}")
    print(f"年化收益率: {annual_return:.2%}")
    print(f"夏普比率: {sharpe_ratio:.2f}")
    print(f"最大回撤: {max_drawdown:.2%}")
    
    # 保存交易记录（可选）
    trade_log.write_csv(f"{stock_code.replace('.', '_')}_trades.csv")
    
    # 绘制图表
    print("\n生成图表...")
    vis.plot_equity_curve(portfolio_history, f"{stock_code} Equity Curve")
    vis.plot_signals_on_price(df_with_signals, short_window, long_window, 
                            f"{stock_code} Price and Signals")

if __name__ == "__main__":
    main() 