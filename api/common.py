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
from api.tools.sysConfig import get_system_unique_id,ws_to_http
from api.tools.tokenManager import generate_token,verify_token

class Common:
    def __init__(self,orm) -> None:
        self.orm = orm
        
    def is_process_exist(self):
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
        
    def revert_transition_code(self,data):
        try:
            # 移除添加的 import 语句
            data = re.sub(r'^import requests\n', '', data, count=1, flags=re.M)
            data = re.sub(r'^import json\n', '', data, count=1, flags=re.M)
            
            # 移除插入的 g.run_params 行
            pattern = r'(def\s+initialize\s*\(\s*\w+\s*\)\s*:.*?)(\n\s+g\.run_params\s*=\s*\w+\.run_params\.type)'
            data = re.sub(pattern, r'\1', data, flags=re.DOTALL)
            
            # 移除 qmt_auto_orders 函数定义
            pattern = r'def qmt_auto_orders\(method_name, \*args, \*\*kwargs\):.*?return orderInfo\s*'
            data = re.sub(pattern, '', data, flags=re.DOTALL)
            
            # 恢复原始的订单方法调用
            pattern = r'qmt_auto_orders\("(order_target|order_value|order_target_value|order)",\s*([^)]*)\)'
            data = re.sub(pattern, r'\1(\2)', data)
            
            # 移除多余的空行
            data = re.sub(r'\n\s*\n', '\n\n', data).strip() + '\n'
            
            return data
        except Exception as e:
            print(f"还原错误: {e}")
            return "还原错误"

    
    def transition_code(self,data,taskDic):
        # server_url = ORM().get_setting_config()["server_url"]
        config =  self.orm.get_setting_config()
        run_model_type = config['run_model_type']
        server_url = ws_to_http(config['server_url'])
        strategy_code = taskDic['strategy_code']

        try:
            unique_id = None
            token = None
            if run_model_type == 2:
                token = self.orm.getStorageVar('qmt_token')
                token = token
            else:
                unique_id = get_system_unique_id()
                plaintext = {
                    "u": unique_id            
                }
                token = generate_token(plaintext,config['salt'])
            
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
        
    # 提取参数并调用系统方法
    system_method = method_map[method_name]
    
    security = args[0] if len(args) > 0 else kwargs.get('security')
    value = args[1] if len(args) > 1 else kwargs.get('value')
    style = args[2] if len(args) > 2 else kwargs.get('style')
    style_str = f"{{type(style).__name__}}({{getattr(style, 'limit_price', '')}})" if style else None
    side = args[3] if len(args) > 3 else kwargs.get('side','long')
    pindex = args[4] if len(args) > 4 else kwargs.get('pindex',0)

    
    
    orderInfo = system_method(security, value,
                        style=style_str,
                        side=side,
                        pindex=pindex)
    if orderInfo == None:
        return None
    jsonDic = json.dumps({{
        'method': method_name,
        'run_params': g.run_params,
        'strategy_code':'{strategy_code}',
        'params': {{
            'security':security,
            'value':value,
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
        except Exception as e:
            print(e)
            return "转译错误"
        
        


