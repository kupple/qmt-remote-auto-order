import time
import random
import threading
from typing import Optional
from api.trading_related.deal import calculate_stock_fee
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QmtTradingSimulator')

class AccountType:
    STOCK = 1
    FUTURE = 2
    OPTION = 3

# 交易类型定义
class OrderType:
    STOCK_BUY = 23
    STOCK_SELL = 24

class PriceType:
    LIMIT_PRICE = 1  # 限价
    BEST_5 = 3  # 五档即成剩撤

class OrderStatus:
    SUBMITTED = 1  # 已提交
    PARTIAL = 2  # 部分成交
    FILLED = 3  # 全部成交
    CANCELLED = 4  # 已撤单
    FAILED = 5  # 废单

class Direction:
    LONG = 1  # 多头
    SHORT = 2  # 空头 (股票不支持)

# XtOrder对象
class XtOrder:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.order_id = 0
        self.order_sysid = ""
        self.order_time = 0  # 报单时间
        self.order_type = OrderType.STOCK_BUY
        self.order_volume = 0
        self.price_type = PriceType.LIMIT_PRICE
        self.price = 0.0
        self.traded_volume = 0
        self.traded_price = 0.0
        self.order_status = OrderStatus.SUBMITTED
        self.status_msg = ""
        self.strategy_name = ""
        self.order_remark = ""
        self.direction = Direction.LONG

# XtAsset对象
class XtAsset:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.total_asset = 0.0  # 总资产
        self.cash = 0.0  # 可用资金
        self.market_value = 0.0  # 证券市值
        self.frozen_cash = 0.0  # 冻结资金
    

# XtTrade对象
class XtTrade:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.order_type = OrderType.STOCK_BUY
        self.traded_id = ""
        self.traded_time = 0  # 成交时间
        self.traded_price = 0.0
        self.traded_volume = 0
        self.traded_amount = 0.0
        self.order_id = 0
        self.order_sysid = ""
        self.strategy_name = ""
        self.order_remark = ""
        self.direction = Direction.LONG

# XtPosition对象
class XtPosition:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.volume = 0
        self.can_use_volume = 0  # 可用数量 (考虑T+1等限制)
        self.yesterday_volume = 0  # 昨日持仓量
        self.today_buy_volume = 0  # 今日买入量
        self.open_price = 0.0
        self.market_value = 0.0
        self.frozen_volume = 0
        self.on_road_volume = 0
        self.avg_price = 0.0
        self.direction = Direction.LONG

# XtOrderResponse对象
class XtOrderResponse:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.order_id = 0
        self.strategy_name = ""
        self.order_remark = ""
        self.seq = 0
        self.error_id = 0
        self.error_msg = ""

# XtOrderError对象
class XtOrderError:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.order_id = 0
        self.error_id = 0
        self.error_msg = ""

# XtCancelError对象
class XtCancelError:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.order_id = 0
        self.error_id = 0
        self.error_msg = ""

# 模拟XtQuantTraderCallback基类
class XtQuantTraderCallback:
    def on_disconnected(self):
        pass
    
    def on_stock_order(self, order: XtOrder):
        pass
    
    def on_stock_asset(self, asset: XtAsset):
        pass
    
    def on_stock_trade(self, trade: XtTrade):
        pass
    
    def on_stock_position(self, position: XtPosition):
        pass
    
    def on_order_error(self, order_error: XtOrderError):
        pass
    
    def on_cancel_error(self, cancel_error: XtCancelError):
        pass
    
    def on_order_stock_async_response(self, response: XtOrderResponse):
        pass

