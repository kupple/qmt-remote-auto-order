from pyapp.pkg.xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from api.global_params import G
import threading
from decimal import Decimal
from api.trading_related.deal import calculate_stock_fee,calculate_average_price
from .qmt_trading_simulator import OrderType

class MyXtQuantTraderCallback(XtQuantTraderCallback):
 
  def __init__(self,is_mock,backtest_id=None,is_pre=False) -> None:
    self.is_mock = is_mock
    self.backtest_id = backtest_id 
    self.is_pre = is_pre
    self.trade_lock = threading.Lock()  # 添加线程锁
    super().__init__()
    
  def on_disconnected(self):
    """
    连接断开
    :return:
    """
    G.logger.warning("QMT连接断开!",extra={
            "showMessage": True
    })

  def on_account_status(self, status):
    """
    :param response: XtAccountStatus 对象
    :return:
    """
    print("on_account_status")
    print(status.account_id, status.account_type, status.status)

  def on_stock_order(self, order):
    
    # 将毫秒级时间戳转换为秒级时间戳
    # timestamp_s = order.order_time / 1000

    # 将时间戳转换为 datetime 对象
    # dt = datetime.fromtimestamp(timestamp_s)

    # 格式化为指定的日期字符串
    # formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    """
    委托回报推送
    :param order: XtOrder对象
    :return:
    """
    pass
    # # 系统下的单
    # if order.order_remark and order.strategy_name:
    #   orderId = order.order_remark
    #   G.orm.save_entrust(order,{
    #     "orders_id": orderId,
    #     "backtest_id": self.backtest_id,
    #     "is_mock": self.is_mock
    #   })
  def on_stock_asset(self, asset):
    """
    资金变动推送
    :param asset: XtAsset对象
    :return:
    """
    pass
  def on_stock_trade(self, trade):
    """
    成交变动推送
    :param trade: XtTrade对象
    :return:
    """
    try:
      with self.trade_lock:  # 使用锁确保线程安全
        if trade.order_remark and trade.strategy_name:
          taskId = trade.strategy_name
          orderId = trade.order_remark
          task_or_backtest = G.orm.query_task_or_backtest(task_id=taskId, backtest_id=self.backtest_id)
          order_count_type = task_or_backtest['order_count_type']

          positions = G.orm.query_position_by_task_or_backtest_id(backtest_id=self.backtest_id,task_id=taskId)
          positions_dict = {position['security_code']: position for position in positions}
          
          # 交易金额
          traded_amount = Decimal(trade.traded_amount)
          
          if trade.stock_code not in positions_dict:
            G.orm.save_position({
                "security_code": trade.stock_code,
                "volume": trade.traded_volume,
                "amount": traded_amount,
                "backtest_id": self.backtest_id,
                "is_mock": self.is_mock,
                "task_id": taskId,
                "average_price": trade.traded_price
            })
          else:
            position = positions_dict[trade.stock_code]
            # 计算均价
            tmp_volume = position['volume']
            tmp_traded_volume = trade.traded_volume
            if trade.order_type == OrderType.STOCK_BUY:
              position['volume'] += trade.traded_volume
            elif trade.order_type == OrderType.STOCK_SELL:
              position['volume'] -= trade.traded_volume
              tmp_traded_volume = -tmp_traded_volume
            
            position['average_price'] = calculate_average_price(position['average_price'], tmp_volume, trade.traded_price, tmp_traded_volume)

                        
            G.orm.update_position(position['id'], {
              'volume': position['volume'],
              'backtest_id': self.backtest_id,
              'task_id': taskId,
              'average_price': position['average_price'],
              'amount': position['amount']
            })
            
          if order_count_type == 1:
            commission = 0  
            if self.is_mock == True:
              mock_service_charge = task_or_backtest['service_charge']
              mock_lower_limit_of_fees = task_or_backtest['lower_limit_of_fees']
              # 计算手续费
              commission = Decimal(calculate_stock_fee("buy" if trade.order_type == OrderType.STOCK_BUY else "sell",
                                              float(trade.traded_price),
                                              int(trade.traded_volume),
                                              float(mock_service_charge),
                                              float(mock_lower_limit_of_fees)))
          else:
            if task_or_backtest:
                if self.is_mock == True:
                  mock_service_charge = task_or_backtest['service_charge']
                  mock_lower_limit_of_fees = task_or_backtest['lower_limit_of_fees']
                else:
                  mock_service_charge = task_or_backtest['service_charge']
                  mock_lower_limit_of_fees = task_or_backtest['lower_limit_of_fees']
            # 计算手续费
            commission = Decimal(calculate_stock_fee("buy" if trade.order_type == OrderType.STOCK_BUY else "sell",
                                          float(trade.traded_price),
                                          int(trade.traded_volume),
                                          float(mock_service_charge),
                                          float(mock_lower_limit_of_fees)))
          # 保存订单信息
          G.orm.save_trade(trade,{
            "orders_id": orderId,
            "backtest_id": self.backtest_id,
            "is_mock": self.is_mock,
            "task_id": taskId,
            "commission": commission
          })
          # 更新任务账户的可用金额
          if trade.order_type == OrderType.STOCK_BUY:
            G.orm.update_task_can_use_amount(self.backtest_id,taskId, round(-(traded_amount + commission),2))
          elif trade.order_type == OrderType.STOCK_SELL:
            G.orm.update_task_can_use_amount(self.backtest_id,taskId, round(traded_amount - commission,2))
        
                
    except Exception as e:
      G.logger.error("on_stock_trade error" + str(e))
    # 系统下的单
  def on_stock_position(self, position):
    """
    持仓变动推送
    :param position: XtPosition对象
    :return:
    """
    pass
  def on_order_error(self, order_error):
    """
    委托失败推送
    :param order_error:XtOrderError 对象
    :return:
    """
    G.logger.error("on order_error callback" + str(order_error.error_msg),extra={
            "showMessage": True
    })
  def on_cancel_error(self, cancel_error):
    """
    撤单失败推送
    :param cancel_error: XtCancelError 对象
    :return:
    """
    G.logger.error("on cancel_error callback" + str(cancel_error),extra={
            "showMessage": True
    })
    
  def on_order_stock_async_response(self, response):
    """
    异步下单回报推送
    :param response: XtOrderResponse 对象
    :return:
    """
    pass
   
