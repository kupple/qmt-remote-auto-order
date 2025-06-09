import logging
from datetime import datetime
from typing import Any, Dict
from api.system import System


# 数据库日志处理器
class DatabaseHandler(logging.Handler):
    def __init__(self, g):
        super().__init__()
        self.g = g


    def emit(self, record: logging.LogRecord) -> None:
        """将日志记录到数据库"""
        try:
            if record.levelname == 'ERROR':
                print(record.message)
            showMessage = getattr(record, 'showMessage', None)
            if showMessage:
                System.system_py2js(self,'remoteCallBack', {"message":record.message})
            
            if self.g.run_model_type == 2:
                user_id = self.g.user_id
            else:
                user_id = self.g.unique_id
                
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
            
            # 插入数据库
            self._insert_log(log_data)
        except Exception as e:
            # 发生错误时，尝试记录到标准错误
            self.g.logger.error(f"记录日志到数据库失败: {e}")
            self.handleError(record)

    def _insert_log(self, log_data: Dict[str, Any]) -> None:
        """执行数据库插入操作"""
        try:
            if self.g.run_model_type == 2:
                log_data['user_id'] = self.g.user_id
            else:
                log_data['user_id'] = self.g.unique_id
            self.g.orm.add_log(log_data)
        except Exception as e:
            raise e

# 配置日志
def setup_logger(g) -> logging.Logger:
    """配置日志记录器，同时输出到文件和数据库"""
    logger = logging.getLogger('my_app')
    logger.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 文件处理器
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 数据库处理器
    db_handler = DatabaseHandler(g)
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)
    
    return logger


# logger.debug('这是一条 DEBUG 级别的日志')
# logger.info('这是一条 INFO 级别的日志')
# logger.warning('这是一条 WARNING 级别的日志')
# logger.error('这是一条 ERROR 级别的日志')
# logger.critical('这是一条 CRITICAL 级别的日志')
