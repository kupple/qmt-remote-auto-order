#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import mimetypes
import os
import sys
import platform
import pystray
from PIL import Image
import webview
import threading
import os
import sys
import multiprocessing

from api.api import API
from pyapp.config.config import Config
from pyapp.db.db import DB

# 单例锁文件路径
def get_lock_file_path():
    if getattr(sys, 'frozen', False):
        # 打包后的应用
        lock_file = os.path.join(sys._MEIPASS, 'lock.txt')
    else:
        # 开发环境
        lock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lock.txt')
    return lock_file

# 检查是否已有实例运行
def check_single_instance():
    lock_file = get_lock_file_path()
    try:
        # 创建或打开锁文件
        if os.path.exists(lock_file):
            # 如果文件已存在，尝试获取锁
            lock = multiprocessing.Lock()
            try:
                lock.acquire(timeout=0.1)  # 尝试获取锁，超时0.1秒
                return True, lock
            except:
                # 如果获取锁失败，说明其他实例正在运行
                return False, None
        else:
            # 如果文件不存在，创建新文件并获取锁
            with open(lock_file, 'w') as f:
                f.write('')
            lock = multiprocessing.Lock()
            lock.acquire()
            return True, lock
    except Exception as e:
        print(f"检查单例失败: {e}")
        return False, None

# 释放锁
def release_lock(lock):
    if lock:
        try:
            lock.release()
        except Exception as e:
            print(f"释放锁失败: {e}")

# 在程序退出时释放锁
def cleanup():
    if hasattr(sys, 'fd'):
        release_lock(sys.fd)

# 注册退出处理
import atexit
atexit.register(cleanup)

# 检查是否已有实例运行
is_first_instance, lock_fd = check_single_instance()
if not is_first_instance:
    print("程序已经在运行中，请不要重复启动！")
    sys.exit(0)

# 保存锁文件描述符
sys.fd = lock_fd

# 全局变量
window = None
icon = None

cfg = Config()    # 配置
cfg.init()    # Initialize config first to set up app data directory
db = DB()    # 数据库类
api = API()    # 本地接口

def create_tray_icon():
    # 创建系统托盘图标
    try:
        # 获取应用根目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用
            application_path = sys._MEIPASS
        else:
            # 如果是开发环境
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        # 构建图标路径
        icon_path = os.path.join(application_path, "pyapp", "icon", "tray.png")
        image = Image.open(icon_path)
    except Exception as e:
        print(f"加载图标失败: {e}")
        # 如果找不到图标文件，创建一个默认的红色图标
        image = Image.new('RGB', (64, 64), color = 'red')
    
    # 创建菜单项
    menu = (
        pystray.MenuItem('显示', show_window),
        pystray.MenuItem('退出', quit_window)
    )
    
    # 创建托盘图标
    icon = pystray.Icon("name", image, "应用名称", menu)
    
    # 添加双击事件
    def on_double_click(icon, event):
        if event == pystray.Icon.DOUBLE_CLICK:
            show_window(icon, None)
    
    # 设置双击事件
    icon.on_click = on_double_click
    
    return icon

def show_window(icon, item):
    if window:
        window.show()
        window.restore()

def quit_window(icon, item):
    if window:
        window.destroy()
    if icon:
        icon.stop()

def on_shown():
    # print('程序启动')
    db.init()    # 初始化数据库

def on_loaded():
    print('DOM加载完毕')
    pass

def on_closing():
    window.hide()  # 隐藏窗口而不是关闭
    return False

def on_closed():
    try:
        print("正在关闭应用...")
        # 断开 WebSocket 连接
        api.disconnect()
        if icon:
            icon.stop()
    except Exception as e:
        print(f'关闭程序时出错: {e}')

def WebViewApp(ifCef=False):
    
    is_win = platform.system().lower() == 'windows'
    if is_win:
        pass
    else:
        debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
        Config.devEnv = debug_mode
    
    
    # 是否为开发环境

    # 视图层页面URL
    if Config.devEnv:
        # 开发环境
        MAIN_DIR = f'http://localhost:{Config.devPort}/'
        template = os.path.join(MAIN_DIR, "")    # 设置页面，指向远程
    else:
        # 生产环境
        MAIN_DIR = os.path.join(".", "web")
        template = os.path.join(MAIN_DIR, "index.html")    # 设置页面，指向本地

        # 修复某些情况下，打包后软件打开白屏的问题
        mimetypes.add_type('application/javascript', '.js')

    # 系统分辨率
    screens = webview.screens
    screens = screens[0]
    width = screens.width
    height = screens.height
    # 程序窗口大小
    initWidth = int(width * 2 / 3)
    initHeight = int(height * 4 / 5)
    minWidth = int(initWidth / 1)
    minHeight = int(initHeight / 2)

    global window, icon
    # 创建窗口
    window = webview.create_window(
        title=Config.appName, 
        url=template, 
        js_api=api, 
        width=initWidth, 
        height=initHeight, 
        min_size=(minWidth, minHeight)
    )

    # 获取窗口实例
    api.setWindow(window)

    # 绑定事件
    window.events.shown += on_shown
    window.events.loaded += on_loaded
    window.events.closing += on_closing
    window.events.closed += on_closed

    # 创建系统托盘图标（在主线程中）
    icon = create_tray_icon()
    icon.run_detached()

    # CEF模式
    guiCEF = 'cef' if ifCef else None

    # 启动窗口
    webview.start(debug=Config.devEnv, http_server=True, gui=guiCEF)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cef", action="store_true", dest="if_cef", help="if_cef")
    args = parser.parse_args()

    ifCef = args.if_cef    # 是否开启cef模式

    WebViewApp(ifCef)