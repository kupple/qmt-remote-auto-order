#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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
                    value = getattr(self, col.name)
                    if value is not None:
                        value = float(value)
                    else:
                        value = getattr(self, col.name)
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
    auto_reorder = Column(Integer, doc='自动重下单', nullable=True, server_default='0')
    auto_startup = Column(Integer, doc='开机自启动', nullable=True, server_default='0')
    account = Column(String(), doc='账号·', nullable=True)
    client_type = Column(Integer, doc='客户端类型', nullable=True, server_default='1')
    ths_path = Column(String(), doc='同花顺路径', nullable=True)
    ths_pwd = Column(String(), doc='同花顺密码', nullable=True)
    ths_client_id = Column(String(), doc='同花顺客户端ID', nullable=True)
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
                run_model_type=0,
                auto_reorder=0,
                auto_startup=0,
                account='',
                client_type=1,
                ths_path='',
                ths_pwd='',
            )
            session.add(default_setting)
            session.commit()


class TaskList(BaseModel):
    '''任务列表表'''
    __tablename__ = "tasklist"
    task_type = Column(Integer, doc='策略类型',server_default='1')
    name = Column(String(), doc='任务名称', nullable=True)
    host_user_email=Column(String(), doc='来自', nullable=True)
    share_secret = Column(String(), doc='分享秘钥', nullable=True)
    strategy_keys_id = Column(Integer(), doc='策略密钥ID', nullable=True)
    account_id = Column(Integer(), doc='关联账号ID', nullable=True)
    strategy_code = Column(String(), doc='策略代码', nullable=True)
    order_count_type = Column(Integer, doc='订单计数类型', nullable=True)
    dynamic_calculation_type = Column(Integer, doc='动态计算类型', nullable=True,server_default='1')
    strategy_amount = Column(Numeric(), doc='策略金额', nullable=True)
    position_amount = Column(Numeric(), doc='持仓额度', nullable=True)
    allocation_amount = Column(Numeric(), doc='分配金额', nullable=True)
    can_use_amount = Column(Numeric(), doc='可用金额', nullable=True)
    accruing_amounts = Column(Numeric(), doc='累计金额', nullable=True)
    enable = Column(Integer, doc='是否启用', nullable=True, server_default='1')
    days_number = Column(Integer, doc='天数', nullable=True)
    is_open = Column(Integer, doc='是否开启', nullable=True, server_default='0')
    delete_time = Column(DateTime(), doc='删除时间', nullable=True)
    start_time = Column(DateTime(), doc='开始时间', nullable=True)
    service_charge = Column(Numeric(), doc='手续费', nullable=True)
    lower_limit_of_fees = Column(Numeric(), doc='手续费下限', nullable=True)
    backtest_id = Column(Integer, doc='回测ID', nullable=True)
    mock_service_charge = Column(Numeric(), doc='回测手续费', nullable=True)
    mock_lower_limit_of_fees = Column(Numeric(), doc='回测手续费下限', nullable=True)
    mock_allocation_amount = Column(Numeric(), doc='回测分配金额', nullable=True)
    user_id = Column(String(), doc='用户id', nullable=True)
    is_simulation = Column(Integer(), doc='是否仿真回测', nullable=True, server_default='0')
    position_ratio = Column(Numeric(), doc='比例调整', nullable=True, server_default='1')
    platform = Column(Integer(), doc='平台', nullable=True, server_default='1')
    open_mandatory_limit_order = Column(Integer(), doc='是否强制使用限价单', nullable=True, server_default='0')
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
    backtest_id = Column(Integer, doc='回测ID', nullable=True)
    positions = Column(String(), doc='持仓', nullable=True)
    is_mock = Column(Integer, doc='是否回测', nullable=True, server_default='0',index=True)
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
    backtest_id = Column(Integer, doc='回测ID', nullable=True)
    is_mock = Column(Integer, doc='是否回测', nullable=True, server_default='0',index=True)
    def __str__(self):
        return f"Entrust: {self.traded_id}"


