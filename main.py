#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: 潘高
LastEditors: 潘高
Date: 2022-03-23 15:41:46
LastEditTime: 2024-09-08 20:29:41
Description: 生成客户端主程序
usage: 运行前，请确保本机已经搭建Python3开发环境，且已经安装 pywebview 模块。
'''

import argparse
import mimetypes
import os
import sys
import platform
import pystray
from PIL import Image
import webview
import threading

from api.api import API
from pyapp.config.config import Config
from pyapp.db.db import DB

cfg = Config()    # 配置
cfg.init()    # Initialize config first to set up app data directory
db = DB()    # 数据库类
api = API()    # 本地接口

# 全局变量
window = None
icon = None

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
        icon_path = os.path.join(application_path, "pyapp", "icon", "logo.png")
        image = Image.open(icon_path)
    except Exception as e:
        print(f"加载图标失败: {e}")
        # 如果找不到图标文件，创建一个默认的红色图标
        image = Image.new('RGB', (64, 64), color = 'red')
    
    menu = (
        pystray.MenuItem('显示', show_window),
        pystray.MenuItem('退出', quit_window)
    )
    return pystray.Icon("name", image, "应用名称", menu)

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
    # 是否为开发环境
    Config.devEnv = sys.flags.dev_mode

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
    minWidth = int(initWidth / 2)
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