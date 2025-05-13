
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 数据库操作相关的API
'''

import sqlite3
import os
import platform
import subprocess
import pyperclip
from api.sql import Remote
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

class Common:

    def is_process_exist(self):
        app_name = "XtMiniQmt.exe"
        try:
            # 创建STARTUPINFO对象并设置隐藏窗口标志
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE  # 隐藏窗口
            
            # 执行tasklist命令并传入STARTUPINFO
            output = subprocess.check_output(
                ['tasklist'], 
                universal_newlines=True,
                startupinfo=startupinfo  # 添加这一行以隐藏终端窗口
            )
            
            # 后续代码保持不变
            index = output.find("System")
            if index == -1:
                return False
            data = output[index:]
            fields = data.split()
            for i, field in enumerate(fields):
                if field == app_name:
                    try:
                        pid = int(fields[i + 1])
                        return True
                    except (IndexError, ValueError):
                        return False
            return False
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False
    def copy_request_code(self,data):
        server_url = Remote.server_url
        try:
            copyText = f"""        
        url = "{server_url}/send_message"
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
        """
            pyperclip.copy(copyText)
            return True
        except Exception as e:
            print(f"复制失败: {e}")
            return False