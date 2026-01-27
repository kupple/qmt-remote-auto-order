from pyapp.pkg.xtquant import xtconstant
import re
from api.global_params import G
from datetime import datetime

def is_auction_period(stock_code: str, check_time: datetime = None) -> bool:
    """
    判断给定时间是否为股票集合竞价时间
    
    参数:
    stock_code (str): 股票代码，用于识别股票所属板块
    check_time (datetime.datetime): 需要判断的时间点，默认为当前时间
    
    返回:
    bool: True表示处于集合竞价时间，False表示不处于
    """
    # 如果未传入时间，使用当前时间
    if check_time is None:
        check_time = datetime.now()
    
    # 判断股票所属板块
    is_main_board = not (stock_code.startswith(("688", "689")) or  # 非科创板
                         stock_code.startswith(("300", "301")) or  # 非创业板
                         stock_code.startswith(("8", "4")))        # 非北交所
    is_science_innovation = stock_code.startswith(("688", "689"))  # 科创板
    is_gem = stock_code.startswith(("300", "301"))  # 创业板
    is_north = stock_code.startswith(("8", "4"))  # 北交所
    
    # 检查是否为交易日（简单判断：周一至周五）
    if check_time.weekday() >= 5:  # 5是周六，6是周日
        return False
    
    # 初始化开盘集合竞价和收盘集合竞价的时间范围
    morning_auction_start = datetime.time(9, 15)
    morning_auction_end = datetime.time(9, 25)
    afternoon_auction_start = datetime.time(14, 57)
    afternoon_auction_end = datetime.time(15, 0)
    
    # 检查时间是否在开盘集合竞价范围内
    morning_check = (check_time.time() >= morning_auction_start) and (check_time.time() <= morning_auction_end)
    
    # 检查时间是否在收盘集合竞价范围内
    afternoon_check = False
    
    # 区分不同板块的收盘集合竞价规则
    if is_main_board:
        # 主板：沪市无收盘集合竞价，深市有
        # 简化处理：假设60开头为沪市，00/30开头为深市
        if stock_code.startswith("60"):
            afternoon_check = False  # 沪市无收盘集合竞价
        else:
            afternoon_check = (check_time.time() >= afternoon_auction_start) and (check_time.time() <= afternoon_auction_end)
    elif is_science_innovation or is_gem or is_north:
        # 科创板、创业板、北交所：有收盘集合竞价
        afternoon_check = (check_time.time() >= afternoon_auction_start) and (check_time.time() <= afternoon_auction_end)
    
    return morning_check or afternoon_check


def calculate_max_possible_price(stock_code: str, previous_close: float, current_price: float,
                                direction: str, is_st: bool = False, auction_period: bool = False,need_limit_up_count = False) -> float:
    """
    计算在当前规则下允许的最大可能成交价格
    
    参数:
    stock_code (str): 股票代码
    previous_close (float): 前一日收盘价
    current_price (float): 当前最新成交价
    direction (str): 交易方向，'buy' 或 'sell'
    is_st (bool): 是否为ST股票，默认为False
    auction_period (bool): 是否为集合竞价阶段，默认为False
    
    返回:
    float: 最大可能成交价格（买入方向）或最小可能成交价格（卖出方向）
    """
    # 计算涨停价和跌停价
    limit_up, limit_down = calculate_price_limits(stock_code, previous_close, is_st)
    
    # 判断股票板块
    is_main_board = not (stock_code.startswith(("688", "689")) or  # 非科创板
                         stock_code.startswith(("300", "301")) or  # 非创业板
                         stock_code.startswith(("8", "4")))        # 非北交所
    is_science_innovation = stock_code.startswith(("688", "689"))  # 科创板
    is_gem = stock_code.startswith(("300", "301"))  # 创业板
    is_star = stock_code.startswith(("8", "4"))  # 北交所
    
    # 初始化价格笼子上下限
    cage_upper = float('inf')
    cage_lower = float('-inf')
    
    # 根据板块和交易时段设置价格笼子
    if is_science_innovation or is_gem:
        # 科创板和创业板：全天有价格笼子
        cage_upper = round(current_price * 1.01, 2)
        cage_lower = round(current_price * 0.99, 2)
    elif is_star and not auction_period:
        # 北交所：连续竞价有价格笼子
        cage_upper = round(current_price * 1.03, 2)
        cage_lower = round(current_price * 0.97, 2)
    elif is_main_board and not auction_period:
        # 主板：连续竞价有价格笼子（修正逻辑）
        cage_upper = round(current_price * 1.01, 2)
        cage_lower = round(current_price * 0.99, 2)
    else:
        cage_upper = round(current_price * 1.01, 2)
        cage_lower = round(current_price * 0.99, 2)
    
    if need_limit_up_count == True:
        # 应用涨跌停限制和价格笼子
        if direction.lower() == 'buy':
            # 买入方向：最终价格为 价格笼子上限 和 涨停价 的较小值
            final_price = min(limit_up, cage_upper)
            print(limit_up, cage_upper)
            return round(final_price, 2)
        elif direction.lower() == 'sell':
            # 卖出方向：最终价格为 价格笼子下限 和 跌停价 的较大值
            final_price = max(limit_down, cage_lower)
            return round(final_price, 2)
        else:
            raise ValueError("交易方向必须是 'buy' 或 'sell'")
    else:
        if direction.lower() == 'buy':
            return round(cage_upper, 2)
        elif direction.lower() == 'sell':
            return round(cage_lower, 2)
        else:
            raise ValueError("交易方向必须是 'buy' 或 'sell'")

