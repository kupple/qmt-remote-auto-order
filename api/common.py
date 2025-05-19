#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 数据库操作相关的API
'''
import subprocess
from api.sql import Database
import json
import re
from api.tools.sysConfig import get_system_unique_id
from api.tools.tokenManager import generate_token,verify_token

class Common:

    def is_process_exist(self):
        app_name = "XtMiniQmt.exe"
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

    
    def transition_code(self,data,taskDic):
        # server_url = Database.setting_config["server_url"]
        server_url = "http://193.112.151.98:8080"
        try:
                unique_id = get_system_unique_id()
                plaintext = {
                    "c": taskDic["strategy_code"],
                    "u": unique_id            
                }
                # 服务端的盐
                # 加密
                token = generate_token(plaintext)
                print(verify_token(token))
                
                if 'import requests' not in data:
                    # 在文件开头添加 import 语句
                    data = 'import requests\n' + data
                if 'import json' not in data:
                    # 在文件开头添加 import 语句
                    data = 'import json\n' + data
                    
                pattern = r'def\s+initialize\s*\(\s*(\w+)\s*\)\s*:'
                match = re.search(pattern, data)
            
                param_name = ''
                if match:
                    # 获取参数名
                    param_name = match.group(1)
                    
                # 构建要插入的代码行
                insert_line = f"    g.run_params = {param_name}.run_params.type"
                
                # 找到函数定义行的位置
                def_line_pos = data.find(match.group(0)) + len(match.group(0))
                
                # 在函数定义后插入新行
                data = data[:def_line_pos] + '\n' + insert_line + data[def_line_pos:]
                
                data = data + '\n'
                data = data + F"""
def qmt_auto_orders(method_name, *args, **kwargs):
    # 获取系统方法
    method_map = {{
        'order_target': order_target,
        'order_value': order_value,
        'order': order,
        'order_target_value': order_target_value,
    }}
    
    if method_name not in method_map:
        raise ValueError(f"不支持的方法名: {{method_name}}")
    
    # 提取参数并调用系统方法
    security, value_or_amount = args[0], args[1]
    system_method = method_map[method_name]
    
    style = kwargs.get('style',None)
    side = kwargs.get('side', 'long')
    pindex = kwargs.get('pindex', 0)
    close_today = kwargs.get('close_today', False)
    
    orderInfo = system_method(security, value_or_amount,
                        style=style,
                        side=side,
                        pindex=pindex,
                        close_today=close_today)
    if orderInfo == None:
        return None
    jsonDic = json.dumps({{
        'method': method_name,
        'run_params': g.run_params,
        'params': {{
            'security':security,
            'value':value_or_amount,
            'style':style,
            'price':orderInfo.price,
            'amount':orderInfo.amount,
            'avg_cost':orderInfo.avg_cost,
            'commission':orderInfo.commission,
            'is_buy':orderInfo.is_buy,
            'add_time':orderInfo.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            'pindex':pindex,
        }}
    }})
    url = "{server_url}/send_message"
    response = requests.request('POST', url, headers=
    {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'
    }}, data= jsonDic)
    return orderInfo
    """ 

                # 匹配方法名和括号内的参数
                pattern = r'\b(order_target|order_value|order_target_value|order)\(([^)]*)\)'
                
                # 使用正则替换，将原方法名作为第一个参数传入 qmt_auto_orders
                data = re.sub(pattern, r'qmt_auto_orders("\1", \2)', data)
                return data
        except:
            return "转译错误"
        
        


