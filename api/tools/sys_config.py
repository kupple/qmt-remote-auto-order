import platform
import subprocess
from datetime import datetime
import string
import secrets
from urllib.parse import urlparse

def get_system_unique_id():
    system = platform.system()
    if system == "Windows":
        try:
            result = subprocess.check_output("wmic csproduct get uuid", shell=True, text=True)
            result = result.replace('\n', '').replace('\r', '')
            uuid_str = result.split()[-1]  # 按空白字符分割字符串，取最后一个元素
            return uuid_str
        except Exception as e:
            print(f"Error getting UUID on Windows: {e}")
    elif system == "Linux":
        try:
            with open('/etc/machine-id', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print("File /etc/machine-id not found.")
        except Exception as e:
            print(f"Error getting machine ID on Linux: {e}")
    elif system == "Darwin":  # macOS
        try:
            command = "ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Error getting UUID on macOS: {result.stderr}")
        except Exception as e:
            print(f"Error getting UUID on macOS: {e}")
    return None



def generate_random_letters():
    # 获取当前时间戳（精确到毫秒）
    timestamp = datetime.now().timestamp()
    # 转换为整数并取后6位作为随机数生成的基础
    time_seed = int(timestamp * 1000) % 1000000
    
    # 使用 secrets 模块（比 random 更安全）生成随机字母
    alphabet = string.ascii_letters  # 包含所有大小写字母
    # 使用时间戳作为随机数生成器的种子
    secrets_generator = secrets.SystemRandom(time_seed)
    
    # 生成5位随机字母
    random_letters = ''.join(secrets_generator.choice(alphabet) for _ in range(5))
    
    return random_letters



def ws_to_http(ws_url):
    """
    将WebSocket URL转换为HTTP基础URL（仅保留主机和端口）
    
    参数:
    ws_url (str): WebSocket URL，如 "ws://example.com/path"
    
    返回:
    str: HTTP基础URL，如 "http://example.com"
    """
    parsed = urlparse(ws_url)
    scheme = {
        "ws": "http",
        "wss": "https"
    }.get(parsed.scheme, parsed.scheme)  # 协议映射，默认保留原协议
    return f"{scheme}://{parsed.netloc}"



def get_os_type():
    """获取当前操作系统类型"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    else:
        return "unknown"