def calculate_price_limits(stock_code: str, previous_close: float, is_st: bool) -> tuple[float, float]:
    """
    计算股票的涨停价和跌停价
    
    参数:
    stock_code (str): 股票代码
    previous_close (float): 前一日收盘价
    is_st (bool): 是否为ST股票
    
    返回:
    tuple[float, float]: 涨停价和跌停价
    """
    # 判断股票板块
    is_main_board = not (stock_code.startswith(("688", "689")) or  # 非科创板
                         stock_code.startswith(("300", "301")) or  # 非创业板
                         stock_code.startswith(("8", "4")))        # 非北交所
    is_science_innovation = stock_code.startswith(("688", "689"))  # 科创板
    is_gem = stock_code.startswith(("300", "301"))  # 创业板
    is_star = stock_code.startswith(("8", "4"))  # 北交所
    
    # 根据板块和ST状态确定涨跌幅限制
    if is_main_board:
        limit_ratio = 0.05 if is_st else 0.10  # 主板ST股票±5%，非ST股票±10%
    elif is_science_innovation or is_gem:
        limit_ratio = 0.20  # 科创板和创业板±20%
    elif is_star:
        limit_ratio = 0.30  # 北交所±30%
    else:
        limit_ratio = 0.10  # 默认±10%
    
    # 计算涨停价和跌停价
    limit_up = round(previous_close * (1 + limit_ratio), 2)
    limit_down = round(previous_close * (1 - limit_ratio), 2)
    
    return limit_up, limit_down



def calculate_stock_fee(
    transaction_type: str,  # 'buy' 或 'sell'
    stock_price: float,     # 股票单价
    quantity: int,          # 交易数量
    commission_rate: float = 0.0003,  # 佣金率，默认0.03%
    min_commission: float = 5.0,      # 最低佣金，默认5元
    stamp_duty_rate: float = 0.001,   # 印花税率，默认0.1%（卖出时收取）
) -> float:
    """
    计算股票交易手续费，返回总费用
    
    参数:
        transaction_type: 交易类型，'buy' 表示买入，'sell' 表示卖出
        stock_price: 股票单价
        quantity: 交易数量
        commission_rate: 佣金率，默认0.03%
        min_commission: 最低佣金，默认5元
        stamp_duty_rate: 印花税率，默认0.1%（卖出时收取）
    
    返回:
        float: 总手续费金额
    """
    turnover = stock_price * quantity
    
    # 计算佣金（不足最低标准时按最低标准收取）
    commission = max(turnover * commission_rate, min_commission)
    
    # 计算印花税（仅卖出时收取）
    stamp_duty = turnover * stamp_duty_rate if transaction_type == 'sell' else 0
    
    # 返回总费用
    return commission + stamp_duty


