from .tools.sys_config import get_system_unique_id
from .db.orm import ORM
import logging
from api.system import System
from datetime import datetime
from typing import Any, Dict
import asyncio

# Remove the get_logger function since we're now creating the logger directly in GlobalParams

class DatabaseLogHandler(logging.Handler):
    def __init__(self, unique_id: str, run_model_type: int, user_id: str = None,orm = None):
        super().__init__()
        self.unique_id = unique_id
        self.run_model_type = run_model_type
        self.user_id = user_id
        self.orm = orm

    def emit(self, record: logging.LogRecord) -> None:
        try:
            if record.levelname == 'ERROR':
                print(record.message)
            
            showMessage = getattr(record, 'showMessage', False)
            if showMessage:
                # 简化处理，直接删除特殊字符
                safe_message = str(record.message)
                # 删除特殊字符
                safe_message = ''.join(c for c in safe_message if c.isalnum() or c in ' .,;:-_()[]{}<>!?=+*/%&|^~$#@!')
                System.system_py2js(self,'remoteCallBack', {"message": safe_message})
            
            user_id = self.user_id if self.run_model_type == 2 else self.unique_id
            
            # 准备日志数据
            log_data = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'logger_name': record.name,
                'level': record.levelname,
                'message': record.message,
                'module': record.module,
                'func_name': record.funcName,
                'line_num': record.lineno,
                'exception': record.exc_info,
                'user_id': user_id  # 存储用户ID
            }
            
            self._insert_log(log_data)
        except Exception as e:
            # 发生错误时，尝试记录到标准错误
            print(f"记录日志到数据库失败: {e}")
            self.handleError(record)

    def _insert_log(self, log_data: Dict[str, Any]) -> None:
        """执行数据库插入操作"""
        try:
            self.orm.add_log(log_data)
        except Exception as e:
            raise e


# 全局参数
class GlobalParams():
    def __init__(self):
        self.user_id = None
        self.run_model_type = 0
        self.is_wx_connected = False
        self.unique_id = get_system_unique_id()
        self.orm = ORM()

        
        # Disable asyncio debug logging
        asyncio.get_event_loop().set_debug(False)
        
        # Create logger with ORM instance
        logger = logging.getLogger('my_app')
        logger.setLevel(logging.INFO)
        
        # Disable asyncio debug logging
        asyncio_logger = logging.getLogger('asyncio')
        asyncio_logger.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # File handler
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Database handler with ORM instance
        db_handler = DatabaseLogHandler(self.unique_id, self.run_model_type, self.user_id, self.orm)
        db_handler.setFormatter(formatter)
        logger.addHandler(db_handler)
        
        self.logger = logger
        
        dic = {
            "st_stock_code": [],
            "all_stock_code": {},
            "trade_date": [],
        }
        self.stock_map = dic




G = GlobalParams()