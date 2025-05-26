from pyapp.pkg.xtquant import xtconstant
import re


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


def get_qmt_price_type(security, order_style_str):
    # 提取交易所代码
    exchange = security.split('.')[-1]
    is_kcb = security.startswith('688') and exchange == 'SH'  # 是否为科创板
    
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

