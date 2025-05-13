#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socketio
import platform
import subprocess
from api.system import System
import requests
import json
from .qmt_trader import qmt_trader
from .sql import Database
class QMT:
    
    def __init__(self):
        self.qmt_trader = None
    
    def connectQMT(self):
        # 获取配置
        config = Database().get_setting_config()
        self.qmt_trader = qmt_trader(config['mini_qmt_path'], config['account'],  config['is_slippage'], 0.01)
        self.qmt_trader.connect()
    
    # 下单协议{code:code,price:price,amount:amount,type:type}
    def manage_qmt_trader(self,data):
        code = data['code']
        amount = data['amount']
        price = data['price']
        direction = data['direction']
        
        if amount < 0:
            print(f"委托数量{amount}小于0有问题")
            return
        
        task = next((item for item in Database.task_list if item.get(code) == code), None)
        if task:
            if task['is_open'] == 1:
                order_count_type = task['order_count_type']
                # 按照策略买入卖出
                if order_count_type == 1:
                    if direction == 'buy':
                        fix_result_order_id = self.qmt_trader.buy(code,amount,price,strategy_name="code")
                    elif direction == 'sell':
                        fix_result_order_id = self.qmt_trader.sell(code,amount,price)
                    data['fix_result_order_id'] = fix_result_order_id
                    Database.create_order(data)
                # 按照策略平均买入卖出
                elif order_count_type == 2:
                    self.qmt_trader.order(code,amount,price)
                    
                else:
                    print(f"任务不存在: {code}")
        else:
            print(f"任务不存在: {code}")

        pass