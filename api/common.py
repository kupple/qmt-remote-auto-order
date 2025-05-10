
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 数据库操作相关的API
'''

import sqlite3
import os
import platform
import subprocess


class Common:
    def __init__(self):
        self.db_file = 'main.db'
        self._init_database()

    def _init_database(self):
        pass

    def is_process_exist(self):
        app_name = "XtMiniQmt.exe"
        try:
            # 执行 tasklist 命令
            output = subprocess.check_output(['tasklist'], universal_newlines=True)
            # 查找 System 位置
            index = output.find("System")
            if index == -1:
                return False
            # 截取从 System 开始的数据
            data = output[index:]
            # 分割数据
            fields = data.split()
            for i, field in enumerate(fields):
                if field == app_name:
                    try:
                        # 尝试获取进程 ID
                        pid = int(fields[i + 1])
                        return True
                    except (IndexError, ValueError):
                        return False
            return False
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False
