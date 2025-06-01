import polars as pl

def add_sma_signals(df: pl.DataFrame, short_window: int, long_window: int) -> pl.DataFrame:
    """
    计算移动平均线并生成交易信号
    
    Args:
        df: 包含价格数据的DataFrame
        short_window: 短期均线周期
        long_window: 长期均线周期
    
    Returns:
        polars.DataFrame: 添加了均线和信号的DataFrame
    """
    # 计算短期和长期移动平均线
    df = df.with_columns([
        pl.col("close").rolling_mean(window_size=short_window).alias(f"sma_{short_window}"),
        pl.col("close").rolling_mean(window_size=long_window).alias(f"sma_{long_window}")
    ])
    
    # 生成交易信号
    df = df.with_columns([
        pl.when(
            (pl.col(f"sma_{short_window}") > pl.col(f"sma_{long_window}")) &
            (pl.col(f"sma_{short_window}").shift(1) <= pl.col(f"sma_{long_window}").shift(1))
        ).then(1)  # 金叉买入信号
        .when(
            (pl.col(f"sma_{short_window}") < pl.col(f"sma_{long_window}")) &
            (pl.col(f"sma_{short_window}").shift(1) >= pl.col(f"sma_{long_window}").shift(1))
        ).then(-1)  # 死叉卖出信号
        .otherwise(0)  # 无信号
        .alias("signal")
    ])
    
    return df 