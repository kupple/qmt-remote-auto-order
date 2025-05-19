
from .xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from .xtquant.xttype import StockAccount
from .xtquant import xtconstant


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
            
    def sell(self,security='600031.SH', order_type=xtconstant.STOCK_SELL,
                    amount=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
        '''
        单独独立股票卖出函数
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code =self.adjust_stock(stock=security)
        price=self.select_slippage(stock=security,price=price,trader_type='sell')
        order_volume=amount
        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
        if order_volume>0:
            fix_result_order_id = self.xt_trader.order_stock(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                                order_volume=order_volume, price_type=price_type,
                                                                price=price, strategy_name=strategy_name, order_remark=order_remark)
            print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
            return fix_result_order_id
        else:
            print('卖出 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume))            
    
    def buy(self,security='600031.SH', order_type=xtconstant.STOCK_BUY,
                    amount=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
        '''
        单独独立股票买入函数
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code =self.adjust_stock(stock=security)
        price=self.select_slippage(stock=security,price=price,trader_type='buy')
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
            return xt_trader,acc
        else:
            print('qmt连接失败')