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
from api.trading_related.additional_data import get_all_trade_day, query_all_stock_by_day, query_st_stock_daily_by_day


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
def sync_data_stocks_data(force=False):
    try:
        if not force:
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
            if force:
                record = None
            elif record and record.get('record_time'):
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

        data = query_all_stock_by_day(quote_day)
        if isinstance(data, pd.DataFrame) and not data.empty:
            data = data.copy()

            column_mapping = {
                "code": "code",
                "code_name": "name",
            }
            data = data.rename(columns=column_mapping)

            if "code" in data.columns:
                data["code"] = data["code"].astype(str).apply(
                    lambda code: code.split(".", 1)[-1]
                )

            # tradeStatus 当前无对应数据库字段，保留 code/name 即可
            expected_columns = ["code", "name"]
            available_columns = [
                column for column in expected_columns if column in data.columns
            ]
            data = data[available_columns].drop_duplicates(subset=["code"])
            data = data.sort_values(by="code").reset_index(drop=True)

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
    try:
        quote_day = get_recent_trade_date_for_query_all_stock()
        G.logger.info(f"data_st_stocks 使用 baostock 日期: {quote_day}", extra={
            "showMessage": True
        })

        data = query_st_stock_daily_by_day(quote_day)
    except Exception as e:
        print(f"Error in save_st_data: {str(e)}")
        return False

    if isinstance(data, pd.DataFrame) and not data.empty:
        data = data.copy()

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "preclose",
            "volume",
            "amount",
            "turn",
            "pctChg",
            "peTTM",
            "pbMRQ",
        ]
        for column in numeric_columns:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors="coerce")

        if "isST" in data.columns:
            data = data[data["isST"].astype(str) == "1"]

        if "code" in data.columns:
            data["code"] = data["code"].astype(str).apply(
                lambda code: code.split(".", 1)[-1]
            )

        data["name"] = data.get("code_name")
        data["latest_price"] = data.get("close")
        data["change_rate"] = data.get("pctChg")
        data["change_amount"] = data.get("close") - data.get("preclose")
        data["turnover"] = data.get("amount")
        data["highest"] = data.get("high")
        data["lowest"] = data.get("low")
        data["close"] = data.get("preclose")
        data["turnover_ratio"] = data.get("turn")
        data["pe_dynamic"] = data.get("peTTM")
        data["pb"] = data.get("pbMRQ")
        data["volume_ratio"] = None

        if "preclose" in data.columns:
            data["amplitude"] = (
                (data.get("high") - data.get("low")) / data.get("preclose") * 100
            )
            data.loc[data["preclose"].isna() | (data["preclose"] == 0), "amplitude"] = None
        else:
            data["amplitude"] = None

        expected_columns = [
            "code",
            "name",
            "latest_price",
            "change_rate",
            "change_amount",
            "volume",
            "turnover",
            "amplitude",
            "highest",
            "lowest",
            "open",
            "close",
            "volume_ratio",
            "turnover_ratio",
            "pe_dynamic",
            "pb",
        ]
        data = data[expected_columns].drop_duplicates(subset=["code"]).reset_index(drop=True)
        
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
