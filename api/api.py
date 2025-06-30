#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 业务层API,供前端JS调用
usage: 在Javascript中调用window.pywebview.api.<methodname>(<parameters>)
'''


from api.system import System
from api.db.orm import ORM
from api.remote import Remote
import json
import asyncio
from api.trade_controller import TradeController
from api.trading_related.task_scheduler import TaskScheduler
from api.trading_related.strategy_analyzer import analyze_stock_data
import threading
from api.system import System
from .tools.sysConfig import get_os_type
import subprocess
import webview
import os
import logging
import sys
from api.trading_related.deal import convert_stock_suffix
from dotenv import load_dotenv
load_dotenv()
from .global_params import G
from .trading_related.sync_data import sync_data_stocks_data
from .tools.common import transition_code,revert_transition_code,create_ths_shortcut,open_ths_shortcut

AUTO_CONNECTION_WS = int(os.getenv('AUTO_CONNECTION_WS',1))
USE_FIXED_WS_URL = int(os.getenv('USE_FIXED_WS_URL',0))
WS_URL_FIXED = os.getenv('WS_URL_FIXED')



class API(System):
    def __init__(self):
        """
        Initialize the API class.
        
        This constructor sets up the trade controller, initializes the task scheduler
        with various scheduled tasks, and starts a loop to sync stock data.

        Attributes:
            trade_controller (TradeController): Manages trade-related operations.
            remote (Remote): Facilitates remote operations with trade controller.
            thread1 (None): Placeholder for a thread object, currently not initialized.
            task_scheduler (TaskScheduler): Manages scheduled tasks related to trading.
            loop (asyncio.AbstractEventLoop): Asynchronous event loop for executing tasks.
        """
        self.trade_controller = TradeController()
        self.remote = Remote(self.trade_controller)
        self.thread1 = None
        
        self.task_scheduler = TaskScheduler(self.trade_controller)
        
        self.task_scheduler.schedule_national_debt(hour=15, minute=10)
        self.task_scheduler.schedule_new_stock(hour=10, minute=10)
        self.task_scheduler.schedule_new_bond(hour=10, minute=10)
        
        self.task_scheduler.schedule_save_all_data(hour=8, minute=56)
        
        self.loop = asyncio.get_event_loop()
        self.loop.run_in_executor(None, sync_data_stocks_data)

    def setWindow(self, window):
        '''获取窗口实例'''
        System._window = window
        
    def set_automatically(self,enable = True):
        
        if sys.platform.startswith('darwin'):
            return True
        else:
            import winreg
            
        # 从应用路径自动生成安全的注册表项名称
        app_basename = os.path.splitext(os.path.basename(sys.executable))[0]
        app_name = f"PyWebView_{app_basename}"  # 添加前缀避免冲突
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, sys.executable)
                G.logger.info(f"已启用自启动: {app_name}")
            else:
                winreg.DeleteValue(key, app_name)
                G.logger.info(f"已禁用自启动: {app_name}")
                
            winreg.CloseKey(key)
        except WindowsError as e:
            G.logger.error(f"注册表操作失败: {e}")        

    def storage_get(self, key):
        value = G.orm.getStorageVar(key)
        if key == 'qmt_user_info':
            G.user_id = json.loads(value)['id'] if value else None

        '''获取存储变量'''
        return  value

    def storage_set(self, key, val):
        '''设置存储变量'''
        G.orm.setStorageVar(key, val)

    def get_setting_config(self):
        config = G.orm.get_setting_config()
        G.run_model_type = config['run_model_type']
        G.client_type = config['client_type']
        return config

    def save_config(self, data):
        if "client_type" in data and  data['client_type'] == 1:
            create_ths_shortcut(data['ths_path'])
        G.orm.save_config(data)
    
    
    def connect_ws(self,server_url,ways = 2,is_login = False):
        if AUTO_CONNECTION_WS == 1:
            if USE_FIXED_WS_URL == 1:
                server_url = WS_URL_FIXED   
            G.orm.save_config({"server_url":server_url})
            self.thread1 = threading.Thread(target=self.remote.connect, args=(server_url,ways,is_login))
            self.thread1.start()
        
    
    def disconnect(self):
        self.remote.close_ws()
        if self.thread1 and self.thread1.is_alive():
            self.thread1.join(timeout=1)  # Wait up to 1 second for thread to finish
        
    def connect_qmt(self,params):
        result = self.trade_controller.connect_qmt(params)
        return result
    
    def get_task_list(self,data):
        return G.orm.get_task_list(data)
    
    def create_task(self,data):
        return G.orm.create_task(data)
    
    def run_task(self,data):
        st = ""
        if data["is_open"]:
            st = '开启'
        else:
            st = "关闭"
        message = data["name"] + "任务已" + st
        
        G.logger.info(message,extra={
            "showMessage": True
        })
        return G.orm.run_task(data)
    
    def delete_task(self,data):
        return G.orm.delete_task(data)
    
    def get_remote_state(self):
        return {"state":self.remote.is_connected,
                "unique_id":G.unique_id,
                }
    
    def get_unique_id(self):
        return G.unique_id
        
    def get_task_detail(self,data):
        return G.orm.get_task_detail(data)
    
    
    def transition_code(self,data,taskDic):
        return transition_code(data,taskDic)
    
    def revert_transition_code(self,data):
        return revert_transition_code(data)
    
    
    def get_order_list(self,data):
        return G.orm.get_order_list(data)
    
    def test_connect(self,path,type):
        return self.trade_controller.test_connect(path,type)
    

    def cancel_daily_task(self):
        """取消所有定时任务"""
        return self.task_scheduler.cancel_all_tasks()
    
    def check_strategy_code_exists(self,strategy_code):
        return G.orm.check_strategy_code_exists(strategy_code)

    def open_directory_dialog(self,client_type):
        """打开系统目录选择对话框（跨平台）"""
        os_type = get_os_type()
        
        if os_type == "windows":
            # Windows 直接使用 PyWebView 的文件夹选择对话框
            directory = System._window.create_file_dialog(
                webview.FOLDER_DIALOG,
                directory=os.path.expanduser("~"),
                allow_multiple=False
            )
            path = directory[0] if directory else None
            if path != None:
                if client_type == 2:
                    userdata_path = os.path.join(path, "userdata_mini")
                    if os.path.exists(userdata_path):
                        return True, userdata_path
                    else:
                        return False, None
                else:
                    xiadan_path = os.path.join(path, "xiadan.exe")
                    if os.path.exists(xiadan_path):
                        return True, path
                    else:
                        return False, None
                
            else:
                return False,None
        
        elif os_type == "macos":
            if client_type == 2:
                return True,"D:\\长城策略交易系统new\\userdata_mini"
            else:
                return True,"D:\\同花顺\\xiadan.exe"
           
        
        else:
            return None        
        
    def create_backtest(self,data):
        return G.orm.create_backtest(data)   
    
    def query_backtest_by_task_id(self, task_id):
        result = G.orm.query_backtest_by_task_id(task_id)
        return result
    
    def count_strategy_analyzer(self,task_id,backtest_id):
        sample_trades = G.orm.count_strategy_analyzer(task_id,backtest_id)
        
        backtest = G.orm.query_backtest_by_id(backtest_id)
        
        if len(sample_trades)>0:
            # 假设 trades 是你的交易数据列表
            result = analyze_stock_data(sample_trades, initial_capital=backtest['initial_capital'])
            return result
        else:
            return None

    def get_position_by_task_id(self, task_id):
        list = G.orm.query_position_by_task_id(task_id)
        for item in list:
            if item['security_code']:
                item['security_name'] = G.stock_map["all_stock_code"][item['security_code']]['name']
        return list

    
    def delete_position_by_id(self, id):
        return G.orm.delete_position_by_id(id)
    
    def update_position(self, id, params):
        return G.orm.update_position(id, params)
    
    def add_position(self, params):
        params['security_code'] = convert_stock_suffix(params['security_code'])
        return G.orm.add_position(params)
    
    def check_position_exists(self, security_code, task_id):
        return G.orm.check_position_exists(convert_stock_suffix(security_code), task_id)    
    
    def update_task(self,task_id, can_use_amount):
        return G.orm.update_task(task_id,can_use_amount=can_use_amount)
    
    def query_trade_today(self, task_id):
        return G.orm.query_trade_today(task_id)
    
    def query_log_list(self,data):
        return G.orm.query_log_list(data,page=data['page'],page_size=data['pageSize'])
    
    def clear_log(self):
        return G.orm.clear_log()
    
    def get_account_info(self):
        return self.trade_controller.get_account_info() 
    
    def is_process_exist_action(self):
        return self.trade_controller.process_check_loop()
        
    def open_ths_shortcut_action(self):
        config = G.orm.get_setting_config()
        return open_ths_shortcut(config['ths_path'] + '/autoxiadan.lnk')