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
    PPXStorageVar, Setting, TaskList, Orders, Entrusts, Trades, Backtest,Positions
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
            if 'id' not in data or data['id'] is None:
                if 'strategy_code' not in data or not data['strategy_code'] and data["task_type"] is 1:
                    data['strategy_code'] = generate_random_letters()
                task = TaskList(**data)
                dbSession.add(task)
            else:
                stmt = select(TaskList).where(TaskList.id == data['id'])
                task = dbSession.execute(stmt).scalar_one_or_none()
                if task:
                    for key, value in data.items():
                        if hasattr(task, key):
                            setattr(task, key, value)
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
                platform=data['platform'],
                run_params=data['run_params'],
                fix_result_order_id=data['fix_result_order_id'],
                strategy_code=data['strategy_code'],
                positions=data['positions']
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
    
    def query_order_by_id(self, order_id):
        """查询订单信息"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Orders).where(Orders.id == order_id)
            order = dbSession.execute(stmt).scalar_one_or_none()
            return order.toDict() if order else {}
        dbSession.close()
        return {}   

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
            return []
            
        try:
            with DB.session() as session:
                stmt = select(Positions).where(Positions.task_id == task_id).where(Positions.is_mock == 0)
                if security_code:
                    stmt = stmt.where(Positions.security_code == security_code).where(Positions.is_mock == 0)
                
                # 获取结果并转换为字典
                positions = session.execute(stmt).scalars().all()
                return [pos.toDict() for pos in positions]
        except Exception as e:
            print(f"查询持仓出错: {str(e)}")
            return []
    
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
    
    
    def query_position_by_task_or_backtest_id(self, task_id=None, backtest_id=None):
        """通过taskid或者backtest_id查找仓位信息"""
        if not task_id and not backtest_id:
            return None
        
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Positions)
            if backtest_id:
                stmt = stmt.where(Positions.backtest_id == backtest_id).where(Positions.is_mock == 1)   
            elif task_id:
                stmt = stmt.where(Positions.task_id == task_id).where(Positions.backtest_id.is_(None)).where(Positions.is_mock == 0)
            
            result = dbSession.execute(stmt).scalars().all()
            result = [task.toDict() for task in result]
            
        dbSession.close()
        return result

    
    def save_position(self,data,sub_data=None):
      """保存持仓"""
      if not data:
        return None

      dbSession = DB.session()
      with dbSession.begin():
        position = Positions()
        for field in Positions.__table__.columns.keys():
          if field in data:
            setattr(position, field, data[field])
        
        # Handle sub data
        if sub_data and isinstance(sub_data, dict):
            for field, value in sub_data.items():
                if hasattr(position, field):
                    setattr(position, field, value)
        
        dbSession.add(position)
        dbSession.flush()
        last_id = position.id
      dbSession.close()
      return last_id
  

    def update_backtest_accruing_amounts(self, backtest_id, profit_loss):
        """更新回测账户的累计金额"""
        dbSession = DB.session()
        with dbSession.begin():
            # 获取当前累计金额
            stmt = select(Backtest.accruing_amounts).where(Backtest.id == backtest_id)
            result = dbSession.execute(stmt).scalar()
            
            # 更新累计金额
            new_accruing_amounts = result + profit_loss if result else profit_loss
            stmt = update(Backtest).where(Backtest.id == backtest_id).values(accruing_amounts=new_accruing_amounts)
            dbSession.execute(stmt)
        dbSession.close()
        return True

  
    def query_backtest_by_task_id(self, task_id):
        """通过taskid获取回测列表"""
        if not task_id:
            return None
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Backtest).where(Backtest.task_id == task_id).order_by(Backtest.created_at.desc())
            result = dbSession.execute(stmt).scalars().all()
            data_list = [order.toDict() for order in result]
        dbSession.close()
        return data_list
    
    def query_backtest_by_id(self, backtest_id):
        """通过backtestid获取回测"""
        if not backtest_id:
            return None
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Backtest).where(Backtest.id == backtest_id)
            result = dbSession.execute(stmt).scalar_one_or_none()
            if result:
                return result.toDict()
        dbSession.close()
        return None
    
    def count_strategy_analyzer(self,task_id=None,backtest_id=None):
        """统计策略分析"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Trades)
            if backtest_id:
                stmt = stmt.where(Trades.backtest_id == backtest_id).where(Trades.is_mock == 1)
            elif task_id:
                stmt = stmt.where(Trades.task_id == task_id).where(Trades.is_mock == 0)
            
            result = dbSession.execute(stmt)
            trades = []
            for row in result:
                trades.append(row[0].toDict())
            return trades
        dbSession.close()
        return []
    
    def update_task_can_use_amount(self,backtest_id = None,task_id = None, profit_loss = 0):
        """更新任务账户的可用金额"""
        dbSession = DB.session()
        with dbSession.begin():
            if backtest_id:
                stmt = update(Backtest).where(Backtest.id == backtest_id).values(can_use_amount=Backtest.can_use_amount + profit_loss)
            else:
                stmt = update(TaskList).where(TaskList.id == task_id).values(can_use_amount=TaskList.can_use_amount + profit_loss)
            dbSession.execute(stmt)
        dbSession.close()
        return True
    
    
    def query_task_or_backtest(self, task_id, backtest_id):
        dbSession = DB.session()
        try:
            with dbSession.begin():
                if backtest_id:
                    stmt = select(Backtest).where(Backtest.id == backtest_id)
                    result = dbSession.execute(stmt).scalar_one_or_none()
                    if result:
                        return {c.name: getattr(result, c.name) for c in result.__table__.columns}
                else:
                    stmt = select(TaskList).where(TaskList.id == task_id)
                    result = dbSession.execute(stmt).scalar_one_or_none()
                    if result:
                        return {c.name: getattr(result, c.name) for c in result.__table__.columns}
            return None
        finally:
            dbSession.close()
    

        
    def update_position(self, id, data):
        """更新持仓信息"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = update(Positions).where(Positions.id == id)
            for key, value in data.items():
                stmt = stmt.values(**{key: value})
            dbSession.execute(stmt)
        dbSession.close()
        return True
    
    def delete_position_by_id(self, id):
        """删除任务的持仓信息"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = Positions.__table__.delete().where(Positions.id == id)
            dbSession.execute(stmt)
        dbSession.close()
        return True
    
    def add_position(self, data):
        """添加持仓信息"""
        dbSession = DB.session()
        with dbSession.begin():
            position = Positions()
            for key, value in data.items():
                if hasattr(position, key):
                    setattr(position, key, value)
            dbSession.add(position)
        dbSession.close()
        return True
    
    # 检测持仓是否已存在
    def check_position_exists(self, security_code, task_id):
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Positions).where(Positions.is_mock == 0).where(Positions.security_code == security_code).where(Positions.task_id == task_id)
            result = dbSession.execute(stmt).scalar_one_or_none()
            return result is not None
    
    # 获取今日成交记录
    def query_trade_today(self, task_id):
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Trades).where(Trades.task_id == task_id).where(Trades.is_mock == 0).where(Trades.created_at >= datetime.now().date())
            result = dbSession.execute(stmt).scalars().all()
            return [trade.toDict() for trade in result]
        dbSession.close()
        
    