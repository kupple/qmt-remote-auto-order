import pandas as pd
from typing import List, Dict, Any, Tuple
import copy
import json
import datetime
from .deal import calculate_stock_fee   
class StockPositionCalculator:
    """股票持仓计算器"""
    
    def __init__(self, trades_data: List[Dict[str, Any]]):
        # 首先检查输入数据
        if not trades_data:
            self.trades_df = pd.DataFrame()
            self.stock_codes = []
            self.start_date = None
            self.end_date = None
            self.all_dates = []
            return
            
        # 转换为DataFrame
        self.trades_df = pd.DataFrame(trades_data)
        
        # 确保持仓信息完整
        required_columns = ['stock_code', 'traded_volume', 'traded_price', 'order_type', 'traded_time']
        missing_columns = [col for col in required_columns if col not in self.trades_df.columns]
        if missing_columns:
            raise ValueError(f"交易数据缺少必要列: {missing_columns}")
            
        # 转换交易时间并提取日期
        self.trades_df['traded_time'] = pd.to_datetime(self.trades_df['traded_time'], unit='ms')
        self.trades_df['date'] = self.trades_df['traded_time'].dt.date
        
        # 提取所有涉及的股票代码
        self.stock_codes = self.trades_df['stock_code'].unique().tolist()
        
        # 计算日期范围
        self.start_date = self.trades_df['date'].min()
        self.end_date = self.trades_df['date'].max()
        self.all_dates = pd.date_range(start=self.start_date, end=self.end_date).date
        
        # 按日期排序
        self.trades_df = self.trades_df.sort_values('date')
        
    # 最新持仓数据
    def get_current_positions(self) -> List[Dict]:
        """获取最新的持仓数据"""
        # 获取所有交易
        trades = self.trades_df.sort_values('traded_time')
        
        # 初始化持仓
        positions = {}
        
        # 处理所有交易
        for _, trade in trades.iterrows():
            stock_code = str(trade['stock_code'])
            volume = float(trade['traded_volume'])
            price = float(trade['traded_price'])
            direction = int(trade['order_type'])
            
            if stock_code not in positions:
                positions[stock_code] = {
                    'volume': 0.0,
                    'avg_price': 0.0,
                    'status': '无持仓'
                }
            
            if direction == 23:  # 买入
                # 更新持仓
                positions[stock_code]['volume'] += volume
                # 计算新的平均成本
                total_volume = positions[stock_code]['volume']
                total_cost = (total_volume - volume) * positions[stock_code]['avg_price'] + volume * price
                positions[stock_code]['avg_price'] = total_cost / total_volume
                positions[stock_code]['status'] = '持仓中'
            elif direction == 24:  # 卖出
                positions[stock_code]['volume'] -= volume
                if positions[stock_code]['volume'] <= 0:
                    positions[stock_code]['volume'] = 0
                    positions[stock_code]['avg_price'] = 0
                    positions[stock_code]['status'] = '无持仓'
            
        # 过滤掉volume=0的持仓
        current_positions = [
            {
                'stock_code': stock,
                'volume': pos['volume'],
                'avg_price': pos['avg_price'],
                'status': pos['status']
            }
            for stock, pos in positions.items()
            if pos['volume'] > 0
        ]
        
        return current_positions

    def calculate_daily_positions(self) -> Dict:
        """计算每天的股票持仓列表，包括变化量"""
        # 按日期分组处理交易
        daily_trades = {date: trades for date, trades in self.trades_df.groupby('date')}
        
        # 初始化持仓
        current_positions = {}  # 当前持仓: {stock_code: {'volume': float, 'avg_price': float, 'status': str}}
        daily_records = {}
        
        # 获取所有交易的股票代码
        all_stock_codes = self.trades_df['stock_code'].unique()
        
        # 初始化所有股票的初始持仓为0
        for stock_code in all_stock_codes:
            current_positions[str(stock_code)] = {
                'volume': 0.0,
                'avg_price': 0.0,
                'status': '无持仓'
            }
        
        # 处理每一天
        for date in self.all_dates:
            date_str = date.strftime('%Y-%m-%d')
            
            # 初始化当日记录
            daily_records[date_str] = {
                'positions': copy.deepcopy(current_positions),  # 使用深拷贝
                'changes': {},                          # 当日变化
                'commission': 0.0,                      # 当日手续费
                'trades': []                            # 当日交易记录
            }
            
            # 如果当天有交易，处理交易并更新持仓
            if date in daily_trades:
                date_trades = daily_trades[date]
                daily_changes, new_positions = self._process_date_trades(date_trades, copy.deepcopy(current_positions))
                
                # 更新当前持仓
                current_positions = new_positions
                
                # 更新当日记录
                daily_records[date_str]['positions'] = copy.deepcopy(current_positions)
                daily_records[date_str]['changes'] = daily_changes
                
                # 添加交易记录和手续费信息
                for _, trade in date_trades.iterrows():
                    stock_code = trade['stock_code']
                    volume = trade['traded_volume']
                    price = trade['traded_price']
                    direction = trade['order_type']
                    
                    # 计算手续费
                    commission = calculate_stock_fee(
                        'buy' if direction == 23 else 'sell',
                        price,
                        volume
                    )
                    
                    # 累加当日手续费
                    daily_records[date_str]['commission'] += commission
                    
                    # # 添加交易记录
                    daily_records[date_str]['trades'].append({
                        'stock_code': stock_code,
                        'volume': volume,
                        'price': price,
                        'direction': '买入' if direction == 23 else '卖出',
                        'commission': commission,
                        'total_amount': volume * price + commission if direction == 23 else volume * price - commission
                    })
            else:
                # 如果当天没有交易，持仓保持前一天的状态
                # 更新当日记录（已经初始化为当前持仓）
                daily_records[date_str]['changes'] = {}  # 当日无变化
        return daily_records
    
    def _process_date_trades(self, date_trades: pd.DataFrame, initial_positions: Dict[str, Dict[str, float]]) -> Tuple[Dict, Dict]:
        """处理单日交易并更新持仓，返回当日变化和新的持仓"""
        daily_changes = {}  # 记录当日每只股票的变化
        current_positions = initial_positions.copy()  # 创建新的持仓副本
        

        
        # 确保持仓信息完整
        for stock_code in initial_positions:
            if stock_code not in current_positions:
                current_positions[stock_code] = initial_positions[stock_code].copy()
        
        for _, trade in date_trades.iterrows():
            stock_code = str(trade['stock_code'])
            volume = float(trade['traded_volume'])
            price = float(trade['traded_price'])
            direction = int(trade['order_type'])
            
            
            # 初始化股票持仓（如果不存在）
            if stock_code not in current_positions:
                current_positions[stock_code] = {
                    'volume': 0.0, 
                    'avg_price': 0.0, 
                    'status': '无持仓'
                }
            
            if stock_code not in daily_changes:
                daily_changes[stock_code] = {
                    'volume_change': 0.0, 
                    'price_change': 0.0, 
                    'trades': [],
                    'avg_price': current_positions[stock_code]['avg_price']
                }
            
            prev_avg_price = current_positions[stock_code]['avg_price']
            
            # 记录交易详情
            trade_info = {
                'direction': 'buy' if direction == 23 else 'sell',
                'volume': volume,
                'price': price
            }
            daily_changes[stock_code]['trades'].append(trade_info)
            
            # 计算变化量
            if direction == 23:  # 买入
                daily_changes[stock_code]['volume_change'] += volume
                self._process_buy(current_positions[stock_code], volume, price)
            elif direction == 24:  # 卖出
                daily_changes[stock_code]['volume_change'] -= volume
                self._process_sell(current_positions[stock_code], volume, price)
            
            # 记录价格变化
            new_avg_price = current_positions[stock_code]['avg_price']
            daily_changes[stock_code]['price_change'] = new_avg_price - prev_avg_price
            daily_changes[stock_code]['avg_price'] = new_avg_price
            
            # 更新状态
            current_positions[stock_code]['status'] = (
                '清仓' if current_positions[stock_code]['volume'] <= 0 else '持仓'
            )
        
        return daily_changes, current_positions
    
    def _process_buy(self, position_info: Dict[str, float], buy_volume: float, buy_price: float) -> None:
        """处理买入操作"""
        # 获取当前持仓信息
        current_volume = float(position_info['volume'])
        current_avg_price = float(position_info['avg_price'])
        
        # 计算新的持仓数量
        new_volume = current_volume + buy_volume
        
        # 计算新的平均成本
        if current_volume == 0:
            new_avg_price = buy_price
        else:
            # 计算新的平均成本
            new_avg_price = (current_volume * current_avg_price + buy_volume * buy_price) / new_volume
        
        # 更新持仓信息
        position_info['volume'] = new_volume
        position_info['avg_price'] = new_avg_price
        position_info['status'] = '持仓'
        
    
    def _process_sell(self, position_info: Dict[str, float], sell_volume: float, sell_price: float) -> None:
        """处理卖出操作"""
        # 获取当前持仓信息
        current_volume = float(position_info['volume'])
        current_avg_price = float(position_info['avg_price'])
        
        # 计算卖出后的剩余数量
        remaining_volume = current_volume - sell_volume
        
        # 更新持仓数量
        position_info['volume'] = remaining_volume
        
        # 如果持仓数量为0，保持平均成本不变
        if remaining_volume <= 0:
            position_info['volume'] = 0
            position_info['avg_price'] = current_avg_price
            position_info['status'] = '清仓'
        else:
            position_info['status'] = '持仓'
        

