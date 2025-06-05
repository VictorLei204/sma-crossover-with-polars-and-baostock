from dataclasses import dataclass

import polars as pl


@dataclass
class Trade:
    date: str
    type: str  # 'buy' or 'sell'
    price: float
    shares: int
    value: float

class SMABacktester:
    def __init__(self, stock_data: pl.DataFrame, initial_capital: float = 100000.0):
        """
        初始化回测器
        
        Args:
            stock_data: 包含股票数据的DataFrame
            initial_capital: 初始资金
        """
        self.stock_data = stock_data
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.shares = 0
        self.portfolio_history = []
        self.trades = []  # 初始化交易记录列表
        
        # 交易费用设置
        self.commission_rate = 0.0003  # 佣金率：万分之三
        self.stamp_tax_rate = 0.001    # 印花税率：千分之一
        self.transfer_fee_rate = 0.001  # 过户费率：每1000股1元，按比例计算
    
    def calculate_trading_fees(self, price: float, shares: int, is_buy: bool) -> float:
        """
        计算交易费用
        
        Args:
            price: 交易价格
            shares: 交易股数
            is_buy: 是否为买入操作
        
        Returns:
            float: 交易费用总额
        """
        amount = price * shares
        fees = 0
        
        # 佣金（最低5元）
        commission = amount * self.commission_rate
        fees += max(commission, 5.0)
        
        # 印花税（仅卖出时收取）
        if not is_buy:
            fees += amount * self.stamp_tax_rate
        
        # 过户费（上海股票收取）
        if self.stock_data.select("code").row(0)[0].startswith("sh"):
            fees += shares * self.transfer_fee_rate
        
        return fees
    
    def run_backtest(self, signals: pl.DataFrame | None = None) -> pl.DataFrame:
        """
        执行回测
        
        Args:
            signals: 包含交易信号的DataFrame，如果为None则使用stock_data中的signal列
        
        Returns:
            plars.DataFrame: 回测结果
        """
        # 合并数据和信号
        if signals is None:
            df = self.stock_data
        else:
            df = self.stock_data.join(signals, on="date")
        
        # 遍历每个交易日
        for row in df.iter_rows(named=True):
            date = row["date"]
            price = row["open"]  # 使用开盘价进行交易
            signal = row["signal"]
            
            # 检查是否停牌（成交量为0）
            if row["volume"] == 0:
                # 记录资产价值（使用前一日收盘价）
                total_value = self.cash + self.shares * row["close"]
                self.portfolio_history.append({
                    "date": date,
                    "cash": self.cash,
                    "shares": self.shares,
                    "stock_value": self.shares * row["close"],
                    "total_value": total_value
                })
                continue
            
            # 根据信号执行交易
            if signal == 1 and self.shares == 0:  # 买入信号
                # 检查是否涨停（开盘价等于涨停价）
                prev_close = row["close"] * 1.1  # 涨停价
                if price >= prev_close:
                    # 涨停无法买入，记录资产价值
                    total_value = self.cash + self.shares * row["close"]
                    self.portfolio_history.append({
                        "date": date,
                        "cash": self.cash,
                        "shares": self.shares,
                        "stock_value": self.shares * row["close"],
                        "total_value": total_value
                    })
                    continue
                
                # 计算可买入的股数（考虑手续费）
                max_shares = int(self.cash / (price * (1 + self.commission_rate + self.transfer_fee_rate)))
                # 向下取整到最接近的100股
                max_shares = (max_shares // 100) * 100
                
                if max_shares > 0:
                    # 计算交易费用
                    fees = self.calculate_trading_fees(price, max_shares, True)
                    # 执行交易
                    self.shares = max_shares
                    self.cash -= (price * max_shares + fees)
                    # 记录交易
                    self.trades.append(Trade(
                        date=date,
                        type="buy",
                        price=price,
                        shares=max_shares,
                        value=price * max_shares
                    ))
            
            elif signal == -1 and self.shares > 0:  # 卖出信号
                # 检查是否跌停（开盘价等于跌停价）
                prev_close = row["close"] * 0.9  # 跌停价
                if price <= prev_close:
                    # 跌停无法卖出，记录资产价值
                    total_value = self.cash + self.shares * row["close"]
                    self.portfolio_history.append({
                        "date": date,
                        "cash": self.cash,
                        "shares": self.shares,
                        "stock_value": self.shares * row["close"],
                        "total_value": total_value
                    })
                    continue
                
                # 计算交易费用
                fees = self.calculate_trading_fees(price, self.shares, False)
                # 执行交易
                self.cash += (price * self.shares - fees)
                # 记录交易
                self.trades.append(Trade(
                    date=date,
                    type="sell",
                    price=price,
                    shares=self.shares,
                    value=price * self.shares
                ))
                self.shares = 0
            
            # 记录每日资产价值（使用收盘价计算）
            total_value = self.cash + self.shares * row["close"]
            self.portfolio_history.append({
                "date": date,
                "cash": self.cash,
                "shares": self.shares,
                "stock_value": self.shares * row["close"],
                "total_value": total_value
            })
        
        # 转换为DataFrame
        return pl.DataFrame(self.portfolio_history)
    
    def get_portfolio_history(self) -> pl.DataFrame:
        """获取回测期间的资产历史"""
        return pl.DataFrame(self.portfolio_history)
    
    def get_trade_log(self) -> pl.DataFrame:
        """获取交易记录"""
        return pl.DataFrame([
            {
                'date': trade.date,
                'type': trade.type,
                'price': trade.price,
                'shares': trade.shares,
                'value': trade.value
            }
            for trade in self.trades
        ]) 