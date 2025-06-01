import baostock as bs
import polars as pl

def fetch_stock_data(stock_code: str, start_date: str, end_date: str) -> pl.DataFrame:
    """
    从baostock获取股票历史数据
    
    Args:
        stock_code: 股票代码，如 'sh.600000'
        start_date: 开始日期，格式 'YYYY-MM-DD'
        end_date: 结束日期，格式 'YYYY-MM-DD'
    
    Returns:
        polars.DataFrame: 包含股票数据的DataFrame
    """
    # 登录系统
    bs.login()
    
    # 获取数据
    rs = bs.query_history_k_data_plus(
        stock_code,
        "date,code,open,high,low,close,volume,amount,turn",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="1"  # 复权类型，1：前复权
    )
    
    # 转换为DataFrame
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    # 登出系统
    bs.logout()
    
    # 创建DataFrame并处理数据类型
    df = pl.DataFrame(
        data_list,
        schema={
            "date": pl.String,
            "code": pl.String,
            "open": pl.Float64,
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "volume": pl.Float64,
            "amount": pl.Float64,
            "turn": pl.Float64
        },
        orient="row"  # 明确指定行方向
    )
    
    # 转换日期格式并排序
    df = df.with_columns([
        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d"),
    ]).sort("date")
    
    return df

def save_data_to_csv(df: pl.DataFrame, filepath: str) -> None:
    """
    将DataFrame保存为CSV文件
    
    Args:
        df: 要保存的DataFrame
        filepath: 保存路径
    """
    df.write_csv(filepath)

def load_data_from_csv(filepath: str) -> pl.DataFrame:
    """
    从CSV文件加载数据
    
    Args:
        filepath: CSV文件路径
    
    Returns:
        polars.DataFrame: 加载的数据
    """
    df = pl.read_csv(filepath)
    
    # 转换日期格式并排序
    df = df.with_columns([
        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d"),
    ]).sort("date")
    
    return df 