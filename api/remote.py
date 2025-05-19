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

class Remote:
    is_connected = False
    unique_id = None
    server_url = None
    RECONNECT_INTERVAL = 5  # seconds
    
    def __init__(self,qmt):
        self.stop_event = asyncio.Event()
        self.loop = asyncio.new_event_loop()
        self.qmt = qmt
        self.ws = None
        self.reconnect_count = 0
        self.should_reconnect = True
        asyncio.set_event_loop(self.loop)  # 设置当前线程的事件循环


    async def handle_messages(self):
        try:
            while True:
                message = await self.ws.recv()
                data = json.loads(message)
                print(f'Received message: {data}')
                self.qmt.manage_qmt_trader(data)
                System.system_py2js(self,'remoteCallBack',  {
                    "state": 1,
                    "message": "",
                    "data":data,
                })

        except websockets.exceptions.ConnectionClosed:
            print('Connection closed')
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "Disconnected from server",
            })
            Remote.is_connected = False
            if self.should_reconnect:
                await self.reconnect()

    async def reconnect(self):
        self.reconnect_count += 1
        print(f'Attempting to reconnect... (Attempt {self.reconnect_count})')
        System.system_py2js(self,'remoteCallBack',  {
            "state": 0,
            "message": f"正在尝试重连... (第{self.reconnect_count}次)",
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
                    "message": "Disconnected from server",
                })
                Remote.is_connected = False
        except Exception as e:
            print(f'Error during disconnect: {e}')
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "Error disconnecting from server",
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
    
    async def connect_ws(self,server_url):
        Remote.server_url = server_url
        try:
            TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjIjoiT21Uc0tkIiwidSI6IkYzMEMyQzM5LUFEQzMtNUEyNC1BRDEzLTc1MEJFNDQ1MjczQyJ9.5Y0OblUKGRQQRBWZImq-lFLsZmGck0SVRTNozcgRcQU"
            self.ws = await websockets.connect(server_url, additional_headers={"Authorization": f"Bearer {TOKEN}"})

            System.system_py2js(self,'remoteCallBack',  {
                "state": 1,
                "message": "Connected to server",
                "data":None
            })
            Remote.is_connected = True
            self.reconnect_count = 0  # Reset reconnect count on successful connection
            
            # Start message handling
            await self.handle_messages()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "服务端访问失败",
            })
            if self.should_reconnect:
                await self.reconnect()

    def connect(self, server_url):
        self.should_reconnect = True
        self.reconnect_count = 0
        self.stop_event.clear()
        self.loop.run_until_complete(self.connect_ws(server_url))

    def close_ws(self):
        self.should_reconnect = False
        self.stop_event.set()
        try:
            future = asyncio.run_coroutine_threadsafe(self.disconnect(), self.loop)
            future.result()  # Wait for the disconnect to complete
        except Exception as e:
            print(f'Error during close_ws: {e}')
        finally:
            self.stop_event.clear()

        
