#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .trading_related.qmt_trader import qmt_trader
from .db.orm import ORM
from pyapp.pkg.xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
import sys
import platform
from api.system import System
from .trading_related.deal import convert_stock_suffix,calculate_stock_fee
from datetime import datetime
from .trading_related.additional_data import stock_xgsglb_em_on_today,bond_zh_cov
from .trading_related.qmt_trading_simulator import QmtTradingSimulator,OrderType,PriceType
from decimal import Decimal
import json
  
class MyXtQuantTraderCallback(XtQuantTraderCallback):
 
  def __init__(self,orm,is_mock,backtest_id=None) -> None:
    self.orm = orm
    self.is_mock = is_mock
    self.backtest_id = backtest_id 
    super().__init__()
    
  def on_disconnected(self):
    """
    连接断开
    :return:
    """
    print("connection lost")
  def on_stock_order(self, order):
    
    # 将毫秒级时间戳转换为秒级时间戳
    timestamp_s = order.order_time / 1000

    # 将时间戳转换为 datetime 对象
    dt = datetime.fromtimestamp(timestamp_s)

    # 格式化为指定的日期字符串
    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    """
    委托回报推送
    :param order: XtOrder对象
    :return:
    """
    # 系统下的单
    if order.order_remark and order.strategy_name:
      orderId = order.order_remark
      self.orm.save_entrust(order,{
        "orders_id": orderId,
        "backtest_id": self.backtest_id,
        "is_mock": self.is_mock
      })
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
      if trade.order_remark and trade.strategy_name:
        taskId = trade.strategy_name
        orderId = trade.order_remark
        task_or_backtest = self.orm.query_task_or_backtest(task_id=taskId, backtest_id=self.backtest_id)
        order_count_type = task_or_backtest['order_count_type']
        # 保存订单信息
        self.orm.save_trade(trade,{
          "orders_id": orderId,
          "backtest_id": self.backtest_id,
          "is_mock": self.is_mock,
          "task_id": taskId
        })
        if order_count_type == 1:
          pass
        else:
          pass

        positions = self.orm.query_position_by_task_or_backtest_id(backtest_id=self.backtest_id,task_id=taskId)
        
        positions_dict = {position['security_code']: position for position in positions}
        
        # 交易金额
        traded_amount = Decimal(trade.traded_amount)
        if trade.stock_code not in positions_dict:
          self.orm.save_position({
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
          if trade.order_type == OrderType.STOCK_BUY:
            position['volume'] += trade.traded_volume
          elif trade.order_type == OrderType.STOCK_SELL:
            position['volume'] -= trade.traded_volume
          
          # 计算新的平均价格（在所有交易发生时更新）
          position['average_price'] = Decimal(position['amount']) / Decimal(position['volume']) if position['volume'] > 0 else Decimal('0')
          self.orm.update_position(position['id'], {
            'volume': position['volume'],
            'backtest_id': self.backtest_id,
            'task_id': taskId,
            'average_price': position['average_price'],
            'amount': position['amount']
          })
        if task_or_backtest:
            if self.is_mock:
              mock_service_charge = task_or_backtest['service_charge']
              mock_lower_limit_of_fees = task_or_backtest['lower_limit_of_fees']
            else:
              mock_service_charge = task_or_backtest['mock_service_charge']
              mock_lower_limit_of_fees = task_or_backtest['mock_lower_limit_of_fees']
        # 计算手续费
        commission = Decimal(calculate_stock_fee("buy" if trade.order_type == OrderType.STOCK_BUY else "sell",
                                         float(trade.traded_price),
                                         int(trade.traded_volume),
                                         float(mock_service_charge),
                                         float(mock_lower_limit_of_fees)))
        # 更新任务账户的可用金额
        if trade.order_type == OrderType.STOCK_BUY:
          self.orm.update_task_can_use_amount(self.backtest_id,taskId, round(-(traded_amount + commission),2))
        elif trade.order_type == OrderType.STOCK_SELL:
          self.orm.update_task_can_use_amount(self.backtest_id,taskId, round(traded_amount - commission,2))
        
                
    except Exception as e:
      print("on_stock_trade error")
      print(e)
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
    print("on order_error callback")
    print(order_error.order_id, order_error.error_id, order_error.error_msg)
  def on_cancel_error(self, cancel_error):
    """
    撤单失败推送
    :param cancel_error: XtCancelError 对象
    :return:
    """
    print("on cancel_error callback")
    print(cancel_error.order_id, cancel_error.error_id, cancel_error.error_msg)
  def on_order_stock_async_response(self, response):
    """
    异步下单回报推送
    :param response: XtOrderResponse 对象
    :return:
    """
    pass
   


class QMT:
  def __init__(self,orm):
    self.qmt_trader = None
    self.orm = orm
    self.callback = MyXtQuantTraderCallback(orm,False)
    
    
    self.is_connect = False
    self.simulator = None
    
    
  def test_connect(self,path):
    if sys.platform.startswith('darwin'):
      return {
        'msg':'',
        'is_connect':True,
        'account_arr':['121600012698']
      }
    
    import random
    from pyapp.pkg.xtquant.xttrader import XtQuantTrader
    
    result = {
      'msg':'',
      'is_connect':False,
      'account_arr':[]
    }
    session_id = int(random.randint(100000, 999999)) 
    xt_trader = XtQuantTrader(path, session_id)
    xt_trader.start() 
    connect_result = xt_trader.connect()
    out = xt_trader.query_account_status()
    account_arr = []
    for obj in out:
      if hasattr(obj, 'account_id'):
        account_arr.append(getattr(obj, 'account_id'))
    result['account_arr'] = account_arr


    if connect_result == 0:
      print('连接成功')
      result['is_connect'] = True
    else:
      result['msg'] = 'QMT路径错误,请重新检查!'
    return result
    
    
  def connect_qmt(self,params):
    if sys.platform.startswith('darwin'):
      self.is_connect = True
      return True

    self.qmt_trader = qmt_trader(params['mini_qmt_path'], params['client_id'])
    
    
    # 连接QMT 传递回调
    self.is_connect = self.qmt_trader.connect(self.callback)
    return self.is_connect
  
  # 购买国债逆回购
  def buy_reverse_repo(self):
    System.system_py2js(self,'remoteCallBack',  {
        "message": "正在执行自动购入国债逆回购",
    })
    judge,text = self.qmt_trader.reverse_repurchase_of_treasury_bonds()
    System.system_py2js(self,'remoteCallBack',  {
        "message": "" + text,
    })
    
  def auto_buy_new_stock(self):
    System.system_py2js(self,'remoteCallBack',  {
        "message": "正在执行自动打新",
    })
    df = stock_xgsglb_em_on_today()
    selected_columns = ['申购代码', '申购上限', '发行价格']
    for _, row in df[selected_columns].iterrows():
      # 获取每行的数据
      code = row['申购代码']
      limit = row['申购上限']
      price = row['发行价格']
      # 这里可以添加你的处理逻辑
      print(f"申购代码: {code}, 申购上限: {limit}, 发行价格: {price}")
      codeSt = convert_stock_suffix(code)
      self.qmt_trader.buy(codeSt,limit,price,order_remark='打新')

  def auto_buy_convertible_bond(self):
    System.system_py2js(self,'remoteCallBack',  {
        "message": "正在执行自动打债",
    })
    df = bond_zh_cov()
    selected_columns = ['申购代码', '申购上限']

    for _, row in df[selected_columns].iterrows():
      # 获取每行的数据
      code = row['申购代码']
      limit = row['申购上限']
      price = 100
      limit = limit * 10000
      codeSt = convert_stock_suffix(code)
      self.qmt_trader.buy(codeSt,limit,price,order_remark='打债')
   
  
  def calculate_stock_returns(self,saveData,order_count_type):

      if order_count_type == 1:
        pass
      else:
        positions_arr = self.orm.query_position_by_task_or_backtest_id(backtest_id=saveData['backtest_id'])
        position_total_value = 0
        positions = json.loads(saveData['positions'])

        for position in positions_arr:
          for order_position in positions:
            if position['security_code'] == convert_stock_suffix(order_position['security']):
              position_total_value += position['volume'] * order_position['price']
              continue
        
        backtest = self.orm.query_backtest_by_id(saveData['backtest_id'])
        self.orm.update_backtest(saveData['backtest_id'], final_amount=position_total_value + backtest['can_use_amount']  )   
  
   
  #  计算配置仓位
  def order_on_pro_rata_basis(self,orderDic:dict,task:dict,backtest_id:int = None)->int:
    if task['order_count_type'] == 1:
      return orderDic['amount']
    else:
      # 获取当前持仓
      total_value = round(orderDic['total_value'],2)
      is_buy = orderDic['is_buy']
      
      # 实际持仓
      actual_position_volume = 0
      positions = json.loads(orderDic['positions'])
      actual_position_volume = next((p['total_amount'] for p in positions if convert_stock_suffix(p['security']) == orderDic['security_code']), 0)
      if is_buy == 1:
        actual_position_volume += orderDic['amount']
      else:
        actual_position_volume -= orderDic['amount']
      
      dynamic_calculation_type = task['dynamic_calculation_type']
      accruing_amounts = 0
      
      
      positions_arr = self.orm.query_position_by_task_or_backtest_id(backtest_id=backtest_id,task_id=task['id'])
      position_total_value = 0
      for position in positions_arr:
        for order_position in positions:
          if position['security_code'] == convert_stock_suffix(order_position['security']):
            position_total_value += position['volume'] * order_position['price']
            continue
      
      # 固定仓位模式
      if dynamic_calculation_type == 1:
        if backtest_id:
          accruing_amounts = self.orm.query_backtest_by_id(backtest_id)['initial_capital']
        else:
          accruing_amounts = task['allocation_amount']
      # 根据盈亏分配
      elif dynamic_calculation_type == 2:
        can_use_amount = 0
        if backtest_id:
          can_use_amount = self.orm.query_backtest_by_id(backtest_id)['can_use_amount']
        else:
          can_use_amount = task['can_use_amount']
        accruing_amounts = round(can_use_amount + position_total_value,2)
      
      # 计算配置仓位
      allocation_amount = round(actual_position_volume * accruing_amounts / total_value,2)
      final_amount = 0
      allocation_amount = (allocation_amount // 100) * 100
      allocation_amount = int(allocation_amount)
      
      position = next((item for item in positions_arr if item.get('security_code') == orderDic['security_code']), None)
      if position:
        final_amount = abs(allocation_amount - position['volume'])
      else:
        if is_buy == 1:
          final_amount = allocation_amount
      
      return final_amount
    
    
  # 下单协议{code:code,price:price,amount:amount,type:type}
  def manage_qmt_trader(self,data):    
    try:    
      strategy_code = data['strategy_code']
      run_params = data['run_params']
      state = data['state']
      # 获取参数
      security = data['params']['security']
      style = data['params']['style']
      price = data['params']['price']
      amount = data['params']['amount']
      avg_cost = data['params']['avg_cost']
      commission = data['params']['commission']
      is_buy = data['params']['is_buy']
      add_time = data['params']['add_time']
      positions = data['positions']
      # 总金额
      total_value = data['params']['total_value']
      status = 0
      # 转换code
      security = convert_stock_suffix(security)
      if self.is_connect == False:
        status = -12
      saveData = {
        'security_code':security,
        'style':style,
        'platform':'joinquant',
        'run_params':run_params,
        'strategy_code':strategy_code,
        'fix_result_order_id':None,
        'is_buy':is_buy,
        'avg_cost':avg_cost,
        'commission':commission,
        'add_time':add_time,
        'amount':amount,
        'price':price,
        'status':status,
        'positions':json.dumps(positions),
        'total_value':total_value
      }
      
      task = next((item for item in self.orm.get_task_list() if item.get('strategy_code') == strategy_code), None)
      if not task:
        print(f"任务不存在: {strategy_code}")
        return
      
      # 获取任务类型 1是跟随 2是动态
      order_count_type = task['order_count_type']
      
      # 不是模拟环境不能受理
      if run_params == 'simple_backtest' or run_params == 'full_backtest':
        #####################     回测环境     ###########################
        if state == 'begin':
          # 创建一个回测
          backtest_id = self.orm.create_backtest({
            'name':strategy_code,
            'service_charge':task['mock_service_charge'],
            'initial_capital':task['mock_allocation_amount'],
            'lower_limit_of_fees':task['mock_lower_limit_of_fees'],
            'final_amount':0,
            'task_id':task['id'],
            'state':state,
            'order_count_type':order_count_type,
            'accruing_amounts':task['mock_allocation_amount'],
            'can_use_amount':task['mock_allocation_amount']
          })
          self.orm.update_task(task['id'], backtest_id=backtest_id) 
          # 设置回测id
          self.mockCallback = MyXtQuantTraderCallback(self.orm,True,backtest_id)
          self.simulator = QmtTradingSimulator(
              self.mockCallback, # 回测环境
          )
        if state == 'end':
          saveData["backtest_id"] = task['backtest_id']
          self.calculate_stock_returns(saveData,order_count_type)
          self.orm.update_backtest(task['backtest_id'], state=state)   
        if state == 'run':
          # 创建空订单
          saveData["backtest_id"] = task['backtest_id']
          orderId = self.orm.save_order(saveData)
          orderId = str(orderId)
          
          # 将字符串转换为 datetime 对象
          dt = datetime.strptime(add_time, '%Y-%m-%d %H:%M:%S')

          # 将 datetime 对象转换为毫秒级时间戳
          timestamp_ms = int(dt.timestamp() * 1000)
          real_amount = self.order_on_pro_rata_basis(saveData,task,saveData["backtest_id"])
          if real_amount == 0:
            print(f"委托数量{real_amount}小于0有问题")
            return
          self.simulator.place_order(
            stock_code=security,
            volume=real_amount,
            price=price,
            order_type=OrderType.STOCK_BUY if is_buy == 1 else OrderType.STOCK_SELL,
            order_time=timestamp_ms,
            price_type=PriceType.LIMIT_PRICE,
            strategy_name=str(task['id']),
            order_remark=orderId
          )
        
      #####################     实盘环境     ###########################
      else:
        # 没有检测没有连接不往下执行
        if self.is_connect == False:
          return 
        # 创建空订单
        orderId = self.orm.save_order(saveData)
        # 判断交易时间
        now = datetime.now()
        if now.hour < 9 or (now.hour == 15 and now.minute > 30) or now.hour > 15:
          System.system_py2js(self,'remoteCallBack',  {
              "message": "非交易时间不能下单",
          })
          return
        # ------------------------------ 交易函数----------------------------------------
        orderId = str(orderId)
        if amount < 0:
          print(f"委托数量{amount}小于0有问题")
          return
        
        if task['is_open'] == 1:
            order_count_type = task['order_count_type']          
            real_amount = self.order_on_pro_rata_basis(saveData,task)
            if real_amount == 0:
              print(f"委托数量{real_amount}小于0有问题")
              return
            self.qmt_trader.place_order(security=security,
                                    amount=real_amount,
                                    price=price,
                                    order_type=OrderType.STOCK_BUY if is_buy == 1 else OrderType.STOCK_SELL,
                                    strategy_name=str(task['id']),
                                    order_remark=orderId) 
        else:
          print(f"任务未开启: {strategy_code}")
    except Exception as e:
        print(e)

    

