from pyapp.pkg.xtquant import xtconstant
import re


def calculate_stock_fee(
    transaction_type: str,  # 'buy' 或 'sell'
    stock_price: float,     # 股票单价
    quantity: int,          # 交易数量
    commission_rate: float = 0.0003,  # 佣金率，默认0.03%
    min_commission: float = 5.0,      # 最低佣金，默认5元
    stamp_duty_rate: float = 0.001,   # 印花税率，默认0.1%（卖出时收取）
    transfer_fee_rate: float = 0.00001  # 过户费率，默认0.001%
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
        transfer_fee_rate: 过户费率，默认0.001%
    
    返回:
        float: 总手续费金额
    """
    turnover = stock_price * quantity
    
    # 计算佣金（不足最低标准时按最低标准收取）
    commission = max(turnover * commission_rate, min_commission)
    
    # 计算印花税（仅卖出时收取）
    stamp_duty = turnover * stamp_duty_rate if transaction_type == 'sell' else 0
    
    # 计算过户费
    transfer_fee = turnover * transfer_fee_rate
    
    # 返回总费用
    return commission + stamp_duty + transfer_fee

# 示例用法
if __name__ == "__main__":
    # 买入示例：单价10元，买入1000股，佣金率0.03%
    buy_result = calculate_stock_fee('buy', 10, 1000)
    print("买入费用计算结果:")
    for key, value in buy_result.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
    
    print("\n------------------------\n")
    
    # 卖出示例：单价15元，卖出1000股，佣金率0.03%
    sell_result = calculate_stock_fee('sell', 15, 1000)
    print("卖出费用计算结果:")
    for key, value in sell_result.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")

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

