#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 数据库操作相关的API
'''
import subprocess
import sys
from api.db.orm import ORM
import json
import re
from api.tools.tokenManager import generate_token,verify_token
from api.tools.template import get_template_order_count_type_1,get_template_order_count_type_2
from api.global_params import G


# 同步数据到全局

def sync_data_to_global():
    
    G.logger.info("同步数据到全局")
    st_code_arr = G.orm.get_st_stock_data()
    G.stock_map["st_stock_code"] = st_code_arr
    
    all_stock_arr = G.orm.get_all_stock_data()
    G.stock_map["all_stock_code"] = {stock['code']:stock for stock in all_stock_arr}
    
    trade_date_arr = G.orm.get_trade_date_list()
    G.stock_map['trade_date'] = trade_date_arr
    G.logger.info("同步数据结束")
    
    


def revert_transition_code(data):
    try:
        # 移除TOKEN定义
        data = re.sub(r'TOKEN\s*=\s*[\'"][^\'"]*[\'"]\n', '', data)
        
        # 移除begin状态请求代码
        begin_pattern = r'# 发送begin状态[\s\S]*?data\s*=\s*jsonDic\s*\)\n'
        data = re.sub(begin_pattern, '', data)
        
        # 移除on_strategy_end函数
        end_pattern = r'def\s+on_strategy_end\s*\([^\)]*\)\s*:[\s\S]*?return\s+response\n'
        data = re.sub(end_pattern, '', data)
        
        # 移除g.context赋值行（如果存在）
        data = re.sub(r'^\s+g\.context\s*=\s*context\n', '', data, flags=re.M)
        
        # 移除g.run_params赋值行
        data = re.sub(r'^\s+g\.run_params\s*=\s*context\.run_params\.type\n', '', data, flags=re.M)
        
        # 还原请求头中的TOKEN引用
        data = re.sub(r"'Authorization':\s+'Bearer\s*'\+\s*TOKEN", r"'Authorization': 'Bearer {token}'", data)
        
        # 移除qmt_auto_orders函数
        auto_orders_pattern = r'def\s+qmt_auto_orders\s*\([^\)]*\)\s*:[\s\S]*?return\s+orderInfo\n'
        data = re.sub(auto_orders_pattern, '', data)
        
        # 还原原始下单函数调用
        data = re.sub(r'qmt_auto_orders\(["\'](order_target|order_value|order_target_value|order)["\'],\s*', r'\1(', data)
        
        # 移除portfolio相关参数（针对type_2）
        portfolio_pattern = r"'total_amount':\s*g\.context\.portfolio\.positions\[security\]\.total_amount,?[\s\n]*'total_value':\s*g\.context\.portfolio\.total_value,?[\s\n]*"
        data = re.sub(portfolio_pattern, '', data)
        
        return data
    except Exception as e:
        G.logger.error(f"还原错误: {e}")
        return "还原错误"    


def is_process_exist():
    app_name = "XtMiniQmt.exe"
    if sys.platform.startswith('darwin'):
        return True
    try:
        # 创建STARTUPINFO对象并设置隐藏窗口标志
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE  # 隐藏窗口
        
        # 执行tasklist命令并传入STARTUPINFO
        output = subprocess.check_output(
            ['tasklist'], 
            universal_newlines=True,
            startupinfo=startupinfo  # 添加这一行以隐藏终端窗口
        )
        
        # 后续代码保持不变
        index = output.find("System")
        if index == -1:
            return False
        data = output[index:]
        fields = data.split()
        for i, field in enumerate(fields):
            if field == app_name:
                try:
                    pid = int(fields[i + 1])
                    return True
                except (IndexError, ValueError):
                    return False
        return False
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False

        



    # 转译代码 
def transition_code(data,taskDic):
    config =  G.orm.get_setting_config()
    run_model_type = config['run_model_type']

    if run_model_type == 2:
        token = G.orm.getStorageVar('qmt_token')
    else:
        unique_id = G.unique_id
        plaintext = {
            "u": unique_id,
            "p":'local'
        }
        token = generate_token(plaintext,config['salt'])
    if taskDic['order_count_type'] == 1:
        return get_template_order_count_type_1(taskDic,data,config,token)
    else:
        return get_template_order_count_type_2(taskDic,data,config,token)