# 将聚宽代码转成qmt
def convert_stock_suffix(stock_code: str) -> str:
    """
    转换股票代码后缀，支持处理无后缀的股票代码
    
    参数:
    stock_code (str): 原始股票代码，如 "600519"、"600519.XSHG" 或 "002719.XSHE"
    
    返回:
    str: 转换后的股票代码，如 "600519.SH" 或 "002719.SZ"
    """
    # 检查是否有后缀
    if '.' not in stock_code:
        # 根据股票代码前缀判断交易所
        if stock_code.startswith(('0', '3', '2')):  # 深市股票代码前缀
            return f"{stock_code}.SZ"
        elif stock_code.startswith(('6', '9','7')):  # 沪市股票代码前缀
            return f"{stock_code}.SH"
        else:
            return stock_code  # 无法判断交易所，返回原代码
    
    # 处理有后缀的情况
    parts = stock_code.rsplit('.', 1)
    if len(parts) != 2:
        return stock_code  # 格式不符合预期，直接返回原代码
    
    code, exchange = parts
    
    # 转换交易所代码
    if exchange.upper() == 'XSHG':
        return f"{code}.SH"
    elif exchange.upper() == 'XSHE':
        return f"{code}.SZ"
    else:
        return stock_code  # 非目标交易所，返回原代码


# 拼装股票代码
def stockcode_mapping_dic(security):
    # {'id': 788, 'code': '600031', 'name': '三一重工', 'latest_price': 18.03, 'change_rate': 1.24, 'change_amount': 0.22, 'volume': 462329.0, 'turnover': 834199896.0, 'amplitude': 1.63, 'highest': 18.17, 'lowest': 17.88, 'open': 17.89, 'close': 17.81, 'volume_ratio': 1.44, 'turnover_ratio': 0.55, 'pe_dynamic': 15.46, 'pb': 2.13, 'total_market_value': 152803854007.0, 'circulating_market_value': 152609811541.0, 'rise_speed': -0.06, 'five_minute_change': 0.06, 'sixty_days_change': -7.82, 'year_to_date_change': 11.85, 'created_at': '2025-06-17 16:46:35', 'updated_at': '2025-06-17 16:46:35'}
    stockDic = {
        "security":security,
        "is_st":security in G.stock_map["st_stock_code"]
    }
    return stockDic

# 按比率买卖股票
def count_stock_price(security,price,is_buy,is_mock_state = 0):
    # 获取上一个收盘价格
    try:
        is_data_synced = G.stock_map["is_data_synced"]
        is_st = security in G.stock_map["st_stock_code"]
        close = G.stock_map["all_stock_code"][security]["close"]

        # 如果数据未同步，使用最新价
        optimal_price = calculate_max_possible_price(
            security, 
            close, 
            price,
            "buy" if is_buy else "sell",
            is_st,
            False,
            is_data_synced and is_mock_state == 0, #同步完就True 否则不判断涨停
        )
        return optimal_price
    except Exception as _exc:
        if is_buy:
            cage_upper = round(price * 1.01, 2)
            return cage_upper
        else:
            cage_lower = round(price * 0.99, 2)
            return cage_lower
       
    
def get_qmt_price_type(security, order_style_str, is_buy=True, price=0, open_mandatory_limit_order=0,is_mock_state = 0):
    # 提取交易所代码
    exchange = security.split('.')[-1]
    cleanCode = security.split('.')[0]
    stockDic = stockcode_mapping_dic(cleanCode)
    # 是否为科创板
    is_kcb = security.startswith('688') and exchange == 'SH'  
    # 是否为普通主板
    is_zhishu = exchange == 'SH' and security[0] == '6' and security[1:3] != '88'
    
    #是否为ST
    is_st = stockDic['is_st'] 
    
    # 如果是ST股票，且是卖出类型 且是上海股票
    if is_st and is_zhishu:
        # G.logger.warning("上海ST股票，使用最新价报单")
        optimal_price = count_stock_price(security,price,is_buy,is_mock_state)
        return xtconstant.LATEST_PRICE,optimal_price
    
    
    #判断order_style_str是否是int类型
    #判断order_style_str是否是int类型
    order_type = 'MarketOrderStyle'
    limit_price = None
    if type(order_style_str) == int:
        if order_style_str == 1:
            order_type = 'MarketOrderStyle'
            limit_price = None
        elif order_style_str == 2:
            order_type = 'LimitOrderStyle'
            limit_price = price
    else:
        # 解析订单类型字符串
        if not order_style_str:
            # 默认为市价单
            order_type = 'MarketOrderStyle'
        else:
            # 使用正则表达式解析订单类型和参数
            match = re.match(r'(\w+)\((.*)\)', order_style_str.strip())
            if not match:
                # 无法解析，默认为市价单
                order_type = 'MarketOrderStyle'
                limit_price = None
            else:
                order_type = match.group(1)
                param = match.group(2).strip()
                limit_price = float(param) if param else None


    if open_mandatory_limit_order == 1:
        optimal_price = count_stock_price(security,price,is_buy,is_mock_state)
        # 默认使用最新价
        return xtconstant.FIX_PRICE,optimal_price
    
    # 处理限价单
    if order_type == 'LimitOrderStyle':
        return xtconstant.FIX_PRICE,price
    
    # 处理市价单
    elif order_type == 'MarketOrderStyle':
        
        # 科创板特殊处理
        if is_kcb and limit_price is not None:
            return xtconstant.MARKET_SH_CONVERT_5_CANCEL,price
        
        # 上交所/北交所股票
        else:
            return xtconstant.MARKET_PEER_PRICE_FIRST,price

    
    optimal_price = count_stock_price(security,price,is_buy)
    # 默认使用最新价
    return xtconstant.LATEST_PRICE,optimal_price


