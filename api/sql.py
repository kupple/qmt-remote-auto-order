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
    setting_config = None
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
                    salt TEXT,
                    server_url TEXT,
                    run_model_type INTEGER DEFAULT 0
                )
            """)
            
            # 插入默认设置
            cursor.execute("INSERT INTO setting (python_path, mini_qmt_path, client_id, salt, server_url, run_model_type) VALUES ('', '', '', '', 'ws://193.112.151.98:8080/ws', 0)")    
            # 创建任务列表表
            cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS tasklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    strategy_code TEXT,
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
                    security_code TEXT,
                    fix_result_order_id TEXT,
                    style TEXT,
                    run_params TEXT,
                    pindex TEXT,
                    platform TEXT,
                    task_id INTEGER,
                    is_buy INTEGER DEFAULT 0,
                    strategy_code TEXT,
                    add_time TEXT,
                    volume  INTEGER,
                    price FLOAT,
                    avg_cost FLOAT,
                    status_msg TEXT,
                    commission FLOAT,
                    status  INTEGER DEFAULT 0,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    transaction_status INTEGER DEFAULT 0, 
                    FOREIGN KEY (task_id) REFERENCES tasklist(id)
                )
            """)
            cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS entrusts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    traded_amount  FLOAT,
                    traded_price FLOAT,
                    stock_code TEXT,
                    traded_volume FLOAT,
                    traded_time INTEGER,
                    traded_id TEXT,
                    status_msg TEXT,
                    orders_id INTEGER,
                    order_type INTEGER,
                    price_type  INTEGER,
                    order_id  INTEGER,
                    order_status INTEGER,
                    order_sysid TEXT,
                    status  INTEGER DEFAULT 0,
                    offset_flag  INTEGER,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (orders_id) REFERENCES orders(id)
                )
            """)
            
            cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    order_sysid TEXT,
                    order_time INTEGER,
                    order_volume INTEGER,
                    price_type  INTEGER,
                    price FLOAT,
                    traded_volume FLOAT,
                    traded_price  FLOAT,
                    order_status INTEGER,
                    status_msg  TEXT,
                    offset_flag INTEGER,
                    orders_id INTEGER,
                    status  INTEGER DEFAULT 0,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (orders_id) REFERENCES orders(id)
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
        Database.setting_config = data
        conn.close()
        return data

    def save_config(self, mini_qmt_path=None, client_id=None, server_url=None, salt=None, run_model_type=None):
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

        if salt is not None:
            update_fields.append("salt = ?")
            params.append(salt)

        if run_model_type is not None:
            update_fields.append("run_model_type = ?")
            params.append(run_model_type)
            
        if update_fields:
            query = f"UPDATE setting SET {', '.join(update_fields)}"
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
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
        if data['strategy_code'] == '':
            strategy_code = generate_random_letters()
        else:
            strategy_code = data['strategy_code']
            
        if 'id' not in data or  data['id'] is None:
            cursor.execute("INSERT INTO tasklist (name, strategy_code, order_count_type, strategy_amount, allocation_amount) VALUES (?, ?, ?, ?, ?)", (data['name'], strategy_code, data['orderCountType'], data['strategyAmount'], data['allocationAmount']))
        else:
            cursor.execute("UPDATE tasklist SET name = ?, strategy_code = ?, order_count_type = ?, strategy_amount = ?, allocation_amount = ? WHERE id = ?", (data['name'], strategy_code, data['orderCountType'], data['strategyAmount'], data['allocationAmount'], data['id']))
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

    def save_order(self,data):
        """保存订单"""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (security_code, style, price, volume, avg_cost, commission, is_buy, add_time, pindex, platform, run_params, fix_result_order_id, strategy_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data['security_code'], data['style'], data['price'], data['amount'], data['avg_cost'], data['commission'], data['is_buy'], data['add_time'], data['pindex'], data['platform'], data['run_params'], data['fix_result_order_id'], data['strategy_code']))
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id
    
    
    def get_order_list(self,data):
        """获取订单列表"""
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_current_date = datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'
        end_current_date = datetime.now().strftime("%Y-%m-%d") + ' 23:59:59'
        if 'date' in data and data['date'] is not None:
            start_current_date = data['date'] + ' 00:00:00'
            end_current_date = data['date'] + ' 23:59:59'
        page = data['page']
        pageSize = data['pageSize']
        
        conditions = []
        params = []
        
        if 'security_code' in data and data['security_code']:
            conditions.append("security_code LIKE ?")
            params.append(f"%{data['security_code']}%")
            
        if 'run_params' in data and data['run_params']:
            conditions.append("run_params = ?")
            params.append(data['run_params'])
            
        conditions.append("create_time >= ?")
        conditions.append("create_time < ?")
        params.extend([start_current_date, end_current_date])
        
        where_clause = " AND ".join(conditions)
        
        print(where_clause)
        
        query = f"SELECT * FROM orders WHERE {where_clause} order by create_time desc limit ? offset ?"
        params.extend([pageSize, (page - 1) * pageSize])
        rows = cursor.execute(query, params).fetchall()
        count_query = f"SELECT COUNT(*) FROM orders WHERE {where_clause}"
        total = cursor.execute(count_query, params[:-2]).fetchall()[0][0]
        data = [dict(row) for row in rows]
        conn.close()
        return {
            'data': data,
            'total': total
        }

    def update_order(self, order_id, **kwargs):
        """更新订单信息
        
        Args:
            order_id (int): 订单ID
            **kwargs: 要更新的字段和值，例如 security_code='000001', amount=100
            
        Returns:
            bool: 更新是否成功
        """
        if not kwargs:
            return False
            
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 构建动态的UPDATE语句
        update_fields = []
        params = []
        
        # 可更新的字段列表
        allowed_fields = [
            'security_code', 'fix_result_order_id', 'style', 'run_params',
            'pindex', 'platform', 'is_buy', 'amount', 'strategy_code',
            'add_time', 'price', 'avg_cost', 'commission', 'status',
            'transaction_status'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            conn.close()
            return False
            
        # 添加更新时间
        update_fields.append("update_time = ?")
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 添加ID参数
        params.append(order_id)
        
        query = f"UPDATE orders SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True

    def save_entrust(self, data, sub_data=None):
        """保存委托记录
        
        Args:
            data (object): 包含要插入的字段和值的对象，例如 EntrustData 对象
            sub_data (dict, optional): 包含要插入的额外字段和值的字典对象
            
        Returns:
            int: 新插入记录的ID，如果插入失败则返回None
        """
        if not data:
            return None
            
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 可插入的字段列表
        allowed_fields = [
            'traded_amount', 'traded_price', 'traded_volume', 'traded_time',
            'traded_id', 'status_msg', 'orders_id', 'order_id', 'order_sysid',
            'status','order_type','price_type','order_status','stock_code','offset_flag'
        ]
        
        # 构建动态的INSERT语句
        fields = []
        placeholders = []
        values = []
        
        # 处理主数据对象
        for field in allowed_fields:
            if hasattr(data, field):
                value = getattr(data, field)
                fields.append(field)
                placeholders.append('?')
                values.append(value)
        
        # 处理子数据
        if sub_data and isinstance(sub_data, dict):
            for field, value in sub_data.items():
                if field in allowed_fields:
                    fields.append(field)
                    placeholders.append('?')
                    values.append(value)
        
        if not fields:
            conn.close()
            return None
            
        # 添加创建时间
        fields.append('create_time')
        placeholders.append('?')
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        query = f"INSERT INTO entrusts ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(query, values)
        
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id

    def save_trade(self, data, sub_data=None):
        """保存成交记录
        
        Args:
            data (object): 包含要插入的字段和值的对象，例如 TradeData 对象
            sub_data (dict, optional): 包含要插入的额外字段和值的字典对象
            
        Returns:
            int: 新插入记录的ID，如果插入失败则返回None
        """
        if not data:
            return None
            
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 可插入的字段列表
        allowed_fields = [
            'order_id', 'order_sysid', 'order_time', 'order_volume',
            'price_type', 'price', 'traded_volume', 'traded_price',
            'order_status', 'status_msg', 'offset_flag', 'orders_id',
            'status'
        ]
        
        # 构建动态的INSERT语句
        fields = []
        placeholders = []
        values = []
        
        # 处理主数据对象
        for field in allowed_fields:
            if hasattr(data, field):
                value = getattr(data, field)
                fields.append(field)
                placeholders.append('?')
                values.append(value)
        
        # 处理子数据
        if sub_data and isinstance(sub_data, dict):
            for field, value in sub_data.items():
                if field in allowed_fields:
                    fields.append(field)
                    placeholders.append('?')
                    values.append(value)
        
        if not fields:
            conn.close()
            return None
            
        # 添加创建时间
        fields.append('create_time')
        placeholders.append('?')
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        query = f"INSERT INTO trades ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(query, values)
        
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id