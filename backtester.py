import polars as pl
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Trade:
    date: str
    type: str  # 'buy' or 'sell'
    price: float
    shares: int
    value: float

class SMABacktester:
    def __init__(self, initial_capital: float, stock_data: pl.DataFrame):
        """
        初始化回测器
        
        Args:
            initial_capital: 初始资金
            stock_data: 包含价格和信号的DataFrame
        """
        self.initial_capital = initial_capital
        self.stock_data = stock_data
        self.cash = initial_capital
        self.shares_held = 0
        self.trades: List[Trade] = []
        self.portfolio_history: List[Dict] = []
    
    def run_backtest(self) -> None:
        """执行回测"""
        for i in range(len(self.stock_data)):
            current_row = self.stock_data.row(i)
            current_date = current_row[0]
            current_price = current_row[3]  # close price
            signal = current_row[-1]  # signal column
            
            # 更新当前持仓市值
            position_value = self.shares_held * current_price
            total_value = self.cash + position_value
            
            # 记录每日资产状态
            self.portfolio_history.append({
                'date': current_date,
                'cash': self.cash,
                'position_value': position_value,
                'total_value': total_value
            })
            
            # 处理交易信号
            if signal == 1 and self.shares_held == 0:  # 买入信号
                shares_to_buy = int(self.cash / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.cash -= cost
                    self.shares_held = shares_to_buy
                    self.trades.append(Trade(
                        date=str(current_date),
                        type='buy',
                        price=current_price,
                        shares=shares_to_buy,
                        value=cost
                    ))
            
            elif signal == -1 and self.shares_held > 0:  # 卖出信号
                value = self.shares_held * current_price
                self.cash += value
                self.trades.append(Trade(
                    date=str(current_date),
                    type='sell',
                    price=current_price,
                    shares=self.shares_held,
                    value=value
                ))
                self.shares_held = 0
    
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