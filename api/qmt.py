#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .trading_related.qmt_trader import qmt_trader
from .db.orm import ORM
from pyapp.pkg.xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
import sys
import platform
from api.system import System
from .trading_related.deal import convert_stock_suffix
import datetime
from .trading_related.additional_data import stock_xgsglb_em_on_today,bond_zh_cov

class MyXtQuantTraderCallback(XtQuantTraderCallback):
 
 def __init__(self,orm) -> None:
  self.orm = orm
  super().__init__()
  
 def on_disconnected(self):
  """
  连接断开
  :return:
  """
  print("connection lost")
 def on_stock_order(self, order):
  """
  委托回报推送
  :param order: XtOrder对象
  :return:
  """
  # 系统下的单
  if order.order_remark and order.strategy_name:
    orderId = order.order_remark
    self.orm.save_entrust(order,{
      "orders_id": orderId
    })
 def on_stock_asset(self, asset):
  """
  资金变动推送
  :param asset: XtAsset对象
  :return:
  """
  print("on asset callback")
  print(asset.account_id, asset.cash, asset.total_asset)
 def on_stock_trade(self, trade):
  """
  成交变动推送
  :param trade: XtTrade对象
  :return:
  """
  print("on trade callback")
  print(trade.account_id, trade.stock_code, trade.order_id)
 def on_stock_position(self, position):
  """
  持仓变动推送
  :param position: XtPosition对象
  :return:
  """
  print("on position callback")
  print(position.stock_code, position.volume)
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
  # 系统下的单
  if response.order_remark and response.strategy_name:
   orderId = response.order_remark
   self.orm.save_trade(response,{
    "orders_id": orderId
   })
   # self.orm.update_order(orderId,status = 1,fix_result_order_id = response.order_id)
   


class QMT:
  def __init__(self,orm):
    self.qmt_trader = None
    self.orm = orm
    self.callback = MyXtQuantTraderCallback(orm)
    self.is_connect = False
    
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
    
    
  def connectQMT(self,params):
    if sys.platform.startswith('darwin'):
      self.is_connect = True
      return True

    self.qmt_trader = qmt_trader(params['mini_qmt_path'], params['client_id'])
    
    
    # 连接QMT 传递回调
    self.is_connect = self.qmt_trader.connect(self.callback)
    return self.is_connect
  
  # 购买国债逆回购
  def buyReverseRepo(self):
    judge,text = self.qmt_trader.reverse_repurchase_of_treasury_bonds()
    System.system_py2js(self,'remoteCallBack',  {
        "message": "" + text,
    })
    
  def autoBuyNewStock(self):
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

  def autoBuyconvertibleBond(self):
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

    
  # 下单协议{code:code,price:price,amount:amount,type:type}
  def manage_qmt_trader(self,data):
    try:    
      strategy_code = data['strategy_code']
      run_params = data['run_params']
      # 获取参数
      security = data['params']['security']
      value = data['params']['value']
      style = data['params']['style']
      pindex = data['params']['pindex']
      price = data['params']['price']
      amount = data['params']['amount']
      avg_cost = data['params']['avg_cost']
      commission = data['params']['commission']
      is_buy = data['params']['is_buy']
      add_time = data['params']['add_time']
      status = 0
      if self.is_connect == False:
        status = -12
      saveData = {
        'security_code':security,
        'value':value,
        'style':style,
        'pindex':pindex,
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
        'status':status
      }
      # 创建空订单
      oderId = self.orm.save_order(saveData)
      
      # 没有检测没有连接不往下执行
      if self.is_connect == False:
        return 
      
      # 不是模拟环境不能受理
      if run_params == 'simple_backtest' or run_params == 'full_backtest':
        print("回测环境不受理")
        return
      # 判断交易时间
      now = datetime.datetime.now()
      if now.hour < 9 or (now.hour == 15 and now.minute > 30) or now.hour > 15:
        System.system_py2js(self,'remoteCallBack',  {
            "message": "非交易时间不能下单",
        })
        return
      # ------------------------------ 交易函数----------------------------------------
      oderId = str(oderId)
      if amount < 0:
        print(f"委托数量{amount}小于0有问题")
        return
      task = next((item for item in self.orm.get_task_list() if item.get('strategy_code') == strategy_code), None)
      if task:
        if task['is_open'] == 1:
          order_count_type = task['order_count_type']
          security = convert_stock_suffix(security)
          # 按照策略买入卖出
          if order_count_type == 1:
            if is_buy ==  1:
              self.qmt_trader.buy(security=security,
                                  amount=amount,
                                  order_style_str='',
                                  price=price,
                                  strategy_name=strategy_code,
                                  order_remark = oderId)
            elif is_buy == 0:
              self.qmt_trader.sell(security=security,
                                   amount=amount,
                                   order_style_str='',
                                   strategy_name=strategy_code,
                                   price=price,
                                   order_remark = oderId)
          
        else:
          print(f"任务不存在: {strategy_code}")
      else:
        print(f"任务不存在: {strategy_code}")
    except Exception as e:
        print(e)

    

