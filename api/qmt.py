#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socketio
import platform
import subprocess
from api.system import System
import requests
import json
from .xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from .xtquant.xttype import StockAccount
from .xtquant import xtconstant

class QMT:
    def __init__(self):
        pass
    def buy(self,security='600031.SH', order_type=xtconstant.STOCK_BUY,
                    amount=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
        '''
        单独独立股票买入函数
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code =self.adjust_stock(stock=security)
        price=self.select_slippage(stock=security,price=price,trader_type='buy')
        order_volume=amount
        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
        if order_volume>0:
            fix_result_order_id = self.xt_trader.order_stock_async(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                                order_volume=order_volume, price_type=price_type,
                                                                price=price, strategy_name=strategy_name, order_remark=order_remark)
            print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
            return fix_result_order_id
        else:
            print('买入 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume))
            
    def sell(self,security='600031.SH', order_type=xtconstant.STOCK_SELL,
                    amount=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
        '''
        单独独立股票卖出函数
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code =self.adjust_stock(stock=security)
        price=self.select_slippage(stock=security,price=price,trader_type='sell')
        order_volume=amount
        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
        if order_volume>0:
            fix_result_order_id = self.xt_trader.order_stock(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                                order_volume=order_volume, price_type=price_type,
                                                                price=price, strategy_name=strategy_name, order_remark=order_remark)
            print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
            return fix_result_order_id
        else:
            print('卖出 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume))    
    # 国债逆回购
    def reverse_repurchase_of_treasury_bonds(self,security='131810.SZ',buy_ratio=0.00001, order_type=xtconstant.STOCK_SELL
                                             ,price_type=xtconstant.FIX_PRICE,strategy_name='',order_remark=''):
        '''
        国债逆回购
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        account=self.balance()
        av_cash=account['可用金额'].tolist()[-1]
        av_cash=float(av_cash)
        av_cash=av_cash*buy_ratio
        spot_data=self.data.get_full_tick(code_list=[security])
        print('{}实时数据'.format(security),spot_data)
        price=spot_data[security]['lastPrice']
        price=float(price)
        amount=math.floor((av_cash/price)/10)*10
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code =self.adjust_stock(stock=security)
        #price=self.select_slippage(stock=security,price=price,trader_type='sell')
        order_volume=amount
        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
        if order_volume>0:
            fix_result_order_id = self.xt_trader.order_stock(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                                order_volume=order_volume, price_type=price_type,
                                                                price=price, strategy_name=strategy_name, order_remark=order_remark)
            text='国债逆回购交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id)
            return '交易成功',text
        else:
            text='国债逆回购卖出 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume)
            return '交易失败',text    

