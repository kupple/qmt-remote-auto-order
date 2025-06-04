from api.tools.sysConfig import ws_to_http
import re

def get_template_order_count_type_1(taskDic, data, config,token):
    run_model_type = config['run_model_type']
    server_url = ws_to_http(config['server_url'])
    strategy_code = taskDic['strategy_code']
    
    try:
        if 'import requests' not in data:
            data = 'import requests\n' + data
        if 'import json' not in data:
            data = 'import json\n' + data
            
        # 在文件开头添加token定义
        data = f"TOKEN = '{token}'\n" + data
            
        pattern = r'def\s+initialize\s*\(\s*(\w+)\s*\)\s*:'
        match = re.search(pattern, data)
    
        param_name = ''
        if match:
            param_name = match.group(1)
            
        # 构建要插入的代码行
        insert_line = f"    g.run_params = {param_name}.run_params.type"
        
        # 找到函数定义行的位置
        def_line_pos = data.find(match.group(0)) + len(match.group(0))
        
        # 在函数定义后插入新行
        data = data[:def_line_pos] + '\n' + insert_line + data[def_line_pos:]
        
        # 在initialize函数末尾添加begin状态请求
        begin_request_code = """
    # 发送begin状态
    jsonDic = json.dumps({
        'run_params': g.run_params,
        'strategy_code':'%s',
        'state':'begin'
    })
    url = "%s/send_message"
    response = requests.request('POST', url, headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
    }, data= jsonDic)
""" % (strategy_code, server_url)
        
        # 查找initialize函数的结束位置
        initialize_end_pos = data.find('def ', data.find(match.group(0)) + len(match.group(0)))
        if initialize_end_pos == -1:
            initialize_end_pos = len(data)
        
        # 在initialize函数末尾添加begin请求
        data = data[:initialize_end_pos] + begin_request_code + data[initialize_end_pos:]
        
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
            'is_buy':orderInfo.is_buy,
            'add_time':orderInfo.add_time.strftime("%Y-%m-%d %H:%M:%S")
        }}
    }})
    url = "{server_url}/send_message"
    response = requests.request('POST', url, headers=
    {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
    }}, data= jsonDic)
    return orderInfo
""" 
        
        # 在代码末尾添加on_strategy_end函数
        data = data + F"""
def on_strategy_end(context):
    jsonDic = json.dumps({{
        'run_params': g.run_params,
        'strategy_code':'{strategy_code}',
        'state':'end'
    }})
    url = "{server_url}/send_message"
    response = requests.request('POST', url, headers=
    {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
    }}, data= jsonDic)
    return response
"""
        
        # 匹配方法名和括号内的参数
        pattern = r'\b(order_target|order_value|order_target_value|order)\(([^)]*)\)'
        
        # 使用正则替换，将原方法名作为第一个参数传入qmt_auto_orders
        data = re.sub(pattern, r'qmt_auto_orders("\1", \2)', data)
        return data
    except Exception as e:
        print(e)
        return "转译错误"    
    
    

def get_template_order_count_type_2(taskDic, data, config,token):
    run_model_type = config['run_model_type']
    server_url = ws_to_http(config['server_url'])
    strategy_code = taskDic['strategy_code']
    
    try:        
        if 'import requests' not in data:
            data = 'import requests\n' + data
        if 'import json' not in data:
            data = 'import json\n' + data
            
        # 在文件开头添加token定义
        data = f"TOKEN = '{token}'\n" + data
            
        pattern = r'def\s+initialize\s*\(\s*(\w+)\s*\)\s*:'
        match = re.search(pattern, data)
    
        param_name = ''
        if match:
            param_name = match.group(1)
            
        # 构建要插入的代码行
        insert_line = f"    g.run_params = {param_name}.run_params.type"
        insert_line += "\n"
        insert_line += "    g.context = context"
        insert_line += "\n"
        
        # 找到函数定义行的位置
        def_line_pos = data.find(match.group(0)) + len(match.group(0))
        
        # 在函数定义后插入新行
        data = data[:def_line_pos] + '\n' + insert_line + data[def_line_pos:]
        
        # 在initialize函数末尾添加begin状态请求
        begin_request_code = """
    # 发送begin状态
    jsonDic = json.dumps({
        'run_params': g.run_params,
        'strategy_code':'%s',
        'state':'begin'
    })
    url = "%s/send_message"
    response = requests.request('POST', url, headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
    }, data= jsonDic)
""" % (strategy_code, server_url)
        
        # 查找initialize函数的结束位置
        initialize_end_pos = data.find('def ', data.find(match.group(0)) + len(match.group(0)))
        if initialize_end_pos == -1:
            initialize_end_pos = len(data)
        
        # 在initialize函数末尾添加begin请求
        data = data[:initialize_end_pos] + begin_request_code + data[initialize_end_pos:]
        
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
    total_value = g.context.portfolio.total_value
    


    orderInfo = system_method(security, value,
                        style=style_str,
                        side=side,
                        pindex=pindex)
    if orderInfo == None:
        return None
    
    positions = [
        {{
            'security': v.security,
            'price': v.price,
            'total_amount': v.total_amount,
            'avg_cost': v.avg_cost,
        }}
        for v in g.context.portfolio.positions.values()
    ]    
    jsonDic = json.dumps({{
        'method': method_name,
        'run_params': g.run_params,
        'strategy_code':'{strategy_code}',
        'state':'run',
        'positions':positions,
        'params': {{
            'security':security,
            'value':value,
            'style':style,
            'price':orderInfo.price,
            'amount':orderInfo.amount,
            'avg_cost':orderInfo.avg_cost,
            'is_buy':orderInfo.is_buy,
            'add_time':orderInfo.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_value':total_value
        }}
    }})
    url = "{server_url}/send_message"
    response = requests.request('POST', url, headers=
    {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
    }}, data= jsonDic)
    return orderInfo
""" 
        
        # 在代码末尾添加on_strategy_end函数
        data = data + F"""
def on_strategy_end(context):
    jsonDic = json.dumps({{
        'run_params': g.run_params,
        'strategy_code':'{strategy_code}',
        'state':'end'
    }})
    url = "{server_url}/send_message"
    response = requests.request('POST', url, headers=
    {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
    }}, data= jsonDic)
    return response
"""
        
        # 匹配方法名和括号内的参数
        pattern = r'\b(order_target|order_value|order_target_value|order)\(([^)]*)\)'
        
        # 使用正则替换，将原方法名作为第一个参数传入qmt_auto_orders
        data = re.sub(pattern, r'qmt_auto_orders("\1", \2)', data)
        return data
    except Exception as e:
        print(e)
        return "转译错误"    