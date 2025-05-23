# 将聚宽代码转成qmt
def convert_stock_suffix(stock_code: str) -> str:
    """
    转换股票代码后缀，将交易所代码从 XSHG/XSHE 转为 SH/SZ
    
    参数:
    stock_code (str): 原始股票代码，如 "600519.XSHG" 或 "002719.XSHE"
    
    返回:
    str: 转换后的股票代码，如 "600519.SH" 或 "002719.SZ"
    """
    # 分割股票代码和后缀
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