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

# 示例用法
if __name__ == "__main__":
    # 初始状态：100股，均价10元
    prev_avg = 10.0
    prev_qty = 100
    
    # 买入50股，价格12元
    buy_volume = 50
    buy_price = 10.0
    new_avg = calculate_average_price(prev_avg, prev_qty, buy_price, buy_volume)
    prev_qty += buy_volume
    print(f"买入后: 均价={new_avg:.2f} 元, 数量={prev_qty} 股")
    
    # 卖出60股，价格15元
    sell_volume = -50
    sell_price = 20.0
    new_avg = calculate_average_price(new_avg, prev_qty, sell_price, sell_volume)
    prev_qty += sell_volume
    print(f"卖出后: 均价={new_avg:.2f} 元, 数量={prev_qty} 股")
    
    # # 再买入20股，价格8元
    # buy_volume2 = 20
    # buy_price2 = 8.0
    # new_avg = calculate_average_price(new_avg, prev_qty, buy_price2, buy_volume2)
    # prev_qty += buy_volume2
    # print(f"再次买入后: 均价={new_avg:.2f} 元, 数量={prev_qty} 股")