import pandas as pd
import requests
from datetime import datetime
from typing import List, Dict
import math
import baostock as bs
import asyncio
import aiohttp


def get_all_trade_day():
    print("zxczx")
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    #### 获取交易日信息 ####
    rs = bs.query_trade_dates(start_date="2025-01-01", end_date="2030-06-30")
    print('query_trade_dates respond error_code:'+rs.error_code)
    print('query_trade_dates respond  error_msg:'+rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    print(result)
    trading_days = result[result['is_trading_day'] == '1']
    trading_days.drop('is_trading_day', axis=1, inplace=True)
    print("result", result)
    #### 登出系统 ####
    bs.logout()

    return trading_days


def stock_xgsglb_em_on_today(symbol: str = "全部股票") -> pd.DataFrame:
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    """
    新股申购与中签查询
    https://data.eastmoney.com/xg/xg/default_2.html
    :param symbol: choice of {"全部股票", "沪市主板", "科创板", "深市主板", "创业板", "北交所"}
    :type symbol: str
    :return: 新股申购与中签数据
    :rtype: pandas.DataFrame
    """
    market_map = {
        "全部股票": F"""(APPLY_DATE='{current_date}')""",
        "沪市主板": F"""(APPLY_DATE='{current_date}')(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE in ("069001001001","069001001003","069001001006"))""",
        "科创板": F"""(APPLY_DATE='{current_date}')(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE="069001001006")""",
        "深市主板": F"""(APPLY_DATE='{current_date}')(SECURITY_TYPE_CODE="058001001")(TRADE_MARKET_CODE in ("069001002001","069001002002","069001002003","069001002005"))""",
        "创业板": F"""(APPLY_DATE='{current_date}')(SECURITY_TYPE_CODE="058001001")(TRADE_MARKET_CODE="069001002002")""",
    }
    url = "http://datacenter-web.eastmoney.com/api/data/v1/get"
    if symbol == "北交所":
        params = {
            "sortColumns": "APPLY_DATE",
            "sortTypes": "-1",
            "pageSize": "500",
            "pageNumber": "1",
            "columns": "ALL",
            "reportName": "RPT_NEEQ_ISSUEINFO_LIST",
            "quoteColumns": "f14~01~SECURITY_CODE~SECURITY_NAME_ABBR",
            "source": "NEEQSELECT",
            "client": "WEB",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        total_page = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        for page in range(1, 1 + int(total_page)):
            params.update({"pageNumber": page})
            r = requests.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = pd.concat([big_df, temp_df], ignore_index=True)

        big_df.rename(
            columns={
                "ORG_CODE": "-",
                "SECURITY_CODE": "代码",
                "SECUCODE": "带市场标识股票代码",
                "SECURITY_NAME_ABBR": "简称",
                "APPLY_CODE": "申购代码",
                "EXPECT_ISSUE_NUM": "发行总数",
                "PRICE_WAY": "定价方式",
                "ISSUE_PRICE": "发行价格",
                "ISSUE_PE_RATIO": "发行市盈率",
                "APPLY_DATE": "申购日",
                "RESULT_NOTICE_DATE": "发行结果公告日期",
                "SELECT_LISTING_DATE": "上市首日-上市日",
                "ONLINE_ISSUE_NUM": "网上-发行数量",
                "APPLY_AMT_UPPER": "网上-顶格所需资金",
                "APPLY_NUM_UPPER": "网上-申购上限",
                "ONLINE_PAY_DATE": "网上申购缴款日期",
                "ONLINE_REFUND_DATE": "网上申购资金退款日",
                "INFO_CODE": "-",
                "ONLINE_ISSUE_LWR": "中签率",
                "NEWEST_PRICE": "最新价格-价格",
                "CLOSE_PRICE": "首日收盘价",
                "INITIAL_MULTIPLE": "-",
                "PER_SHARES_INCOME": "上市首日-每百股获利",
                "LD_CLOSE_CHANGE": "上市首日-涨幅",
                "TURNOVERRATE": "首日换手率",
                "AMPLITUDE": "首日振幅",
                "ONLINE_APPLY_LOWER": "-",
                "MAIN_BUSINESS": "主营业务",
                "INDUSTRY_PE_RATIO": "行业市盈率",
                "APPLY_AMT_100": "稳获百股需配资金",
                "TAKE_UP_TIME": "资金占用时间",
                "CAPTURE_PROFIT": "上市首日-约合年化收益",
                "APPLY_SHARE_100": "每获配百股需配股数",
                "AVERAGE_PRICE": "上市首日-均价",
                "ORG_VAN": "参与申购人数",
                "VA_AMT": "参与申购资金",
                "ISSUE_PRICE_ADJFACTOR": "-",
            },
            inplace=True,
        )
        big_df["最新价格-累计涨幅"] = big_df["首日收盘价"] / big_df["最新价格-价格"]

        big_df = big_df[
            [
                "代码",
                "简称",
                "申购代码",
                "发行总数",
                "网上-发行数量",
                "网上-申购上限",
                "网上-顶格所需资金",
                "发行价格",
                "申购日",
                "中签率",
                "稳获百股需配资金",
                "最新价格-价格",
                "最新价格-累计涨幅",
                "上市首日-上市日",
                "上市首日-均价",
                "上市首日-涨幅",
                "上市首日-每百股获利",
                "上市首日-约合年化收益",
                "发行市盈率",
                "行业市盈率",
                "参与申购资金",
                "参与申购人数",
            ]
        ]
        big_df["发行总数"] = pd.to_numeric(big_df["发行总数"], errors="coerce")
        big_df["网上-发行数量"] = pd.to_numeric(
            big_df["网上-发行数量"], errors="coerce"
        )
        big_df["网上-申购上限"] = pd.to_numeric(
            big_df["网上-申购上限"], errors="coerce"
        )
        big_df["网上-顶格所需资金"] = pd.to_numeric(
            big_df["网上-顶格所需资金"], errors="coerce"
        )
        big_df["发行价格"] = pd.to_numeric(big_df["发行价格"], errors="coerce")
        big_df["中签率"] = pd.to_numeric(big_df["中签率"], errors="coerce")
        big_df["稳获百股需配资金"] = pd.to_numeric(
            big_df["稳获百股需配资金"], errors="coerce"
        )
        big_df["最新价格-价格"] = pd.to_numeric(
            big_df["最新价格-价格"], errors="coerce"
        )
        big_df["最新价格-累计涨幅"] = pd.to_numeric(
            big_df["最新价格-累计涨幅"], errors="coerce"
        )
        big_df["上市首日-均价"] = pd.to_numeric(
            big_df["上市首日-均价"], errors="coerce"
        )
        big_df["上市首日-涨幅"] = pd.to_numeric(
            big_df["上市首日-涨幅"], errors="coerce"
        )
        big_df["上市首日-每百股获利"] = pd.to_numeric(
            big_df["上市首日-每百股获利"], errors="coerce"
        )
        big_df["上市首日-约合年化收益"] = pd.to_numeric(
            big_df["上市首日-约合年化收益"], errors="coerce"
        )
        big_df["发行市盈率"] = pd.to_numeric(big_df["发行市盈率"], errors="coerce")
        big_df["行业市盈率"] = pd.to_numeric(big_df["行业市盈率"], errors="coerce")
        big_df["参与申购资金"] = pd.to_numeric(big_df["参与申购资金"], errors="coerce")
        big_df["参与申购人数"] = pd.to_numeric(big_df["参与申购人数"], errors="coerce")
        big_df["申购日"] = pd.to_datetime(big_df["申购日"], errors="coerce").dt.date
        big_df["上市首日-上市日"] = pd.to_datetime(
            big_df["上市首日-上市日"], errors="coerce"
        ).dt.date
        return big_df
    else:
        params = {
            "sortColumns": "APPLY_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1",
            "pageSize": "5000",
            "pageNumber": "1",
            "reportName": "RPTA_APP_IPOAPPLY",
            "columns": "SECURITY_CODE,SECURITY_NAME,TRADE_MARKET_CODE,APPLY_CODE,TRADE_MARKET,MARKET_TYPE,ORG_TYPE,ISSUE_NUM,ONLINE_ISSUE_NUM,OFFLINE_PLACING_NUM,TOP_APPLY_MARKETCAP,PREDICT_ONFUND_UPPER,ONLINE_APPLY_UPPER,PREDICT_ONAPPLY_UPPER,ISSUE_PRICE,LATELY_PRICE,CLOSE_PRICE,APPLY_DATE,BALLOT_NUM_DATE,BALLOT_PAY_DATE,LISTING_DATE,AFTER_ISSUE_PE,ONLINE_ISSUE_LWR,INITIAL_MULTIPLE,INDUSTRY_PE_NEW,OFFLINE_EP_OBJECT,CONTINUOUS_1WORD_NUM,TOTAL_CHANGE,PROFIT,LIMIT_UP_PRICE,INFO_CODE,OPEN_PRICE,LD_OPEN_PREMIUM,LD_CLOSE_CHANGE,TURNOVERRATE,LD_HIGH_CHANG,LD_AVERAGE_PRICE,OPEN_DATE,OPEN_AVERAGE_PRICE,PREDICT_PE,PREDICT_ISSUE_PRICE2,PREDICT_ISSUE_PRICE,PREDICT_ISSUE_PRICE1,PREDICT_ISSUE_PE,PREDICT_PE_THREE,ONLINE_APPLY_PRICE,MAIN_BUSINESS",
            "filter": market_map[symbol],
            "source": "WEB",
            "client": "WEB",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        total_page = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        for page in range(1, total_page + 1):
            params.update({"pageNumber": page})
            r = requests.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = pd.concat([big_df, temp_df], ignore_index=True)
        big_df.rename(
            columns={
                "SECURITY_CODE": "股票代码",
                "SECURITY_NAME": "股票简称",
                "TRADE_MARKET_CODE": "-",
                "APPLY_CODE": "申购代码",
                "TRADE_MARKET": "-",
                "MARKET_TYPE": "-",
                "ORG_TYPE": "-",
                "ISSUE_NUM": "发行总数",
                "ONLINE_ISSUE_NUM": "网上发行",
                "OFFLINE_PLACING_NUM": "_",
                "TOP_APPLY_MARKETCAP": "顶格申购需配市值",
                "PREDICT_ONFUND_UPPER": "_",
                "ONLINE_APPLY_UPPER": "申购上限",
                "PREDICT_ONAPPLY_UPPER": "_",
                "ISSUE_PRICE": "发行价格",
                "LATELY_PRICE": "最新价",
                "CLOSE_PRICE": "首日收盘价",
                "APPLY_DATE": "申购日期",
                "BALLOT_NUM_DATE": "中签号公布日",
                "BALLOT_PAY_DATE": "中签缴款日期",
                "LISTING_DATE": "上市日期",
                "AFTER_ISSUE_PE": "发行市盈率",
                "ONLINE_ISSUE_LWR": "中签率",
                "INITIAL_MULTIPLE": "询价累计报价倍数",
                "INDUSTRY_PE_NEW": "行业市盈率",
                "OFFLINE_EP_OBJECT": "配售对象报价家数",
                "CONTINUOUS_1WORD_NUM": "连续一字板数量",
                "TOTAL_CHANGE": "涨幅",
                "PROFIT": "每中一签获利",
                "LIMIT_UP_PRICE": "_",
                "INFO_CODE": "_",
                "OPEN_PRICE": "_",
                "LD_OPEN_PREMIUM": "_",
                "LD_CLOSE_CHANGE": "_",
                "TURNOVERRATE": "_",
                "LD_HIGH_CHANG": "_",
                "LD_AVERAGE_PRICE": "_",
                "OPEN_DATE": "_",
                "OPEN_AVERAGE_PRICE": "_",
                "PREDICT_PE": "_",
                "PREDICT_ISSUE_PRICE2": "_",
                "PREDICT_ISSUE_PRICE": "_",
                "PREDICT_ISSUE_PRICE1": "_",
                "PREDICT_ISSUE_PE": "_",
                "PREDICT_PE_THREE": "_",
                "ONLINE_APPLY_PRICE": "_",
                "MAIN_BUSINESS": "_",
                "IS_REGISTRATION": "_",
            },
            inplace=True,
        )
        big_df = big_df[
            [
                "股票代码",
                "股票简称",
                "申购代码",
                "发行总数",
                "网上发行",
                "顶格申购需配市值",
                "申购上限",
                "发行价格",
                "最新价",
                "首日收盘价",
                "申购日期",
                "中签号公布日",
                "中签缴款日期",
                "上市日期",
                "发行市盈率",
                "行业市盈率",
                "中签率",
                "询价累计报价倍数",
                "配售对象报价家数",
                "连续一字板数量",
                "涨幅",
                "每中一签获利",
            ]
        ]

        big_df["申购日期"] = pd.to_datetime(big_df["申购日期"], errors="coerce").dt.date
        big_df["中签号公布日"] = pd.to_datetime(big_df["中签号公布日"]).dt.date
        big_df["中签缴款日期"] = pd.to_datetime(big_df["中签缴款日期"]).dt.date
        big_df["发行总数"] = pd.to_numeric(big_df["发行总数"], errors="coerce")
        big_df["网上发行"] = pd.to_numeric(big_df["网上发行"], errors="coerce")
        big_df["顶格申购需配市值"] = pd.to_numeric(
            big_df["顶格申购需配市值"], errors="coerce"
        )
        big_df["申购上限"] = pd.to_numeric(big_df["申购上限"], errors="coerce")
        big_df["发行价格"] = pd.to_numeric(big_df["发行价格"], errors="coerce")
        big_df["最新价"] = pd.to_numeric(big_df["最新价"], errors="coerce")
        big_df["首日收盘价"] = pd.to_numeric(big_df["首日收盘价"], errors="coerce")
        big_df["发行市盈率"] = pd.to_numeric(big_df["发行市盈率"], errors="coerce")
        big_df["行业市盈率"] = pd.to_numeric(big_df["行业市盈率"], errors="coerce")
        big_df["中签率"] = pd.to_numeric(big_df["中签率"], errors="coerce")
        big_df["询价累计报价倍数"] = pd.to_numeric(
            big_df["询价累计报价倍数"], errors="coerce"
        )
        big_df["配售对象报价家数"] = pd.to_numeric(
            big_df["配售对象报价家数"], errors="coerce"
        )
        big_df["涨幅"] = pd.to_numeric(big_df["涨幅"], errors="coerce")
        big_df["每中一签获利"] = pd.to_numeric(big_df["每中一签获利"], errors="coerce")
    
    # 过滤掉北交所的股票（股票代码以8开头）
    # 只保留0字头、6字头、3字头的股票
    big_df = big_df[big_df["股票代码"].str.startswith(("0", "6", "3"))]
    return big_df



def bond_zh_cov() -> pd.DataFrame:
    current_date = datetime.now().strftime('%Y-%m-%d')
    """
    东方财富网-数据中心-新股数据-可转债数据
    https://data.eastmoney.com/kzz/default.html
    :return: 可转债数据
    :rtype: pandas.DataFrame
    """
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        "sortColumns": "PUBLIC_START_DATE",
        "sortTypes": "-1",
        "pageSize": "1",
        "pageNumber": "1",
        "reportName": "RPT_BOND_CB_LIST",
        "columns": "ALL",
        "quoteColumns": "f2~01~CONVERT_STOCK_CODE~CONVERT_STOCK_PRICE,"
        "f235~10~SECURITY_CODE~TRANSFER_PRICE,f236~10~SECURITY_CODE~TRANSFER_VALUE,"
        "f2~10~SECURITY_CODE~CURRENT_BOND_PRICE,f237~10~SECURITY_CODE~TRANSFER_PREMIUM_RATIO,"
        "f239~10~SECURITY_CODE~RESALE_TRIG_PRICE,f240~10~SECURITY_CODE~REDEEM_TRIG_PRICE,"
        "f23~01~CONVERT_STOCK_CODE~PBV_RATIO",
        "source": "WEB",
        "client": "WEB",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    total_page = 5
    big_df = pd.DataFrame()
    for page in range(1, total_page + 1):
        params.update({"pageNumber": page})
        r = requests.get(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["result"]["data"])
        big_df = pd.concat(objs=[big_df, temp_df], ignore_index=True)

    big_df.columns = [
        "债券代码",
        "_",
        "_",
        "债券简称",
        "_",
        "上市时间",
        "正股代码",
        "_",
        "信用评级",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "发行规模",
        "申购上限",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "申购代码",
        "_",
        "申购日期",
        "_",
        "_",
        "中签号发布日",
        "原股东配售-股权登记日",
        "正股简称",
        "原股东配售-每股配售额",
        "_",
        "中签率",
        "-",
        "_",
        "_",
        "_",
        "_",
        "_",
        "正股价",
        "转股价",
        "转股价值",
        "债现价",
        "转股溢价率",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
    ]
    big_df = big_df[
        [
            "债券代码",
            "债券简称",
            "申购日期",
            "申购代码",
            "申购上限",
            "正股代码",
            "正股简称",
            "正股价",
            "转股价",
            "转股价值",
            "债现价",
            "转股溢价率",
            "原股东配售-股权登记日",
            "原股东配售-每股配售额",
            "发行规模",
            "中签号发布日",
            "中签率",
            "上市时间",
            "信用评级",
        ]
    ]

    big_df["申购上限"] = pd.to_numeric(big_df["申购上限"], errors="coerce")
    big_df["正股价"] = pd.to_numeric(big_df["正股价"], errors="coerce")
    big_df["转股价"] = pd.to_numeric(big_df["转股价"], errors="coerce")
    big_df["转股价值"] = pd.to_numeric(big_df["转股价值"], errors="coerce")
    big_df["债现价"] = pd.to_numeric(big_df["债现价"], errors="coerce")
    big_df["转股溢价率"] = pd.to_numeric(big_df["转股溢价率"], errors="coerce")
    big_df["原股东配售-每股配售额"] = pd.to_numeric(
        big_df["原股东配售-每股配售额"], errors="coerce"
    )
    big_df["发行规模"] = pd.to_numeric(big_df["发行规模"], errors="coerce")
    big_df["中签率"] = pd.to_numeric(big_df["中签率"], errors="coerce")
    big_df["中签号发布日"] = pd.to_datetime(
        big_df["中签号发布日"], errors="coerce"
    ).dt.date
    big_df["上市时间"] = pd.to_datetime(big_df["上市时间"], errors="coerce").dt.date
    big_df["申购日期"] = pd.to_datetime(big_df["申购日期"], errors="coerce").dt.date
    big_df["原股东配售-股权登记日"] = pd.to_datetime(
        big_df["原股东配售-股权登记日"], errors="coerce"
    ).dt.date
    big_df["债现价"] = big_df["债现价"].fillna(100)
    

    
    big_df = big_df.loc[big_df['申购日期'] == pd.to_datetime(current_date)]
    
    
    return big_df


def fetch_paginated_data(url: str, base_params: Dict, timeout: int = 15):
    """
    东方财富-分页获取数据并合并结果
    https://quote.eastmoney.com/f1.html?newcode=0.000001
    :param url: 股票代码
    :type url: str
    :param base_params: 基础请求参数
    :type base_params: dict
    :param timeout: 请求超时时间
    :type timeout: str
    :return: 合并后的数据
    :rtype: pandas.DataFrame
    """
    # 复制参数以避免修改原始参数
    params = base_params.copy()
    # 获取第一页数据，用于确定分页信息
    r = requests.get(url, params=params, timeout=timeout)
    data_json = r.json()
    # 计算分页信息
    per_page_num = len(data_json["data"]["diff"])
    total_page = math.ceil(data_json["data"]["total"] / per_page_num)
    # 存储所有页面数据
    temp_list = []
    # 添加第一页数据
    temp_list.append(pd.DataFrame(data_json["data"]["diff"]))
    # 获取剩余页面数据
    for page in range(2, total_page + 1):
        params.update({"pn": page})
        r = requests.get(url, params=params, timeout=timeout)
        data_json = r.json()
        inner_temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_list.append(inner_temp_df)
    # 合并所有数据
    temp_df = pd.concat(temp_list, ignore_index=True)
    temp_df["f3"] = pd.to_numeric(temp_df["f3"], errors="coerce")
    temp_df.sort_values(by=["f3"], ascending=False, inplace=True, ignore_index=True)
    temp_df.reset_index(inplace=True)
    temp_df["index"] = temp_df["index"].astype(int) + 1
    return temp_df


def stock_zh_a_st_em() -> pd.DataFrame:
    """
    东方财富网-行情中心-沪深个股-风险警示板
    https://quote.eastmoney.com/center/gridlist.html#st_board
    :return: 风险警示板
    :rtype: pandas.DataFrame
    """
    url = "https://40.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 f:4,m:1 f:4",
        "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,"
        "f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
    }
    temp_df = fetch_paginated_data(url, params)
    temp_df.columns = [
        "序号",
        "最新价",
        "涨跌幅",
        "涨跌额",
        "成交量",
        "成交额",
        "振幅",
        "换手率",
        "市盈率-动态",
        "量比",
        "_",
        "代码",
        "_",
        "名称",
        "最高",
        "最低",
        "今开",
        "昨收",
        "_",
        "_",
        "_",
        "市净率",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
    ]
    temp_df = temp_df[
        [
            "序号",
            "代码",
            "名称",
            "最新价",
            "涨跌幅",
            "涨跌额",
            "成交量",
            "成交额",
            "振幅",
            "最高",
            "最低",
            "今开",
            "昨收",
            "量比",
            "换手率",
            "市盈率-动态",
            "市净率",
        ]
    ]
    temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
    temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
    temp_df["成交量"] = pd.to_numeric(temp_df["成交量"], errors="coerce")
    temp_df["成交额"] = pd.to_numeric(temp_df["成交额"], errors="coerce")
    temp_df["振幅"] = pd.to_numeric(temp_df["振幅"], errors="coerce")
    temp_df["最高"] = pd.to_numeric(temp_df["最高"], errors="coerce")
    temp_df["最低"] = pd.to_numeric(temp_df["最低"], errors="coerce")
    temp_df["今开"] = pd.to_numeric(temp_df["今开"], errors="coerce")
    temp_df["量比"] = pd.to_numeric(temp_df["量比"], errors="coerce")
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
    return temp_df


async def fetch_single_page(
    session: aiohttp.ClientSession, url: str, params: Dict
) -> Dict:
    """异步获取单页数据"""
    async with session.get(url, params=params, ssl=False) as response:
        return await response.json()


async def fetch_all_pages_async(url: str, base_params: Dict) -> List[Dict]:
    """异步获取所有页面数据"""
    # 首先获取总数以计算页数
    first_page_params = base_params.copy()
    first_page_params["pn"] = "1"

    async with aiohttp.ClientSession() as session:
        first_page_data = await fetch_single_page(session, url, first_page_params)

        # 检查是否成功获取数据
        if first_page_data.get("rc") != 0 or not first_page_data.get("data"):
            return [first_page_data]  # 返回错误信息

        total = first_page_data["data"]["total"]
        page_size = int(base_params["pz"])
        total_pages = (total + page_size - 1) // page_size

        # 限制页数，避免过大请求
        total_pages = min(total_pages, 100)

        # 创建所有页面的任务
        tasks = []
        for page in range(1, total_pages + 1):
            page_params = base_params.copy()
            page_params["pn"] = str(page)
            tasks.append(fetch_single_page(session, url, page_params))

        # 并发执行所有任务
        results = await asyncio.gather(*tasks)
        return results


def process_data(page_results: List[Dict]) -> pd.DataFrame:
    """处理获取到的数据，转换为DataFrame"""
    all_data = []

    # 保存每个页面的结果和页码
    page_number = 1
    items_per_page = 100  # 假设每页100条

    for result in page_results:
        if result.get("rc") == 0 and result.get("data") and result["data"].get("diff"):
            page_data = result["data"]["diff"]
            for item in page_data:
                item["page_number"] = page_number
                item["page_index"] = page_data.index(item)
            all_data.extend(page_data)
            page_number += 1
    if not all_data:
        return pd.DataFrame()
    df = pd.DataFrame(all_data)
    df["序号"] = df.apply(
        lambda row: (row["page_number"] - 1) * items_per_page + row["page_index"] + 1,
        axis=1,
    )
    df.drop(columns=["page_number", "page_index"], inplace=True, errors="ignore")
    column_map = {
        "f1": "原序号",
        "f2": "最新价",
        "f3": "涨跌幅",
        "f4": "涨跌额",
        "f5": "成交量",
        "f6": "成交额",
        "f7": "振幅",
        "f8": "换手率",
        "f9": "市盈率-动态",
        "f10": "量比",
        "f11": "5分钟涨跌",
        "f12": "代码",
        "f13": "_",
        "f14": "名称",
        "f15": "最高",
        "f16": "最低",
        "f17": "今开",
        "f18": "昨收",
        "f20": "总市值",
        "f21": "流通市值",
        "f22": "涨速",
        "f23": "市净率",
        "f24": "60日涨跌幅",
        "f25": "年初至今涨跌幅",
        "f62": "-",
        "f115": "-",
        "f128": "-",
        "f136": "-",
        "f152": "-",
    }

    df.rename(columns=column_map, inplace=True)
    desired_columns = [
        "序号",
        "代码",
        "名称",
        "最新价",
        "涨跌幅",
        "涨跌额",
        "成交量",
        "成交额",
        "振幅",
        "最高",
        "最低",
        "今开",
        "昨收",
        "量比",
        "换手率",
        "市盈率-动态",
        "市净率",
        "总市值",
        "流通市值",
        "涨速",
        "5分钟涨跌",
        "60日涨跌幅",
        "年初至今涨跌幅",
    ]
    available_columns = [col for col in desired_columns if col in df.columns]
    df = df[available_columns]
    numeric_columns = [
        "最新价",
        "涨跌幅",
        "涨跌额",
        "成交量",
        "成交额",
        "振幅",
        "最高",
        "最低",
        "今开",
        "昨收",
        "量比",
        "换手率",
        "市盈率-动态",
        "市净率",
        "总市值",
        "流通市值",
        "涨速",
        "5分钟涨跌",
        "60日涨跌幅",
        "年初至今涨跌幅",
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_values(by="涨跌幅", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["序号"] = df.index + 1
    return df


async def stock_zh_a_spot_em_async() -> pd.DataFrame:
    """
    异步获取东方财富网-沪深京 A 股-实时行情
    https://quote.eastmoney.com/center/gridlist.html#hs_a_board
    :return: 实时行情
    :rtype: pandas.DataFrame
    """
    url = "https://82.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f12",
        "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
        "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,"
        "f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
    }
    results = await fetch_all_pages_async(url, params)
    return process_data(results)


def stock_zh_a_spot_em() -> pd.DataFrame:
    return asyncio.run(stock_zh_a_spot_em_async())


def query_all_stock_by_day(day: str = "") -> pd.DataFrame:
    """
    使用 baostock 查询指定交易日的全部证券信息。
    返回字段通常包含: code, tradeStatus, code_name
    """
    lg = bs.login()
    print("login respond error_code:" + lg.error_code)
    print("login respond  error_msg:" + lg.error_msg)

    try:
        rs = bs.query_all_stock(day=day)
        print("query_all_stock respond error_code:" + rs.error_code)
        print("query_all_stock respond  error_msg:" + rs.error_msg)

        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())
        return pd.DataFrame(data_list, columns=rs.fields)
    finally:
        bs.logout()


def query_st_stock_daily_by_day(day: str = "") -> pd.DataFrame:
    """
    使用 baostock 获取指定交易日的 ST 股票列表，并补充对应日线字段。
    返回字段包含:
    updateDate, date, code, code_name, open, high, low, close, preclose,
    volume, amount, turn, pctChg, peTTM, pbMRQ, isST
    """
    from baostock.security.sectorinfo import query_st_stocks

    lg = bs.login()
    print("login respond error_code:" + lg.error_code)
    print("login respond  error_msg:" + lg.error_msg)

    try:
        st_rs = query_st_stocks(date=day)
        print("query_st_stocks respond error_code:" + st_rs.error_code)
        print("query_st_stocks respond  error_msg:" + st_rs.error_msg)

        st_rows = []
        while (st_rs.error_code == "0") & st_rs.next():
            st_rows.append(st_rs.get_row_data())
        st_df = pd.DataFrame(st_rows, columns=st_rs.fields)
        if st_df.empty:
            return st_df

        history_fields = (
            "date,code,open,high,low,close,preclose,volume,amount,"
            "turn,pctChg,peTTM,pbMRQ,isST"
        )
        result_rows = []
        for _, st_row in st_df.iterrows():
            code = st_row.get("code", "")
            history_rs = bs.query_history_k_data_plus(
                code,
                history_fields,
                start_date=day,
                end_date=day,
                frequency="d",
                adjustflag="3",
            )

            history_rows = []
            while (history_rs.error_code == "0") & history_rs.next():
                history_rows.append(history_rs.get_row_data())

            if history_rows:
                history_df = pd.DataFrame(history_rows, columns=history_rs.fields)
                history_item = history_df.iloc[0].to_dict()
                history_item["updateDate"] = st_row.get("updateDate")
                history_item["code_name"] = st_row.get("code_name")
                result_rows.append(history_item)
            else:
                result_rows.append(
                    {
                        "updateDate": st_row.get("updateDate"),
                        "date": day,
                        "code": code,
                        "code_name": st_row.get("code_name"),
                        "open": None,
                        "high": None,
                        "low": None,
                        "close": None,
                        "preclose": None,
                        "volume": None,
                        "amount": None,
                        "turn": None,
                        "pctChg": None,
                        "peTTM": None,
                        "pbMRQ": None,
                        "isST": "1",
                    }
                )

        return pd.DataFrame(result_rows)
    finally:
        bs.logout()

if __name__ == "__main__":
    stock_zh_a_spot_em_df = stock_zh_a_spot_em()
    print(stock_zh_a_spot_em_df)
    # stock_zh_a_st_em()
