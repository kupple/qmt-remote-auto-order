import pandas as pd
import requests
from datetime import datetime
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
