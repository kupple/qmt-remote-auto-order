#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: 业务层API,供前端JS调用
usage: 在Javascript中调用window.pywebview.api.<methodname>(<parameters>)
"""


import time
from api.system import System
from api.db.orm import ORM
from api.remote import Remote
import json
import asyncio
from api.trade_controller import TradeController
from api.trading_related.task_scheduler import TaskScheduler
from api.trading_related.strategy_analyzer import analyze_stock_data
import threading
from api.system import System
from .tools.sys_config import get_os_type
import subprocess
import webview
import os
import logging
from datetime import datetime
import sys
from api.trading_related.deal import convert_stock_suffix
from dotenv import load_dotenv

from api.tools import common

load_dotenv()
from .global_params import G
from .trading_related.sync_data import sync_data_stocks_data
from .tools.common import (
    transition_code,
    revert_transition_code,
    create_ths_shortcut,
    open_ths_shortcut,
    get_ths_window_state,
    control_ths_window,
)
from api.httpserver.request_api import APIService

AUTO_CONNECTION_WS = int(os.getenv("AUTO_CONNECTION_WS", 1))
USE_FIXED_WS_URL = int(os.getenv("USE_FIXED_WS_URL", 0))
WS_URL_FIXED = os.getenv("WS_URL_FIXED")


class API(System):
    def __init__(self):
        """
        Initialize the API class.

        This constructor sets up the trade controller, initializes the task scheduler
        with various scheduled tasks, and starts a loop to sync stock data.

        Attributes:
            trade_controller (TradeController): Manages trade-related operations.
            remote (Remote): Facilitates remote operations with trade controller.
            thread1 (None): Placeholder for a thread object, currently not initialized.
            task_scheduler (TaskScheduler): Manages scheduled tasks related to trading.
            loop (asyncio.AbstractEventLoop): Asynchronous event loop for executing tasks.
        """
        self.trade_controller = TradeController()
        self.remote = Remote(self.trade_controller)
        self.http_service = APIService(self.trade_controller)

        self.thread1 = None

        self.task_scheduler = TaskScheduler(self.trade_controller)

        self.task_scheduler.schedule_national_debt(hour=15, minute=10)
        self.task_scheduler.schedule_new_stock(hour=10, minute=10)
        self.task_scheduler.schedule_new_bond(hour=10, minute=10)

        self.task_scheduler.schedule_save_all_data(hour=8, minute=56)

        self.loop = asyncio.get_event_loop()
        self.loop.run_in_executor(None, sync_data_stocks_data)



    def setWindow(self, window):
        """获取窗口实例"""
        System._window = window

    def storage_get(self, key):
        value = G.orm.get_storage_var(key)
        if key == "qmt_user_info":
            G.user_id = json.loads(value)["id"] if value else None

        """获取存储变量"""
        return value

    def storage_set(self, key, val):
        """设置存储变量"""
        G.orm.set_storage_var(key, val)

    def get_setting_config(self):
        config = G.orm.get_setting_config()
        G.run_model_type = config["run_model_type"]
        G.client_type = config["client_type"]
        return config

    def save_config(self, data):
        if "client_type" in data and data["client_type"] == 1:
            create_ths_shortcut(data["ths_path"] + "/xiadan.exe")
        G.orm.save_config(data)

    def add_account(self, data):
        if "client_type" in data and data["client_type"] == 1 and data.get("ths_path"):
            create_ths_shortcut(data["ths_path"] + "/xiadan.exe")
        return G.orm.add_account(data)

    def get_account_list(self):
        return G.orm.get_account_list()

    def delete_account(self, account_id):
        return G.orm.delete_account(account_id)

    def update_account(self, account_id, data):
        return G.orm.update_account(account_id, data)

    def connect_ws(self, server_url, ways=2, is_login=False):
        if AUTO_CONNECTION_WS == 1:
            if USE_FIXED_WS_URL == 1:
                server_url = WS_URL_FIXED
            G.orm.save_config({"server_url": server_url})
            self.thread1 = threading.Thread(
                target=self.remote.connect, args=(server_url, ways, is_login)
            )
            self.thread1.start()

    def disconnect(self):
        self.remote.close_ws()
        if self.thread1 and self.thread1.is_alive():
            self.thread1.join(timeout=1)  # Wait up to 1 second for thread to finish

    def connect_qmt(self):
        result = self.trade_controller.connect_qmt()
        return result

    def get_task_list(self, data):
        return G.orm.get_task_list(data)

    def get_account_task_list(self, data):
        return G.orm.get_account_task_list(data)

    def create_task(self, data):
        return G.orm.create_task(data)

    def run_task(self, data):
        st = ""
        if data["is_open"]:
            st = "开启"
        else:
            st = "关闭"
        message = data["name"] + "任务已" + st

        G.logger.info(message, extra={"showMessage": True})
        return G.orm.run_task(data)

    def delete_task(self, data):
        return G.orm.delete_task(data)

    def get_remote_state(self):
        return {
            "state": self.remote.is_connected,
            "unique_id": G.unique_id,
        }

    def get_unique_id(self):
        return G.unique_id

    def get_task_detail(self, data):
        return G.orm.get_task_detail(data)

    def transition_code(self, data, taskDic):
        return transition_code(data, taskDic)

    def revert_transition_code(self, data):
        return revert_transition_code(data)

    def get_order_list(self, data):
        return G.orm.get_order_list(data)

    def test_connect(self, path, type):
        return self.trade_controller.test_connect(path, type)

    def cancel_daily_task(self):
        """取消所有定时任务"""
        return self.task_scheduler.cancel_all_tasks()

    def check_strategy_code_exists(self, strategy_code):
        return G.orm.check_strategy_code_exists(strategy_code)

    def open_directory_dialog(self, client_type):
        """打开系统目录选择对话框（跨平台）"""
        os_type = get_os_type()

        if os_type == "windows":
            # Windows 直接使用 PyWebView 的文件夹选择对话框
            directory = System._window.create_file_dialog(
                webview.FOLDER_DIALOG,
                directory=os.path.expanduser("~"),
                allow_multiple=False,
            )
            path = directory[0] if directory else None
            if path != None:
                if client_type == 2:
                    dlls_path = os.path.join(path, "DLLs")
                    data_path = os.path.join(path, "data")
                    if os.path.exists(dlls_path) and os.path.exists(data_path):
                        return True, path
                    else:
                        return False, None
                else:
                    xiadan_path = os.path.join(path, "xiadan.exe")
                    if os.path.exists(xiadan_path):
                        return True, path
                    else:
                        return False, None

            else:
                return False, None

        elif os_type == "macos":
            if client_type == 2:
                return True, "D:\\长城策略交易系统new\\userdata_mini"
            else:
                return True, "D:\\同花顺\\xiadan.exe"

        else:
            return None

    def create_backtest(self, data):
        return G.orm.create_backtest(data)

    def query_backtest_by_task_id(self, task_id):
        result = G.orm.query_backtest_by_task_id(task_id)
        return result

    def count_strategy_analyzer(self, task_id, backtest_id):
        sample_trades = G.orm.count_strategy_analyzer(task_id, backtest_id)

        backtest = G.orm.query_backtest_by_id(backtest_id)

        if len(sample_trades) > 0:
            # 假设 trades 是你的交易数据列表
            result = analyze_stock_data(
                sample_trades, initial_capital=backtest["initial_capital"]
            )
            return result
        else:
            return None

    def get_position_by_task_id(self, task_id):
        list = G.orm.query_position_by_task_id(task_id)
        for item in list:
            if item["security_code"]:
                if item["security_code"] in G.stock_map["all_stock_code"]:
                    item["security_name"] = G.stock_map["all_stock_code"][
                        item["security_code"]
                    ]["name"]
                else:
                    item["security_name"] = "其他"
        return list

    def delete_position_by_id(self, id):
        return G.orm.delete_position_by_id(id)

    def update_position(self, id, params):
        return G.orm.update_position(id, params)

    def add_position(self, params):
        params["security_code"] = convert_stock_suffix(params["security_code"])
        return G.orm.add_position(params)

    def check_position_exists(self, security_code, task_id):
        return G.orm.check_position_exists(convert_stock_suffix(security_code), task_id)

    def update_task(self, task_id, can_use_amount):
        return G.orm.update_task(task_id, can_use_amount=can_use_amount)

    def query_trade_today(self, task_id):
        return G.orm.query_trade_today(task_id)

    def query_log_list(self, data):
        return G.orm.query_log_list(data, page=data["page"], page_size=data["pageSize"])

    def clear_log(self):
        return G.orm.clear_log()

    def get_account_info(self, account_id=None):
        account = G.orm.get_account_by_id(account_id) if account_id else None
        return self.trade_controller.get_account_info(account)

    def is_process_exist_action(self,account_id):
        return self.trade_controller.process_check_loop()

    def open_ths_shortcut_action(self):
        config = G.orm.get_setting_config()
        return open_ths_shortcut(config["ths_path"] + "/autoxiadan.lnk")

    def get_ths_window_state_action(self,account_id):
        if sys.platform.startswith("darwin"):
            return True
        return get_ths_window_state()

    def control_ths_window_action(self, show: bool):
        if sys.platform.startswith("darwin"):
            return True
        control_ths_window(show)

    def open_http_server_action(self, open, host, port):
        if open:
            G.orm.set_storage_var("open_api_server", "1")
            G.orm.set_storage_var("http_server_host", host)
            G.orm.set_storage_var("http_server_port", port)
            self.http_service.start(host=host, port=port)
        else:
            G.orm.set_storage_var("open_api_server", "0")
            self.http_service.stop()

    def is_http_server_running_action(self):
        return self.http_service.is_running()


    def get_all_xtminiqmt_processes(self):
        return common.get_all_xtminiqmt_processes()

    def program_start(self):
        if G.orm.get_storage_var("open_api_server") == "1":
            host = G.orm.get_storage_var("http_server_host")
            port = G.orm.get_storage_var("http_server_port")
            self.http_service.start(host=host, port=port)
            G.logger.info(
                "api服务已启动 host:" + host + " port:" + port,
                extra={"showMessage": True},
            )

    def get_remote_position(self, task_id):
        list = G.orm.get_remote_position(task_id)
        for item in list:
            if item["security_code"]:
                if item["security_code"] in G.stock_map["all_stock_code"]:
                    item["security_name"] = G.stock_map["all_stock_code"][
                        item["security_code"]
                    ]["name"]
                else:
                    item["security_name"] = "其他"
        return list

    def reset_remote_position(self, task_id):
        return G.orm.reset_remote_position(task_id)

    # 一键清空持仓股票
    def clear_all_stock_by_task_id(self, task_id):
        try:
            stock_list = G.orm.query_position_by_task_id(task_id)
            task_detail = G.orm.get_task_detail({"id": task_id})
            # 获取全推行情
            full_tick = self.trade_controller.qmt_trader.data.get_full_tick(
                [item["security_code"] for item in stock_list]
            )

            for item in stock_list:
                price = full_tick[item["security_code"]]["lastPrice"]
                saveData = {
                    "security_code": item["security_code"],
                    "style": 1,
                    "platform": "joinquant",
                    "run_params": 'sim_trade',
                    "strategy_code": task_detail["strategy_code"],
                    "fix_result_order_id": None,
                    "is_buy": 0,
                    "avg_cost": price,
                    "commission": 0,
                    "add_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": item['volume'],
                    "price": price,
                    "status": 0,
                    "positions": json.dumps([x["security_code"] for x in stock_list]),
                }
                orderId = G.orm.save_order(saveData)
                orderId = str(orderId)
                self.trade_controller.place_order(
                    stock_code=item["security_code"],
                    volume=item["volume"],
                    price=full_tick[item["security_code"]]["lastPrice"],
                    is_buy=False,
                    order_time=None,
                    task_id=task_id,
                    order_remark=orderId,
                    is_mock_state=0,
                )
            return True
        except Exception as e:
            G.logger.error("clear_all_stock_by_task_id 发生异常: " + str(e),extra={
            "showMessage": True
            })

    def sync_position_action_by_task_id(self, task_id):
        try:
            # 检查 QMT 连接状态
            if not self.trade_controller.acc_is_connect:
                G.logger.error("QMT未连接，无法同步持仓", extra={"showMessage": True})
                return False

            # 获取持仓的股票列表
            local_stock_list = G.orm.query_position_by_task_or_backtest_id(task_id=task_id)
            # 获取远程端股票列表
            remote_stock_list = G.orm.get_remote_position(task_id)
            # 获取任务详情
            task_detail = G.orm.get_task_detail({"id": task_id})
            print(task_detail)

            full_tick = self.trade_controller.qmt_trader.data.get_full_tick(
                [item["security_code"] for item in remote_stock_list]
            )

            remote_total_value = sum(full_tick[item["security_code"]]["lastPrice"] * item["volume"] for item in remote_stock_list)
            if task_detail['order_count_type'] == 1:
                for stocksItem in remote_stock_list:
                    remote_num = (stocksItem["volume"] * task_detail["position_ratio"]) // 100 * 100
                    remote_num = int(remote_num)
                    local_stock_item = next((x['volume'] for x in local_stock_list if x["security_code"] == stocksItem["security_code"]), 0)
                    final_amount = 0
                    price = full_tick[stocksItem["security_code"]]["lastPrice"]
                    if remote_num > local_stock_item:
                        is_buy = 1
                        final_amount = abs(remote_num - local_stock_item)
                    else:
                        is_buy = 0
                        final_amount = abs(local_stock_item - remote_num)

                    # 跳过无需下单的场景
                    if final_amount == 0:
                        continue

                    saveData = {
                        "security_code": stocksItem["security_code"],
                        "style": 1,
                        "platform": "joinquant",
                        "run_params": 'sim_trade',
                        "strategy_code": task_detail["strategy_code"],
                        "fix_result_order_id": None,
                        "is_buy": is_buy,
                        "avg_cost": price,
                        "commission": 0,
                        "add_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": final_amount,
                        "price": price,
                        "status": 0,
                        "positions": json.dumps([x["security_code"] for x in remote_stock_list]),
                    }
                    orderId = G.orm.save_order(saveData)
                    orderId = str(orderId)
                    self.trade_controller.place_order(
                        stock_code=stocksItem["security_code"],
                        volume=final_amount,
                        price=price,
                        is_buy=True if is_buy == 1 else False,
                        order_time=None,
                        task_id=str(task_detail["id"]),
                        order_remark=orderId,
                        is_mock_state=0,
                        open_mandatory_limit_order=task_detail['open_mandatory_limit_order']
                    )
            else:
                # 获取全推行情

                # 计算所有股票的总市值

                dynamic_calculation_type = task_detail["dynamic_calculation_type"]

                allocation_amount = 0
                if dynamic_calculation_type == 1:
                    allocation_amount = task_detail["allocation_amount"]
                elif dynamic_calculation_type == 2:
                    can_use_amount = task_detail["can_use_amount"]
                    position_total_value = sum(full_tick[item["security_code"]]["lastPrice"] * item["volume"] for item in local_stock_list)
                    allocation_amount = round(can_use_amount + position_total_value, 2)

                if allocation_amount == 0:
                    print("可用资金不足")
                    return False

                for item in remote_stock_list:
                    security_code = item["security_code"]
                    volume = item["volume"]
                    price = full_tick[security_code]["lastPrice"]
                    stock_value = price * volume
                    actual_stock_value = stock_value * allocation_amount / remote_total_value
                    stock_volume = actual_stock_value / price
                    stock_volume = (stock_volume // 100) * 100

                    local_stock_item = next((x['volume'] for x in local_stock_list if x["security_code"] == item["security_code"]), 0)
                    final_amount = 0
                    is_buy = 1
                    if stock_volume > local_stock_item:
                        is_buy = 1
                        final_amount = abs(stock_volume - local_stock_item)
                    else:
                        is_buy = 0
                        final_amount = abs(local_stock_item - stock_volume)

                    saveData = {
                        "security_code": item["security_code"],
                        "style": 1,
                        "platform": "joinquant",
                        "run_params": 'sim_trade',
                        "strategy_code": task_detail["strategy_code"],
                        "fix_result_order_id": None,
                        "is_buy": is_buy,
                        "avg_cost": price,
                        "commission": 0,
                        "add_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": final_amount,
                        "price": price,
                        "status": 0,
                        "positions": json.dumps([it["security_code"] for it in remote_stock_list]),
                        "total_value": remote_total_value,
                    }
                    orderId = G.orm.save_order(saveData)
                    orderId = str(orderId)
                    self.trade_controller.place_order(
                        stock_code=item["security_code"],
                        volume=final_amount,
                        price=price,
                        is_buy=True if is_buy == 1 else False,
                        order_time=None,
                        task_id=str(task_detail["id"]),
                        order_remark=orderId,
                        open_mandatory_limit_order=task_detail['open_mandatory_limit_order']
                    )


        except Exception as e:
            G.logger.error("sync_position_action_by_task_id 发生异常: " + str(e),extra={
            "showMessage": True
            })
        
