import time
import random
import threading
from typing import Optional
from api.trading_related.deal import calculate_stock_fee

# 模拟数据字典
class AccountType:
    STOCK = 1  # 股票账户

class OrderType:
    LIMIT = 1  # 限价委托
    MARKET = 2  # 市价委托

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
    SHORT = 2  # 空头

class OffsetFlag:
    BUY = 1  # 买入
    SELL = 2  # 卖出

# XtOrder对象
class XtOrder:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.order_id = 0
        self.order_sysid = ""
        self.order_time = 0  # 报单时间
        self.order_type = OrderType.LIMIT
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
        self.offset_flag = OffsetFlag.BUY

# XtAsset对象
class XtAsset:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.total_asset = 0.0  # 总资产
        self.cash = 0.0  # 可用资金
        self.market_value = 0.0  # 证券市值
        self.frozen_cash = 0.0  # 冻结资金
        self.position_profit = 0.0  # 持仓盈亏
        self.day_profit = 0.0  # 当日盈亏

# XtTrade对象
class XtTrade:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.order_type = OrderType.LIMIT
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
        self.offset_flag = OffsetFlag.BUY

# XtPosition对象
class XtPosition:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.volume = 0
        self.can_use_volume = 0
        self.open_price = 0.0
        self.market_value = 0.0
        self.frozen_volume = 0
        self.on_road_volume = 0
        self.yesterday_volume = 0
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
    def __init__(self, callback: XtQuantTraderCallback, commission_rate=0.0003, initial_cash=1000000.0, min_commission=5.0, stamp_duty_rate=0.001, transfer_fee_rate=0.00001):
        """
        初始化QMT交易模拟器
        
        Args:
            callback: 回调函数对象，处理各种交易事件
            commission_rate: 佣金率，默认万3
            initial_cash: 初始现金，默认100万
            min_commission: 最低佣金，默认5元
            stamp_duty_rate: 印花税率，默认0.1%
            transfer_fee_rate: 过户费率，默认0.001%
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
    
    def calculate_fee(self, transaction_type: str, stock_price: float, quantity: int) -> float:
        """计算交易手续费"""
        return calculate_stock_fee(
            transaction_type,
            stock_price,
            quantity,
            self.commission_rate,
            self.min_commission,
            self.stamp_duty_rate,
            self.transfer_fee_rate
        )
    
    def place_order(self, stock_code: str, volume: int, price: float, order_type: int, price_type: int, order_time: int = None, direction: int = Direction.LONG, offset_flag: int = OffsetFlag.BUY, strategy_name: str = "", order_remark: str = ""):
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
            offset_flag: 交易操作，参见OffsetFlag
            strategy_name: 策略名称
            order_remark: 委托备注
        """
        # 生成唯一订单ID和请求序号
        order_id = self._generate_order_id()
        seq = self._generate_seq()
        
        # 如果未提供下单时间，使用当前时间
        if order_time is None:
            order_time = int(time.time() * 1000)
        
        # 验证订单合法性
        error_id, error_msg = self._validate_order(stock_code, volume, price, offset_flag)
        if error_id != 0:
            # 立即返回错误响应
            response = self._create_order_response(order_id, seq, error_id, error_msg, strategy_name, order_remark)
            self.callback.on_order_stock_async_response(response)
            return
        
        # 创建订单对象
        order = self._create_order(
            order_id, stock_code, volume, price, 
            order_type, price_type, direction, offset_flag,
            strategy_name, order_remark, order_time
        )
        
        # 计算订单手续费
        transaction_type = "buy" if offset_flag == OffsetFlag.BUY else "sell"
        fee = self.calculate_fee(transaction_type, price, volume)
        
        # 更新资金(买入时冻结资金，卖出时不做处理)
        if offset_flag == OffsetFlag.BUY:
            with self.lock:
                self.cash -= (price * volume + fee)
        
        # 立即调用异步下单响应
        response = self._create_order_response(order_id, seq, 0, "下单成功", strategy_name, order_remark)
        self.callback.on_order_stock_async_response(response)
        
        # 立即调用订单回报
        self.callback.on_stock_order(order)
        
        # 立即调用成交回报
        self._simulate_trades(order)
    
    def _validate_order(self, stock_code: str, volume: int, price: float, offset_flag: int) -> (int, str):
        """验证订单合法性"""
        if volume <= 0:
            return 1001, "订单数量必须大于0"
        
        if price <= 0:
            return 1002, "订单价格必须大于0"
        
        if offset_flag not in [OffsetFlag.BUY, OffsetFlag.SELL]:
            return 1003, "订单类型必须是买入或卖出"
        
        # 计算订单手续费
        transaction_type = "buy" if offset_flag == OffsetFlag.BUY else "sell"
        fee = self.calculate_fee(transaction_type, price, volume)
        
        with self.lock:
            # 买入时检查资金是否充足
            if offset_flag == OffsetFlag.BUY:
                if self.cash < (price * volume + fee):
                    return 1004, "资金不足"
            # 卖出时检查持仓是否足够
            else:
                if stock_code not in self.positions or self.positions[stock_code].volume < volume:
                    return 1006, "持仓不足"
        
        return 0, "订单验证通过"
    
    def _create_order(self, order_id: int, stock_code: str, volume: int, price: float, order_type: int, price_type: int, direction: int, offset_flag: int, strategy_name: str, order_remark: str, order_time: int) -> XtOrder:
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
        order.offset_flag = offset_flag
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
        # 生成1-3笔成交
        num_trades = random.randint(1, 3)
        remaining_volume = order.order_volume
        
        for i in range(num_trades):
            # 最后一笔成交处理剩余全部数量
            if i == num_trades - 1:
                trade_volume = remaining_volume
            else:
                # 每笔成交数量为随机值
                max_volume = max(1, remaining_volume // 2)
                trade_volume = random.randint(1, max_volume)
            
            remaining_volume -= trade_volume
            
            # 生成略有差异的成交价格
            trade_price = order.price * random.uniform(0.999, 1.001)
            
            # 生成成交时间（略晚于下单时间）
            traded_time = order.order_time + random.randint(1, 100)  # 毫秒级偏移
            
            # 创建成交对象
            trade = self._create_trade(order, trade_price, trade_volume, traded_time)
            
            # 立即处理每笔成交
            self._process_trade(trade, order)
        
        # 更新订单状态为全部成交
        order.order_status = OrderStatus.FILLED
        order.traded_volume = order.order_volume
        order.traded_price = order.price  # 简化处理，实际应为加权平均价
        self.callback.on_stock_order(order)
    
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
        trade.offset_flag = order.offset_flag
        return trade
    
    def _process_trade(self, trade: XtTrade, order: XtOrder):
        """处理成交并触发相关回调"""
        # 触发成交回调
        self.callback.on_stock_trade(trade)
        
        # 更新资金和持仓
        with self.lock:
            # 计算该笔成交的手续费
            transaction_type = "buy" if order.offset_flag == OffsetFlag.BUY else "sell"
            fee = self.calculate_fee(transaction_type, trade.traded_price, trade.traded_volume)
            
            if order.offset_flag == OffsetFlag.BUY:
                # 买入: 增加持仓，更新资金(手续费已在下单时扣除)
                if order.stock_code in self.positions:
                    position = self.positions[order.stock_code]
                    total_volume = position.volume + trade.traded_volume
                    position.avg_price = (position.avg_price * position.volume + trade.traded_price * trade.traded_volume) / total_volume
                    position.volume = total_volume
                    position.can_use_volume = total_volume  # 简化处理，实际T+1可用
                else:
                    position = XtPosition()
                    position.account_type = AccountType.STOCK
                    position.account_id = self.account_id
                    position.stock_code = order.stock_code
                    position.volume = trade.traded_volume
                    position.can_use_volume = trade.traded_volume  # 简化处理
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

# 使用示例
if __name__ == "__main__":
    # 创建回调类实例
    class MyXtQuantTraderCallback(XtQuantTraderCallback):
        def on_disconnected(self):
            print("connection lost")
            
        def on_stock_order(self, order: XtOrder):
            status_map = {
                OrderStatus.SUBMITTED: "已提交",
                OrderStatus.PARTIAL: "部分成交",
                OrderStatus.FILLED: "全部成交",
                OrderStatus.CANCELLED: "已撤单",
                OrderStatus.FAILED: "废单"
            }
            status_text = status_map.get(order.order_status, "未知状态")
            order_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order.order_time / 1000))
            print(f"订单回报: {order.order_id}, {order.stock_code}, {order.order_volume}, {order.price}, {status_text}, 策略={order.strategy_name}, 备注={order.order_remark}, 时间={order_time}")
            
        def on_stock_asset(self, asset: XtAsset):
            print(f"资金变动: 账户ID={asset.account_id}, 现金={asset.cash:.2f}, 市值={asset.market_value:.2f}, 总资产={asset.total_asset:.2f}")
            
        def on_stock_trade(self, trade: XtTrade):
            traded_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(trade.traded_time / 1000))
            print(f"成交回报: {trade.traded_id}, {trade.stock_code}, {trade.traded_volume}, {trade.traded_price}, 策略={trade.strategy_name}, 备注={trade.order_remark}, 时间={traded_time}")
            
        def on_stock_position(self, position: XtPosition):
            print(f"持仓变动: {position.stock_code}, 数量={position.volume}, 可用={position.can_use_volume}, 成本价={position.avg_price:.2f}")
            
        def on_order_error(self, order_error: XtOrderError):
            print(f"委托失败: {order_error.order_id}, {order_error.error_msg}")
            
        def on_cancel_error(self, cancel_error: XtCancelError):
            print(f"撤单失败: {cancel_error.order_id}, {cancel_error.error_msg}")
            
        def on_order_stock_async_response(self, response: XtOrderResponse):
            print(f"异步下单响应: {response.order_id}, {response.error_msg}, 策略={response.strategy_name}, 备注={response.order_remark}")
    
    # 创建模拟器实例
    callback = MyXtQuantTraderCallback()
    simulator = QmtTradingSimulator(
        callback, 
        commission_rate=0.00025,  # 佣金率万2.5
        initial_cash=2000000.0,   # 初始资金200万
        min_commission=5.0,       # 最低佣金5元
        stamp_duty_rate=0.001,    # 印花税率0.1%
        transfer_fee_rate=0.00001 # 过户费率0.001%
    )
    
    # 获取当前时间戳（毫秒）
    current_time = int(time.time() * 1000)
    
    # 模拟买入
    print("===== 模拟买入 =====")
    simulator.place_order(
        stock_code="600000.SH",
        volume=1000,
        price=10.0,
        order_type=OrderType.LIMIT,
        price_type=PriceType.LIMIT_PRICE,
        order_time=current_time,  # 传入当前时间
        offset_flag=OffsetFlag.BUY,
        strategy_name="DemoStrategy",
        order_remark="TestBuyOrder"
    )
    
    # 模拟卖出
    print("\n===== 模拟卖出 =====")
    simulator.place_order(
        stock_code="600000.SH",
        volume=500,
        price=11.0,
        order_type=OrderType.LIMIT,
        price_type=PriceType.LIMIT_PRICE,
        order_time=current_time + 1000,  # 1秒后的时间
        offset_flag=OffsetFlag.SELL,
        strategy_name="DemoStrategy",
        order_remark="TestSellOrder"
    )    