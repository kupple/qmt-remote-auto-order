import pandas as pd
from datetime import datetime,timedelta
from api.global_params import G
from pyapp.db.db import DB
import time
from api.db.models import (
    DATA_ALL_STOCKS,DATA_ST_STOCKS,
    DATA_TRADE_DATE_HIST
)
from ..tools.common import sync_data_to_global,timestamp_to_date
from api.trading_related.additional_data import stock_zh_a_spot_em, stock_zh_a_st_em, get_all_trade_day, query_all_stock_by_day


def get_recent_trade_date_for_query_all_stock():
    """
    从 data_trade_date_hist 中找出离今天最近且不晚于今天的交易日。
    如果不存在，则回退到最早可用交易日；再不行则返回今天。
    """
    trade_date_list = G.orm.get_trade_date_list()
    if not trade_date_list:
        return datetime.now().strftime("%Y-%m-%d")

    date_objects = []
    for date_str in trade_date_list:
        try:
            date_objects.append(datetime.strptime(date_str, "%Y-%m-%d").date())
        except Exception:
            continue

    if not date_objects:
        return datetime.now().strftime("%Y-%m-%d")

    today = datetime.now().date()
    available_dates = [date_obj for date_obj in date_objects if date_obj <= today]
    if available_dates:
        return max(available_dates).strftime("%Y-%m-%d")
    return min(date_objects).strftime("%Y-%m-%d")

# 同步数据表
def sync_data_stocks_data():
    try:
        time.sleep(8)
        TABLE_NAME_LIST = [{
            'table_name':'data_trade_date_hist',
            'diff': 7,
        },{
            'table_name':'data_all_stocks',
            'diff': 1,
        },{
            'table_name':'data_st_stocks',
            'diff': 1,
        }]
        for item in TABLE_NAME_LIST:
            table_name = item['table_name']
            diff = item['diff']  # 间隔同步的天数
            record = G.orm.get_data_table_record(table_name)
            # print(record)

            # 根据上次同步时间 + diff 天 来判断是否需要重新同步
            if record and record.get('record_time'):
                # 兼容异常 float 情况，直接视为未同步
                if isinstance(record['record_time'], float):
                    record = None
                else:
                    date_obj = datetime.strptime(record['record_time'], '%Y-%m-%d %H:%M:%S')
                    last_sync_date = date_obj.date()
                    today = datetime.now().date()

                    # diff > 0: 间隔 diff 天同步一次；到达/超过下次同步日则需要重新同步
                    if diff > 0:
                        next_sync_date = last_sync_date + timedelta(days=int(diff))
                        if today >= next_sync_date:
                            # 需要重新同步，当作没有有效记录
                            record = None
                    # diff <= 0: 按照“永不过期”处理，不动 record

            if record and record.get('record_time'):
                G.logger.info(f"数据表: {table_name} 已同步", extra={
                    "showMessage": True
                })
            else:
                G.logger.info(f"正在同步数据表: {table_name}", extra={
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
                    G.logger.info(f"数据表: {table_name} 同步成功", extra={
                        "showMessage": True
                    })
                    G.orm.add_data_table_record(table_name)
                else:
                    G.logger.error(f"数据表: {table_name} 同步失败", extra={
                        "showMessage": True
                    })
        sync_data_to_global()        
    except Exception as e:
        G.logger.error(f"同步数据表失败: {str(e)}",extra={
            "showMessage": True
        })
    


# 保存数据到数据库
def save_all_data():
    try:
        quote_day = get_recent_trade_date_for_query_all_stock()
        G.logger.info(f"data_all_stocks 使用 query_all_stock 日期: {quote_day}", extra={
            "showMessage": True
        })

        stock_basic_data = query_all_stock_by_day(quote_day)
        data = stock_zh_a_spot_em()
        if isinstance(data, pd.DataFrame) and not data.empty:
            # 确保列名与数据库模型匹配
            column_mapping = {
                "日期":"date",
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

            if isinstance(stock_basic_data, pd.DataFrame) and not stock_basic_data.empty:
                stock_basic_data = stock_basic_data.copy()
                if "code" in stock_basic_data.columns:
                    stock_basic_data["code"] = stock_basic_data["code"].astype(str).apply(
                        lambda code: code.split(".", 1)[-1]
                    )
                stock_basic_data = stock_basic_data.rename(columns={"code_name": "name"})
                stock_basic_data = stock_basic_data[["code", "name"]].drop_duplicates(subset=["code"])

                if "name" in data.columns:
                    data = data.merge(stock_basic_data, on="code", how="left", suffixes=("_em", "_bs"))
                    data["name"] = data["name_em"].fillna(data["name_bs"])
                    data = data.drop(columns=["name_em", "name_bs"])
                else:
                    data = data.merge(stock_basic_data, on="code", how="left")
            
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
   data = get_all_trade_day()
   print(data)
   print("datazxczxc")
   if isinstance(data, pd.DataFrame) and not data.empty:
        # 确保列名与数据库模型匹配
        column_mapping = {
            'calendar_date': 'trade_date',
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
    data = stock_zh_a_st_em()
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
