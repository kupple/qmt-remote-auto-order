#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import subprocess
from api.system import System
import requests
import json
from .qmt_trader import qmt_trader
from .sql import Database
from .xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback




class MyXtQuantTraderCallback(XtQuantTraderCallback):
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
        print("on order callback:")
        print(order.stock_code, order.order_status, order.order_sysid)
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
        print("on_order_stock_async_response")
        print(response.account_id, response.order_id, response.seq)


class QMT:
    def __init__(self,sql):
        self.qmt_trader = None
        self.sql = sql
        self.callback = MyXtQuantTraderCallback()
        
    def connectQMT(self):
        # 获取配置
        config = Database().get_setting_config()
        self.qmt_trader = qmt_trader(config['mini_qmt_path'], config['account'],  config['is_slippage'], 0.01)
        
        # 连接QMT 传递回调
        self.qmt_trader.connect(self.callback)
    
    # 下单协议{code:code,price:price,amount:amount,type:type}
    def manage_qmt_trader(self,data):
        user_id = data['user_id']
        strategy_id = data['strategy_id']
        method = data['method']
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
        saveData = {
            'security_code':security,
            'value':value,
            'style':style,
            'pindex':pindex,
            'platform':'joinquant',
            'run_params':run_params,
            'strategy_code':strategy_id,
            'fix_result_order_id':None,
            'is_buy':is_buy,
            'avg_cost':avg_cost,
            'commission':commission,
            'add_time':add_time,
            'amount':amount,
            'price':price,
        }
        # 创建空订单
        self.sql.save_order(saveData)
        if amount < 0:
            print(f"委托数量{amount}小于0有问题")
            return
        
        task = next((item for item in Database.task_list if item.get(strategy_id) == strategy_id), None)
        if task:
            if task['is_open'] == 1:
                order_count_type = task['order_count_type']
                # 按照策略买入卖出
                if order_count_type == 1:
                    if is_buy == 1:
                        fix_result_order_id = self.qmt_trader.buy(security,amount,price,strategy_name=strategy_id)
                    elif is_buy == 0:
                        fix_result_order_id = self.qmt_trader.sell(security,amount,price)
                    data['fix_result_order_id'] = fix_result_order_id
                    Database.create_order(data)
                # 按照策略平均买入卖出
                elif order_count_type == 2:
                    pass
                    
                else:
                    print(f"任务不存在: {strategy_id}")
        else:
            print(f"任务不存在: {strategy_id}")

        