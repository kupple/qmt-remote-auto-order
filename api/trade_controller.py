#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .trading_related.qmt_trader import qmt_trader
import sys

import platform
from api.system import System
from .trading_related.deal import (
    convert_stock_suffix,
    calculate_stock_fee,
    calculate_dividend_effect,
    get_qmt_price_type,
)
from datetime import datetime
from .trading_related.additional_data import stock_xgsglb_em_on_today, bond_zh_cov
from .trading_related.qmt_trading_simulator import (
    QmtTradingSimulator,
    OrderType,
    PriceType,
)
from decimal import Decimal
import json
import os
from api.global_params import G
import threading
import asyncio
from .tools.common import get_all_xtminiqmt_processes, check_mini_qmt_path_match
from threading import Timer
from .trading_related.trader_call_back import MyXtQuantTraderCallback
from .trading_related.ths_blocking_queue import NonBlockingQueue
from .trading_related.ths_auto import ThsAuto
from dataclasses import dataclass


@dataclass
class TraderRuntimeState:
    info: dict
    trader: qmt_trader
    qmt_is_connect: bool = False
    acc_is_connect: bool = False
    ths_is_connect: bool = False
    is_ths_need_reconnection: bool = True
    is_ths_need_reconnection_lock: bool = False
    is_qmt_need_reconnection: bool = True
    is_qmt_need_reconnection_lock: bool = False


