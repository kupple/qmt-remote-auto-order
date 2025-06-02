#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: 潘高
LastEditors: 潘高
Date: 2023-03-12 20:08:30
LastEditTime: 2024-01-22 17:08:27
Description: 操作数据库类
usage:
    from api.db.orm import ORM

    orm = ORM()    # 操作数据库类
    author = self.orm.getStorageVar('author')    # 获取储存变量
    print('author', author)
'''

from datetime import datetime
from api.db.models import (
    PPXStorageVar, Setting, TaskList, Orders, Entrusts, Trades, Backtest
)
from pyapp.db.db import DB
from sqlalchemy import select, update, insert, and_, or_, desc, func
from api.tools.sysConfig import generate_random_letters

class ORM:
    '''操作数据库类'''

    def __init__(self):
        """初始化数据库"""
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        db = DB()    # 创建DB实例
        db.init()    # 初始化数据库连接
        dbSession = DB.session()
        try:
            # 初始化设置表
            Setting.initialize_default(dbSession)
        finally:
            dbSession.close()

    def getStorageVar(self, key):
        '''获取储存变量'''
        resVal = ''
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(PPXStorageVar.val).where(PPXStorageVar.key == key)
            result = dbSession.execute(stmt)
            result = result.one_or_none()
            if result is None:
                # 新建
                stmt = insert(PPXStorageVar).values(key=key)
                dbSession.execute(stmt)
            else:
                resVal = result[0]
        dbSession.close()
        return resVal

    def setStorageVar(self, key, val):
        '''更新储存变量'''
        dbSession = DB.session()
        with dbSession.begin():
            stmt = update(PPXStorageVar).where(PPXStorageVar.key == key).values(val=val)
            dbSession.execute(stmt)
        dbSession.close()

    def get_setting_config(self):
        """获取设置配置"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Setting)
            result = dbSession.execute(stmt).first()
            if result:
                return result[0].toDict()
        dbSession.close()
        return {}

    def save_config(self, config_dict):
        """保存配置
        Args:
            config_dict (dict): 配置字典，key为字段名，value为要更新的值
        """
        from datetime import datetime
        
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Setting)
            result = dbSession.execute(stmt).first()
            if result:
                setting = result[0]
                for key, value in config_dict.items():
                    if hasattr(setting, key):
                        # Handle datetime fields
                        if key in ['created_at', 'updated_at'] and isinstance(value, str):
                            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        setattr(setting, key, value)
            else:
                # Convert datetime strings to datetime objects for new records
                for key, value in config_dict.items():
                    if key in ['created_at', 'updated_at'] and isinstance(value, str):
                        config_dict[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                setting = Setting(**config_dict)
                dbSession.add(setting)
        dbSession.close()

    def get_task_list(self):
        """获取任务列表"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(TaskList).where(TaskList.delete_time.is_(None))
            result = dbSession.execute(stmt).scalars().all()
            return [task.toDict() for task in result]
        dbSession.close()
        return []

    def create_task(self, data):
        """创建任务"""
        dbSession = DB.session()
        with dbSession.begin():
            strategy_code = data.get('strategy_code', '')
            if strategy_code == '':
                strategy_code = generate_random_letters()
                
            if 'id' not in data or data['id'] is None:
                task = TaskList(
                    name=data['name'],
                    strategy_code=strategy_code,
                    order_count_type=data['order_count_type'],
                    strategy_amount=data['strategy_amount'],
                    allocation_amount=data['allocation_amount'],
                    service_charge=data['service_charge'],
                    lower_limit_of_fees=data['service_charge']
                )
                dbSession.add(task)
            else:
                stmt = select(TaskList).where(TaskList.id == data['id'])
                task = dbSession.execute(stmt).scalar_one_or_none()
                if task:
                    task.name = data['name']
                    task.strategy_code = strategy_code
                    task.order_count_type = data['order_count_type']
                    task.strategy_amount = data['strategy_amount']
                    task.allocation_amount = data['allocation_amount']
                    task.service_charge=data['service_charge']
                    task.lower_limit_of_fees=data['service_charge']
        dbSession.close()
        return True

    def run_task(self, data):
        """编辑任务"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(TaskList).where(TaskList.id == data['id'])
            task = dbSession.execute(stmt).scalar_one_or_none()
            if task:
                task.is_open = data['is_open']
                task.start_time = datetime.now()
        dbSession.close()
        return True

    def delete_task(self, data):
        """删除任务"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(TaskList).where(TaskList.id == data['id'])
            task = dbSession.execute(stmt).scalar_one_or_none()
            if task:
                task.delete_time = datetime.now()
        dbSession.close()
        return True

    def get_task_detail(self, data):
        """获取任务详情"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(TaskList).where(TaskList.id == data['id'])
            task = dbSession.execute(stmt).scalar_one_or_none()
            return task.toDict() if task else {}
        dbSession.close()
        return {}

    def save_order(self, data):
        """保存订单"""
        dbSession = DB.session()
        with dbSession.begin():
            order = Orders(
                security_code=data['security_code'],
                style=data['style'],
                price=data['price'],
                volume=data['amount'],
                avg_cost=data['avg_cost'],
                commission=data['commission'],
                is_buy=data['is_buy'],
                add_time=data['add_time'],
                pindex=data['pindex'],
                platform=data['platform'],
                run_params=data['run_params'],
                fix_result_order_id=data['fix_result_order_id'],
                strategy_code=data['strategy_code']
            )
            dbSession.add(order)
            dbSession.flush()
            last_id = order.id
        dbSession.close()
        return last_id

    def get_order_list(self, data):
        # full_backtest
        # simple_backtest
        """获取订单列表"""
        dbSession = DB.session()
        if 'time' not in data or data['time'] == None:
            data['time'] = ['00:00',"23:59"]
        with dbSession.begin():
            start_current_date = datetime.now().strftime("%Y-%m-%d") + f' {data["time"][0]}:00'
            end_current_date = datetime.now().strftime("%Y-%m-%d") + F' {data["time"][1]}:59'
            if 'date' in data and data['date'] is not None:
                start_current_date = data['date'] + F' {data["time"][0]}:00'
                end_current_date = data['date'] +  F' {data["time"][1]}:59'

            conditions = []
            if 'security_code' in data and data['security_code']:
                conditions.append(Orders.security_code.like(f"%{data['security_code']}%"))
            if 'run_params' in data and data['run_params']:
                if data['run_params'] == 'simple_backtest':
                    conditions.append(or_(Orders.run_params == 'simple_backtest', Orders.run_params == 'full_backtest'))
                else:
                    conditions.append(Orders.run_params == data['run_params'])
            conditions.append(Orders.created_at >= start_current_date)
            conditions.append(Orders.created_at < end_current_date)

            stmt = select(Orders).where(and_(*conditions)).order_by(desc(Orders.created_at))
            stmt = stmt.offset((data['page'] - 1) * data['pageSize']).limit(data['pageSize'])
            
            result = dbSession.execute(stmt).scalars().all()
            data_list = [order.toDict() for order in result]

            # Get total count
            count_stmt = select(func.count()).select_from(Orders).where(and_(*conditions))
            total = dbSession.execute(count_stmt).scalar()

        dbSession.close()
        print(data_list)
        return {
            'data': data_list,
            'total': total
        }

    def update_order(self, order_id, **kwargs):
        """更新订单信息"""
        if not kwargs:
            return False

        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Orders).where(Orders.id == order_id)
            order = dbSession.execute(stmt).scalar_one_or_none()
            if order:
                for key, value in kwargs.items():
                    if hasattr(order, key):
                        setattr(order, key, value)
        dbSession.close()
        return True

    def save_entrust(self, data, sub_data=None):
        """保存委托记录"""
        if not data:
            return None

        dbSession = DB.session()
        with dbSession.begin():
            entrust = Entrusts()
            
            # Handle main data object
            for field in Entrusts.__table__.columns.keys():
                if hasattr(data, field):
                    setattr(entrust, field, getattr(data, field))
            
            # Handle sub data
            if sub_data and isinstance(sub_data, dict):
                for field, value in sub_data.items():
                    if hasattr(entrust, field):
                        setattr(entrust, field, value)
            
            dbSession.add(entrust)
            dbSession.flush()
            last_id = entrust.id
        dbSession.close()
        return last_id

    def save_trade(self, data, sub_data=None):
        """保存成交记录"""
        if not data:
            return None

        dbSession = DB.session()
        with dbSession.begin():
            trade = Trades()
            
            # Handle main data object
            for field in Trades.__table__.columns.keys():
                if hasattr(data, field):
                    setattr(trade, field, getattr(data, field))
            
            # Handle sub data
            if sub_data and isinstance(sub_data, dict):
                for field, value in sub_data.items():
                    if hasattr(trade, field):
                        setattr(trade, field, value)
            
            dbSession.add(trade)
            dbSession.flush()
            last_id = trade.id
        dbSession.close()
        return last_id

    def check_strategy_code_exists(self, strategy_code):
        """检查策略代码是否已存在
        Args:
            strategy_code (str): 要检查的策略代码
        Returns:
            bool: 如果策略代码存在返回True，否则返回False
        """
        if not strategy_code:
            return False
            
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(TaskList).where(
                and_(
                    TaskList.strategy_code == strategy_code,
                    TaskList.delete_time.is_(None)
                )
            )
            result = dbSession.execute(stmt).first()
        dbSession.close()
        return result is not None

    def query_position_by_task_id(self, task_id, security_code=None):
        """通过任务id查找当前持仓"""
        if not task_id:
            return None
        
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Positions).where(Positions.task_id == task_id)
            if security_code:
                stmt = stmt.where(Positions.security_code == security_code)
            stmt = stmt.where(Positions.delete_time.is_(None))
            result = dbSession.execute(stmt).all()
        dbSession.close()
        return result
    
    def create_backtest(self, data):
        """创建回测"""
        dbSession = DB.session()
        with dbSession.begin():
            backtest = Backtest(**data)
            dbSession.add(backtest)
            dbSession.flush()
            last_id = backtest.id
        dbSession.close()
        return last_id
    
    def update_backtest(self, id, **kwargs):
        """更新回测"""
        if not id:
            return False
        
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Backtest).where(Backtest.id == id)
            backtest = dbSession.execute(stmt).scalar_one_or_none()
            if backtest:
                for key, value in kwargs.items():
                    if hasattr(backtest, key):
                        setattr(backtest, key, value)
        dbSession.close()
        return True
    
    def update_task(self, id, **kwargs):
        """更新任务"""
        if not id:
            return False
        
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(TaskList).where(TaskList.id == id)
            task = dbSession.execute(stmt).scalar_one_or_none()
            if task:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
        dbSession.close()
        return True
    