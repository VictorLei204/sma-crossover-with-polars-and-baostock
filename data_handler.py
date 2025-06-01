import baostock as bs
import polars as pl
import os
from datetime import datetime, timedelta

def check_data_completeness(df: pl.DataFrame, start_date: str, end_date: str) -> tuple[bool, str]:
    """
    检查股票数据在指定时间区间内的完整性
    
    Args:
        df: 股票数据DataFrame
        start_date: 开始日期，格式 'YYYY-MM-DD'
        end_date: 结束日期，格式 'YYYY-MM-DD'
    
    Returns:
        tuple[bool, str]: (数据是否完整, 错误信息)
    """
    # 检查数据是否为空
    if len(df) == 0:
        return False, f"未找到股票数据，该股票可能已退市或代码错误"
    
    # 转换日期字符串为datetime对象
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # 获取数据中的第一个和最后一个交易日
    first_trade_date = df.select("date").row(0)[0]
    last_trade_date = df.select("date").row(-1)[0]
    
    # 检查是否在开始日期前上市
    # 允许最早交易日比开始日期晚最多5个交易日（考虑到节假日）
    if first_trade_date > start_dt + timedelta(days=5):
        return False, f"股票在开始日期 {start_date} 后超过5个交易日仍未上市，最早交易日为 {first_trade_date.strftime('%Y-%m-%d')}"
    
    # 检查是否在结束日期后退市
    if last_trade_date < end_dt:
        return False, f"股票在结束日期 {end_date} 前已退市，最后交易日为 {last_trade_date.strftime('%Y-%m-%d')}"
    
    # 检查期间是否有停牌
    # 计算理论上的交易日数量（不包括周末）
    current_date = start_dt
    expected_trading_days = 0
    while current_date <= end_dt:
        if current_date.weekday() < 5:  # 0-4 表示周一到周五
            expected_trading_days += 1
        current_date += timedelta(days=1)
    
    # 计算实际交易日数量
    actual_trading_days = len(df.filter(
        (pl.col("date") >= start_dt) & 
        (pl.col("date") <= end_dt)
    ))
    
    # 如果实际交易日数量明显少于预期，可能存在停牌
    if actual_trading_days < expected_trading_days * 0.9:  # 允许10%的误差
        return False, f"股票在期间内可能存在停牌，预期交易日数：{expected_trading_days}，实际交易日数：{actual_trading_days}"
    
    return True, "数据完整"

def fetch_stock_data(stock_code: str, start_date: str, end_date: str) -> pl.DataFrame:
    """
    从baostock获取股票历史数据，优先从CSV文件读取
    
    Args:
        stock_code: 股票代码，如 'sh.600000'
        start_date: 开始日期，格式 'YYYY-MM-DD'
        end_date: 结束日期，格式 'YYYY-MM-DD'
    
    Returns:
        polars.DataFrame: 包含股票数据的DataFrame
    """
    # 构建CSV文件路径
    csv_file = f"data/{stock_code.replace('.', '_')}.csv"
    
    # 如果CSV文件存在，直接读取
    if os.path.exists(csv_file):
        print(f"从本地文件 {csv_file} 读取数据...")
        df = load_data_from_csv(csv_file)
    else:
        # 如果CSV文件不存在，从baostock获取数据
        print("从baostock获取数据...")
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
        
        # 确保data目录存在
        os.makedirs("data", exist_ok=True)
        
        # 保存数据到CSV文件
        save_data_to_csv(df, csv_file)
        print(f"数据已保存到 {csv_file}")
    
    # 检查数据完整性
    is_complete, message = check_data_completeness(df, start_date, end_date)
    if not is_complete:
        raise ValueError(f"数据不完整: {message}")
    
    # 过滤日期范围
    start_year, start_month, start_day = map(int, start_date.split('-'))
    end_year, end_month, end_day = map(int, end_date.split('-'))
    start_dt = pl.datetime(start_year, start_month, start_day)
    end_dt = pl.datetime(end_year, end_month, end_day)
    df = df.filter(
        (pl.col("date") >= start_dt) & 
        (pl.col("date") <= end_dt)
    )
    
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