class TradeController:
    def __init__(self):
        # self.qmt_trader = qmt_trader()
        self.multiple_traders = {}
        self.multiple_traders_lock = threading.RLock()
        # 同花顺队列
        self.ths_queue = NonBlockingQueue()
        self.callback = MyXtQuantTraderCallback(False)
        self.simulator = None
        self._thread = None

        self.ths_auto = ThsAuto()

        self.consumer_thread = self.ths_queue.start_consumer(self.ths_deal_order)
        self.refresh_multe_trader_arr()
        # self.process_check_loop()

    def refresh_multe_trader_arr(self):
        with self.multiple_traders_lock:
            # 先释放旧的 trader 连接，避免资源泄漏
            for trader_state in self.multiple_traders.values():
                trader = trader_state.trader
                if trader is not None:
                    try:
                        trader.disconnection_qmt()
                    except Exception:
                        pass

            # 清空容器，移除对旧对象的引用
            self.multiple_traders.clear()

            account_list = G.orm.get_account_list()
            for item in account_list:
                if item["status"] == 1:
                    self.multiple_traders[item["id"]] = TraderRuntimeState(
                        info=item,
                        trader=qmt_trader(),
                    )

    # 同花顺处理订单
    def ths_deal_order(self, order):
        result = self.ths_auto.get_balance()
        # order_type = order['order_type']
        # if order_type == OrderType.STOCK_BUY:
        #   self.ths_auto.buy(order['stock_code'],order['volume'],order['price'])
        # elif order_type == OrderType.STOCK_SELL:
        #   self.ths_auto.sell(order['stock_code'],order['volume'],order['price'])
        # stock_code = order['stock_code']
        # volume = order['volume']
        # price = order['price']
        # order_time = order['order_time']
        # price_type = order['price_type']
        # strategy_name = order['strategy_name']
        # order_remark = order['order_remark']
        # "stock_code": stock_code,
        # "volume": volume,
        # "price": optimal_price,
        # "order_type": order_type,
        # "order_time": order_time,
        # "price_type": price_type,
        # "strategy_name": strategy_name,
        # "order_remark": order_remark
        pass

    # 检测账号是否开启订阅功能
    def process_check_loop(self):
        try:
            xt_list = get_all_xtminiqmt_processes()  # 直接调用，不需要await
            with self.multiple_traders_lock:
                for acc_id, trader_state in self.multiple_traders.items():
                    account_info = trader_state.info
                    
                    client_type = account_info.get("client_type")
                    mini_qmt_path = account_info.get("mini_qmt_path")
                    client_id = account_info.get("client_id")

                    if client_type == 2:
                        qmt_is_connect = check_mini_qmt_path_match(
                            account_info, xt_list
                        )
                        # print(qmt_is_connect)
                        # print(account_info)
                        # print(xt_list)
                        System.system_py2js(
                            self, "remoteCallBack", {"type": "qmtProcessCheck", "event": {
                                "id":acc_id,
                                "status":qmt_is_connect
                            }}
                        )
                        if qmt_is_connect:
                            if (
                                trader_state.is_qmt_need_reconnection == True
                                and trader_state.is_qmt_need_reconnection_lock == True
                            ):
                                trader_state.is_qmt_need_reconnection = False
                                if mini_qmt_path != "" and client_id != "":
                                    G.logger.info(
                                        f"{client_id}:重新连接QMT",
                                        extra={"showMessage": True},
                                    )
                                trader_state.is_qmt_need_reconnection_lock = True
                                self.connect_qmt(acc_id=acc_id)
                        else:
                            trader_state.is_qmt_need_reconnection = True
        except Exception as e:
            import traceback

            tb = traceback.extract_tb(e.__traceback__)
            line_no = tb[-1].lineno if tb else "unknown"
            error_msg = f"进程检查出错(行号: {line_no}): {str(e)}"
            if G.logger:
                G.logger.error(error_msg)

    def connect_qmt(self, acc_id):
        try:
            # 设置id
            account_info = self.multiple_traders[acc_id].info
            mini_qmt_path = account_info.get("mini_qmt_path")
            client_id = account_info.get("client_id")

            # 如果是mac 电脑开发环境直接返回成功
            if sys.platform.startswith("darwin"):
                self.multiple_traders[acc_id].acc_is_connect = True
                System.system_py2js(
                    self,
                    "remoteCallBack",
                    {
                        "type": "accSubSuccess",
                        "message": f"QMT{client_id}账号订阅成功",
                        "event": {"id": acc_id, "status": True},
                    },
                )
                return True
            # 1. 拆分路径：获取父目录
            parent_dir = os.path.dirname(mini_qmt_path)
            # 2. 拼接新的最后一级目录
            new_path = os.path.join(parent_dir, "userdata_mini")

            self.multiple_traders[acc_id].trader.path = new_path
            self.multiple_traders[acc_id].trader.account = client_id
            print(mini_qmt_path)
            # 连接QMT 传递回调
            is_connect = self.multiple_traders[acc_id].trader.connect(self.callback)
            self.multiple_traders[acc_id].acc_is_connect = is_connect
            print(is_connect)
            if self.multiple_traders[acc_id].acc_is_connect:
                message = "QMT连接成功"
            else:
                message = "QMT连接失败"

            print("zxczxc3")
            System.system_py2js(
                self,
                "remoteCallBack",
                {
                    "type": "accSubSuccess",
                    "message": message,
                    "event": {
                        "id": acc_id,
                        "status": self.multiple_traders[acc_id].acc_is_connect,
                    },
                },
            )
            self.multiple_traders[acc_id].is_qmt_need_reconnection_lock = False
        except Exception as e:
            G.logger.error("连接QMT失败! code 1980" + str(e))
            self.is_qmt_need_reconnection_lock = False

    # 购买国债逆回购（多账号）
    def buy_reverse_repo(self, account_id=None):
        trade_date_list = G.orm.get_trade_date_list()
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str not in trade_date_list:
            G.logger.info(
                "今日不是交易日，不执行自动购入国债逆回购", extra={"showMessage": True}
            )
            return

        with self.multiple_traders_lock:
            trader_state = self.multiple_traders.get(account_id)
        if not trader_state or trader_state.info.get("client_type") != 2:
            return

        G.logger.info(
            f"正在执行自动购入国债逆回购, 账号: {trader_state.info.get('client_id')}",
            extra={"showMessage": True},
        )
        judge, text = trader_state.trader.reverse_repurchase_of_treasury_bonds()

        if judge:
            G.logger.info(text, extra={"showMessage": True})
        else:
            G.logger.error(text, extra={"showMessage": True})

    def auto_buy_new_stock(self, account_id=None):
        trade_date_list = G.orm.get_trade_date_list()
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str not in trade_date_list:
            G.logger.info("今日不是交易日，不执行自动打新", extra={"showMessage": True})
            return

        with self.multiple_traders_lock:
            trader_state = self.multiple_traders.get(account_id)
        if not trader_state or trader_state.info.get("client_type") != 2:
            return

        G.logger.info(
            f"正在执行自动打新, 账号: {trader_state.info.get('client_id')}",
            extra={"showMessage": True},
        )
        df = stock_xgsglb_em_on_today()
        selected_columns = ["申购代码", "申购上限", "发行价格"]
        for _, row in df[selected_columns].iterrows():
            code = row["申购代码"]
            limit = row["申购上限"]
            price = row["发行价格"]
            G.logger.info(
                "申购代码: {} 申购上限: {} 发行价格: {}".format(code, limit, price),
                extra={"showMessage": True},
            )
            codeSt = convert_stock_suffix(code)
            trader_state.trader.buy(codeSt, limit, price, order_remark="打新")

    def auto_buy_convertible_bond(self, account_id=None):
        trade_date_list = G.orm.get_trade_date_list()
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str not in trade_date_list:
            G.logger.info("今日不是交易日，不执行自动打债", extra={"showMessage": True})
            return

        with self.multiple_traders_lock:
            trader_state = self.multiple_traders.get(account_id)
        if not trader_state or trader_state.info.get("client_type") != 2:
            return

        G.logger.info(
            f"正在执行自动打债, 账号: {trader_state.info.get('client_id')}",
            extra={"showMessage": True},
        )
        df = bond_zh_cov()
        selected_columns = ["申购代码", "申购上限"]

        for _, row in df[selected_columns].iterrows():
            code = row["申购代码"]
            limit = row["申购上限"]
            price = 100
            limit = limit * 10000
            codeSt = convert_stock_suffix(code)
            trader_state.trader.buy(codeSt, limit, price, order_remark="打债")

    def calculate_stock_returns(self, saveData, order_count_type):

        positions_arr = G.orm.query_position_by_task_or_backtest_id(
            backtest_id=saveData["backtest_id"]
        )
        position_total_value = 0
        positions = json.loads(saveData["positions"])

        for position in positions_arr:
            for order_position in positions:
                if position["security_code"] == convert_stock_suffix(
                    order_position["security"]
                ):
                    position_total_value += position["volume"] * order_position["price"]
                    continue

        backtest = G.orm.query_backtest_by_id(saveData["backtest_id"])
        G.orm.update_backtest(
            saveData["backtest_id"],
            final_amount=position_total_value + backtest["can_use_amount"],
        )

    #  计算配置仓位
    def order_on_pro_rata_basis(
        self, orderDic: dict, task: dict, backtest_id: int = None
    ) -> int:
        if task["order_count_type"] == 1:
            num = (orderDic["amount"] * task["position_ratio"]) // 100 * 100
            num = int(num)
            return num
        else:
            # 获取当前持仓
            total_value = round(orderDic["total_value"], 2)
            is_buy = orderDic["is_buy"]

            # 实际持仓
            actual_position_volume = 0
            positions = json.loads(orderDic["positions"])
            actual_position_volume = next(
                (
                    p["total_amount"]
                    for p in positions
                    if convert_stock_suffix(p["security"]) == orderDic["security_code"]
                ),
                0,
            )

            if is_buy == 1:
                actual_position_volume += orderDic["amount"]
            else:
                actual_position_volume -= orderDic["amount"]
            dynamic_calculation_type = task["dynamic_calculation_type"]
            accruing_amounts = 0

            positions_arr = G.orm.query_position_by_task_or_backtest_id(
                backtest_id=backtest_id, task_id=task["id"]
            )
            position_total_value = 0
            for position in positions_arr:
                for order_position in positions:
                    if position["security_code"] == convert_stock_suffix(
                        order_position["security"]
                    ):
                        position_total_value += (
                            position["volume"] * order_position["price"]
                        )
                        continue

            # 固定仓位模式
            if dynamic_calculation_type == 1:
                if backtest_id:
                    accruing_amounts = G.orm.query_backtest_by_id(backtest_id)[
                        "initial_capital"
                    ]
                else:
                    accruing_amounts = task["allocation_amount"]
            # 根据盈亏分配
            elif dynamic_calculation_type == 2:
                can_use_amount = 0
                if backtest_id:
                    can_use_amount = G.orm.query_backtest_by_id(backtest_id)[
                        "can_use_amount"
                    ]
                else:
                    can_use_amount = task["can_use_amount"]
                    accruing_amounts = round(can_use_amount + position_total_value, 2)

            # 计算配置仓位
            allocation_amount = round(
                actual_position_volume * accruing_amounts / total_value, 2
            )
            print(
                allocation_amount, accruing_amounts, actual_position_volume, total_value
            )
            final_amount = 0
            allocation_amount = (allocation_amount // 100) * 100
            allocation_amount = int(allocation_amount)

            position = next(
                (
                    item
                    for item in positions_arr
                    if item.get("security_code") == orderDic["security_code"]
                ),
                None,
            )
            if position:
                final_amount = abs(allocation_amount - position["volume"])
            else:
                if is_buy == 1:
                    final_amount = allocation_amount

            return final_amount

    # 统一处理-下单接口
    def place_order(
        self,
        stock_code="600031.SH",
        volume=100,
        price=20,
        is_buy=True,
        order_time=None,
        order_style_str="",
        task_id="",
        order_remark="",
        is_mock_state=1,
        open_mandatory_limit_order=0,
        account_id=None,
    ):

        price_type, optimal_price = get_qmt_price_type(
            stock_code,
            order_style_str,
            is_buy,
            price,
            open_mandatory_limit_order,
            is_mock_state,
        )

        order_type = OrderType.STOCK_BUY if is_buy == 1 else OrderType.STOCK_SELL
        System.system_py2js(
            self,
            "remoteCallBack",
            {
                "message": "下单数量: "
                + str(volume)
                + " 价格: "
                + str(optimal_price)
                + " 股票代码: "
                + stock_code
                + " 方向: "
                + ("买入" if is_buy == 1 else "卖出"),
            },
        )

        account_client_type = None
        trader = None
        if account_id is not None:
            with self.multiple_traders_lock:
                trader_state = self.multiple_traders.get(account_id)
                if trader_state:
                    account_client_type = trader_state.info.get("client_type")
                    trader = trader_state.trader

        if is_mock_state == 0:
            if account_client_type is None:
                G.logger.error(
                    f"未找到账号类型 account_id={account_id}",
                    extra={"showMessage": True},
                )
                return

            # 如果是同花顺类型
            if account_client_type == 1:
                self.ths_queue.enqueue(
                    {
                        "stock_code": stock_code,
                        "volume": volume,
                        "price": optimal_price,
                        "order_type": order_type,
                        "order_time": order_time,
                        "price_type": price_type,
                        "strategy_name": task_id,
                        "order_remark": order_remark,
                    }
                )
            else:
                if trader is None:
                    G.logger.error(
                        f"未找到账号对应的交易实例 account_id={account_id}",
                        extra={"showMessage": True},
                    )
                    return

                trader.place_order(
                    stock_code=stock_code,
                    volume=int(volume),
                    price=optimal_price,
                    order_type=order_type,
                    price_type=price_type,
                    strategy_name=task_id,
                    order_remark=order_remark,
                )
        elif is_mock_state == 1:
            self.simulator.place_order(
                stock_code=stock_code,
                volume=volume,
                price=optimal_price,
                order_type=order_type,
                order_time=order_time,
                price_type=price_type,
                strategy_name=task_id,
                order_remark=order_remark,
            )
        elif is_mock_state == 2:
            if account_client_type is None:
                G.logger.error(
                    f"未找到账号类型 account_id={account_id}",
                    extra={"showMessage": True},
                )
                return

            if account_client_type == 2:
                mockCallback = MyXtQuantTraderCallback(False, is_pre=True)
                self.simulator = QmtTradingSimulator(
                    2,
                    mockCallback,  # 回测环境
                )
                self.simulator.place_order(
                    stock_code=stock_code,
                    volume=volume,
                    price=optimal_price,
                    order_type=order_type,
                    price_type=price_type,
                    order_time=order_time,
                    strategy_name=task_id,
                    order_remark=order_remark,
                )
            else:
                self.ths_queue.enqueue(
                    {
                        "stock_code": stock_code,
                        "volume": volume,
                        "price": optimal_price,
                        "order_type": order_type,
                        "order_time": order_time,
                        "price_type": price_type,
                        "strategy_name": task_id,
                        "order_remark": order_remark,
                    }
                )
        else:
            G.logger.error("is_mock_state参数错误")

    def manage_api_trader(self, data):
        try:
            if G.run_model_type == 2:
                user_id = G.user_id
            else:
                user_id = G.unique_id
            taskList = G.orm.get_task_list({"user_id": str(user_id)})
            task = next(
                (
                    item
                    for item in taskList
                    if item.get("strategy_code") == data["strategy_code"]
                ),
                None,
            )
            if not task:
                G.logger.info(
                    "任务不存在: {}".format(data["strategy_code"]),
                    extra={"showMessage": True},
                )
                return False, "任务不存在"

            strategy_code = data.get("strategy_code")
            stock_code = data.get("stock_code")
            volume = data.get("volume")
            price = data.get("price")
            order_type = data.get("order_type", 1)
            is_buy = data.get("is_buy", 1)

            saveData = {
                "security_code": stock_code,
                "style": order_type,
                "platform": "api",
                "strategy_code": strategy_code,
                "is_buy": is_buy,
                "add_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": volume,
                "price": price,
                "status": 0,
            }
            orderId = G.orm.save_order(saveData)
            orderId = str(orderId)

            self.place_order(
                stock_code=stock_code,
                volume=volume,
                price=price,
                is_buy=True if is_buy == 1 else False,
                order_time=None,
                order_style_str=order_type,
                task_id=str(task["id"]),
                order_remark=orderId,
                is_mock_state=0,
                account_id=task.get("account_id"),
            )
            return True, "下单成功"
        except Exception as e:
            G.logger.error(
                "manage_api_trader参数错误: {}".format(e), extra={"showMessage": True}
            )
            return False, str(e)

    # 下单协议{code:code,price:price,amount:amount,type:type}
    def manage_platform_trader(self, data):
        try:
            strategy_code = data["strategy_code"]
            run_params = data["run_params"]
            state = data["state"]
            # 获取参数
            security = data["params"]["security"]
            style = data["params"]["style"]
            price = data["params"]["price"]
            amount = data["params"]["amount"]
            avg_cost = data["params"]["avg_cost"]
            commission = data["params"]["commission"]
            is_buy = data["params"]["is_buy"]
            add_time = data["params"]["add_time"]
            positions = data["positions"]
            dividends = data["dividends"]
            # 总金额
            total_value = data["params"]["total_value"]
            # 转换code
            security = convert_stock_suffix(security)
            positions_arr = json.dumps(positions)

            saveData = {
                "security_code": security,
                "style": style,
                "platform": "joinquant",
                "run_params": run_params,
                "strategy_code": strategy_code,
                "fix_result_order_id": None,
                "is_buy": is_buy,
                "avg_cost": avg_cost,
                "commission": commission,
                "add_time": add_time,
                "amount": amount,
                "price": price,
                "status": 0,
                "positions": positions_arr,
                "total_value": total_value,
            }

            if G.run_model_type == 2:
                user_id = G.user_id
            else:
                user_id = G.unique_id

            taskList = G.orm.get_task_list({"user_id": str(user_id)})
            task = next(
                (
                    item
                    for item in taskList
                    if item.get("strategy_code") == strategy_code
                ),
                None,
            )
            if not task:
                G.logger.info(
                    "任务不存在: {}".format(strategy_code), extra={"showMessage": True}
                )
                return
            # 获取任务类型 1是跟随 2是动态
            order_count_type = task["order_count_type"]

            # 不是模拟环境不能受理
            if run_params == "simple_backtest" or run_params == "full_backtest":
                #####################     回测环境     ###########################
                if state == "begin":
                    if task["order_count_type"] == 2:
                        accruing_amounts = task["mock_allocation_amount"]
                        can_use_amount = task["mock_allocation_amount"]
                        initial_capital = task["mock_allocation_amount"]
                    else:
                        accruing_amounts = total_value
                        can_use_amount = total_value
                        initial_capital = total_value
                    # 创建一个回测
                    backtest_id = G.orm.create_backtest(
                        {
                            "name": strategy_code,
                            "service_charge": task["mock_service_charge"],
                            "lower_limit_of_fees": task["mock_lower_limit_of_fees"],
                            "final_amount": 0,
                            "task_id": task["id"],
                            "state": state,
                            "order_count_type": order_count_type,
                            "initial_capital": initial_capital,
                            "accruing_amounts": accruing_amounts,
                            "can_use_amount": can_use_amount,
                        }
                    )
                    G.orm.update_task(task["id"], backtest_id=backtest_id)
                    # 设置回测id
                    self.mockCallback = MyXtQuantTraderCallback(True, backtest_id)
                    self.simulator = QmtTradingSimulator(
                        1 if task["is_simulation"] == True else 0,  # 是否需要仿真回测
                        self.mockCallback,  # 回测环境
                    )
                if state == "dividends":
                    if dividends == None:
                        return
                    if len(dividends) == 0:
                        return
                    backtest_id = task["backtest_id"]
                    positions = G.orm.query_position_by_task_or_backtest_id(
                        backtest_id=backtest_id, task_id=task["id"]
                    )
                    positions_dict = {
                        position["security_code"]: position for position in positions
                    }
                    if security in positions_dict:
                        position = positions_dict[security]
                        dividend = dividends[0]
                        effect = calculate_dividend_effect(
                            security_code=security,
                            holding_shares=position["volume"],
                            purchase_price=price,
                            bonus_pre_tax=dividend["bonus_pre_tax"],
                            scale_factor=dividend["scale_factor"],
                        )
                        G.orm.update_position(
                            position["id"],
                            {
                                "volume": effect["new_shares"],
                                "backtest_id": backtest_id,
                                "task_id": task["id"],
                                "average_price": effect["new_cost_per_share"],
                            },
                        )
                        # G.orm.update_task_can_use_amount(backtest_id,task['id'], round(position['volume'] * dividends[0]['scale_factor'],2))
                if state == "end":
                    saveData["backtest_id"] = task["backtest_id"]
                    self.calculate_stock_returns(saveData, order_count_type)
                    G.orm.update_backtest(task["backtest_id"], state=state)
                if state == "run":
                    # 创建空订单
                    saveData["backtest_id"] = task["backtest_id"]
                    orderId = G.orm.save_order(saveData)
                    orderId = str(orderId)

                    G.orm.save_remote_positions(task["id"], positions_arr)

                    # 将字符串转换为 datetime 对象
                    dt = datetime.strptime(add_time, "%Y-%m-%d %H:%M:%S")

                    # 将 datetime 对象转换为毫秒级时间戳
                    timestamp_ms = int(dt.timestamp() * 1000)
                    real_amount = self.order_on_pro_rata_basis(
                        saveData, task, saveData["backtest_id"]
                    )
                    if real_amount == 0:
                        G.logger.error(
                            "委托数量{}小于0有问题".format(real_amount),
                            extra={"showMessage": True},
                        )
                        return
                    if self.simulator != None:
                        self.place_order(
                            stock_code=security,
                            volume=real_amount,
                            price=price,
                            is_buy=True if is_buy == 1 else False,
                            order_time=timestamp_ms,
                            order_style_str=style,
                            task_id=str(task["id"]),
                            order_remark=orderId,
                            is_mock_state=1,
                            open_mandatory_limit_order=task[
                                "open_mandatory_limit_order"
                            ],
                        )
                    else:
                        G.logger.error("异常Code 121", extra={"showMessage": True})

            #####################     实盘环境     ###########################
            else:
                is_mock_state = 2 if run_params == "pre" else 0
                if state != "run":
                    G.logger.error(
                        "实盘只有run状态,请不要修改运行环境",
                        extra={"showMessage": True},
                    )
                    return

                # 保存持仓信息到数据库
                G.orm.save_remote_positions(task["id"], positions_arr)

                # 没有检测没有连接不往下执行
                if self.acc_is_connect == False:
                    G.logger.error("qmt 没有正常运行", extra={"showMessage": True})
                    return
                # 创建空订单
                orderId = G.orm.save_order(saveData)
                # 判断交易时间
                now = datetime.now()
                if is_mock_state != 2 and (
                    now.hour < 9
                    or (now.hour == 15 and now.minute > 30)
                    or now.hour > 15
                ):
                    G.logger.info("非交易时间不能下单", extra={"showMessage": True})
                    return
                # ------------------------------ 交易函数----------------------------------------
                orderId = str(orderId)
                if amount < 0:
                    G.logger.info(
                        "委托数量{}小于0有问题".format(amount),
                        extra={"showMessage": True},
                    )
                    return

                if task["is_open"] == 1:
                    real_amount = self.order_on_pro_rata_basis(saveData, task)
                    if real_amount == 0:
                        G.logger.info(
                            "委托数量{}小于0有问题".format(real_amount),
                            extra={"showMessage": True},
                        )
                        return

                    self.place_order(
                        stock_code=security,
                        volume=real_amount,
                        price=price,
                        is_buy=True if is_buy == 1 else False,
                        order_time=None,
                        order_style_str=style,
                        task_id=str(task["id"]),
                        order_remark=orderId,
                        is_mock_state=is_mock_state,
                        open_mandatory_limit_order=task["open_mandatory_limit_order"],
                        account_id=task.get("account_id"),
                    )
                else:
                    G.logger.info(
                        "任务未开启: {}".format(strategy_code),
                        extra={"showMessage": True},
                    )
        except Exception as e:
            import traceback

            error_msg = (
                f"manage_platform_trader error: {str(e)}\n{traceback.format_exc()}"
            )
            G.logger.error(error_msg, extra={"showMessage": True})

    def test_connect(self, path, client_type, **kwargs):
        print(path)
        if client_type == 2:
            if sys.platform.startswith("darwin"):
                return {"msg": "", "is_connect": True, "account_arr": ["888888888"]}

            import random
            from pyapp.pkg.xtquant.xttrader import XtQuantTrader

            result = {"msg": "", "is_connect": False, "account_arr": []}
            session_id = int(random.randint(100000, 999999))
            xt_trader = XtQuantTrader(path, session_id)
            xt_trader.start()
            connect_result = xt_trader.connect()
            out = xt_trader.query_account_status()
            account_arr = []
            for obj in out:
                if hasattr(obj, "account_id"):
                    account_arr.append(getattr(obj, "account_id"))
            result["account_arr"] = account_arr

            if connect_result == 0:
                result["is_connect"] = True
            else:
                result["msg"] = "QMT路径错误,请重新检查!"
            return result
        else:
            pass

    def get_account_info(self, account=None):
        print(account)
        # 多账号模式：按指定账号获取
        if account.get("client_type") == 2:
            path = account.get("mini_qmt_path")
            client_id = account.get("client_id")
            if not path or not client_id:
                return {
                    "cash": 0,
                    "frozen_cash": 0,
                    "market_value": 0,
                    "total_asset": 0,
                }

            with self.multiple_traders_lock:
                trader_state = self.multiple_traders.get(account['id'])
                if not trader_state:
                    return {
                        "cash": 0,
                        "frozen_cash": 0,
                        "market_value": 0,
                        "total_asset": 0,
                    }

            # 如果未连接，尝试连接
            if not trader_state.acc_is_connect:
                try:
                    # 如果是mac 电脑开发环境直接返回成功
                    if sys.platform.startswith("darwin"):
                        trader_state.acc_is_connect = True
                    else:
                        # 设置id
                        trader_state.trader.path = path
                        trader_state.trader.account = client_id
                        # 连接QMT 传递回调
                        trader_state.acc_is_connect = trader_state.trader.connect(
                            self.callback
                        )
                except Exception as e:
                    G.logger.error(f"连接QMT账号 {client_id} 失败: {str(e)}")
                    trader_state.acc_is_connect = False

            if trader_state.acc_is_connect:
                return trader_state.trader.balance()
            return {"cash": 0, "frozen_cash": 0, "market_value": 0, "total_asset": 0}
        else:
            result = self.ths_auto.get_balance()
            if result.get("code") != 0:
                return {
                    "cash": 0,
                    "frozen_cash": 0,
                    "market_value": 0,
                    "total_asset": 0,
                }
            return {
                "cash": result["data"]["资金余额"],
                "frozen_cash": result["data"]["冻结金额"],
                "market_value": result["data"]["股票市值"],
                "total_asset": result["data"]["总资产"],
            }
