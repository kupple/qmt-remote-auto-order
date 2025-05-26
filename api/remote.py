#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import websockets
import platform
import subprocess
from api.system import System
import requests
import json
import time
from .tools.sysConfig import get_system_unique_id
from datetime import datetime,timezone
from api.tools.tokenManager import generate_token

class Remote:
    is_connected = False
    unique_id = None
    server_url = None
    RECONNECT_INTERVAL = 5  # seconds
    
    def __init__(self,qmt, orm):
        self.stop_event = asyncio.Event()
        self.qmt = qmt
        self.orm = orm
        self.ws = None
        self.reconnect_count = 0
        self.should_reconnect = True
        self.loop = None  # 初始化为 None

    async def handle_messages(self):
        try:
            while True:
                message = await self.ws.recv()
                data = json.loads(message)
                content = data['content'] = json.loads(data['content'])
                # 发送确认消息给服务端
                await self.ws.send(json.dumps({
                    "type": "ack",
                    "id": data.get("id", ""),
                    "timestamp": int(time.time() * 1000)  # 转换为毫秒级整数时间戳
                }))
                # 发送信息 写法没错
                System.system_py2js(self,'remoteCallBack',  {
                    "state": 1,
                    "message": "",
                    "data":content,
                })
                
                if self.qmt.is_connect == False :
                    System.system_py2js(self,'remoteCallBack',  {
                        "state": 1,
                        "message": "",
                        "status": "2",
                        "data":"请先在个人页面配置好qmt路径和资金账号",
                    })
                self.qmt.manage_qmt_trader(content)

        except websockets.exceptions.ConnectionClosed:
            print('Connection closed')
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "已断开服务器连接",
            })
            Remote.is_connected = False
            if self.should_reconnect:
                await self.reconnect()

    async def reconnect(self):
        self.reconnect_count += 1
        print(f'Attempting to reconnect... (Attempt {self.reconnect_count})')
        System.system_py2js(self,'remoteCallBack',  {
            "state": 0,
            "message": f"正在尝试重连... (第{self.reconnect_count}次) - {time.strftime('%Y-%m-%d %H:%M:%S')}",
        })
        
        await asyncio.sleep(self.RECONNECT_INTERVAL)
        await self.connect_ws(Remote.server_url)

    async def disconnect(self):
        self.should_reconnect = False
        try:
            if self.ws:
                await self.ws.close()
                self.ws = None
                System.system_py2js(self,'remoteCallBack',  {
                    "state": 0,
                    "message": "已断开服务器连接",
                })
                Remote.is_connected = False
        except Exception as e:
            print(f'Error during disconnect: {e}')
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "断开服务器连接时出错",
            })
            Remote.is_connected = False
        
    def testConnect(self):
        url = f"{Remote.server_url}/send_message"
        unique_id = get_system_unique_id()
        payload = json.dumps({
            "message": "Hello, specific client!",
            "client_id": unique_id
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            System.system_py2js(self,'remoteCallBack',  {
                "state": 2,
                "type": 'test',
                "message": "测试-通信正常",
            })
    
    async def connect_ws(self,server_url,ways = 1):
        print("Starting connect_ws...")
        Remote.server_url = server_url
        try:
            TOKEN = None
            if ways == 2:
                TOKEN = self.orm.getStorageVar('qmt_token')
            else:
                config = self.orm.get_setting_config()
                unique_id = get_system_unique_id()
                plaintext = {
                    "u": unique_id            
                }
                TOKEN = generate_token(plaintext,config['salt'])
            
            print("Attempting to connect to WebSocket...")
            self.ws = await websockets.connect(server_url, additional_headers={"Authorization": f"Bearer {TOKEN}"})
            print("WebSocket connected successfully!")

            System.system_py2js(self,'remoteCallBack',  {
                "state": 1,
                "message": "已连接到服务器",
                "data":None
            })
            Remote.is_connected = True
            self.reconnect_count = 0  # Reset reconnect count on successful connection
            
            print("Starting handle_messages...")
            # Start message handling
            await self.handle_messages()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "服务端访问失败",
            })
            if self.should_reconnect:
                print("Attempting to reconnect...")
                await self.reconnect()

    def connect(self, server_url,ways):
        print(ways)
        print("Starting connect method...")
        self.should_reconnect = True
        self.reconnect_count = 0
        self.stop_event.clear()
        
        # 为当前线程创建新的事件循环
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        async def start_connection():
            try:
                await self.connect_ws(server_url,ways)
            except Exception as e:
                print(f"Error in connect_ws: {e}")
        
        # 直接在当前线程的事件循环中运行
        self.loop.run_until_complete(start_connection())

    def close_ws(self):
        self.should_reconnect = False
        self.stop_event.set()
        if self.loop and self.loop.is_running():
            try:
                # 在事件循环中运行断开连接
                future = asyncio.run_coroutine_threadsafe(self.disconnect(), self.loop)
                future.result()  # 等待断开连接完成
            except Exception as e:
                print(f'Error during close_ws: {e}')
        self.loop = None  # 清理事件循环
        self.stop_event.clear()

        
