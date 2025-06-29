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
import multiprocessing
import ctypes
from ctypes import wintypes
import time

from api.api import API
from pyapp.config.config import Config
from pyapp.db.db import DB

# 全局变量
window = None
icon = None
mutex = None  # 新增：用于存储互斥锁对象

cfg = Config()    # 配置
cfg.init()    # Initialize config first to set up app data directory
db = DB()    # 数据库类
api = API()    # 本地接口

def create_mutex():
    """创建系统级互斥锁，确保应用只能运行一个实例"""
    global mutex
    
    # 为互斥锁生成一个唯一名称，使用应用ID确保唯一性
    mutex_name = Config.appNameEN  # 使用应用的唯一标识符
    
    try:
        if platform.system() == "Windows":
            # Windows平台使用CreateMutex
            kernel32 = ctypes.windll.kernel32
            mutex = kernel32.CreateMutexW(None, False, mutex_name)
            error = kernel32.GetLastError()
            
            if error == 183:  # ERROR_ALREADY_EXISTS
                print("应用程序已在运行中！")
                # 尝试激活已运行的实例窗口
                activate_existing_instance()
                return False
        else:
            import fcntl
            # Linux/macOS平台使用文件锁
            lock_file = os.path.join(cfg.appDataDir, ".app.lock")
            mutex = open(lock_file, 'w')
            
            try:
                fcntl.flock(mutex, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("应用程序已在运行中！")
                # 尝试激活已运行的实例窗口
                activate_existing_instance()
                return False
                
        return True
    except Exception as e:
        print(f"创建互斥锁时出错: {e}")
        # 发生错误时不阻止应用启动
        return True

def activate_existing_instance():
    """尝试激活已运行的实例窗口（需要配合进程间通信实现）"""
    # 这里可以添加代码尝试与已运行的实例通信并激活其窗口
    # 简单实现可以通过socket或文件标记来通知已运行的实例
    pass

def release_mutex():
    """释放系统级互斥锁"""
    global mutex
    
    try:
        if mutex:
            if platform.system() == "Windows":
                ctypes.windll.kernel32.ReleaseMutex(mutex)
            else:
                import fcntl
                fcntl.flock(mutex, fcntl.LOCK_UN)
                mutex.close()
    except Exception as e:
        print(f"释放互斥锁时出错: {e}")

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
    def default_action(icon, item):
        show_window(icon, None)
        return True
    
    # 创建菜单项
    menu = (
        pystray.MenuItem('显示', show_window),
        pystray.MenuItem('退出', quit_window),
        pystray.MenuItem('default', default_action, default=True, visible=False)
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
    release_mutex()  # 新增：退出时释放互斥锁

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
        release_mutex()  # 新增：关闭时释放互斥锁
    except Exception as e:
        print(f'关闭程序时出错: {e}')

def WebViewApp(ifCef=False):
    
    is_win = platform.system().lower() == 'windows'
    if is_win:
        Config.devEnv = sys.flags.dev_mode
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
    # 确保在Windows上正确处理多进程
    if platform.system() == "Windows":
        multiprocessing.freeze_support()
    
    # 创建互斥锁，检查应用是否已在运行
    if not create_mutex():
        sys.exit(0)  # 应用已在运行，退出当前实例
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cef", action="store_true", dest="if_cef", help="if_cef")
    args = parser.parse_args()

    ifCef = args.if_cef    # 是否开启cef模式

    WebViewApp(ifCef)