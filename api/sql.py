#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 数据库操作相关的API
'''

import sqlite3
import os
import platform
import subprocess
from datetime import datetime
import string
import secrets

def generate_random_letters():
    # 获取当前时间戳（精确到毫秒）
    timestamp = datetime.now().timestamp()
    # 转换为整数并取后6位作为随机数生成的基础
    time_seed = int(timestamp * 1000) % 1000000
    
    # 使用 secrets 模块（比 random 更安全）生成随机字母
    alphabet = string.ascii_letters  # 包含所有大小写字母
    # 使用时间戳作为随机数生成器的种子
    secrets_generator = secrets.SystemRandom(time_seed)
    
    # 生成6位随机字母
    random_letters = ''.join(secrets_generator.choice(alphabet) for _ in range(6))
    
    return random_letters

db_file = 'main.db'
class Database:
    task_list = []  
    def __init__(self):
        self._init_database()

    def _init_database(self):
        """初始化数据库，创建必要的表"""
        if not os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 创建设置表
            cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS setting (
                    python_path TEXT,
                    mini_qmt_path TEXT,
                    client_id TEXT,
                    server_url TEXT
                )
            """)
            
            # 插入默认设置
            cursor.execute("INSERT INTO setting (python_path, mini_qmt_path, client_id, server_url) VALUES ('', '', '', 'http://127.0.0.1:5000')")    
            # 创建任务列表表
            cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS tasklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    code TEXT,
                    order_count_type INTEGER,
                    strategy_amount INTEGER,
                    allocation_amount INTEGER,
                    enable INTEGER DEFAULT 1,
                    days_number INTEGER,
                    is_open INTEGER DEFAULT 0,
                    delete_time TEXT,
                    start_time TEXT,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 创建订单表
            cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    amount INTEGER,
                    price INTEGER,
                    direction TEXT,
                    fix_result_order_id TEXT,
                    order_type TEXT,
                    price_type TEXT,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    task_id INTEGER,
                    transaction_status INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasklist(id)
                )
            """)
            
            conn.commit()
            conn.close()
    @staticmethod
    def get_setting_config():
        """获取设置配置"""
        conn = sqlite3.connect("main.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        rows = cursor.execute("SELECT * FROM setting LIMIT 1").fetchall()
        data = dict(rows[0]) if rows else {}
        
        conn.close()
        return data

    def save_config(self,  mini_qmt_path=None, client_id=None, server_url=None):
        """保存配置"""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 构建动态的UPDATE语句
        update_fields = []
        params = []
        
        if mini_qmt_path is not None:
            update_fields.append("mini_qmt_path = ?")
            params.append(mini_qmt_path)
            
        if client_id is not None:
            update_fields.append("client_id = ?")
            params.append(client_id)
            
        if server_url is not None:
            update_fields.append("server_url = ?")
            params.append(server_url)
            
        if update_fields:
            query = f"UPDATE setting SET {', '.join(update_fields)}"
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
    def find_python_directory():
        try:
            if platform.system() == "Windows":
                # Windows 系统使用 where 命令
                cmd = ["where", "python"]
            else:
                # 类 Unix 系统使用 which 命令
                cmd = ["which", "python"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            python_path = result.stdout.strip()
            # 提取目录部分
            python_dir = os.path.dirname(python_path)
            python_dir = os.path.join(python_dir, "python")
            return python_dir
        except subprocess.CalledProcessError as e:
            raise Exception(f"查找 Python 可执行文件时出错: {e}")
    
    def get_task_list(self):
        """获取任务列表"""
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        rows = cursor.execute("SELECT * FROM tasklist WHERE delete_time IS NULL").fetchall()
        data = [dict(row) for row in rows]
        
        
        conn.close()
        Database.task_list = data
        return data
    
    def create_task(self,data):
        """创建任务"""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        code = generate_random_letters()
        cursor.execute("INSERT INTO tasklist (name, code, order_count_type, strategy_amount, allocation_amount) VALUES (?, ?, ?, ?, ?)", (data['name'], code, data['orderCountType'], data['strategyAmount'], data['allocationAmount']))
        conn.commit()
        conn.close()
        return True

    def run_task(self,data):
        """编辑任务"""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasklist SET is_open = {data['is_open']}, start_time = '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' WHERE id = {data['id']}")
        conn.commit()
        conn.close()
        return True
    
    def delete_task(self,data):
        """删除任务"""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        delete_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE tasklist SET delete_time = ? WHERE id = ?", (delete_time, data['id']))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def create_order(data):
        """创建订单"""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (code, amount, price, direction, order_type, price_type,fix_result_order_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (data['code'], data['amount'], data['price'], data['direction'], data['order_type'], data['price_type'], data['fix_result_order_id']))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_task_detail(data):
        """获取任务详情"""
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM tasklist WHERE id = ?", (data['id'],)).fetchall()
        data = dict(rows[0]) if rows else {}
        conn.close()
        return data
