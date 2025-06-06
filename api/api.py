#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 业务层API,供前端JS调用
usage: 在Javascript中调用window.pywebview.api.<methodname>(<parameters>)
'''

from api.system import System
from api.db.orm import ORM
from api.common import Common
from api.remote import Remote
from api.qmt import QMT
from api.trading_related.task_scheduler import TaskScheduler
from api.trading_related.strategy_analyzer import analyze_stock_data
import threading
from api.system import System
from .tools.sysConfig import get_os_type
import subprocess
import webview
import os
import datetime
import logging
import sys
from api.trading_related.deal import convert_stock_suffix



class API(System):
    def __init__(self):
        # 创建一个qmt对象
        self.orm = ORM()
        self.common = Common(self.orm)
        self.qmt = QMT(self.orm)
        self.remote = Remote(self.qmt, self.orm)
        self.thread1 = None
        
        # 初始化任务调度器
        self.task_scheduler = TaskScheduler(self.qmt, self.orm)
        
        # 启动定时任务
        self.task_scheduler.schedule_national_debt(hour=15, minute=10)
        self.task_scheduler.schedule_new_stock(hour=10, minute=10)
        self.task_scheduler.schedule_new_bond(hour=10, minute=10)

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
                print(f"已启用自启动: {app_name}")
            else:
                winreg.DeleteValue(key, app_name)
                print(f"已禁用自启动: {app_name}")
                
            winreg.CloseKey(key)
        except WindowsError as e:
            print(f"注册表操作失败: {e}")        

    def storage_get(self, key):
        '''获取存储变量'''
        return self.orm.getStorageVar(key)

    def storage_set(self, key, val):
        '''设置存储变量'''
        self.orm.setStorageVar(key, val)

    def getSettingConfig(self):
        return self.orm.get_setting_config()

    def save_config(self, data):
        self.orm.save_config(data)
    
    def is_process_exist(self):
        return self.common.is_process_exist()
    
    def connect_ws(self,server_url,ways = 2):
        server_url = "ws://127.0.0.1:8080/ws"
        self.orm.save_config({"server_url":server_url})
        self.thread1 = threading.Thread(target=self.remote.connect, args=(server_url,ways,))
        self.thread1.start()
    
    def disconnect(self):
        self.remote.close_ws()
        if self.thread1 and self.thread1.is_alive():
            self.thread1.join(timeout=1)  # Wait up to 1 second for thread to finish
        
    def connect_qmt(self,params):
        result = self.qmt.connect_qmt(params)
        return result

        
        
    def test_connect(self,server_url):
        self.remote.testConnect(server_url)
        
    def get_task_list(self):
        return self.orm.get_task_list()
    
    def create_task(self,data):
        return self.orm.create_task(data)
    
    def run_task(self,data):
        st = ""
        if data["is_open"]:
            st = '开启'
        else:
            st = "关闭"
        message = data["name"] + "任务已" + st
        System.system_py2js(self,'remoteCallBack',  {
            "message": message,
        })
        return self.orm.run_task(data)
    
    def delete_task(self,data):
        return self.orm.delete_task(data)
    
    def get_remote_state(self):
        return {"state":self.remote.is_connected,
                "unique_id":self.remote.unique_id,
                }
    def get_task_detail(self,data):
        return self.orm.get_task_detail(data)
    
    
    def transition_code(self,data,taskDic):
        return self.common.transition_code(data,taskDic)
    
    def revert_transition_code(self,data):
        return self.common.revert_transition_code(data)
    
    
    def get_order_list(self,data):
        return self.orm.get_order_list(data)
    
    def test_qmt_connect(self,path):
        return self.qmt.test_connect(path)

    def cancel_daily_task(self):
        """取消所有定时任务"""
        return self.task_scheduler.cancel_all_tasks()
    
    def check_strategy_code_exists(self,strategy_code):
        return self.orm.check_strategy_code_exists(strategy_code)

    def open_directory_dialog(self):
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
                userdata_path = os.path.join(path, "userdata_mini")
                if os.path.exists(userdata_path):
                    return True, userdata_path
                else:
                    return False, None
                
            else:
                return False,None
        
        elif os_type == "macos":
           return True,"D:\\长城策略交易系统new\\userdata_mini"
        
        else:
            return None        
        
    def create_backtest(self,data):
        return self.orm.create_backtest(data)   
    
    def query_backtest_by_task_id(self, task_id):
        result = self.orm.query_backtest_by_task_id(task_id)
        return result
    
    def count_strategy_analyzer(self,task_id,backtest_id):
        sample_trades = self.orm.count_strategy_analyzer(task_id,backtest_id)
        
        
        backtest = self.orm.query_backtest_by_id(backtest_id)
        
        # 假设 trades 是你的交易数据列表
        result = analyze_stock_data(sample_trades, initial_capital=backtest['initial_capital'],
                                    service_charge=backtest['service_charge'],
                                    lower_limit_of_fees=backtest['lower_limit_of_fees'])
        return result

    def get_position_by_task_id(self, task_id):
        return self.orm.query_position_by_task_id(task_id)
    
    def delete_position_by_id(self, id):
        return self.orm.delete_position_by_id(id)
    
    def update_position(self, id, params):
        return self.orm.update_position(id, params)
    
    def add_position(self, params):
        params['security_code'] = convert_stock_suffix(params['security_code'])
        return self.orm.add_position(params)
    
    def check_position_exists(self, security_code, task_id):
        return self.orm.check_position_exists(convert_stock_suffix(security_code), task_id)    
    
    def update_task(self,task_id, can_use_amount):
        return self.orm.update_task(task_id,can_use_amount=can_use_amount)
    
    def query_trade_today(self, task_id):
        return self.orm.query_trade_today(task_id)