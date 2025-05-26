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
import threading
from api.system import System


class API(System):
    def __init__(self):
        # 创建一个qmt对象
        self.orm = ORM()
        self.common = Common(self.orm)
        self.qmt = QMT(self.orm)
        self.remote = Remote(self.qmt,self.orm)
        self.thread1 = None
        self.daily_timer = None  # 用于存储定时器对象
        
        # 国债逆回购
        self.schedule_daily_task_new_purchase(hour=15, minute=10)
        # 打新打债
        self.schedule_daily_task_new_stock(hour=10, minute=10)
        

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
    
    def connectWs(self,server_url):
        self.orm.save_config({"server_url":server_url})
        self.thread1 = threading.Thread(target=self.remote.connect, args=(server_url,))
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

    # 开启国债逆回购
    def schedule_daily_task_new_purchase(self, hour=15, minute=10):
        """
        设置每天定时执行的任务
        :param hour: 小时（24小时制），默认21（晚上9点）
        :param minute: 分钟，默认0
        """
        import datetime
        import time

        def calculate_delay():
            now = datetime.datetime.now()
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果目标时间已经过了，就设置为明天
            if now >= target_time:
                target_time = target_time + datetime.timedelta(days=1)
            
            # 计算延迟秒数
            delay = (target_time - now).total_seconds()
            return delay

        def schedule_next():
            config =  self.orm.get_setting_config()
            if config["auto_national_debt"] == 1 and config["client_id"] != "" and config["mini_qmt_path"] != "" and self.qmt.qmt_trader != None:
                self.qmt.buyReverseRepo()
            
            # 重新调度下一次执行
            if self.daily_timer is not None:  # 只有在定时器未被取消的情况下才继续调度
                delay = calculate_delay()
                self.daily_timer = threading.Timer(delay, schedule_next)
                self.daily_timer.start()

        # 取消现有的定时器（如果存在）
        self.cancel_daily_task()
        
        # 启动新的定时器
        delay = calculate_delay()
        self.daily_timer = threading.Timer(delay, schedule_next)
        self.daily_timer.start()
        return True
    
       # 开启国债逆回购
    def schedule_daily_task_new_stock(self, hour=10, minute=10):
        """
        设置每天定时执行的任务
        :param hour: 小时（24小时制），默认21（晚上9点）
        :param minute: 分钟，默认0
        """
        import datetime
        import time

        def calculate_delay():
            now = datetime.datetime.now()
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果目标时间已经过了，就设置为明天
            if now >= target_time:
                target_time = target_time + datetime.timedelta(days=1)
            
            # 计算延迟秒数
            delay = (target_time - now).total_seconds()
            return delay

        def schedule_next():
            config =  self.orm.get_setting_config()
            # 新股
            if config["auto_buy_stock_ipo"] == 1 and config["client_id"] != "" and config["mini_qmt_path"] != "" and self.qmt.qmt_trader != None:
                self.qmt.autoBuyNewStock()
                
            # 新债
            if config["auto_buy_purchase_ipo"] == 1 and config["client_id"] != "" and config["mini_qmt_path"] != "" and self.qmt.qmt_trader != None:
                self.qmt.autoBuyconvertibleBond()
            
            # 重新调度下一次执行
            if self.daily_timer is not None:  # 只有在定时器未被取消的情况下才继续调度
                delay = calculate_delay()
                self.daily_timer = threading.Timer(delay, schedule_next)
                self.daily_timer.start()

        # 取消现有的定时器（如果存在）
        self.cancel_daily_task()
        
        # 启动新的定时器
        delay = calculate_delay()
        self.daily_timer = threading.Timer(delay, schedule_next)
        self.daily_timer.start()
        return True

    def cancel_daily_task(self):
        """
        取消定时任务
        """
        if self.daily_timer is not None:
            self.daily_timer.cancel()
            self.daily_timer = None
            return True
        return False
    
    def check_strategy_code_exists(self,strategy_code):
        return self.orm.check_strategy_code_exists(strategy_code)