import requests
import json

def make_request_with_requests():
    """使用 requests 库发送 GET 请求"""
    url = "http://127.0.0.1:5000/thsauto/balance"
    
    try:
        # 发送 GET 请求
        response = requests.get(url)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 处理响应内容
            if response.headers.get('Content-Type') == 'application/json':
                # 如果是 JSON 格式，解析为字典
                data = response.json()
                print("请求成功，响应数据（JSON 格式）：")
                print(json.dumps(data, indent=4, ensure_ascii=False))
            else:
                # 其他格式直接输出文本
                print("请求成功，响应数据：")
                print(response.text)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"请求过程中发生错误：{e}")

def make_request_with_params():
    """发送带参数的 GET 请求示例"""
    url = "http://192.168.0.116:5000/thsauto/balance"
    
    # 请求参数
    params = {
        "user_id": "12345",
        "timestamp": "2025-06-16"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("带参数请求成功，响应数据：")
            print(response.text)
        else:
            print(f"带参数请求失败，状态码：{response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"带参数请求错误：{e}")

def make_post_request():
    """发送 POST 请求示例（如果 API 支持）"""
    url = "http://192.168.0.116:5000/thsauto/orders/active"
    
    # POST 请求数据
    payload = {
        "user_id": "12345",
        "operation": "query"
    }
    
    try:
        # 发送 POST 请求，自动处理 JSON 格式
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("POST 请求成功，响应数据：")
            print(response.text)
        else:
            print(f"POST 请求失败，状态码：{response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"POST 请求错误：{e}")

# 执行请求
if __name__ == "__main__":
    print("=== 使用 requests 库发送 GET 请求 ===")
    make_request_with_requests()
    
