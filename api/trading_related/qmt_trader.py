
from pyapp.pkg.xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from pyapp.pkg.xtquant.xttype import StockAccount
from pyapp.pkg.xtquant import xtconstant
import random
import pandas as pd
import math
from .qmt_data import qmt_data
from .deal import get_qmt_price_type





class qmt_trader:
 def __init__(self,path= r'D:/国金QMT交易端模拟/userdata_mini',
    account='55009640',account_type='STOCK',
    is_slippage=True,slippage=0.01) -> None:
  self.xt_trader=''
  self.acc=''
  self.path=path
  self.session_id=int(self.random_session_id())
  self.account=account
  self.account_type=account_type
  if is_slippage==True:
   self.slippage=slippage
  else:
   self.slippage=0
  self.data=qmt_data()
 def select_slippage(self,stock='600031',price=15.01,trader_type='buy'):
  '''
  选择滑点
  安价格来滑点，比如0.01就是一块
  etf3位数,股票可转债2位数
  '''
  stock=self.adjust_stock(stock=stock)
  data_type=self.select_data_type(stock=stock)
  if data_type=='fund' or data_type=='bond':
   slippage=self.slippage/10
   if trader_type=='buy' or trader_type==23:
    price=price+slippage
   else:
    price=price-slippage
  else:
   slippage=self.slippage
   if trader_type=='buy' or trader_type==23:
    price=price+slippage
   else:
    price=price-slippage
  return price
 def adjust_stock(self,stock='600031.SH'):
  '''
  调整代码
  '''
  if stock[-2:]=='SH' or stock[-2:]=='SZ' or stock[-2:]=='sh' or stock[-2:]=='sz':
   stock=stock.upper()
  else:
   if stock[:3] in ['600','601','603','688','510','511',
       '512','513','515','113','110','118','501'] or stock[:2] in ['11']:
    stock=stock+'.SH'
   else:
    stock=stock+'.SZ'
  return stock

 def random_session_id(self):
  '''
  随机id
  '''
  session_id=''
  for i in range(0,9):
   session_id+=str(random.randint(1,9))
  return session_id
 
 def select_data_type(self,stock='600031'):
  '''
  选择数据类型
  '''
  if stock[:3] in ['110','113','123','127','128','111','118']:
   return 'bond'
  elif stock[:3] in ['510','511','512','513','514','515','516','517','518','588','159','501']:
   return 'fund'
  else:
   return 'stock'
   
 def sell(self,security='600031.SH',
     amount=100,order_style_str='',price=20,strategy_name='',order_remark=''):
  '''
  单独独立股票卖出函数
  '''
  
  order_type=xtconstant.STOCK_SELL
  price_type = get_qmt_price_type(security,order_style_str)
  # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
  subscribe_result = self.xt_trader.subscribe(self.acc)
  stock_code =self.adjust_stock(stock=security)
  # price=self.select_slippage(stock=security,price=price,trader_type='sell')
  order_volume=amount
  # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
  if order_volume>0:
   fix_result_order_id = self.xt_trader.order_stock(account=self.acc,stock_code=stock_code, order_type=order_type,
                order_volume=order_volume, price_type=price_type,
                price=price, strategy_name=strategy_name, order_remark=order_remark)
   print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
  #  fix_result_order_id - 1有问题
   return fix_result_order_id
  else:
   print('卖出 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume))   
 
 def place_order(self,security='600031.SH',
     amount=100,price=20,order_type=xtconstant.STOCK_BUY,order_style_str='',strategy_name='',order_remark=''):
     if order_type == xtconstant.STOCK_BUY:
      self.buy(security=security,
      amount=amount,
      price=price,
      order_style_str=order_style_str,
      strategy_name=strategy_name,
      order_remark=order_remark)
     elif order_type == xtconstant.STOCK_SELL:
      self.sell(security=security,
      amount=amount,
      price=price,
      order_style_str=order_style_str,
      strategy_name=strategy_name,
      order_remark=order_remark)  
 
 
 def buy(self,security='600031.SH',
     amount=100,price=20,order_style_str='',strategy_name='',order_remark=''):
  '''
  单独独立股票买入函数
  '''
  order_type = xtconstant.STOCK_BUY
  price_type = get_qmt_price_type(security, order_style_str)
  # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
  subscribe_result = self.xt_trader.subscribe(self.acc)
  stock_code =self.adjust_stock(stock=security)
  # price=self.select_slippage(stock=security,price=price,trader_type='buy')
  order_volume=amount
  # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
  if order_volume>0:
   fix_result_order_id = self.xt_trader.order_stock_async(account=self.acc,stock_code=stock_code, order_type=order_type,
                order_volume=order_volume, price_type=price_type,
                price=price, strategy_name=strategy_name, order_remark=order_remark)
   print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
   return fix_result_order_id
  else:
   print('买入 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume))
  
 def connect(self,callback):
  '''
  连接
  path qmt userdata_min是路径
  session_id 账户的标志,随便
  account账户,
  account_type账户内类型
  '''
  print('链接qmt')
  # path为mini qmt客户端安装目录下userdata_mini路径
  path = self.path
  # session_id为会话编号，策略使用方对于不同的Python策略需要使用不同的会话编号
  session_id = self.session_id
  xt_trader = XtQuantTrader(path, session_id)
  # 创建资金账号为1000000365的证券账号对象
  account=self.account
  account_type=self.account_type
  acc = StockAccount(account_id=account,account_type=account_type)
  # 创建交易回调类对象，并声明接收回调
  
  xt_trader.register_callback(callback)
  # 启动交易线程
  xt_trader.start()
  # 建立交易连接，返回0表示连接成功
  connect_result = xt_trader.connect()
  if connect_result==0:
   # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
   subscribe_result = xt_trader.subscribe(acc)
   print(subscribe_result)
   self.xt_trader=xt_trader
   self.acc=acc
   return True
  else:
   return False


 def balance(self):
  '''
  对接同花顺
  '''
  try:
    asset = self.xt_trader.query_stock_asset(account=self.acc)
    df=pd.DataFrame()
    if asset:
      df['账号类型']=[asset.account_type]
      df['资金账户']=[asset.account_id]
      df['可用金额']=[asset.cash]
      df['冻结金额']=[asset.frozen_cash]
      df['持仓市值']=[asset.market_value]
      df['总资产']=[asset.total_asset]
      return df
  except:
    print('获取账户失败，读取上次数据，谨慎使用')
    df=pd.read_excel(r'账户数据\账户数据.xlsx',dtype='object')
    try:
      del df['Unnamed: 0']
    except:
      pass
    return df

 def reverse_repurchase_of_treasury_bonds(self,security='131810.SZ', order_type=xtconstant.STOCK_SELL
                      ,price_type=xtconstant.FIX_PRICE,strategy_name='',order_remark=''):
  '''
  国债逆回购
  '''
  # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
  account=self.balance()
  av_cash=account['可用金额'].tolist()[-1]
  av_cash=float(av_cash)
  spot_data=self.data.get_full_tick(code_list=[security])
  price=spot_data[security]['lastPrice']
  price=float(price)
  stock_code =self.adjust_stock(stock=security)
  order_volume= ((av_cash // 100) // 10) * 10
  if order_volume>0:
    fix_result_order_id = self.xt_trader.order_stock(account=self.acc,stock_code=stock_code, order_type=order_type,
                order_volume=order_volume, price_type=price_type,
                price=price, strategy_name=strategy_name, order_remark=order_remark)
    text='国债逆回购交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id)
    return True,text
  else:
    text='国债逆回购卖出 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume)
    return False,text

