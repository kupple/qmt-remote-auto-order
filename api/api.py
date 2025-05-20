#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 业务层API,供前端JS调用
usage: 在Javascript中调用window.pywebview.api.<methodname>(<parameters>)
'''

from api.system import System
from api.sql import Database
from api.common import Common
from api.remote import Remote
from api.qmt import QMT
import threading
from api.system import System


class API(System):
    def __init__(self):
        # 创建一个qmt对象
        self.sql = Database()
        self.common = Common()
        self.qmt = QMT(self.sql)
        self.remote = Remote(self.qmt)

    def setWindow(self, window):
        '''获取窗口实例'''
        System._window = window

    def getSettingConfig(self):
        return Database().get_setting_config()

    def saveConfig(self, data):
        self.sql.save_config(
            mini_qmt_path=data.get('mini_qmt_path'),
            client_id=data.get('client_id'),
            server_url=data.get('server_url'),
            salt=data.get('salt'),
            run_model_type=data.get('run_model_type')
        )
    
    def isProcessExist(self):
        return self.common.is_process_exist()
    
    def connectWs(self,server_url):
        self.sql.save_config(server_url=server_url)
        print(server_url)
        thread1 = threading.Thread(target=self.remote.connect, args=(server_url,))
        thread1.start()
        # self.remote.connect(server_url)
        
    def disconnect(self):
        self.remote.close_ws()
        
    def testConnect(self,server_url):
        self.remote.testConnect(server_url)
        
    def getTaskList(self):
        return self.sql.get_task_list()
    
    def createTask(self,data):
        return self.sql.create_task(data)
    
    def runTask(self,data):
        return self.sql.run_task(data)
    
    def deleteTask(self,data):
        return self.sql.delete_task(data)
    
    def getRemoteState(self):
        return {"state":self.remote.is_connected,
                "unique_id":self.remote.unique_id,
                }
    def getTaskDetail(self,data):
        return self.sql.get_task_detail(data)
    
    def getWsConfig(self):
        config = self.sql.get_setting_config()
        return {
            "server_url":config['server_url'],
            "unique_id":self.remote.unique_id,
            "is_connected":self.remote.is_connected,
        }
    
    
    def transitionCode(self,data,taskDic):
        return self.common.transition_code(data,taskDic)
    
    def getOrderList(self,data):
        return self.sql.get_order_list(data)