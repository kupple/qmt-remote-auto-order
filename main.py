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
import time
import signal
import subprocess

from api.api import API
from pyapp.config.config import Config
from pyapp.db.db import DB

# 全局变量
window = None
icon = None
mutex = None
lock_file = None
is_quitting = False  # 退出标志

cfg = Config()    # 配置
cfg.init()    # Initialize config first to set up app data directory
db = DB()    # 数据库类
api = API()    # 本地接口

def create_mutex():
    """创建系统级互斥锁，确保应用只能运行一个实例"""
    global mutex, lock_file
    
    # 使用应用ID生成唯一互斥锁名称
    mutex_name = Config.appNameEN
    
    try:
        if platform.system() == "Windows":
            # Windows平台使用CreateMutex
            kernel32 = ctypes.windll.kernel32
            mutex = kernel32.CreateMutexW(None, False, mutex_name)
            error = kernel32.GetLastError()
            
            if error == 183:  # ERROR_ALREADY_EXISTS
                print("应用程序已在运行中！")
                activate_existing_instance()
                return False
        else:
            # Linux/macOS平台使用文件锁
            lock_file = os.path.join(cfg.appDataDir, ".app.lock")
            os.makedirs(os.path.dirname(lock_file), exist_ok=True)
            mutex = open(lock_file, 'w')
            
            try:
                import fcntl
                fcntl.flock(mutex, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("应用程序已在运行中！")
                activate_existing_instance()
                return False
                
        return True
    except Exception as e:
        print(f"创建互斥锁时出错: {e}")
        return True

def activate_existing_instance():
    """尝试激活已运行的实例窗口"""
    # 可通过socket或文件标记实现进程间通信
    # 此处简化处理，仅打印提示
    print("尝试激活已运行的实例...")

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
    icon = pystray.Icon("name", image, "自动下单", menu)
    
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

def force_exit():
    """强制退出程序（Windows平台）"""
    try:
        # 关闭数据库连接
        try:
            db.close()
        except:
            pass
        
        # 断开WebSocket连接
        try:
            api.disconnect()
        except:
            pass
        
        # 释放互斥锁
        if mutex:
            try:
                ctypes.windll.kernel32.ReleaseMutex(mutex)
            except:
                pass
        
        # 停止托盘图标
        if icon:
            try:
                icon.stop()
            except:
                pass
        
        # Windows平台强制终止进程
        current_pid = os.getpid()
        kernel32 = ctypes.windll.kernel32
        PROCESS_TERMINATE = 0x0001
        handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, current_pid)
        if handle:
            kernel32.TerminateProcess(handle, 0)
            kernel32.CloseHandle(handle)
        else:
            # 备用方案：使用taskkill
            try:
                subprocess.run(["taskkill", "/F", "/PID", str(current_pid)], timeout=2, check=False)
            except:
                pass
        
        # 最后的保障
        os._exit(0)
    except:
        os._exit(1)

def quit_window(icon, item):
    global is_quitting
    is_quitting = True  # 设置退出标志
    
    # 先尝试正常退出
    try:
        if window:
            window.destroy()  # 这会触发 on_closing 事件
        if icon:
            icon.stop()
    except Exception as e:
        print(f'正常退出失败: {e}')
    
    # 设置超时，如果3秒后还没退出，强制退出
    def force_exit_after_timeout():
        time.sleep(3)
        print('超时未退出，强制终止进程...')
        force_exit()
    
    threading.Thread(target=force_exit_after_timeout, daemon=True).start()

def on_shown():
    # print('程序启动')
    db.init()    # 初始化数据库

def on_loaded():
    print('DOM加载完毕')
    pass

def on_closing():
    global is_quitting
    # 如果是从托盘退出，允许关闭窗口
    if is_quitting:
        return True  # 允许关闭
    # 否则隐藏窗口而不是关闭
    window.hide()
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
        Config.devEnv = sys.flags.dev_mode
    else:
        debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
        Config.devEnv = debug_mode
    
    # 是否为开发环境
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

    # 创建系统托盘图标
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