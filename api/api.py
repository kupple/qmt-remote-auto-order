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
import sqlite3
import os
from io import BytesIO
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler




class API():
    def __init__(self):
        # 创建一个qmt对象
        self.qmt = QMT()
        self.db = Database()
        self.common = Common()
        self.remote = Remote(self.qmt)

    def setWindow(self, window):
        '''获取窗口实例'''
        System.window = window

    def getSettingConfig(self):
        return Database().get_setting_config()

    def saveConfig(self, data):
        self.db.save_config(data['mini_qmt_path'], data['client_id'])
    
    def isProcessExist(self):
        return self.common.is_process_exist()
    
    def connectWs(self,server_url):
        self.db.save_config(server_url=server_url)
        self.remote.connect_ws(server_url)
        
    def disconnect(self):
        self.remote.disconnect()
        
    def testConnect(self,server_url):
        self.remote.testConnect(server_url)
        
    def getTaskList(self):
        return self.db.get_task_list()
    
    def createTask(self,data):
        return self.db.create_task(data)
    
    def runTask(self,data):
        return self.db.run_task(data)
    
    def deleteTask(self,data):
        return self.db.delete_task(data)
    
    def getRemoteState(self):
        return {"state":self.remote.is_connected,
                "unique_id":self.remote.unique_id,
                }
    def getTaskDetail(self,data):
        return self.db.get_task_detail(data)
    
    def getWsConfig(self):
        config = self.db.get_setting_config()
        return {
            "server_url":config['server_url'],
            "unique_id":self.remote.unique_id,
            "is_connected":self.remote.is_connected,
        }
    
    def copyRequestCode(self,data):
        return self.common.copy_request_code(data)