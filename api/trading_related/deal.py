from pyapp.pkg.xtquant import xtconstant
import re
from api.global_params import G

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
    stockDic = {
        "security":security,
        "is_st":security in G.stock_map["st_stock_code"]    
    }
    return stockDic

def get_qmt_price_type(security, order_style_str, is_buy=True):
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
    if is_st and is_buy == False and is_zhishu:
        G.logger.warning("ST股票，且是卖出类型 且是上海股票，最新价报单")
        return xtconstant.LATEST_PRICE
    
    
    # 解析订单类型字符串
    if not order_style_str:
        # 默认为市价单
        order_type = 'MarketOrderStyle'
        limit_price = None
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
    
    # 处理限价单
    if order_type == 'LimitOrderStyle':
        return xtconstant.FIX_PRICE
    
    # 处理市价单
    elif order_type == 'MarketOrderStyle':
        
        # 科创板特殊处理
        if is_kcb and limit_price is not None:
            return xtconstant.MARKET_SH_CONVERT_5_CANCEL
        
        # 上交所/北交所股票
        else:
            return xtconstant.MARKET_PEER_PRICE_FIRST

        
    
    # 默认使用最新价
    return xtconstant.LATEST_PRICE


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