class QmtTradingSimulator:
    def __init__(self, callback: XtQuantTraderCallback, commission_rate=0.00025, initial_cash=1000000, min_commission=5, stamp_duty_rate=0.001, transfer_fee_rate=0.00001, calculate_commission=False, is_following_mode=False):
        """
        初始化交易模拟器
        
        Args:
            callback: 回调对象
            commission_rate: 佣金率
            initial_cash: 初始资金
            min_commission: 最低佣金
            stamp_duty_rate: 印花税率
            transfer_fee_rate: 过户费率
            calculate_commission: 是否计算手续费
            is_following_mode: 是否跟随模式，为True时不验证订单和冻结资金
        """
        self.callback = callback
        self.account_id = "SIM001"
        self.next_order_id = 10000
        self.next_trade_id = 20000
        self.next_seq = 1
        self.lock = threading.Lock()
        self.market_data = {}  # 模拟市场数据
        self.calculate_commission = calculate_commission
        self.is_following_mode = is_following_mode
        
        # 如果是跟随模式，使用默认值
        if is_following_mode:
            self.commission_rate = 0.0  # 跟随模式下不考虑手续费
            self.min_commission = 0.0
            self.stamp_duty_rate = 0.0
            self.transfer_fee_rate = 0.0
            self.cash = 0.0
            self.positions = {}
        else:
            self.commission_rate = commission_rate
            self.min_commission = min_commission
            self.stamp_duty_rate = stamp_duty_rate
            self.transfer_fee_rate = transfer_fee_rate
            self.cash = initial_cash
            self.positions = {}
        """
        初始化交易模拟器
        
        Args:
            callback: 回调对象
            commission_rate: 佣金率
            initial_cash: 初始资金
            min_commission: 最低佣金
            stamp_duty_rate: 印花税率
            transfer_fee_rate: 过户费率
            calculate_commission: 是否计算手续费
            is_following_mode: 是否跟随模式，为True时不验证订单和冻结资金
        """
        """
        初始化交易模拟器
        
        Args:
            callback: 回调对象
            commission_rate: 佣金率
            initial_cash: 初始资金
            min_commission: 最低佣金
            stamp_duty_rate: 印花税率
            transfer_fee_rate: 过户费率
            calculate_commission: 是否计算手续费
        """
        self.callback = callback
        self.commission_rate = commission_rate
        self.account_id = "SIM001"
        self.cash = initial_cash  # 初始资金
        self.positions = {}  # 持仓情况: {stock_code: XtPosition}
        self.next_order_id = 10000
        self.next_trade_id = 20000
        self.next_seq = 1
        self.lock = threading.Lock()
        self.min_commission = min_commission  # 最低佣金
        self.stamp_duty_rate = stamp_duty_rate  # 印花税率
        self.transfer_fee_rate = transfer_fee_rate  # 过户费率
        self.market_data = {}  # 模拟市场数据
        self.calculate_commission = calculate_commission
        self.is_following_mode = is_following_mode
    
    def calculate_fee(self, transaction_type: str, stock_price: float, quantity: int) -> float:
        """计算交易手续费"""
        if self.calculate_commission:
            return calculate_stock_fee(
                transaction_type,
                stock_price,
                quantity,
                self.commission_rate,
                self.min_commission,
                self.stamp_duty_rate,
                self.transfer_fee_rate
            )
        else:
            return 0.0
    
    def place_order(self, stock_code: str, volume: int, price: float, order_type: int, price_type: int, order_time: int = None, direction: int = Direction.LONG, strategy_name: str = "", order_remark: str = ""):
        """
        下单方法
        
        Args:
            stock_code: 股票代码，格式如"600000.SH"
            volume: 数量
            price: 价格
            order_type: 委托类型，参见OrderType
            price_type: 报价类型，参见PriceType
            order_time: 下单时间（毫秒级时间戳），默认为当前时间
            direction: 多空方向，参见Direction
            strategy_name: 策略名称
            order_remark: 委托备注
        """
        """
        下单方法
        
        Args:
            stock_code: 股票代码，格式如"600000.SH"
            volume: 数量
            price: 价格
            order_type: 委托类型，参见OrderType
            price_type: 报价类型，参见PriceType
            order_time: 下单时间（毫秒级时间戳），默认为当前时间
            direction: 多空方向，参见Direction
            strategy_name: 策略名称
            order_remark: 委托备注
        """
        
        # 生成唯一订单ID和请求序号
        order_id = self._generate_order_id()
        seq = self._generate_seq()
        
        # 如果未提供下单时间，使用当前时间
        if order_time is None:
            order_time = int(time.time() * 1000)
        
        # 如果是跟随模式，直接下单，不验证订单和冻结资金
        if self.is_following_mode:
            # 创建订单对象
            order = self._create_order(
                order_id, stock_code, volume, price, 
                order_type, price_type, direction,
                strategy_name, order_remark, order_time
            )
            
            # 立即调用异步下单响应
            response = self._create_order_response(order_id, seq, 0, "下单成功", strategy_name, order_remark)
            self.callback.on_order_stock_async_response(response)
            return
        
        # 验证订单合法性
        error_id, error_msg = self._validate_order(stock_code, volume, price, order_type, price_type)
        if error_id != 0:
            # 立即返回错误响应
            response = self._create_order_response(order_id, seq, error_id, error_msg, strategy_name, order_remark)
            self.callback.on_order_stock_async_response(response)
            logger.error(f"订单验证失败: {error_msg}")
            return
        
        # 创建订单对象
        order = self._create_order(
            order_id, stock_code, volume, price, 
            order_type, price_type, direction,
            strategy_name, order_remark, order_time
        )
        
        # 计算订单手续费
        transaction_type = "buy" if order_type == OrderType.STOCK_BUY else "sell"
        fee = self.calculate_fee(transaction_type, price, volume)

        # 更新资金(买入时冻结资金，卖出时不做处理)
        if order_type == OrderType.STOCK_BUY:
            with self.lock:
                self.cash -= (price * volume + fee)
                logger.info(f"买入冻结资金: {price * volume + fee:.2f}")
        
        # 立即调用异步下单响应
        response = self._create_order_response(order_id, seq, 0, "下单成功", strategy_name, order_remark)
        self.callback.on_order_stock_async_response(response)
        
        # 立即调用订单回报
        self.callback.on_stock_order(order)
        
        # 模拟成交回报
        self._simulate_trades(order)
    
    def _validate_order(self, stock_code: str, volume: int, price: float, order_type: int, price_type: int) -> (int, str):
        """验证订单合法性"""
        if volume <= 0:
            return 1001, "订单数量必须大于0"
        
        if price <= 0 and price_type != PriceType.BEST_5:
            return 1002, "订单价格必须大于0"
        
        if order_type not in [OrderType.STOCK_BUY, OrderType.STOCK_SELL]:
            return 1003, "订单类型必须是买入或卖出"
        
        if price_type not in [PriceType.LIMIT_PRICE, PriceType.BEST_5]:
            return 1005, "不支持的报价类型"
        
        with self.lock:
            # 买入时检查资金是否充足
            if order_type == OrderType.STOCK_BUY:
                fee = self.calculate_fee("buy", price, volume)
                if self.cash < (price * volume + fee):
                    # order_time_str = time.strftime("%Y-%m-%d", time.localtime(order_time // 1000))
                    # print("order_time_str",order_time_str)
                    
                    return 1004, "资金不足"
            # 卖出时检查持仓是否足够        
            else:
                position = self.positions.get(stock_code)
                if not position or position.volume < volume:
                    return 1007, "可用持仓不足"
        
        return 0, "订单验证通过"
    
    def _create_order(self, order_id: int, stock_code: str, volume: int, price: float, order_type: int, price_type: int, direction: int, strategy_name: str, order_remark: str, order_time: int) -> XtOrder:
        """创建订单对象"""
        order = XtOrder()
        order.account_type = AccountType.STOCK
        order.account_id = self.account_id
        order.stock_code = stock_code
        order.order_id = order_id
        order.order_sysid = f"SYS{order_id}"
        order.order_time = order_time  # 设置下单时间
        order.order_type = order_type
        order.order_volume = volume
        order.price_type = price_type
        order.price = price
        order.traded_volume = 0
        order.traded_price = 0.0
        order.order_status = OrderStatus.SUBMITTED
        order.strategy_name = strategy_name  # 确保策略名称被正确设置
        order.order_remark = order_remark[:24]  # 限制备注长度
        order.direction = direction
        return order
    
    def _create_order_response(self, order_id: int, seq: int, error_id: int, error_msg: str, strategy_name: str, order_remark: str) -> XtOrderResponse:
        """创建订单响应对象"""
        response = XtOrderResponse()
        response.account_type = AccountType.STOCK
        response.account_id = self.account_id
        response.order_id = order_id
        response.seq = seq
        response.error_id = error_id
        response.error_msg = error_msg
        response.strategy_name = strategy_name  # 确保策略名称被正确设置
        response.order_remark = order_remark[:24]  # 限制备注长度
        return response
    
    def _generate_order_id(self) -> int:
        """生成唯一订单ID"""
        with self.lock:
            order_id = self.next_order_id
            self.next_order_id += 1
            return order_id
    
    def _generate_trade_id(self) -> str:
        """生成唯一成交ID"""
        with self.lock:
            trade_id = f"TRADE{self.next_trade_id}"
            self.next_trade_id += 1
            return trade_id
    
    def _generate_seq(self) -> int:
        """生成唯一请求序号"""
        with self.lock:
            seq = self.next_seq
            self.next_seq += 1
            return seq
    
    def _simulate_trades(self, order: XtOrder):
        """模拟成交回报"""
        trade_volume = order.order_volume
        trade_price = self._get_trade_price(order)
        traded_time = order.order_time + random.randint(1, 100)  # 毫秒级偏移
        trade = self._create_trade(order, trade_price, trade_volume, traded_time)
        self._process_trade(trade, order)
        
        # 更新订单状态
        order.traded_volume = order.order_volume
        order.order_status = OrderStatus.FILLED 
        order.status_msg = "全部成交"
        
        # 计算成交均价
        if order.traded_volume > 0:
            order.traded_price = order.price  # 简化处理，实际应为加权平均价
        
        # 触发订单状态更新回调
        self.callback.on_stock_order(order)
    
    def _get_trade_price(self, order: XtOrder) -> float:
        """根据价格类型生成成交价格"""
        if order.price_type == PriceType.BEST_5:
            # 五档即成剩撤：价格在当前价上下浮动
            current_price = order.price or 10.0  # 默认10元
            return current_price * random.uniform(0.995, 1.005)
        else:
            # 限价单：在委托价附近微小波动
            return order.price * random.uniform(0.999, 1.001)
    
    def _create_trade(self, order: XtOrder, trade_price: float, trade_volume: int, traded_time: int) -> XtTrade:
        """创建成交对象"""
        trade = XtTrade()
        trade.account_type = order.account_type
        trade.account_id = order.account_id
        trade.stock_code = order.stock_code
        trade.order_type = order.order_type
        trade.traded_id = self._generate_trade_id()
        trade.traded_time = traded_time  # 设置成交时间
        trade.traded_price = trade_price
        trade.traded_volume = trade_volume
        trade.traded_amount = trade_price * trade_volume
        trade.order_id = order.order_id
        trade.order_sysid = order.order_sysid
        trade.strategy_name = order.strategy_name  # 确保策略名称被正确设置
        trade.order_remark = order.order_remark  # 确保备注被正确设置
        trade.direction = order.direction
        return trade
    
    def _process_trade(self, trade: XtTrade, order: XtOrder):
        """处理成交并触发相关回调"""
        # 触发成交回调
        self.callback.on_stock_trade(trade)
        
        # 更新资金和持仓
        with self.lock:
            # 计算该笔成交的手续费
            transaction_type = "buy" if order.order_type == OrderType.STOCK_BUY else "sell"
            fee = self.calculate_fee(transaction_type, trade.traded_price, trade.traded_volume)
            
            if order.order_type == OrderType.STOCK_BUY:
                # 买入: 增加持仓，更新资金(手续费已在下单时扣除)
                if order.stock_code in self.positions:
                    position = self.positions[order.stock_code]
                    total_volume = position.volume + trade.traded_volume
                    print(total_volume)
                    position.avg_price = (position.avg_price * position.volume + trade.traded_price * trade.traded_volume) / total_volume
                    position.volume = total_volume
                    position.today_buy_volume += trade.traded_volume
                    # 可用数量不增加，模拟T+1限制
                else:
                    position = XtPosition()
                    position.account_type = AccountType.STOCK
                    position.account_id = self.account_id
                    position.stock_code = order.stock_code
                    position.volume = trade.traded_volume
                    position.today_buy_volume = trade.traded_volume
                    position.can_use_volume = 0  # 今日买入不可用，模拟T+1
                    position.avg_price = trade.traded_price
                    position.market_value = trade.traded_price * trade.traded_volume
                    self.positions[order.stock_code] = position
            else:
                # 卖出: 减少持仓，增加资金
                if order.stock_code in self.positions:
                    position = self.positions[order.stock_code]
                    position.volume -= trade.traded_volume
                    position.can_use_volume -= trade.traded_volume
                    
                    # 计算卖出收益
                    cost = position.avg_price * trade.traded_volume
                    proceeds = trade.traded_price * trade.traded_volume
                    
                    # 更新资金
                    self.cash += proceeds - fee
                    
                    # 如果持仓为0，移除该股票
                    if position.volume <= 0:
                        del self.positions[order.stock_code]
            
            # 更新总资产
            total_assets = self.cash
            market_value = 0.0
            for stock_code, position in self.positions.items():
                # 假设当前市值等于最新成交价
                position.market_value = position.volume * trade.traded_price
                market_value += position.market_value
                total_assets += position.market_value
            
            # 创建资金对象
            asset = XtAsset()
            asset.account_type = AccountType.STOCK
            asset.account_id = self.account_id
            asset.total_asset = total_assets
            asset.cash = self.cash
            asset.market_value = market_value
            asset.frozen_cash = 0.0  # 简化处理
            
            # 触发资金变动回调
            self.callback.on_stock_asset(asset)
            
            # 如果持仓还存在，触发持仓变动回调
            if order.stock_code in self.positions:
                self.callback.on_stock_position(self.positions[order.stock_code])
            else:
                # 持仓为0时，发送一个虚拟持仓对象表示已清空
                position = XtPosition()
                position.account_type = AccountType.STOCK
                position.account_id = self.account_id
                position.stock_code = order.stock_code
                position.volume = 0
                position.can_use_volume = 0
                self.callback.on_stock_position(position)

