from .xtquant import xtdata
from .xtquant import xttrader
import time
import pandas as pd

class qmt_data:
    def __init__(self):
        '''
        qmt数据
        '''
        pass
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
    def adjust_stock(self,stock='600031.SH'):
        '''
        调整代码
        '''
        if stock[-2:]=='SH' or stock[-2:]=='SZ':
            stock=stock
        else:
            if stock[:3] in ['600','601','603','688','510','511',
                             '512','513','515','113','110','128','123','127']:
                stock=stock+'.SH'
            else:
                stock=stock+'.SZ'
        return stock
    def get_all_data(self):
        return xtdata
    def on_data(self,datas):
        for stock_code in datas:
                print(stock_code, datas[stock_code])
    def conv_time(self,ct):
        '''
        conv_time(1476374400000) --> '20161014000000.000'
        '''
        local_time = time.localtime(ct / 1000)
        data_head = time.strftime('%Y%m%d%H%M%S', local_time)
        data_secs = (ct - int(ct)) * 1000
        time_stamp = '%s.%03d' % (data_head, data_secs)
        return time_stamp
    def subscribe_quote(self,stock_code='600031.SH', period='1d', start_time='20210105', end_time='20230601', count=1000, callback=on_data):
            '''
            释义

            订阅单股的行情数据，返回订阅号
            订阅成功后，可以用get_market_data或get_l2_xxx获取行情，同时当指定callback回调函数后，动态行情会推送到callback里。传入不同period，其callback里收到的字段有所不同，详见行情数据字段列表
            当仅需要动态行情时，适合count=0，此时不管start_time和end_time传入何值，均不会像服务器订阅历史行情
            当同时需要获取历史数据和动态行情时，end_time传空字符串或当前时间且count传大于0或-1，且用get_market_data获取历史和实时行情，但是建议历史行情提前用download_history_data提前下载到本地
            当仅需要历史行情时，不宜使用该接口，建议用download_history_data配合get_market_data使用
            参数
            
            - 返回

            - 订阅号，订阅成功返回`大于0`，失败返回`-1`

            - 备注

            - 单股订阅数量不宜过多，详见 接口概述-请求限制
            '''
            data=xtdata.subscribe_quote(stock_code=stock_code,period=period,start_time=start_time,
                                        end_time=end_time,count=count,callback=self.on_data)
            if data >0:
                print('订阅成功订阅号{}'.format(data))
                result=xtdata.get_market_data()
                return result
            elif data==-1:
                print('{}订阅失败'.format(stock_code))
            else:
                print('{}订阅失败'.format(stock_code))
    def subscribe_whole_quote(self,code_list=['600031.SH','600111.SH'], callback=on_data):
        '''
        
        - 释义

        - 订阅全推行情数据，返回订阅号
        - 数据推送从callback返回，数据类型为分笔数据

        - 参数

        - code_list - 代码列表，支持传入市场代码或合约代码两种方式

            - 传入市场代码代表订阅全市场，示例：`['SH', 'SZ']`
            - 传入合约代码代表订阅指定的合约，示例：`['600000.SH', '000001.SZ']`

        - callback - 数据推送回调
        '''
        data=xtdata.subscribe_whole_quote(code_list=code_list,callback=callback)
        if data>0:
            result=xtdata.get_market_data()
            return result
        elif data==-1:
            print('{}订阅失败'.format(code_list))
        else:
            print('{}订阅失败'.format(code_list))
    def unsubscribe_quote(self,seq=1):
        '''
        取消订阅
        '''
        xtdata.unsubscribe_quote(seq=seq)
    def run(self,):
        '''
        阻塞线程接收行情回调
        - 释义
        - 阻塞当前线程来维持运行状态，一般用于订阅数据后维持运行状态持续处理回调
        - 参数
        - seq - 订阅时返回的订阅号
        - 返回
        - 无
        - 备注
        - 实现方式为持续循环sleep，并在唤醒时检查连接状态，若连接断开则抛出异常结束循环
        '''
        xtdata.run()
    def data_to_pandas(self,data='',stock_list=[]):
        '''
        把qmt数据转pandas
        '''
        data_dict={}
        columns=data.keys()
        df=pd.DataFrame()
        for stock in stock_list:
            for column in columns:
                df1=data[column] 
                df2=pd.DataFrame(df1).T
                df[column]=df2[stock]
            df['time']=df['time'].apply(self.conv_time).astype(str).apply(lambda x:x[:8])
            data_dict[stock]=df
        print(data_dict)
    def get_market_data(self,field_list=[], stock_list=['600031.SH','600111.SH'], period='1d', 
                        start_time='20210105', end_time='20230703', count=1000,
                        dividend_type='none', fill_data=True):
        '''
        释义

        从缓存获取行情数据，是主动获取行情的主要接口
        获取实时行情需要先调用单股订阅接口subscribe_quote订阅实时行情
        当已经提前用download_history_data下载数据或subscribe_quote订阅历史数据时，该接口可以获取到历史行情
        参数

        field_list - list 数据字段列表，传空则为全部字段
        周期为1m、5m、1d 时，字段可选 含义说明
        释义
        - 从本地数据文件获取行情数据，用于快速批量获取历史部分的行情数据
        - 参数
        - field_list - list 数据字段列表，传空则为全部字段
        - stock_list - list 合约代码列表
        - period - string 周期
        - start_time - string 起始时间
        - end_time - string 结束时间
        - count - int 数据个数
        - dividend_type - string 除权方式
        - fill_data - bool 是否向后填充空缺数据
        - data_dir - string MiniQmt配套路径的userdata_mini路径，用于直接读取数据文件。默认情况下xtdata会通过连接向MiniQmt直接获取此路径，无需额外设置。如果需要调整，可以将数据路径作为`data_dir`传入，也可以直接修改`xtdata.data_dir`以改变默认值
        - 返回
        - period为`1m` `5m` `1d`K线周期时
            - 返回dict { field1 : value1, field2 : value2, ... }
            - field1, field2, ... ：数据字段
            - value1, value2, ... ：pd.DataFrame 数据集，index为stock_list，columns为time_list
            - 各字段对应的DataFrame维度相同、索引相同
        - period为`tick`分笔周期时
            - 返回dict { stock1 : value1, stock2 : value2, ... }
            - stock1, stock2, ... ：合约代码
            - value1, value2, ... ：np.ndarray 数据集，按数据时间戳`time`增序排列
        - 备注
        - 仅用于获取level1数据
        '''
        data=xtdata.get_market_data(field_list= field_list,stock_list=stock_list,period=period,
                                    start_time=start_time,end_time=end_time,count=count,
                                    dividend_type=dividend_type,fill_data=fill_data)
        try:
            df=self.data_to_pandas(data=data,stock_list=stock_list)
            return df
        except:
            return data
    def get_market_data_spot(self,stock_code='600031.SH', period='1d',
                            start_time='20210105', end_time='20230703', count=11, callback=on_data):
        '''
        来自什么订阅单个股票实时数据
        '''
        xtdata.subscribe_quote(stock_code=stock_code,period=period,
                            start_time=start_time,end_time=end_time,count=count,callback=callable)
        df=xtdata.get_market_data()
        return df
    def get_full_tick(self,code_list=['600031.SH','600111.SH']):
        '''
        - 释义
        - 获取全推数据
        - 参数
        - code_list - 代码列表，支持传入市场代码或合约代码两种方式
            - 传入市场代码代表订阅全市场，示例：`['SH', 'SZ']`
            - 传入合约代码代表订阅指定的合约，示例：`['600000.SH', '000001.SZ']`
        - 返回
        - dict 数据集 { stock1 : data1, stock2 : data2, ... }
        - 备注
        - 无
        '''
        df=xtdata.get_full_tick(code_list=code_list)
        return df
    def get_divid_factors(self,stock_code='600031.SH', start_time='20210331', end_time='20230331'):
        '''
        - 释义
        - 获取除权数据
        - 参数
        - stock_code - 合约代码
        - start_time - string 起始时间
        - end_time - string 结束时间
        - 返回
        - pd.DataFrame 数据集
        - 备注
        - 无
        '''
        df=xtdata.get_divid_factors(stock_code=stock_code,start_time=start_time,end_time=end_time)
        return df
    def get_l2_quote(self,field_list=[], stock_code='600031.SH', 
                    start_time='20210105', end_time='20230709', count=-1):
        '''
        - 释义
        - 获取level2行情快照数据
        - 参数
        - field_list - list 数据字段列表，传空则为全部字段
        - stock_code - string 合约代码
        - start_time - string 起始时间
        - end_time - string 结束时间
        - count - int 数据个数
        - 返回
        - np.ndarray 数据集，按数据时间戳`time`增序排列
        - 备注
        - 需要缓存中有接收过的数据才能获取到
        '''
        df=xtdata.get_l2_quote(field_list=field_list,stock_code=stock_code,start_time=start_time,end_time=end_time,count=count)
        return df
    def get_l2_order(self,field_list=[], stock_code='', start_time='', end_time='', count=-1):
        '''
        - 释义
        - 获取level2逐笔委托数据
        - 参数
        - field_list - list 数据字段列表，传空则为全部字段
        - stock_code - string 合约代码
        - start_time - string 起始时间
        - end_time - string 结束时间
        - count - int 数据个数
        - 返回
        - np.ndarray 数据集，按数据时间戳`time`增序排列
        - 备注
        - 需要缓存中有接收过的数据才能获取到
        '''
        df=xtdata.get_l2_order(field_list=field_list,stock_code=stock_code,start_time=start_time,end_time=end_time,count=count)
        return df
    def get_l2_transaction(self,field_list=[], stock_code='', start_time='', end_time='', count=-1):
        '''
        
            - 释义
            - 获取level2逐笔成交数据
            - 参数
            - field_list - list 数据字段列表，传空则为全部字段
            - stock_code - string 合约代码
            - start_time - string 起始时间
            - end_time - string 结束时间
            - count - int 数据个数
            - 返回
            - np.ndarray 数据集，按数据时间戳`time`增序排列
            - 备注
            - 需要缓存中有接收过的数据才能获取到
        '''
        df=xtdata.get_l2_transaction(field_list=field_list,stock_code=stock_code,start_time=start_time,end_time=end_time,count=count)
        return df
    def download_history_data(self,stock_code='600031.SH', period='1d', 
                            start_time='20230101', end_time='20230709'):
        '''
                - 释义
            - 补充历史行情数据
            - 参数
            - stock_code - string 合约代码
            - period - string 周期
            - start_time - string 起始时间
            - end_time - string 结束时间
            - 返回
            - 无
            - 备注
            - 同步执行，补充数据完成后返回
        '''
        df=xtdata.download_history_data(stock_code=stock_code,period=period,start_time=start_time,end_time=end_time)
        return df
    def download_history_data2(stock_list=['600031.SH','600111.SH'], period='1d', start_time='20230101', end_time='20230709'):
        '''
                - 释义
            - 补充历史行情数据
            - 参数
            - stock_code - string 合约代码
            - period - string 周期
            - start_time - string 起始时间
            - end_time - string 结束时间
            - 返回
            - 无
            - 备注
            - 同步执行，补充数据完成后返回
        '''
        df=xtdata.download_history_data2(stock_list=stock_list,period=period,start_time=start_time,end_time=end_time)
        return df
    def get_financial_data(self,stock_list=['600031.SH'], table_list=['Balance'], start_time='20220331',
                            end_time='20230630', report_type='report_time'):
        '''
                - 释义
            
            - 获取财务数据
            - 参数
            
            - stock_list - list 合约代码列表
            
            - table_list - list 财务数据表名称列表
            
                - ```python
                'Balance' 	#资产负债表
                'Income' 	#利润表
                'CashFlow' 	#现金流量表
                ```
            
            - start_time - string 起始时间
            
            - end_time - string 结束时间
            
            - report_type - string 报表筛选方式
            
                - ```python
                'report_time' 	#截止日期
                'announce_time' #披露日期
                ```
            - 返回
            
            - dict 数据集 { stock1 : datas1, stock2 : data2, ... }
            - stock1, stock2, ... ：合约代码
            - datas1, datas2, ... ：dict 数据集 { table1 : table_data1, table2 : table_data2, ... }
                - table1, table2, ... ：财务数据表名
                - table_data1, table_data2, ... ：pd.DataFrame 数据集，数据字段详见附录 - 财务数据字段列表
            - 备注
            
            - 无
        '''
        df=xtdata.get_financial_data2(stock_list=stock_list,table_list=table_list,
                                    start_time=start_time,end_time=end_time,report_type=report_type)
        return df
    def download_financial_data(self,stock_list='600031.SH', table_list=['Balance']):
        '''

        - 释义
        - 下载财务数据
        - 参数
        - stock_list - list 合约代码列表
        - table_list - list 财务数据表名列表
        - 返回
        - 无
        - 备注
        - 同步执行，补充数据完成后返回
        - table_list - list 财务数据表名称列表
            
                - ```python
                'Balance' 	#资产负债表
                'Income' 	#利润表
                'CashFlow' 	#现金流量表
                ```

        '''
        df=xtdata.download_financial_data(stock_list=stock_list,table_list=table_list)
        return df
    def get_instrument_detail(self,stock_code='600031.SH'):
        '''
            ```

        - 释义

        - 获取合约基础信息

        - 参数

        - stock_code - string 合约代码

        - 返回

        - dict 数据字典，{ field1 : value1, field2 : value2, ... }，找不到指定合约时返回`None`

        - ```python
            ExchangeID - string 合约市场代码
            InstrumentID - string 合约代码
            InstrumentName - string 合约名称
            ProductID - string 合约的品种ID(期货)
            ProductName - string 合约的品种名称(期货)
            CreateDate - int 上市日期(期货)
            OpenDate - int IPO日期(股票)
            ExpireDate - int 退市日或者到期日
            PreClose - float 前收盘价格
            SettlementPrice - float 前结算价格
            UpStopPrice - float 当日涨停价
            DownStopPrice - float 当日跌停价
            FloatVolume - float 流通股本
            TotalVolume - float 总股本
            LongMarginRatio - float 多头保证金率
            ShortMarginRatio - float 空头保证金率
            PriceTick - float 最小价格变动单位
            VolumeMultiple - int 合约乘数(对期货以外的品种，默认是1)
            MainContract - int 主力合约标记，1、2、3分别表示第一主力合约，第二主力合约，第三主力合约
            LastVolume - int 昨日持仓量
            InstrumentStatus - int 合约停牌状态
            IsTrading - bool 合约是否可交易
            IsRecent - bool 是否是近月合约
            ```
        '''
        df=xtdata.get_instrument_detail(stock_code=stock_code)
        return df
    def get_instrument_type(self,stock_code='600031.SH'):
        '''
        ```

            - 释义
            
            - 获取合约类型
            - 参数
            
            - stock_code - string 合约代码
            - 返回
            
            - dict 数据字典，{ type1 : value1, type2 : value2, ... }，找不到指定合约时返回`None`
            
                - type1, type2, ... ：string 合约类型
                - value1, value2, ... ：bool 是否为该类合约
            
            - ```python
                'index'		#指数
                'stock'		#股票
                'fund'		#基金
                'etf'		#ETF
                ```
            - 备注
        '''
        df=xtdata.get_instrument_type(stock_code=stock_code)
        return df
if __name__=='__main__':
    data=qmt_data()
    data.subscribe_quote()
    print(data.get_full_tick())