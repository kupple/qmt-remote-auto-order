#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
FilePath: /PPX/api/db/models.py
Author: 潘高
LastEditors: 潘高
Date: 2023-03-12 20:29:49
LastEditTime: 2024-08-09 09:50:03
Description: 创建数据表
usage: 更新数据表格式后，请按如下操作迁移数据库：
        m=备注更改内容 npm run alembic

        注意：上述命令仅能迁移打包程序自带数据库(Config.staticDir)。在程序运行初始化时，会自动检测并迁移本地电脑中保存的数据库(Config.appDataDir)
'''

import json

from sqlalchemy import Column, DateTime, Integer, Numeric, String, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    '''基类'''
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(), doc='创建时间', comment='创建时间', server_default=text("(DATETIME(CURRENT_TIMESTAMP, 'localtime'))"))
    updated_at = Column(DateTime(), doc='更新时间', comment='更新时间', server_default=text("(DATETIME(CURRENT_TIMESTAMP, 'localtime'))"), onupdate=text("(DATETIME(CURRENT_TIMESTAMP, 'localtime'))"))

    def _gen_tuple(self):
        # 处理 日期 等无法正常序列化的对象
        def convert_datetime(value):
            if value:
                return value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return ""
        for col in self.__table__.columns:
            try:
                if isinstance(col.type, DateTime):
                    value = convert_datetime(getattr(self, col.name))
                elif isinstance(col.type, Numeric):
                    value = float(getattr(self, col.name))
                else:
                    value = getattr(self, col.name)
                yield (col.name, value)
            except Exception as e:
                print(e)
                pass

    def toDict(self):
        # 转化为 字典
        return dict(self._gen_tuple())

    def toJson(self):
        # 序列化为 JSON
        return json.dumps(self.toDict())


class PPXStorageVar(BaseModel):
    '''储存变量'''
    __tablename__ = "ppx_storage_var"
    key = Column(String(), doc='键', nullable=False, index=True)
    val = Column(String(), doc='值', server_default='', nullable=False)
    remark = Column(String(), doc='备注', server_default='', nullable=False)

    def __str__(self):
        return self.key + ' => ' + self.val


class Setting(BaseModel):
    '''设置表'''
    __tablename__ = "setting"
    python_path = Column(String(), doc='Python路径', nullable=True)
    mini_qmt_path = Column(String(), doc='MiniQMT路径', nullable=True)
    client_id = Column(String(), doc='客户端ID', nullable=True)
    salt = Column(String(), doc='盐值', nullable=True)
    server_url = Column(String(), doc='服务器URL', nullable=True)
    run_model_type = Column(Integer, doc='运行模式类型', nullable=True, server_default='0')
    auto_national_debt = Column(Integer, doc='自动逆回购', nullable=True, server_default='0')
    auto_buy_stock_ipo = Column(Integer, doc='自动打新股', nullable=True, server_default='0')
    auto_buy_purchase_ipo = Column(Integer, doc='自动打新债·', nullable=True, server_default='0')
    account = Column(String(), doc='账号·', nullable=True)
    def __str__(self):
        return f"Setting: {self.client_id}"

    @classmethod
    def initialize_default(cls, session):
        """初始化默认设置"""
        # 检查是否已存在设置
        existing = session.query(cls).first()
        if not existing:
            # 创建默认设置
            default_setting = cls(
                python_path='',
                mini_qmt_path='',
                client_id='',
                salt='',
                server_url='',
                run_model_type=0
            )
            session.add(default_setting)
            session.commit()


class TaskList(BaseModel):
    '''任务列表表'''
    __tablename__ = "tasklist"
    name = Column(String(), doc='任务名称', nullable=True)
    strategy_code = Column(String(), doc='策略代码', nullable=True)
    order_count_type = Column(Integer, doc='订单计数类型', nullable=True)
    strategy_amount = Column(Integer, doc='策略金额', nullable=True)
    allocation_amount = Column(Integer, doc='分配金额', nullable=True)
    enable = Column(Integer, doc='是否启用', nullable=True, server_default='1')
    days_number = Column(Integer, doc='天数', nullable=True)
    is_open = Column(Integer, doc='是否开启', nullable=True, server_default='0')
    delete_time = Column(DateTime(), doc='删除时间', nullable=True)
    start_time = Column(DateTime(), doc='开始时间', nullable=True)

    def __str__(self):
        return f"Task: {self.name}"


class Orders(BaseModel):
    '''订单表'''
    __tablename__ = "orders"
    security_code = Column(String(), doc='证券代码', nullable=True)
    fix_result_order_id = Column(String(), doc='固定结果订单ID', nullable=True)
    style = Column(String(), doc='风格', nullable=True)
    run_params = Column(String(), doc='运行参数', nullable=True)
    pindex = Column(String(), doc='平台索引', nullable=True)
    platform = Column(String(), doc='平台', nullable=True)
    task_id = Column(Integer, doc='任务ID', nullable=True)
    is_buy = Column(Integer, doc='是否买入', nullable=True, server_default='0')
    strategy_code = Column(String(), doc='策略代码', nullable=True)
    add_time = Column(String(), doc='添加时间', nullable=True)
    volume = Column(Integer, doc='数量', nullable=True)
    price = Column(Numeric(), doc='价格', nullable=True)
    avg_cost = Column(Numeric(), doc='平均成本', nullable=True)
    status_msg = Column(String(), doc='状态消息', nullable=True)
    commission = Column(Numeric(), doc='佣金', nullable=True)
    status = Column(Integer, doc='状态', nullable=True, server_default='0')
    transaction_status = Column(Integer, doc='交易状态', nullable=True, server_default='0')

    def __str__(self):
        return f"Order: {self.security_code}"


class Entrusts(BaseModel):
    '''委托表'''
    __tablename__ = "entrusts"
    traded_amount = Column(Numeric(), doc='交易金额', nullable=True)
    traded_price = Column(Numeric(), doc='交易价格', nullable=True)
    stock_code = Column(String(), doc='股票代码', nullable=True)
    traded_volume = Column(Numeric(), doc='交易数量', nullable=True)
    traded_time = Column(Integer, doc='交易时间', nullable=True)
    traded_id = Column(String(), doc='交易ID', nullable=True)
    status_msg = Column(String(), doc='状态消息', nullable=True)
    orders_id = Column(Integer, doc='订单ID', nullable=True)
    order_type = Column(Integer, doc='订单类型', nullable=True)
    price_type = Column(Integer, doc='价格类型', nullable=True)
    order_id = Column(Integer, doc='订单ID', nullable=True)
    order_status = Column(Integer, doc='订单状态', nullable=True)
    order_sysid = Column(String(), doc='订单系统ID', nullable=True)
    status = Column(Integer, doc='状态', nullable=True, server_default='0')
    offset_flag = Column(Integer, doc='偏移标志', nullable=True)

    def __str__(self):
        return f"Entrust: {self.traded_id}"


class Trades(BaseModel):
    '''成交表'''
    __tablename__ = "trades"
    order_id = Column(Integer, doc='订单ID', nullable=True)
    order_sysid = Column(String(), doc='订单系统ID', nullable=True)
    order_time = Column(Integer, doc='订单时间', nullable=True)
    order_volume = Column(Integer, doc='订单数量', nullable=True)
    price_type = Column(Integer, doc='价格类型', nullable=True)
    price = Column(Numeric(), doc='价格', nullable=True)
    traded_volume = Column(Numeric(), doc='交易数量', nullable=True)
    traded_price = Column(Numeric(), doc='交易价格', nullable=True)
    order_status = Column(Integer, doc='订单状态', nullable=True)
    status_msg = Column(String(), doc='状态消息', nullable=True)
    offset_flag = Column(Integer, doc='偏移标志', nullable=True)
    orders_id = Column(Integer, doc='订单ID', nullable=True)
    status = Column(Integer, doc='状态', nullable=True, server_default='0')

    def __str__(self):
        return f"Trade: {self.order_sysid}"
