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
is_quitting = False  # 退出状态标记

cfg = Config()    # 配置
cfg.init()    # Initialize config first to set up app data directory
db = DB()    # 数据库类
api = API()    # 本地接口

def create_mutex():
    """创建系统级互斥锁，确保应用只能运行一个实例"""
    global mutex, lock_file
    
    mutex_name = Config.appNameEN
    
    try:
        if platform.system() == "Windows":
            kernel32 = ctypes.windll.kernel32
            mutex = kernel32.CreateMutexW(None, False, mutex_name)
            error = kernel32.GetLastError()
            
            if error == 183:  # ERROR_ALREADY_EXISTS
                print("应用程序已在运行中！")
                activate_existing_instance()
                return False
        else:
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
    print("尝试激活已运行的实例...")

def create_tray_icon():
    # 创建系统托盘图标
    try:
        application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(application_path, "pyapp", "icon", "tray.png")
        image = Image.open(icon_path)
    except Exception as e:
        print(f"加载图标失败: {e}")
        image = Image.new('RGB', (64, 64), color='red')
        
    menu = (
        pystray.MenuItem('显示', show_window),
        pystray.MenuItem('退出', quit_window),
        pystray.MenuItem('default', lambda i, i2: None, default=True, visible=False)
    )
    
    icon = pystray.Icon("name", image, "应用名称", menu)
    icon.on_click = lambda i, e: show_window(i, None) if e == pystray.Icon.DOUBLE_CLICK else None
    return icon

def show_window(icon, item):
    if window:
        window.show()
        window.restore()

def force_quit_application():
    """强制终止进程，确保一次点击生效"""
    global is_quitting
    if is_quitting:
        return  # 避免重复执行
        
    is_quitting = True
    current_pid = os.getpid()
    print(f"强制退出进程 {current_pid}...")
    
    try:
        # 快速清理核心资源（减少一次点击无效的问题）
        if api:
            api.disconnect()
        if window:
            window.destroy()
        if icon:
            icon.stop()
        if mutex and platform.system() == "Windows":
            ctypes.windll.kernel32.ReleaseMutex(mutex)
        elif mutex:
            mutex.close()
            
    except:
        pass  # 清理失败时直接强制终止
    
    # 平台特定强制终止
    try:
        if platform.system() == "Windows":
            # 方法1: 直接调用Windows API
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x0001, False, current_pid)
            if handle:
                kernel32.TerminateProcess(handle, 0)
                kernel32.CloseHandle(handle)
                return
                
            # 方法2: 备用的taskkill命令
            subprocess.run(["taskkill", "/F", "/PID", str(current_pid)], timeout=2, check=False)
            
        elif platform.system() in ("Linux", "Darwin"):
            # 方法1: 调用C库发送SIGKILL
            try:
                libc = ctypes.CDLL("libc.so.6") if platform.system() == "Linux" else ctypes.CDLL("/usr/lib/libc.dylib")
                libc.kill(current_pid, 9)
                return
            except:
                pass
                
            # 方法2: 备用的os.kill
            os.kill(current_pid, signal.SIGKILL)
            
        # 通用兜底方案
        os._exit(0)
        
    except Exception as e:
        print(f"强制退出异常: {e}")
        os._exit(1)  # 终极兜底

def quit_window(icon, item):
    """处理退出事件，确保一次点击生效"""
    # 直接在新线程中执行强制退出，跳过中间状态
    threading.Thread(target=force_quit_application, daemon=True).start()

def on_shown():
    db.init()

def on_loaded():
    print('DOM加载完毕')

def on_closing():
    window.hide()
    return False  # 阻止窗口关闭按钮的默认行为

def on_closed():
    print("窗口已关闭")

def WebViewApp(ifCef=False):
    global window, icon
    
    is_win = platform.system().lower() == 'windows'
    Config.devEnv = sys.flags.dev_mode if is_win else os.environ.get("DEBUG", "false").lower() == "true"
    
    MAIN_DIR = f'http://localhost:{Config.devPort}/' if Config.devEnv else os.path.join(".", "web")
    template = MAIN_DIR if Config.devEnv else os.path.join(MAIN_DIR, "index.html")
    
    if not Config.devEnv:
        mimetypes.add_type('application/javascript', '.js')
    
    screens = webview.screens[0]
    initWidth, initHeight = int(screens.width * 2/3), int(screens.height * 4/5)
    minWidth, minHeight = initWidth, int(initHeight / 2)
    
    window = webview.create_window(
        title=Config.appName, 
        url=template, 
        js_api=api, 
        width=initWidth, 
        height=initHeight, 
        min_size=(minWidth, minHeight)
    )
    
    api.setWindow(window)
    window.events.shown += on_shown
    window.events.loaded += on_loaded
    window.events.closing += on_closing
    window.events.closed += on_closed
    
    icon = create_tray_icon()
    icon.run_detached()
    
    guiCEF = 'cef' if ifCef else None
    webview.start(debug=Config.devEnv, http_server=True, gui=guiCEF)

if __name__ == "__main__":
    if platform.system() == "Windows":
        multiprocessing.freeze_support()
    
    if not create_mutex():
        sys.exit(0)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cef", action="store_true", dest="if_cef")
    args = parser.parse_args()
    
    WebViewApp(args.if_cef)