def calculate_dividend_effect(
    security_code: str,
    holding_shares: int,
    purchase_price: float,
    bonus_pre_tax: float,
    scale_factor: float,
    tax_rate: float = 0.2,  # 默认红利税20%
    ex_dividend_price: float = None  # 除权除息价（可选）
) -> dict:
    """
    计算股票分红对持仓的影响
    
    参数:
        security_code: 股票代码
        holding_shares: 分红前持有股数
        purchase_price: 买入价格
        bonus_pre_tax: 每股税前分红金额
        scale_factor: 送股比例（如1.2表示每股送1.2股）
        tax_rate: 红利税税率
        ex_dividend_price: 除权除息价（若未提供则自动计算）
    
    返回:
        dict: 包含分红前后持仓变化的详细信息
    """
    # 计算送股后的总股数
    total_shares = int(holding_shares * scale_factor)
    
    # 计算税前和税后现金分红
    cash_dividend_pre_tax = holding_shares * bonus_pre_tax
    tax_amount = cash_dividend_pre_tax * tax_rate
    cash_dividend_after_tax = cash_dividend_pre_tax - tax_amount
    
    # 计算除权除息价（如果未提供）
    if ex_dividend_price is None:
        ex_dividend_price = (purchase_price - bonus_pre_tax) / (1 + scale_factor)
    
    # 计算分红前后的市值
    market_value_before = holding_shares * purchase_price
    market_value_after = total_shares * ex_dividend_price
    total_value_after = market_value_after + cash_dividend_after_tax
    
    # 计算持仓成本变化
    original_cost = holding_shares * purchase_price
    new_cost_per_share = original_cost / total_shares
    
    return {
        "security_code": security_code,
        "holding_shares_before": holding_shares,
        "purchase_price": purchase_price,
        "market_value_before": market_value_before,
        
        "bonus_pre_tax": bonus_pre_tax,
        "scale_factor": scale_factor,
        "tax_rate": tax_rate,
        
        "new_shares": total_shares,
        "cash_dividend_pre_tax": cash_dividend_pre_tax,
        "tax_amount": tax_amount,
        "cash_dividend_after_tax": cash_dividend_after_tax,
        
        "ex_dividend_price": ex_dividend_price,
        "market_value_after": market_value_after,
        "total_value_after": total_value_after,
        "new_cost_per_share": new_cost_per_share,
        
        "value_change": total_value_after - market_value_before,
        "cost_change_percentage": (new_cost_per_share / purchase_price - 1) * 100
    }
    
    

# 计算平均成本
def calculate_average_price(
    previous_avg_price: float,
    previous_quantity: int,
    traded_price: float,
    traded_volume: int
) -> float:
    """
    计算股票的平均成本（均价）
    
    参数:
    previous_avg_price (float): 上一次保存的平均均价
    previous_quantity (int): 上一次的仓位数量
    traded_price (float): 本次交易价格
    traded_volume (int): 本次交易数量(买入为正，卖出为负)
    
    返回:
    float: 新的平均均价
    """
    # 计算交易后的总数量
    new_quantity = previous_quantity + traded_volume
    
    # 处理全部卖出的情况：均价重置为0
    if new_quantity == 0:
        return 0.0
    
    # 计算交易后的总价值
    # 注意：卖出时 traded_volume 为负，总价值会减少
    total_value = previous_avg_price * previous_quantity + traded_price * traded_volume
    
    # 计算新的平均成本
    return total_value / new_quantity
