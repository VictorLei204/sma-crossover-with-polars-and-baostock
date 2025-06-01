import numpy as np
import polars as pl


def calculate_total_return(portfolio_history: pl.DataFrame) -> float:
    """
    计算总收益率
    
    Args:
        portfolio_history: 包含每日资产价值的DataFrame
    
    Returns:
        float: 总收益率
    """
    initial_value = portfolio_history.select("total_value").row(0)[0]
    final_value = portfolio_history.select("total_value").row(-1)[0]
    return (final_value / initial_value) - 1

def calculate_annualized_return(portfolio_history: pl.DataFrame, num_trading_days_year: int = 252) -> float:
    """
    计算年化收益率
    
    Args:
        portfolio_history: 包含每日资产价值的DataFrame
        num_trading_days_year: 一年的交易日数量
    
    Returns:
        float: 年化收益率
    """
    total_return = calculate_total_return(portfolio_history)
    num_days = len(portfolio_history)
    return (1 + total_return) ** (num_trading_days_year / num_days) - 1

def calculate_sharpe_ratio(portfolio_history: pl.DataFrame, risk_free_rate: float = 0.02, num_trading_days_year: int = 252) -> float:
    """
    计算夏普比率
    
    Args:
        portfolio_history: 包含每日资产价值的DataFrame
        risk_free_rate: 无风险利率
        num_trading_days_year: 一年的交易日数量
    
    Returns:
        float: 夏普比率
    """
    # 计算每日收益率
    daily_returns = portfolio_history.with_columns([
        pl.col("total_value").pct_change().alias("daily_return")
    ]).select("daily_return").drop_nulls()
    
    # 计算年化收益率和波动率
    annual_return = calculate_annualized_return(portfolio_history)
    annual_volatility = float(daily_returns.select("daily_return").std().row(0)[0]) * np.sqrt(num_trading_days_year)
    
    # 计算夏普比率
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    return float(sharpe_ratio)

def calculate_max_drawdown(portfolio_history: pl.DataFrame) -> float:
    """
    计算最大回撤
    
    Args:
        portfolio_history: 包含每日资产价值的DataFrame
    
    Returns:
        float: 最大回撤
    """
    # 计算累计最大值
    portfolio_history = portfolio_history.with_columns([
        pl.col("total_value").cum_max().alias("peak")
    ])
    
    # 计算回撤
    portfolio_history = portfolio_history.with_columns([
        ((pl.col("total_value") - pl.col("peak")) / pl.col("peak")).alias("drawdown")
    ])
    
    # 返回最大回撤
    return abs(float(portfolio_history.select("drawdown").min().row(0)[0])) 