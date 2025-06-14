import time
import threading
from typing import Optional
from api.global_params import G
import asyncio
import random

class AccountType:
    STOCK = 1
    FUTURE = 2
    OPTION = 3

class OrderType:
    STOCK_BUY = 23
    STOCK_SELL = 24

class PriceType:
    # 最新价
    LATEST_PRICE = 5
    # 指定价/限价
    FIX_PRICE = 11
    # 市价最优价[郑商所][期货]
    MARKET_BEST = 18
    # 市价即成剩撤[大商所][期货]
    MARKET_CANCEL = 19
    # 市价全额成交或撤[大商所][期货]
    MARKET_CANCEL_ALL = 20
    # 市价最优一档即成剩撤[中金所][期货]
    MARKET_CANCEL_1 = 21
    # 市价最优五档即成剩撤[中金所][期货]
    MARKET_CANCEL_5 = 22
    # 市价最优一档即成剩转[中金所][期货]
    MARKET_CONVERT_1 = 23
    # 市价最优五档即成剩转[中金所][期货]
    MARKET_CONVERT_5 = 24
    # 最优五档即时成交剩余撤销[上交所][股票]
    MARKET_SH_CONVERT_5_CANCEL = 42
    # 最优五档即时成交剩转限价[上交所][股票]
    MARKET_SH_CONVERT_5_LIMIT = 43
    # 对手方最优价格委托[上交所[股票]][深交所[股票][期权]]
    MARKET_PEER_PRICE_FIRST = 44
    # 本方最优价格委托[上交所[股票]][深交所[股票][期权]]
    MARKET_MINE_PRICE_FIRST = 45
    # 即时成交剩余撤销委托[深交所][股票][期权]
    MARKET_SZ_INSTBUSI_RESTCANCEL = 46
    # 最优五档即时成交剩余撤销[深交所][股票][期权]
    MARKET_SZ_CONVERT_5_CANCEL = 47
    # 全额成交或撤销委托[深交所][股票][期权]
    MARKET_SZ_FULL_OR_CANCEL = 48


class OrderStatus:
    SUBMITTED = 1
    PARTIAL = 2
    FILLED = 3
    CANCELLED = 4
    FAILED = 5

class Direction:
    LONG = 1
    SHORT = 2

class XtOrder:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.order_id = 0
        self.order_sysid = ""
        self.order_time = 0
        self.order_type = OrderType.STOCK_BUY
        self.order_volume = 0
        self.price_type = PriceType.LATEST_PRICE
        self.price = 0.0
        self.traded_volume = 0
        self.traded_price = 0.0
        self.order_status = OrderStatus.SUBMITTED
        self.strategy_name = ""
        self.order_remark = ""
        self.direction = Direction.LONG

class XtAsset:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.total_asset = 0.0
        self.cash = 0.0
        self.market_value = 0.0
        self.frozen_cash = 0.0

class XtTrade:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.order_type = OrderType.STOCK_BUY
        self.traded_id = ""
        self.traded_time = 0
        self.traded_price = 0.0
        self.traded_volume = 0
        self.traded_amount = 0.0
        self.order_id = 0
        self.order_sysid = ""
        self.strategy_name = ""
        self.order_remark = ""
        self.direction = Direction.LONG

class XtPosition:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.stock_code = ""
        self.volume = 0
        self.can_use_volume = 0
        self.yesterday_volume = 0
        self.today_buy_volume = 0
        self.open_price = 0.0
        self.market_value = 0.0
        self.frozen_volume = 0
        self.on_road_volume = 0
        self.avg_price = 0.0

class XtOrderResponse:
    def __init__(self):
        self.account_type = AccountType.STOCK
        self.account_id = ""
        self.order_id = 0
        self.seq = 0
        self.error_id = 0
        self.error_msg = ""
        self.strategy_name = ""
        self.order_remark = ""

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

    def on_order_stock_async_response(self, response: XtOrderResponse):
        pass

