#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 数据库操作相关的API
'''
from ast import Try
import subprocess
import sys
from api.db.orm import ORM
import json
import re
from api.tools.tokenManager import generate_token,verify_token
from api.tools.template import get_template_order_count_type_1,get_template_order_count_type_2
from api.global_params import G
from api.trading_related.deal import convert_stock_suffix
from datetime import datetime
import os

def timestamp_to_date(timestamp):
    """
    将 Unix 时间戳转换为 'YYYY-MM-DD' 格式的日期字符串
    
    参数:
    timestamp (int/float): Unix 时间戳（从 1970-01-01 开始的秒数）
    
    返回:
    str: 格式化的日期字符串
    """
    # 将时间戳转换为 datetime 对象
    dt_object = datetime.fromtimestamp(timestamp)
    
    # 格式化为 'YYYY-MM-DD' 字符串
    return dt_object.strftime('%Y-%m-%d')


def find_nearest_date(dates):
    # 将字符串转换为日期对象
    date_objects = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in dates]
    
    # 获取当前日期
    current_date = datetime.now().date()
    
    # 计算每个日期与当前日期的时间差
    deltas = [(date, abs(date - current_date)) for date in date_objects]
    
    # 找出时间差最小的日期
    nearest_date = min(deltas, key=lambda x: x[1])[0]
    
    return nearest_date.strftime('%Y-%m-%d')

# 同步数据到全局
def sync_data_to_global():
    
    try:
        G.logger.info("同步数据到全局")
        st_code_arr = G.orm.get_st_stock_data()
        G.stock_map["st_stock_code"] = st_code_arr
        
        all_stock_arr = G.orm.get_all_stock_data()
        G.stock_map["all_stock_code"] = {convert_stock_suffix(stock['code']):stock for stock in all_stock_arr}
        
        trade_date_arr = G.orm.get_trade_date_list()

        G.stock_map['trade_date'] = trade_date_arr
        
        nearest_date = find_nearest_date(trade_date_arr)
        G.stock_map['nearest_trade_date'] = nearest_date
        
        record = G.orm.get_data_table_record("data_all_stocks")        
        if record and record['record_time']:
            # 将其时间部分设置为 00:00:00
            dt1 = datetime.strptime(record['record_time'], '%Y-%m-%d %H:%M:%S')
            # 解析第二个日期时间字符串（YYYY-MM-DD HH:mm:ss）
            dt2 = datetime.strptime(nearest_date, '%Y-%m-%d')
            if dt1.date() >= dt2.date():
                G.stock_map['is_data_synced'] = True
            else:
                G.stock_map['is_data_synced'] = False
        else:
            G.stock_map['is_data_synced'] = False
            
            
            
        
        
        G.logger.info("同步数据结束")
    except Exception as e:
        G.logger.error(f"同步数据到全局失败: {e}")
    
    


def revert_transition_code(data):
    try:
        # 移除TOKEN定义
        data = re.sub(r'TOKEN\s*=\s*[\'"][^\'"]*[\'"]\n', '', data)
        
        # 移除begin状态请求代码 - 精准匹配版本
        # 1. 首先匹配initialize函数定义
        initialize_pattern = r'(def\s+initialize\s*\([^\)]*\)\s*:)([\s\S]*?)(?=def\s+|$)'
        initialize_match = re.search(initialize_pattern, data)
        
        if initialize_match:
            # 获取initialize函数定义
            initialize_def = initialize_match.group(1)
            # 获取initialize函数体
            initialize_body = initialize_match.group(2)
            
            # 2. 在函数体中查找begin状态代码块
            begin_pattern = r'(\s*)(# 发送begin状态[\s\S]*?)(?=\s*def\s+|$)'
            begin_match = re.search(begin_pattern, initialize_body)
            
            if begin_match:
                # 获取begin状态代码块的缩进
                indent = begin_match.group(1)
                # 构建替换后的函数体（移除begin状态代码块）
                new_body = initialize_body.replace(begin_match.group(0), '')
                
                # 3. 重新组合数据
                data = data.replace(initialize_def + initialize_body, initialize_def + new_body)
        
        # 移除on_strategy_end函数
        end_pattern = r'def\s+on_strategy_end\s*\([^\)]*\)\s*:[\s\S]*?return\s+response\s*'
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
        
        # 移除添加的 on_event 函数
        event_pattern = r'def\s+on_event\s*\([^)]*\)\s*:[\s\S]*?return\s+response\s*'
        data = re.sub(event_pattern, '', data)
        
        # 清理多余的空行
        data = re.sub(r'\n{3,}', '\n\n', data)
        
        return data
    except Exception as e:
        G.logger.error(f"还原错误: {e}")
        return "还原错误"

# 打开同花顺
def open_ths_shortcut(file_path):
    """打开Windows快捷方式文件"""
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件不存在 - {file_path}")
            return False
        
        # 检查是否为.lnk文件
        if not file_path.lower().endswith('.lnk'):
            print(f"错误：不是有效的快捷方式文件 - {file_path}")
            return False
        
        # 使用shell命令打开快捷方式
        subprocess.run(['start', '', file_path], shell=True, check=True)
        print(f"成功打开：{file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误：无法打开文件 - {e}")
        return False
    except Exception as e:
        print(f"未知错误：{e}")
        return False

    
# 创建同花顺快捷方式
def create_ths_shortcut(exe_path):
    """为指定的exe文件在同级目录创建快捷方式"""
    try:
        # 创建的快捷方式名称
        exe_dir = os.path.dirname(exe_path)
        shortcut_name = f"autoxiadan.lnk"
        shortcut_path = os.path.join(exe_dir, shortcut_name)
        
        # 检查快捷方式是否已存在
        if os.path.exists(shortcut_path):
            print(f"快捷方式已存在：{shortcut_path}")
            return True

        # 检查文件是否存在
        if not os.path.exists(exe_path):
            print(f"错误：文件不存在 - {exe_path}")
            return False
        
            # 检查是否为exe文件
        if not exe_path.lower().endswith('.exe'):
            print(f"错误：不是有效的exe文件 - {exe_path}")
            return False
        
        # 创建快捷方式对象
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        
        # 设置快捷方式属性
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = exe_dir   # 设置工作目录为exe所在目录
        shortcut.Description = f"快捷方式：{os.path.basename(exe_path)}"
        
        # 保存快捷方式
        shortcut.Save()
        
        print(f"成功创建快捷方式：{shortcut_path}")
        return True
    except Exception as e:
        print(f"错误：创建快捷方式失败 - {e}")
        return False


def is_process_exist():
    app_name = "XtMiniQmt.exe"
    if G.client_type == 1:
        app_name = "xiadan.exe"
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