class Trades(BaseModel):
    '''成交表'''
    __tablename__ = "trades"
    order_id = Column(Integer, doc='订单ID', nullable=True)
    order_sysid = Column(String(), doc='订单系统ID', nullable=True)
    stock_code = Column(String(), doc='股票代码', nullable=True)
    traded_volume = Column(Integer(), doc='交易数量', nullable=True)
    traded_time = Column(Integer(), doc='交易时间', nullable=True)
    traded_price = Column(Numeric(), doc='交易价格', nullable=True) 
    traded_amount = Column(Numeric(), doc='交易金额', nullable=True)
    commission = Column(Numeric(), doc='佣金', nullable=True)
    order_status = Column(Integer, doc='订单状态', nullable=True)
    order_type = Column(Integer, doc='订单类型', nullable=True)
    status_msg = Column(String(), doc='状态消息', nullable=True)
    offset_flag = Column(Integer, doc='偏移标志', nullable=True)
    orders_id = Column(Integer, doc='订单ID', nullable=True)
    task_id = Column(Integer, doc='任务ID', nullable=True)
    status = Column(Integer, doc='状态', nullable=True, server_default='0')
    backtest_id = Column(Integer, doc='回测ID', nullable=True)
    is_mock = Column(Integer, doc='是否回测', nullable=True, server_default='0',index=True)
    def __str__(self):
        return f"Trade: {self.order_sysid}"


class Positions(BaseModel):
    __tablename__ = "positions"
    security_code = Column(String(), doc='证券代码', nullable=True)
    volume = Column(Integer, doc='数量', nullable=True)
    amount = Column(Numeric(), doc='金额', nullable=True)
    task_id = Column(Integer, doc='任务ID', nullable=True)
    average_price = Column(Numeric(), doc='平均成本', nullable=True)
    backtest_id = Column(Integer, doc='回测ID', nullable=True)
    delete_time = Column(DateTime(), doc='删除时间', nullable=True)
    is_mock = Column(Integer, doc='是否回测', nullable=True, server_default='0', index=True)
    def __str__(self):
        return f"Positions: {self.security_code}"


class RemotePositions(BaseModel):
    __tablename__ = "remote_positions"
    security_code = Column(String(), doc='证券代码', nullable=True)
    volume = Column(Integer, doc='数量', nullable=True)
    task_id = Column(Integer, doc='任务ID', nullable=True)
    def __str__(self):
        return f"RemotePositions: {self.security_code}"
    

class Account(BaseModel):
    __tablename__ = "account"
    
    remark = Column(String(), doc='备注', nullable=True)
    status = Column(Integer(), doc='状态0是禁用1是启用', nullable=True)
    is_connected = Column(Integer(), doc='是否连接', nullable=True)
    is_main = Column(Integer(), doc='是否主账号', nullable=True)
    
    mini_qmt_path = Column(String(), doc='路径', nullable=True)
    client_id = Column(String(), doc='客户ID', nullable=True)
    client_type = Column(Integer(), doc='账户类型', nullable=True)
    ths_path = Column(String(), doc='同花顺路径', nullable=True)
    ths_client_id = Column(String(), doc='同花顺客户ID', nullable=True)
    ths_pwd = Column(String(), doc='同花顺密码', nullable=True)
    auto_national_debt = Column(Integer, doc='自动逆回购', nullable=True, server_default='0')
    auto_buy_stock_ipo = Column(Integer, doc='自动打新股', nullable=True, server_default='0')
    auto_buy_purchase_ipo = Column(Integer, doc='自动打新债·', nullable=True, server_default='0')

    def __str__(self):
        return f"Account: {self.id}"    

class Backtest(BaseModel):
    __tablename__ = "backtest"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(), doc='名称', nullable=True)
    order_count_type = Column(Integer(), doc='订单计数类型', nullable=True) 
    service_charge = Column(Numeric(), doc='手续费', nullable=True)
    accruing_amounts = Column(Numeric(), doc='累计金额', nullable=True)
    initial_capital = Column(Numeric(), doc='起始资金', nullable=True) 
    lower_limit_of_fees = Column(Numeric(), doc='手续费下限', nullable=True)
    final_amount = Column(Numeric(), doc='结束金额', nullable=True)
    task_id = Column(Integer, doc='任务ID', nullable=True) 
    frequency = Column(String(), doc='频率', nullable=True)
    state = Column(String(), doc='状态', nullable=True)
    can_use_amount = Column(Numeric(), doc='可用金额', nullable=True)
    def __str__(self):
        return f"Backtest: {self.id}"
    
    
