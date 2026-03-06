from datetime import datetime
import json
from api.db.models import (
    Base,
    PPXStorageVar, Setting, TaskList, Orders, Entrusts,
    Trades, Backtest,Positions,Logger,RemotePositions,Account,
    DATA_TABLE_RECORD,DATA_ALL_STOCKS,DATA_ST_STOCKS,DATA_TRADE_DATE_HIST
)
from pyapp.db.db import DB
from sqlalchemy import select, update, insert, and_, or_, desc, func, text
from api.tools.sys_config import generate_random_letters
def _convert_stock_suffix(stock_code: str) -> str:
    """转换股票代码后缀"""
    if not stock_code:
        return stock_code

    if "." not in stock_code:
        if stock_code.startswith(("0", "3", "2")):
            return f"{stock_code}.SZ"
        if stock_code.startswith(("6", "9", "7")):
            return f"{stock_code}.SH"
        return stock_code

    code, exchange = stock_code.rsplit(".", 1)
    if exchange.upper() == "XSHG":
        return f"{code}.SH"
    if exchange.upper() == "XSHE":
        return f"{code}.SZ"
    return stock_code
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
            # 兜底创建新增表（避免旧库缺少 account 表）
            engine = dbSession.get_bind()
            Base.metadata.create_all(bind=engine, tables=[Account.__table__])

            # 旧库迁移：tasklist 增加 account_id 字段
            columns_stmt = text("PRAGMA table_info(tasklist)")
            columns = dbSession.execute(columns_stmt).fetchall()
            column_names = [row[1] for row in columns]
            if "account_id" not in column_names:
                dbSession.execute(text("ALTER TABLE tasklist ADD COLUMN account_id INTEGER"))

            # 旧库迁移：account 增加自动交易开关字段
            account_columns_stmt = text("PRAGMA table_info(account)")
            account_columns = dbSession.execute(account_columns_stmt).fetchall()
            account_column_names = [row[1] for row in account_columns]
            if "auto_national_debt" not in account_column_names:
                dbSession.execute(text("ALTER TABLE account ADD COLUMN auto_national_debt INTEGER DEFAULT 0"))
            if "auto_buy_stock_ipo" not in account_column_names:
                dbSession.execute(text("ALTER TABLE account ADD COLUMN auto_buy_stock_ipo INTEGER DEFAULT 0"))
            if "auto_buy_purchase_ipo" not in account_column_names:
                dbSession.execute(text("ALTER TABLE account ADD COLUMN auto_buy_purchase_ipo INTEGER DEFAULT 0"))

            # 初始化设置表
            Setting.initialize_default(dbSession)
        finally:
            dbSession.close()

    def get_storage_var(self, key):
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

    def set_storage_var(self, key, val):
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

    def add_account(self, data):
        """添加账号"""
        dbSession = DB.session()
        with dbSession.begin():
            # 客户编号唯一性校验
            unique_field = "ths_client_id" if data.get("client_type") == 1 else "client_id"
            unique_value = data.get(unique_field)
            if isinstance(unique_value, str):
                unique_value = unique_value.strip()
            if unique_value:
                stmt = select(Account.id).where(
                    or_(
                        Account.client_id == unique_value,
                        Account.ths_client_id == unique_value,
                    )
                )
                exists = dbSession.execute(stmt).first()
                if exists:
                    raise ValueError("客户编号已存在，请勿重复添加")

            account = Account()
            for key, value in data.items():
                if hasattr(account, key):
                    setattr(account, key, value)
            dbSession.add(account)
        dbSession.close()
        return True

    def get_account_list(self):
        """获取账号列表"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Account).order_by(desc(Account.created_at))
            result = dbSession.execute(stmt).scalars().all()
            return [item.toDict() for item in result]
        dbSession.close()
        return []

    def get_account_by_id(self, account_id):
        """根据ID获取账号"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Account).where(Account.id == account_id)
            account = dbSession.execute(stmt).scalar_one_or_none()
            return account.toDict() if account else None
        dbSession.close()
        return None

    def delete_account(self, account_id):
        """删除账号（有关联任务时禁止删除）"""
        dbSession = DB.session()
        with dbSession.begin():
            task_stmt = select(TaskList.id).where(
                TaskList.account_id == account_id,
                TaskList.delete_time.is_(None)
            )

            task_exists = dbSession.execute(task_stmt).first()
            print(task_exists)
            print("task_stmt")
            if task_exists:
                raise ValueError("该账号已关联任务，不能删除")

            account_stmt = select(Account).where(Account.id == account_id)
            account = dbSession.execute(account_stmt).scalar_one_or_none()
            if not account:
                raise ValueError("账号不存在")

            dbSession.delete(account)
        dbSession.close()
        return True

    def update_account(self, account_id, data):
        """编辑账号"""
        dbSession = DB.session()
        with dbSession.begin():
            account = dbSession.execute(select(Account).where(Account.id == account_id)).scalar_one_or_none()
            if not account:
                raise ValueError("账号不存在")

            # 客户编号唯一性校验（排除自身）
            unique_field = "ths_client_id" if data.get("client_type", account.client_type) == 1 else "client_id"
            unique_value = data.get(unique_field)
            if isinstance(unique_value, str):
                unique_value = unique_value.strip()
            if unique_value:
                exists_stmt = select(Account.id).where(
                    and_(
                        or_(Account.client_id == unique_value, Account.ths_client_id == unique_value),
                        Account.id != account_id,
                    )
                )
                exists = dbSession.execute(exists_stmt).first()
                if exists:
                    raise ValueError("客户编号已存在，请勿重复添加")

            for key, value in data.items():
                if hasattr(account, key):
                    setattr(account, key, value)
        dbSession.close()
        return True

    def get_task_list(self,data):
        """获取任务列表（关联账号信息）"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(TaskList, Account).outerjoin(Account, TaskList.account_id == Account.id).where(TaskList.delete_time.is_(None))

            for key, value in data.items():
                if hasattr(TaskList, key):
                    stmt = stmt.where(getattr(TaskList, key) == value)

            rows = dbSession.execute(stmt).all()
            result = []
            for task, account in rows:
                item = task.toDict()
                if account:
                    account_name = account.ths_client_id if account.client_type == 1 else account.client_id
                    item["account_name"] = account_name
                    item["account_type"] = account.client_type
                else:
                    item["account_name"] = ""
                    item["account_type"] = None
                result.append(item)
            return result
        dbSession.close()
        return []

    def get_account_task_list(self, data):
        """获取账号及其关联任务列表"""
        dbSession = DB.session()
        with dbSession.begin():
            account_stmt = select(Account).order_by(desc(Account.created_at))
            accounts = dbSession.execute(account_stmt).scalars().all()

            task_stmt = select(TaskList).where(TaskList.delete_time.is_(None))
            for key, value in data.items():
                if hasattr(TaskList, key):
                    task_stmt = task_stmt.where(getattr(TaskList, key) == value)
            tasks = dbSession.execute(task_stmt).scalars().all()

            task_map = {}
            for task in tasks:
                task_map.setdefault(task.account_id, []).append(task.toDict())

            result = []
            for account in accounts:
                account_dict = account.toDict()
                account_dict["account_name"] = account.ths_client_id if account.client_type == 1 else account.client_id
                account_dict["task_list"] = task_map.get(account.id, [])
                result.append(account_dict)

            if task_map.get(None):
                result.append({
                    "id": None,
                    "client_type": None,
                    "account_name": "未关联账号",
                    "task_list": task_map.get(None, [])
                })

            return result
        dbSession.close()
        return []

    def create_task(self, data):
        """创建任务"""
        dbSession = DB.session()
        with dbSession.begin():
            if 'id' not in data or data['id'] is None:
                if 'strategy_code' not in data or not data['strategy_code'] and data["task_type"] == 1:
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
            order = Orders()
            for key, value in data.items():
                if hasattr(order, key) and value is not None:
                    setattr(order, key, value)
            
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

    def add_log(self, log_data):
        """添加日志记录"""
        dbSession = DB.session()
        with dbSession.begin():
            log = Logger(
                timestamp=log_data['timestamp'],
                logger_name=log_data['logger_name'],
                level=log_data['level'],
                message=log_data['message'],
                module=log_data['module'],
                func_name=log_data['func_name'],
                line_num=log_data['line_num'],
                exception=str(log_data['exception']) if log_data['exception'] else None,
                user_id=log_data['user_id']
            )
            dbSession.add(log)
        dbSession.close()
        return True

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
            # G.logger.error(f"查询持仓出错: {str(e)}")
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
        
    
    def add_log(self, data):
        """添加日志记录"""
        dbSession = DB.session()
        with dbSession.begin():
            log = Logger(**data)
            dbSession.add(log)
        dbSession.close()
        return True
    
    def query_log_list(self, query_data: dict, page=1, page_size=50):
        """
        :param query_data: 字典形式的查询参数
        :param page: 页码
        :param page_size: 每页大小
        :return: 日志记录列表
        """
        offset = (page - 1) * page_size
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(Logger)
            for key, value in query_data.items():
                if hasattr(Logger, key):
                    stmt = stmt.where(getattr(Logger, key) == value)
            stmt = stmt.order_by(desc(Logger.created_at))
            result = dbSession.execute(stmt).scalars().all()
            data_list = [log.toDict() for log in result[offset:offset+page_size]]
            
        dbSession.close()
        return {
            'data': data_list,
        }
    def clear_log(self):
        """清除日志"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = Logger.__table__.delete()
            dbSession.execute(stmt)
        dbSession.close()
        return True
    
    def list_data_table_record(self):
        """列出数据表记录"""
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(DATA_TABLE_RECORD)
            result = dbSession.execute(stmt).scalars().all()
            data_list = [record.toDict() for record in result]
        dbSession.close()
        return data_list
    
    
    def add_data_table_record(self, table_name):
        """添加数据表记录"""
        dbSession = DB.session()
        record_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        record_type = 1
        record_content = ''
        with dbSession.begin():
            stmt = select(DATA_TABLE_RECORD).where(DATA_TABLE_RECORD.table_name == table_name)
            result = dbSession.execute(stmt).scalar_one_or_none()
            
            if result is not None:
                # update
                stmt = update(DATA_TABLE_RECORD).where(DATA_TABLE_RECORD.table_name == table_name).values(
                    record_type=record_type,
                    record_time=record_time,
                    record_content=record_content
                )
                dbSession.execute(stmt)
            else:
                # insert
                data = DATA_TABLE_RECORD(
                    table_name=table_name,
                    record_type=record_type,
                    record_time=record_time,
                    record_content=record_content
                )
                dbSession.add(data)
        dbSession.close()
        return True
    
    
    def get_data_table_record(self, table_name):
        """获取数据表记录"""
        record = None
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(DATA_TABLE_RECORD).where(DATA_TABLE_RECORD.table_name == table_name)
            result = dbSession.execute(stmt).scalar_one_or_none()
            if result:
                record = {
                    'table_name': result.table_name,
                    'record_type': result.record_type,
                    'record_time': result.record_time,
                    'record_content': result.record_content
                }
        return record
    

    def get_all_stock_data(self):
        with DB.session() as dbSession:
            return [stock.toDict() for stock in dbSession.query(DATA_ALL_STOCKS).all()]
        
        
    def get_st_stock_data(self):
        with DB.session() as dbSession:
            return [code.code for code in dbSession.query(DATA_ST_STOCKS.code).all()]
        
        
    def get_trade_date_list(self):
        with DB.session() as dbSession:
            return [date.trade_date for date in dbSession.query(DATA_TRADE_DATE_HIST.trade_date).all()]


    # 重置远程持仓为0
    def reset_remote_position(self, task_id):
        dbSession = DB.session()
        with dbSession.begin():
            stmt = RemotePositions.__table__.delete().where(RemotePositions.task_id == task_id)
            dbSession.execute(stmt)
        dbSession.close()
        return True    
    
    def get_remote_position(self, task_id):
        dbSession = DB.session()
        with dbSession.begin():
            stmt = select(RemotePositions).where(RemotePositions.task_id == task_id)
            result = dbSession.execute(stmt).scalars().all()
            return [position.toDict() for position in result]

    def save_remote_position(self, data):
        """保存远程持仓（如果已存在则更新volume，否则插入新记录；如果volume为0则删除该记录）"""
        dbSession = DB.session()
        with dbSession.begin():
            # 查询是否已存在该security_code和task_id的记录
            stmt = select(RemotePositions).where(
                RemotePositions.security_code == data['security_code'],
                RemotePositions.task_id == data['task_id']
            )
            result = dbSession.execute(stmt).scalar_one_or_none()
            if data['volume'] == 0:
                # 如果volume为0，删除该记录（如果存在）
                if result:
                    delete_stmt = (
                        RemotePositions.__table__.delete()
                        .where(
                            RemotePositions.security_code == data['security_code'],
                            RemotePositions.task_id == data['task_id']
                        )
                    )
                    dbSession.execute(delete_stmt)
            else:
                if result:
                    # 已存在，则更新volume
                    update_stmt = (
                        update(RemotePositions)
                        .where(
                            RemotePositions.security_code == data['security_code'],
                            RemotePositions.task_id == data['task_id']
                        )
                        .values(volume=data['volume'])
                    )
                    dbSession.execute(update_stmt)
                else:
                    # 不存在，则插入新记录
                    insert_stmt = insert(RemotePositions).values(data)
                    dbSession.execute(insert_stmt)
        dbSession.close()
        return True

    def save_remote_positions(self, task_id, positions_arr):
        """重置并批量保存远程持仓"""
        normalized_positions = positions_arr
        if isinstance(normalized_positions, str):
            try:
                normalized_positions = json.loads(normalized_positions)
            except json.JSONDecodeError:
                normalized_positions = []

        if not normalized_positions:
            return True

        dbSession = DB.session()
        with dbSession.begin():
            stmt = RemotePositions.__table__.delete().where(
                RemotePositions.task_id == task_id
            )
            dbSession.execute(stmt)

            insert_data = []
            for position in normalized_positions:
                security_code = (
                    position.get("security_code")
                    or position.get("security")
                    or ""
                )
                if not security_code:
                    continue
                security_code = _convert_stock_suffix(security_code)
                volume_val = position.get("volume")
                if volume_val is None:
                    volume_val = position.get("total_amount", 0)
                try:
                    volume = int(volume_val)
                except (TypeError, ValueError):
                    continue
                insert_data.append(
                    {
                        "security_code": security_code,
                        "volume": volume,
                        "task_id": task_id,
                    }
                )
            if insert_data:
                dbSession.execute(insert(RemotePositions), insert_data)
        dbSession.close()
        return True

    ############################################################################################################## 
    
    def get_shippings_on_api(self):
        with DB.session() as dbSession:
            shippings = dbSession.query(TaskList).all()
            return [shipping.toDict() for shipping in shippings]
    
    def get_positions_on_api(self, strategy_code):
        with DB.session() as dbSession:
            trades = dbSession.query(TaskList).where(TaskList.strategy_code == strategy_code).first()
            positions = dbSession.query(Positions).where(Positions.task_id == trades.id).where(Positions.is_mock == 0).all()
            return [position.toDict() for position in positions]
        