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
from api.tools.token_manager import generate_token,verify_token
from api.tools.template import get_template_order_count_type_1,get_template_order_count_type_2
from api.global_params import G
from api.trading_related.deal import convert_stock_suffix
from datetime import datetime
import os

if sys.platform.startswith('darwin'):
    pass
else:
    import win32api
    import win32gui
    import win32ui
    import win32con
    import win32clipboard
    import win32process
    import psutil


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
        # print(trade_date_arr)
        # print("trade_date_arr")

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
        token = G.orm.get_storage_var('qmt_token')
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


def control_ths_window(show: bool):
    """
    控制同花顺交易软件窗口的显示或隐藏
    :param show: True 显示窗口，False 隐藏窗口
    """
    # 获取窗口句柄
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        if show:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)   # 恢复窗口
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)   # 显示窗口
            win32gui.SetForegroundWindow(hwnd)   # 将窗口置于最前面
            # 设置窗口大小和位置
            win32gui.MoveWindow(hwnd, 0, 0, 1024, 768, True)   # 设置窗口为1024x768
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)   # 隐藏窗口
    
    
# 获取同花顺交易软件窗口的显示状态
def get_ths_window_state() -> bool:
    """
    获取同花顺交易软件窗口的显示状态
    :return: True 窗口可见，False 窗口隐藏
    """
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        return win32gui.IsWindowVisible(hwnd)
    return False   # 窗口不存在时返回隐藏状态





def get_all_xtminiqmt_processes():
    """
    一次性获取所有正在运行的 XtMiniQmt.exe 进程信息
    返回值：列表，每个元素是字典，包含进程的核心信息
            字典结构：{'pid': 进程ID, 'path': 程序完整路径, 'name': 进程名}
    """
    if sys.platform.startswith('darwin'):
        return [{'pid': 888, 'path': 'C:\\Users\\mubin\\AppData\\Local\\长城策略交易系统\\bin.x64_rtys789\\XtMiniQmt.exe', 'name': 'XtMiniQmt.exe'}]
    else:
        # 目标进程名（小写，用于快速匹配）
        target_name = "xtminiqmt.exe"
        all_processes = []

        # 仅遍历一次所有进程，收集目标进程信息
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_info = proc.info
                # 跳过无名称/无路径的进程，快速过滤非目标进程
                if not proc_info['name'] or not proc_info['exe']:
                    continue
                
                # 匹配目标进程（忽略大小写）
                if proc_info['name'].lower() == target_name:
                    # 标准化路径（统一格式，方便后续匹配）
                    exe_path = os.path.normpath(proc_info['exe'])
                    # 添加到结果列表
                    all_processes.append({
                        'pid': proc_info['pid'],
                        'path': exe_path,
                        'name': proc_info['name']
                    })

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 忽略无权限/已退出/僵尸进程，不影响结果
                continue
            except Exception as e:
                # 捕获意外异常，避免函数崩溃
                print(f"扫描进程 PID {proc_info.get('pid', '未知')} 时出错: {e}")
                continue

        return all_processes




def check_mini_qmt_path_match(account_info: dict, process_list: list):
   
    
    # 2. 获取mini_qmt_path并处理空值
    mini_qmt_path = account_info.get('mini_qmt_path')
    if not mini_qmt_path:
        print("错误：account_info中未找到有效的mini_qmt_path字段")
        return False
    
    # 3. 标准化路径（解决路径分隔符/大小写等潜在问题）
    try:
        # 标准化路径，统一处理Windows/Linux路径格式，消除末尾斜杠等差异
        standard_target_path = os.path.normpath(mini_qmt_path)
    except Exception as e:
        print(f"错误：路径标准化失败 - {e}")
        return False
    
    # 4. 遍历列表匹配path字段
    for item in process_list:
        # 跳过非字典类型的项
        if not isinstance(item, dict):
            continue
        
        # 获取并标准化当前项的path
        item_path = item.get('path', '')
        if not item_path:
            continue
        
        try:
            standard_item_path = os.path.normpath(item_path)
        except Exception:
            continue
        
        # 核心匹配逻辑
        if standard_item_path == standard_target_path:
            return True
    
    # 5. 未找到匹配项
    return False
