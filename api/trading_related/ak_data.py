import akshare as ak
import pandas as pd
from datetime import datetime
from api.global_params import G
from pyapp.db.db import DB
import time
from api.db.models import (
    DATA_ALL_STOCKS,DATA_ST_STOCKS,
    DATA_TRADE_DATE_HIST
)
from ..tools.common import sync_data_to_global


# 同步数据表
def sync_data_stocks_data():
    time.sleep(4)
    TABLE_NAME_LIST = [{
        'table_name':'data_trade_date_hist',
        'diff': 30,
    },{
        'table_name':'data_all_stocks',
        'diff': 5,
    },{
        'table_name':'data_st_stocks',
        'diff': 0,
    }]
    for item in TABLE_NAME_LIST:
        table_name = item['table_name']
        diff = item['diff']
        record = G.orm.get_data_table_record(table_name)
        if record and record['record_time']:
            today = datetime.today()
            record_date = datetime.fromtimestamp(record['record_time']).replace(hour=0, minute=0, second=0, microsecond=0)
            if record_date < today and (today - record_date).days > diff:
                record = None
            
        if record and record['record_time']:
            G.logger.info(f"数据表: {table_name} 已同步",extra={
                "showMessage": True
            })
        else:    
            G.logger.info(f"正在同步数据表: {table_name}",extra={
                "showMessage": True
            })
            is_success = False
            if table_name == 'data_all_stocks':
                is_success = save_all_data()
            elif table_name == 'data_st_stocks':
                is_success = save_st_data()
   
            elif table_name == 'data_trade_date_hist':
                is_success = save_trade_date_hist()
                
            if is_success:
                G.logger.info(f"数据表: {table_name} 同步成功",extra={
                    "showMessage": True
                })
                G.orm.add_data_table_record(table_name)
            else:
                G.logger.error(f"数据表: {table_name} 同步失败",extra={
                    "showMessage": True
                })
    sync_data_to_global()


# 保存数据到数据库
def save_all_data():
    try:
        data = ak.stock_zh_a_spot_em()
        if isinstance(data, pd.DataFrame) and not data.empty:
            # 确保列名与数据库模型匹配
            column_mapping = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'latest_price',
                '涨跌幅': 'change_rate',
                '涨跌额': 'change_amount',
                '成交量': 'volume',
                '成交额': 'turnover',
                '振幅': 'amplitude',
                '最高': 'highest',
                '最低': 'lowest',
                '今开': 'open',
                '昨收': 'close',
                '量比': 'volume_ratio',
                '换手率': 'turnover_ratio',
                '市盈率-动态': 'pe_dynamic',
                '市净率': 'pb',
                '总市值': 'total_market_value',
                '流通市值': 'circulating_market_value',
                '涨速': 'rise_speed',
                '5分钟涨跌': 'five_minute_change',
                '60日涨跌幅': 'sixty_days_change',
                '年初至今涨跌幅': 'year_to_date_change'
            }
            
            # 移除不需要的序号列
            if '序号' in data.columns:
                data = data.drop(columns=['序号'])
            
            # 重命名列以匹配数据库模型
            data = data.rename(columns=column_mapping)
            
            with DB.session() as dbSession:
                try:
                    # 删除现有数据
                    dbSession.query(DATA_ALL_STOCKS).delete()
                    
                    # 添加新数据
                    for index, row in data.iterrows():
                        record = DATA_ALL_STOCKS(**row.to_dict())
                        dbSession.add(record)
                    
                    # 提交事务
                    dbSession.commit()
                    print("Successfully saved data")
                    return True
                except Exception as e:
                    # 如果发生错误，回滚事务
                    dbSession.rollback()
                    print(f"Error saving data: {str(e)}")
                    return None
            
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in save_all_data: {str(e)}")
        return None

# 保存日期到数据库
def save_trade_date_hist():
   data = ak.tool_trade_date_hist_sina()
   if isinstance(data, pd.DataFrame) and not data.empty:
        # 确保列名与数据库模型匹配
        column_mapping = {
            'trade_date': 'trade_date',
        }
        
        # 移除不需要的序号列
        if '序号' in data.columns:
            data = data.drop(columns=['序号'])
        
        # 重命名列以匹配数据库模型
        data = data.rename(columns=column_mapping)
        
        with DB.session() as dbSession:
            try:
                # 删除现有数据
                dbSession.query(DATA_TRADE_DATE_HIST).delete()
                
                # 添加新数据
                for index, row in data.iterrows():
                    record = DATA_TRADE_DATE_HIST(**row.to_dict())
                    dbSession.add(record)
                
                # 提交事务
                dbSession.commit()
                print("Successfully saved data")
                return True
            except Exception as e:
                # 如果发生错误，回滚事务
                dbSession.rollback()
                print(f"Error saving data: {str(e)}")
                return None
   return False

# 保存数据到数据库
def save_st_data():
    data = ak.stock_zh_a_st_em()
    if isinstance(data, pd.DataFrame) and not data.empty:
        # 确保列名与数据库模型匹配
        column_mapping = {
            '代码': 'code',
            '名称': 'name',
            '最新价': 'latest_price',
            '涨跌幅': 'change_rate',
            '涨跌额': 'change_amount',
            '成交量': 'volume',
            '成交额': 'turnover',
            '振幅': 'amplitude',
            '最高': 'highest',
            '最低': 'lowest',
            '今开': 'open',
            '昨收': 'close',
            '量比': 'volume_ratio',
            '换手率': 'turnover_ratio',
            '市盈率-动态': 'pe_dynamic',
            '市净率': 'pb'
        }
        
        # 移除不需要的序号列
        if '序号' in data.columns:
            data = data.drop(columns=['序号'])
        
        # 重命名列以匹配数据库模型
        data = data.rename(columns=column_mapping)
        
        with DB.session() as dbSession:
            try:
                # 删除现有数据
                dbSession.query(DATA_ST_STOCKS).delete()
                
                # 添加新数据
                for index, row in data.iterrows():
                    record = DATA_ST_STOCKS(**row.to_dict())
                    dbSession.add(record)
                
                # 提交事务
                dbSession.commit()
            except Exception as e:
                # 如果发生错误，回滚事务
                dbSession.rollback()
                print(f"Error saving data: {str(e)}")
                return False    
        
        return True
    return False