class Logger(BaseModel):
    __tablename__ = "logger"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(), doc='时间戳', nullable=True)
    logger_name = Column(String(), doc='日志名称', nullable=True)
    level = Column(String(), doc='日志级别', nullable=True)
    message = Column(String(), doc='日志消息', nullable=True)
    module = Column(String(), doc='模块', nullable=True)
    func_name = Column(String(), doc='函数名称', nullable=True)
    line_num = Column(Integer(), doc='行号', nullable=True)
    exception = Column(String(), doc='异常信息', nullable=True)
    user_id = Column(String(), doc='用户ID', nullable=True)
    task_id = Column(Integer(), doc='任务ID', nullable=True)
    def __str__(self):
        return f"Logger: {self.id}"
    
    
    
class DATA_ST_STOCKS(BaseModel):
    __tablename__ = "data_st_stocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(), doc='代码', nullable=True)
    name = Column(String(), doc='名称', nullable=True)
    latest_price = Column(Numeric(), doc='最新价', nullable=True)
    change_rate = Column(Numeric(), doc='涨跌幅', nullable=True)
    change_amount = Column(Numeric(), doc='涨跌额', nullable=True)
    volume = Column(Numeric(), doc='成交量', nullable=True)
    turnover = Column(Numeric(), doc='成交额', nullable=True)
    amplitude = Column(Numeric(), doc='振幅', nullable=True)
    highest = Column(Numeric(), doc='最高', nullable=True)
    lowest = Column(Numeric(), doc='最低', nullable=True)
    open = Column(Numeric(), doc='今开', nullable=True)
    close = Column(Numeric(), doc='昨收', nullable=True)
    volume_ratio = Column(Numeric(), doc='量比', nullable=True)
    turnover_ratio = Column(Numeric(), doc='换手率', nullable=True)
    pe_dynamic = Column(Numeric(), doc='市盈率-动态', nullable=True)
    pb = Column(Numeric(), doc='市净率', nullable=True)
    def __str__(self):
        return f"STOCKDATA_ST_STOCKS: {self.id}"
    
    
class DATA_ALL_STOCKS(BaseModel):
    __tablename__ = "data_all_stocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(), doc='代码', nullable=True)
    name = Column(String(), doc='名称', nullable=True)
    latest_price = Column(Numeric(), doc='最新价', nullable=True)
    change_rate = Column(Numeric(), doc='涨跌幅', nullable=True)
    change_amount = Column(Numeric(), doc='涨跌额', nullable=True)
    volume = Column(Numeric(), doc='成交量', nullable=True)
    turnover = Column(Numeric(), doc='成交额', nullable=True)
    amplitude = Column(Numeric(), doc='振幅', nullable=True)
    highest = Column(Numeric(), doc='最高', nullable=True)
    lowest = Column(Numeric(), doc='最低', nullable=True)
    open = Column(Numeric(), doc='今开', nullable=True)
    close = Column(Numeric(), doc='昨收', nullable=True)
    volume_ratio = Column(Numeric(), doc='量比', nullable=True)
    turnover_ratio = Column(Numeric(), doc='换手率', nullable=True)
    pe_dynamic = Column(Numeric(), doc='市盈率-动态', nullable=True)
    pb = Column(Numeric(), doc='市净率', nullable=True)
    total_market_value = Column(Numeric(), doc='总市值', nullable=True)
    circulating_market_value = Column(Numeric(), doc='流通市值', nullable=True)
    rise_speed = Column(Numeric(), doc='涨速', nullable=True)
    five_minute_change = Column(Numeric(), doc='5分钟涨跌', nullable=True)
    sixty_days_change = Column(Numeric(), doc='60日涨跌幅', nullable=True)
    year_to_date_change = Column(Numeric(), doc='年初至今涨跌幅', nullable=True)
    def __str__(self):
        return f"STOCKDATA_ALL_STOCKS: {self.id}"
    
class DATA_TRADE_DATE_HIST(BaseModel):
    __tablename__ = "data_trade_date_hist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String(), doc='交易日', nullable=True)
    def __str__(self):
        return f"DATA_TRADE_DATE_HIST: {self.id}"

class DATA_TABLE_RECORD(BaseModel):
    __tablename__ = "data_table_record"
    table_name = Column(String(), doc='表名', nullable=True)
    record_type = Column(Integer(), doc='记录类型', nullable=True)
    record_time = Column(String(), doc='记录时间', nullable=True)
    record_content = Column(String(), doc='记录内容', nullable=True)
    def __str__(self):
        return f"DATA_TABLE_RECORD: {self.id}"
    