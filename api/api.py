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
import threading
from api.system import System
from .tools.sysConfig import get_os_type
import subprocess
import webview
import os
import datetime
import logging


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

    def storage_get(self, key):
        '''获取存储变量'''
        return self.orm.getStorageVar(key)

    def storage_set(self, key, val):
        '''设置存储变量'''
        self.orm.setStorageVar(key, val)

    def getSettingConfig(self):
        return self.orm.get_setting_config()

    def saveConfig(self, data):
        self.orm.save_config(data)
    
    def isProcessExist(self):
        return self.common.is_process_exist()
    
    def connectWs(self,server_url,ways = 2):
        self.orm.save_config({"server_url":server_url})
        self.thread1 = threading.Thread(target=self.remote.connect, args=(server_url,ways,))
        self.thread1.start()
    
    def disconnect(self):
        self.remote.close_ws()
        if self.thread1 and self.thread1.is_alive():
            self.thread1.join(timeout=1)  # Wait up to 1 second for thread to finish
        
    def connectQMT(self,params):
        result = self.qmt.connectQMT(params)
        return result

        
        
    def testConnect(self,server_url):
        self.remote.testConnect(server_url)
        
    def getTaskList(self):
        return self.orm.get_task_list()
    
    def createTask(self,data):
        return self.orm.create_task(data)
    
    def runTask(self,data):
        return self.orm.run_task(data)
    
    def deleteTask(self,data):
        return self.orm.delete_task(data)
    
    def getRemoteState(self):
        return {"state":self.remote.is_connected,
                "unique_id":self.remote.unique_id,
                }
    def getTaskDetail(self,data):
        return self.orm.get_task_detail(data)
    
    def getWsConfig(self):
        config = self.orm.get_setting_config()
        return {
            "server_url":config['server_url'],
            "unique_id":self.remote.unique_id,
            "is_connected":self.remote.is_connected,
        }
    
    
    def transitionCode(self,data,taskDic):
        return self.common.transition_code(data,taskDic)
    
    def revertTransitionCode(self,data):
        return self.common.revert_transition_code(data)
    
    
    def getOrderList(self,data):
        return self.orm.get_order_list(data)
    
    def testQMTConnect(self,path):
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