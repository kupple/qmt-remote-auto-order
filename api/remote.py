#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socketio
import platform
import subprocess
from api.system import System
import requests
import json

def get_system_unique_id():
    system = platform.system()
    if system == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            for system in c.Win32_ComputerSystemProduct():
                return system.UUID
        except Exception as e:
            print(f"Error getting UUID on Windows: {e}")
    elif system == "Linux":
        try:
            with open('/etc/machine-id', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print("File /etc/machine-id not found.")
        except Exception as e:
            print(f"Error getting machine ID on Linux: {e}")
    elif system == "Darwin":  # macOS
        try:
            command = "ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Error getting UUID on macOS: {result.stderr}")
        except Exception as e:
            print(f"Error getting UUID on macOS: {e}")
    return None


class Remote:
    is_connected = False
    unique_id = None
    server_url = None
    def __init__(self,qmt):
        self.sio = socketio.Client()
        self.qmt = qmt

    def setup_events(self):
        @self.sio.on('connect')
        def on_connect():
            print('Connected to server')
            unique_id = get_system_unique_id()
            self.sio.emit('join_with_mac', unique_id)
            System.system_py2js(self,'remoteCallBack',  {
                "state": 1,
                "message": "Connected to server",
                "data":None,
                "unique_id":unique_id
            })
            Remote.is_connected = True
            
        @self.sio.on('message')
        def on_message(data):
            if isinstance(data, dict) and 'status' in data:
                if data['status'] == 'success':
                    Remote.unique_id = data['client_id']
            else:
                print(f'Received message: {data}')
                self.qmt.manage_qmt_trader(data)
                System.system_py2js(self,'remoteCallBack',  {
                    "state": 1,
                    "message": "",
                    "data":data,
                })

        @self.sio.on('disconnect')
        def on_disconnect():
            print('Disconnected from server')
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "Disconnected from server",
            })
            Remote.is_connected = False
    
    def disconnect(self):
        if self.sio.connected:
            self.sio.disconnect()
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "Disconnected from server",
            })
            Remote.is_connected = False
        else:
            print('Client is not connected.')
        
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
        
    
    
    def connect_ws(self,server_url):
        Remote.server_url = server_url
        try:
            self.setup_events()
            self.sio.connect(Remote.server_url)
            self.sio.wait()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            System.system_py2js(self,'remoteCallBack',  {
                "state": 0,
                "message": "服务端访问失败",
            })


        