class StrategyPerformanceAnalyzer:
    """策略绩效分析器"""
    
    def __init__(self, trades: List[Dict], initial_capital: float = 100000.0):
        """初始化策略分析器"""
        self.trades = pd.DataFrame(trades)
        self.trades['traded_time'] = pd.to_datetime(self.trades['traded_time'], unit='ms')
        self.trades = self.trades.sort_values('traded_time')
        self.initial_capital = initial_capital
        self.daily_equity = []  # 每日权益记录
    
    def calculate_performance(self) -> Dict:
        """计算策略绩效"""
        # 初始化变量
        cash = self.initial_capital
        positions = {}  # 当前持仓: {stock_code: {'volume': float, 'avg_price': float}}
        current_date = None
        daily_equity = []
        
        # 处理每笔交易
        for _, trade in self.trades.iterrows():
            trade_date = trade['traded_time'].date()
            stock_code = trade['stock_code']
            volume = trade['traded_volume']
            price = trade['traded_price']
            direction = trade['order_type']
            
            # 新的一天开始，记录前一天的权益
            if current_date is not None and trade_date != current_date:
                portfolio_value = sum(pos['volume'] * pos['avg_price'] for pos in positions.values())
                daily_equity.append({
                    'date': current_date,
                    'cash': cash,
                    'portfolio_value': portfolio_value,
                    'total_equity': cash + portfolio_value
                })
            
            current_date = trade_date
            
            # 处理买入
            if direction == 23:
                # 计算买入手续费
                commission = calculate_stock_fee('buy', price, volume)
                total_cost = volume * price + commission
                
                if total_cost > cash:
                    raise ValueError(f"现金不足: {trade}")
                cash -= total_cost
                
                if stock_code not in positions:
                    positions[stock_code] = {'volume': 0, 'avg_price': 0}
                
                # 计算新的平均成本
                total_volume = positions[stock_code]['volume'] + volume
                total_cost = positions[stock_code]['volume'] * positions[stock_code]['avg_price'] + volume * price
                positions[stock_code] = {'volume': total_volume, 'avg_price': total_cost / total_volume}
            
            # 处理卖出
            elif direction == 24:
                if stock_code not in positions or positions[stock_code]['volume'] < volume:
                    raise ValueError(f"持仓不足: {trade}")
                
                # 计算卖出手续费
                commission = calculate_stock_fee('sell', price, volume)
                total_proceed = volume * price - commission
                cash += total_proceed
                
                # 更新持仓
                positions[stock_code]['volume'] -= volume
                if positions[stock_code]['volume'] <= 0:
                    positions[stock_code]['volume'] = 0
                    positions[stock_code]['avg_price'] = 0
        
        # 记录最后一天的权益
        if positions:
            portfolio_value = sum(pos['volume'] * pos['avg_price'] for pos in positions.values())
            daily_equity.append({
                'date': current_date,
                'cash': cash,
                'portfolio_value': portfolio_value,
                'total_equity': cash + portfolio_value
            })
        
        # 保存每日权益数据
        self.daily_equity = pd.DataFrame(daily_equity)
        
        # 计算绩效指标
        return self._calculate_performance_metrics()
    
    def _calculate_performance_metrics(self) -> Dict:
        """计算绩效指标"""
        if not len(self.daily_equity):
            return {
                '总收益率(%)': 0.0,
                '最大回撤(%)': 0.0,
                '最大回撤区间': '无',
                '每日平均收益率(%)': 0.0,
                '夏普比率': 0.0
            }
        
        # 计算每日收益率
        self.daily_equity['daily_return'] = self.daily_equity['total_equity'].pct_change()
        
        # 总收益率
        total_return = (self.daily_equity['total_equity'].iloc[-1] / self.initial_capital - 1) * 100
        
        # 最大回撤
        self.daily_equity['cumulative_max'] = self.daily_equity['total_equity'].cummax()
        self.daily_equity['drawdown'] = (self.daily_equity['cumulative_max'] - self.daily_equity['total_equity']) / self.daily_equity['cumulative_max'] * 100
        
        # 找到最大回撤的日期
        max_drawdown_row = self.daily_equity[self.daily_equity['drawdown'] == self.daily_equity['drawdown'].max()].iloc[0]
        max_drawdown_date = max_drawdown_row['date']
        max_drawdown = max_drawdown_row['drawdown']
        
        # 找到回撤开始的峰值日期
        peak_df = self.daily_equity[self.daily_equity['date'] <= max_drawdown_date]
        peak_row = peak_df[peak_df['total_equity'] == peak_df['cumulative_max']].iloc[-1]
        peak_date = peak_row['date']
        
        # 找到回撤结束的谷底日期
        trough_df = self.daily_equity[self.daily_equity['date'] >= max_drawdown_date]
        trough_row = trough_df[trough_df['date'] == max_drawdown_date].iloc[0]
        trough_date = max_drawdown_date
        
        max_drawdown_period = f"{peak_date} 至 {trough_date}"
        
        # 每日平均收益率
        avg_daily_return = self.daily_equity['daily_return'].mean() * 100
        
        # 夏普比率 (假设无风险收益率为0)
        risk_free_rate = 0
        daily_risk_free = (1 + risk_free_rate) ** (1/252) - 1
        excess_returns = self.daily_equity['daily_return'] - daily_risk_free
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * (252 ** 0.5) if excess_returns.std() != 0 else 0
        
        return {
            '总收益率(%)': round(total_return, 2),
            '最大回撤(%)': round(max_drawdown, 2),
            '最大回撤区间': max_drawdown_period,
            '每日平均收益率(%)': round(avg_daily_return, 4),
            '夏普比率': round(sharpe_ratio, 2)
        }

