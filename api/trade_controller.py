#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .trading_related.qmt_trader import qmt_trader
import sys
import platform
from api.system import System
from .trading_related.deal import convert_stock_suffix,calculate_stock_fee,calculate_dividend_effect,get_qmt_price_type
from datetime import datetime
from .trading_related.additional_data import stock_xgsglb_em_on_today,bond_zh_cov
from .trading_related.qmt_trading_simulator import QmtTradingSimulator,OrderType,PriceType
from decimal import Decimal
import json
from api.global_params import G
import threading
import asyncio
from .tools.common import is_process_exist
from threading import Timer
from .trading_related.trader_call_back import MyXtQuantTraderCallback

class TradeController:
  def __init__(self):
    self.qmt_trader = qmt_trader()
    self.callback = MyXtQuantTraderCallback(False)
    self.simulator = None
    self._thread = None
    self.qmt_is_connect = False
    self.acc_is_connect = False
    self.is_need_reconnection = False
    self.is_need_reconnection_lock = True
    
  
  def process_check_loop(self):
    try:
        event = is_process_exist()  # 直接调用，不需要await
        System.system_py2js(self,'remoteCallBack',  {
            "type": "qmtProcessCheck",
            "event": event
        })
        self.qmt_is_connect = event
        if event:
          if self.is_need_reconnection == True and self.is_need_reconnection_lock == False:          
            self.is_need_reconnection = False
            config = G.orm.get_setting_config()
            # 已配置才可以选择
            if config['mini_qmt_path'] != "" and config['client_id'] != "":
              G.logger.info("正在重新连接QMT",extra={
                "showMessage": True
              })
              self.is_need_reconnection_lock = True
              # 在主线程中运行connect_qmt
              self.connect_qmt({
                "mini_qmt_path": config['mini_qmt_path'],
                "client_id": config['client_id']
              })
        else:
          # 如果之前连过才给他重连
          # if self.acc_is_connect:
          self.is_need_reconnection = True
    except Exception as e:
      error_msg = f"进程检查出错: {str(e)}"
      if G.logger:
          G.logger.error(error_msg)
  

  def connect_qmt(self,params):
    try:
      # 如果是mac 电脑开发环境直接返回成功
      if sys.platform.startswith('darwin'):
          self.acc_is_connect = True
          System.system_py2js(self,'remoteCallBack',  {
            "type": "accSubSuccess",
            "message": "QMT连接成功",
            "event": True
          })
          return True
      # 设置id
      self.qmt_trader.path = params['mini_qmt_path']
      self.qmt_trader.account = params['client_id']
      # 连接QMT 传递回调
      self.acc_is_connect = self.qmt_trader.connect(self.callback)
      if self.acc_is_connect:
        message = "QMT连接成功"
      else:
        message = "QMT连接失败"
      System.system_py2js(self,'remoteCallBack',  {
        "type": "accSubSuccess",
        "message": message,
        "event": self.acc_is_connect
      })
      self.is_need_reconnection_lock = False
    except Exception as e:
      G.logger.error("连接QMT失败! code 1980" + str(e))
      self.is_need_reconnection_lock = False
      
  
  # 购买国债逆回购
  def buy_reverse_repo(self):

    G.logger.info("正在执行自动购入国债逆回购",extra={
            "showMessage": True
    })
    
    judge,text = self.qmt_trader.reverse_repurchase_of_treasury_bonds()

    if judge:
      G.logger.info("" + text,extra={
              "showMessage": True
      })
    else:
      G.logger.error("" + text,extra={
              "showMessage": True
      })
    
  def auto_buy_new_stock(self):
    G.logger.info("正在执行自动打新",extra={
            "showMessage": True
    })
    df = stock_xgsglb_em_on_today()
    selected_columns = ['申购代码', '申购上限', '发行价格']
    for _, row in df[selected_columns].iterrows():
      # 获取每行的数据
      code = row['申购代码']
      limit = row['申购上限']
      price = row['发行价格']
      # 这里可以添加你的处理逻辑
      G.logger.info("申购代码: {} 申购上限: {} 发行价格: {}".format(code, limit, price),extra={
              "showMessage": True
      })
      codeSt = convert_stock_suffix(code)
      self.qmt_trader.buy(codeSt,limit,price,order_remark='打新')

  def auto_buy_convertible_bond(self):
    G.logger.info("正在执行自动打债",extra={
            "showMessage": True
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

    positions_arr = G.orm.query_position_by_task_or_backtest_id(backtest_id=saveData['backtest_id'])
    position_total_value = 0
    positions = json.loads(saveData['positions'])

    for position in positions_arr:
      for order_position in positions:
        if position['security_code'] == convert_stock_suffix(order_position['security']):
          position_total_value += position['volume'] * order_position['price']
          continue

    backtest = G.orm.query_backtest_by_id(saveData['backtest_id'])
    G.orm.update_backtest(saveData['backtest_id'], final_amount=position_total_value + backtest['can_use_amount']  )   

  
   
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
      print(actual_position_volume)
      dynamic_calculation_type = task['dynamic_calculation_type']
      accruing_amounts = 0
      
      
      positions_arr = G.orm.query_position_by_task_or_backtest_id(backtest_id=backtest_id,task_id=task['id'])
      position_total_value = 0
      for position in positions_arr:
        for order_position in positions:
          if position['security_code'] == convert_stock_suffix(order_position['security']):
            position_total_value += position['volume'] * order_position['price']
            continue
      
      # 固定仓位模式
      if dynamic_calculation_type == 1:
        if backtest_id:
          accruing_amounts = G.orm.query_backtest_by_id(backtest_id)['initial_capital']
        else:
          accruing_amounts = task['allocation_amount']
      # 根据盈亏分配
      elif dynamic_calculation_type == 2:
        can_use_amount = 0
        if backtest_id:
          can_use_amount = G.orm.query_backtest_by_id(backtest_id)['can_use_amount']
        else:
          can_use_amount = task['can_use_amount']
        accruing_amounts = round(can_use_amount + position_total_value,2)
        
      
      # 计算配置仓位
      allocation_amount = round(actual_position_volume * accruing_amounts / total_value,2)
      print(allocation_amount,accruing_amounts,actual_position_volume,total_value)
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
    
  
  # 统一处理-下单接口
  def place_order(self, 
                   stock_code='600031.SH',
                   volume=100, 
                   price=20,
                   is_buy=True,
                   order_time=None,
                   order_style_str='', 
                   strategy_name='', 
                   order_remark='',
                   is_mock_state=1,
                   ):
    price_type, optimal_price = get_qmt_price_type(stock_code, order_style_str, is_buy, price)
    order_type = OrderType.STOCK_BUY if is_buy == 1 else OrderType.STOCK_SELL
    
    if is_mock_state == 0:
        self.qmt_trader.place_order(
          stock_code=stock_code,
          volume=volume,
          price=optimal_price,
          order_type=order_type,
          price_type=price_type,
          strategy_name=strategy_name,
          order_remark=order_remark
        ) 
    elif is_mock_state == 1:
        self.simulator.place_order(
          stock_code=stock_code,
          volume=volume,
          price=optimal_price,
          order_type=order_type,
          order_time=order_time,
          price_type=price_type,
          strategy_name=strategy_name,
          order_remark=order_remark
        )
    elif is_mock_state == 2:
      mockCallback = MyXtQuantTraderCallback(False,is_pre=True)
      self.simulator = QmtTradingSimulator(
          2,
          mockCallback, # 回测环境
      )
      self.simulator.place_order(
          stock_code=stock_code,
          volume=volume,
          price=optimal_price,
          order_type=order_type,
          price_type=price_type,
          order_time=order_time,
          strategy_name=strategy_name,
          order_remark=order_remark
        ) 
    else:
      G.logger.error("is_mock_state参数错误")
  # 下单协议{code:code,price:price,amount:amount,type:type}
  def manage_qmt_trader(self,data):    
    print(data)
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
      dividends = data['dividends']
      # 总金额
      total_value = data['params']['total_value']
      # 转换code
      security = convert_stock_suffix(security)
      
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
        'status':0,
        'positions':json.dumps(positions),
        'total_value':total_value
      }
      
      if G.run_model_type == 2:
        user_id = G.user_id
      else:
        user_id = G.unique_id
      
      taskList =  G.orm.get_task_list({"user_id":str(user_id)})
      task = next((item for item in taskList if item.get('strategy_code') == strategy_code), None)
      if not task:
        G.logger.info("任务不存在: {}".format(strategy_code),extra={
          "showMessage": True
        })
        return
      # 获取任务类型 1是跟随 2是动态
      order_count_type = task['order_count_type']
      
      # 不是模拟环境不能受理
      if run_params == 'simple_backtest' or run_params == 'full_backtest':
        #####################     回测环境     ###########################
        if state == 'begin':
          if task['order_count_type'] == 2:
            accruing_amounts = task['mock_allocation_amount']
            can_use_amount = task['mock_allocation_amount']
            initial_capital = task['mock_allocation_amount']
          else:
            accruing_amounts = total_value
            can_use_amount = total_value
            initial_capital = total_value
          # 创建一个回测
          backtest_id = G.orm.create_backtest({
            'name':strategy_code,
            'service_charge':task['mock_service_charge'],
            'lower_limit_of_fees':task['mock_lower_limit_of_fees'],
            'final_amount':0,
            'task_id':task['id'],
            'state':state,
            'order_count_type':order_count_type,
            'initial_capital':initial_capital,
            'accruing_amounts':accruing_amounts,
            'can_use_amount':can_use_amount
          })
          G.orm.update_task(task['id'], backtest_id = backtest_id) 
          # 设置回测id
          self.mockCallback = MyXtQuantTraderCallback(True, backtest_id)
          self.simulator = QmtTradingSimulator(
              1 if task['is_simulation'] == True else 0, #是否需要仿真回测
              self.mockCallback # 回测环境
          )
        if state == 'dividends':
          if dividends == None:
            return
          if len(dividends) == 0:
            return
          backtest_id = task['backtest_id']
          positions = G.orm.query_position_by_task_or_backtest_id(backtest_id=backtest_id,task_id=task['id'])
          positions_dict = {position['security_code']: position for position in positions}
          if security in positions_dict:
            position = positions_dict[security] 
            dividend = dividends[0]
            effect = calculate_dividend_effect(
              security_code=security,
              holding_shares=position['volume'],
              purchase_price=price,
              bonus_pre_tax=dividend['bonus_pre_tax'],
              scale_factor=dividend['scale_factor'],
            )
            G.orm.update_position(position['id'], {
              'volume': effect['new_shares'],
              'backtest_id': backtest_id,
              'task_id': task['id'],
              'average_price': effect['new_cost_per_share'],
            })
            # G.orm.update_task_can_use_amount(backtest_id,task['id'], round(position['volume'] * dividends[0]['scale_factor'],2))
        if state == 'end':
          saveData["backtest_id"] = task['backtest_id']
          self.calculate_stock_returns(saveData,order_count_type)
          G.orm.update_backtest(task['backtest_id'], state=state)   
        if state == 'run':
          # 创建空订单
          saveData["backtest_id"] = task['backtest_id']
          orderId = G.orm.save_order(saveData)
          orderId = str(orderId)
          
          # 将字符串转换为 datetime 对象
          dt = datetime.strptime(add_time, '%Y-%m-%d %H:%M:%S')

          # 将 datetime 对象转换为毫秒级时间戳
          timestamp_ms = int(dt.timestamp() * 1000)
          real_amount = self.order_on_pro_rata_basis(saveData,task,saveData["backtest_id"])
          if real_amount == 0:
            G.logger.error("委托数量{}小于0有问题".format(real_amount),extra={
                    "showMessage": True
            })
            return
          if self.simulator != None:
            self.place_order(
              stock_code=security,
              volume=real_amount,
              price=price,
              is_buy=True if is_buy == 1 else False,
              order_time=timestamp_ms,
              order_style_str=style,
              strategy_name=str(task['id']),
              order_remark=orderId,
              is_mock_state=1
            )
          else:
            G.logger.error("异常Code 121",extra={
                    "showMessage": True
            })
        
      #####################     实盘环境     ###########################
      else:
        is_mock_state = 2 if run_params == 'pre' else 0
        if state != 'run':
          G.logger.error("实盘只有run状态,请不要修改运行环境",extra={
                  "showMessage": True
          })
          return
          
        # 没有检测没有连接不往下执行
        if self.acc_is_connect == False:
          G.logger.error("qmt 没有正常运行",extra={
                  "showMessage": True
          })
          return 
        # 创建空订单
        orderId = G.orm.save_order(saveData)
        # 判断交易时间
        now = datetime.now()
        if is_mock_state != 2 and (now.hour < 9 or (now.hour == 15 and now.minute > 30) or now.hour > 15):
          G.logger.info("非交易时间不能下单",extra={
                  "showMessage": True
          })
          return
        # ------------------------------ 交易函数----------------------------------------
        orderId = str(orderId)
        if amount < 0:
          G.logger.info("委托数量{}小于0有问题".format(amount),extra={
                  "showMessage": True
          })
          return
        
        if task['is_open'] == 1:
            order_count_type = task['order_count_type']          
            real_amount = self.order_on_pro_rata_basis(saveData,task)
            if real_amount == 0:
              G.logger.info("委托数量{}小于0有问题".format(real_amount),extra={
                      "showMessage": True
              })
              return
            
            self.place_order(
                stock_code=security,
                volume=real_amount,
                price=price,
                is_buy=True if is_buy == 1 else False,
                order_time=None,
                order_style_str=style,
                strategy_name=str(task['id']),
                order_remark=orderId,
                is_mock_state=is_mock_state
            )
        else:
          G.logger.info("任务未开启: {}".format(strategy_code),extra={
                  "showMessage": True
          })
    except Exception as e:
        import traceback
        error_msg = f"manage_qmt_trader error: {str(e)}\n{traceback.format_exc()}"
        G.logger.error(error_msg,extra={
          "showMessage": True
        })

    

  def test_connect(self,path,client_type,**kwargs):
    if client_type == 2:
      if sys.platform.startswith('darwin'):
        return {
          'msg':'',
          'is_connect':True,
          'account_arr':['888888888']
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
        result['is_connect'] = True
      else:
        result['msg'] = 'QMT路径错误,请重新检查!'
      return result
    else:
      pass
      
  
  
  def get_account_info(self):
    if self.qmt_is_connect == False or self.acc_is_connect == False:
       G.logger.error("QMT没有正常运行,请打开或重新打开qmt客户端",extra={
          "showMessage": True
        })
    else:
      return self.qmt_trader.balance()