class QmtTradingSimulator:
    def __init__(self,is_simulation_state:int,callback: XtQuantTraderCallback):
        self.callback = callback
        self.account_id = "SIM001"
        self.next_order_id = 10000
        self.next_trade_id = 20000
        self.next_seq = 1
        self.lock = threading.Lock()
        self.is_simulation_state = is_simulation_state

    def place_order(self, stock_code: str, volume: int, price: float, order_type: int, price_type: int, order_time: int = None, direction: int = Direction.LONG, strategy_name: str = "", order_remark: str = ""):
        order_id = self._generate_order_id()
        seq = self._generate_seq()
        
        # 验证订单合法性
        error_id, error_msg = self._validate_order(stock_code, volume, price, order_type, price_type)
        if error_id != 0:
            # 立即返回错误响应
            response = self._create_order_response(order_id, seq, error_id, error_msg, strategy_name, order_remark)
            self.callback.on_order_stock_async_response(response)
            G.logger.error(f"订单验证失败: {error_msg}")
            return
        
        # 创建订单对象
        order = self._create_order(
            order_id, stock_code, volume, price, 
            order_type, price_type, direction,
            strategy_name, order_remark, order_time
        )
        
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
        
        if order_type not in [OrderType.STOCK_BUY, OrderType.STOCK_SELL]:
            return 1003, "订单类型必须是买入或卖出"
        
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
        import random
        import asyncio
        
        trade_price = order.price
        traded_time = order.order_time
        total_volume = order.order_volume
        current_volume = 0
        
        # 在模拟模式下，将订单拆分成随机次数的成交
        if self.is_simulation_state == 1:
            # 随机决定成交次数（1-5次）
            num_trades = random.randint(1, 5)
            remaining_volume = total_volume
            
            for i in range(num_trades):
                if remaining_volume <= 0:
                    break
                    
                # 确保最后一次成交正好完成剩余数量
                if i == num_trades - 1:
                    # 最后一次成交，确保剩余数量是100的倍数
                    if remaining_volume % 100 != 0:
                        remaining_volume = (remaining_volume // 100) * 100  # 向下取整到100的倍数
                    trade_volume = remaining_volume
                else:
                    # 随机决定本次成交的数量（必须是100的倍数）
                    max_possible = min(1000, remaining_volume)  # 最大1000股或剩余数量
                    if max_possible < 100:
                        break  # 如果最大可能成交量小于100股，结束循环
                        
                    # 随机选择1-10之间的数，然后乘以100
                    trade_volume = random.randint(1, min(10, max_possible // 100)) * 100
                
                # 创建并处理成交
                trade = self._create_trade(order, trade_price, trade_volume, traded_time)
                self._process_trade(trade, order)
                
                # 更新订单状态
                current_volume += trade_volume
                order.traded_volume = current_volume
                remaining_volume -= trade_volume
                
                # # 更新订单状态
                # if current_volume < total_volume:
                #     order.order_status = OrderStatus.PARTIAL
                #     order.status_msg = f"部分成交 {current_volume}/{total_volume}"
                # else:
                #     order.order_status = OrderStatus.FILLED
                #     order.status_msg = "全部成交"
                
                # # 触发订单状态更新回调
                # self.callback.on_stock_order(order)
                
        elif self.is_simulation_state == 2:
            trade = self._create_trade(order, trade_price, total_volume, traded_time)
            
            # 使用5个线程并行处理trade
            threads = []
            for _ in range(110):
                t = threading.Thread(target=self._process_trade, args=(trade, order))
                threads.append(t)
                t.start()
            
            # 等待所有线程完成
            for t in threads:
                t.join()
            
            # 更新订单状态
            order.traded_volume = total_volume
            order.order_status = OrderStatus.FILLED 
            order.status_msg = "全部成交"
            
            # 触发订单状态更新回调
            # self.callback.on_stock_order(order)
            
        # 计算成交均价
        if order.traded_volume > 0:
            order.traded_price = order.price  # 简化处理，实际应为加权平均价
            
        elif self.is_simulation_state == 0:
            # 非模拟模式，直接全部成交
            trade = self._create_trade(order, trade_price, total_volume, traded_time)
            self._process_trade(trade, order)
            
            # 更新订单状态
            order.traded_volume = total_volume
            order.order_status = OrderStatus.FILLED 
            order.status_msg = "全部成交"
            
            # 触发订单状态更新回调
            # self.callback.on_stock_order(order)
            
        # 计算成交均价
        if order.traded_volume > 0:
            order.traded_price = order.price  # 简化处理，实际应为加权平均价
    
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
        
        # 创建虚拟持仓对象
        position = XtPosition()
        position.account_type = AccountType.STOCK
        position.account_id = self.account_id
        position.stock_code = order.stock_code
        position.volume = trade.traded_volume
        position.market_value = trade.traded_price * trade.traded_volume
        position.avg_price = trade.traded_price
        
        # 触发持仓回调
        self.callback.on_stock_position(position)
        
        # 创建虚拟资金对象
        asset = XtAsset()
        asset.account_type = AccountType.STOCK
        asset.account_id = self.account_id
        asset.total_asset = 1000000  # 固定值
        asset.cash = 1000000  # 固定值
        asset.market_value = trade.traded_price * trade.traded_volume
        
        # 触发资金回调
        self.callback.on_stock_asset(asset)


    def _process_trade_thread(self, order: XtOrder, trade_price: float, trade_volume: int, traded_time: int):
        """线程处理函数，用于处理单个成交"""
        trade = self._create_trade(order, trade_price, trade_volume, traded_time)
        self._process_trade(trade, order)
        
        with self.lock:  # 使用锁确保线程安全
            order.traded_volume += trade_volume
            if order.traded_volume == order.order_volume:
                order.order_status = OrderStatus.FILLED
                order.status_msg = "全部成交"