def analyze_stock_data(trades: List[Dict], initial_capital: float = 100000.0) -> Dict:
    """分析股票交易数据并返回综合结果"""
    # 计算每日持仓（含变化量）
    position_calculator = StockPositionCalculator(trades)
    daily_positions = position_calculator.calculate_daily_positions()
    
    # 将daily_positions转换为按日期排序的数组格式
    sorted_daily_positions = []
    for date_str in sorted(daily_positions.keys()):
        # 将持仓转换为数组格式
        positions_array = []
        for stock, pos in daily_positions[date_str]['positions'].items():
            if pos['volume'] > 0:
                positions_array.append({
                    'stock_code': stock,
                    'volume': pos['volume'],
                    'avg_price': pos['avg_price'],
                    'status': pos['status']
                })
        
        sorted_daily_positions.append({
            'date': date_str,
            'positions': positions_array,
            'changes': daily_positions[date_str]['changes'],
            'commission': daily_positions[date_str]['commission'],
            'trades': daily_positions[date_str]['trades']
        })
    
    # 计算策略绩效
    # performance_analyzer = StrategyPerformanceAnalyzer(trades, initial_capital)
    # performance = performance_analyzer.calculate_performance()
    return {
        "daily_positions": sorted_daily_positions,
        # "performance": performance,
        # "daily_equity": json.dumps(performance_analyzer.daily_equity.to_dict('records'), default=lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else x)  # 提供每日权益数据
    }