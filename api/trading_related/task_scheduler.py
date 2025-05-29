#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 交易相关的定时任务调度器
用于管理所有交易相关的定时任务，包括国债逆回购、新股打新、新债打新等
'''

import threading
import datetime
import logging
from typing import Optional, Callable
from api.system import System


class TaskScheduler:
    """定时任务调度器，用于管理所有交易相关的定时任务"""
    
    def __init__(self, qmt, orm):
        """
        初始化任务调度器
        
        Args:
            qmt: QMT交易接口实例
            orm: 数据库操作实例
        """
        self.qmt = qmt
        self.orm = orm
        self.timers = {}  # 存储所有定时器
        self.logger = logging.getLogger(__name__)
        
    def _calculate_delay(self, hour: int, minute: int) -> float:
        """
        计算到目标时间的延迟秒数
        
        Args:
            hour: 目标小时（24小时制）
            minute: 目标分钟
            
        Returns:
            float: 延迟的秒数
        """
        now = datetime.datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if now >= target_time:
            target_time = target_time + datetime.timedelta(days=1)
        
        return (target_time - now).total_seconds()
    
    def _check_config(self, task_type: str) -> bool:
        """
        检查任务配置是否满足执行条件
        
        Args:
            task_type: 任务类型，可选值：'national_debt', 'new_stock', 'new_bond'
            
        Returns:
            bool: 是否满足执行条件
        """
        config = self.orm.get_setting_config()
        base_conditions = (
            config["client_id"] != "" and 
            config["mini_qmt_path"] != "" and 
            self.qmt.qmt_trader is not None
        )
        
        if task_type == "national_debt":
            return base_conditions and config["auto_national_debt"] == 1
        elif task_type == "new_stock":
            return base_conditions and config["auto_buy_stock_ipo"] == 1
        elif task_type == "new_bond":
            return base_conditions and config["auto_buy_purchase_ipo"] == 1
        return False
    
    def _schedule_task(self, task_type: str, hour: int, minute: int, task_func: Callable) -> bool:
        """
        调度单个任务
        
        Args:
            task_type: 任务类型
            hour: 执行小时（24小时制）
            minute: 执行分钟
            task_func: 要执行的任务函数
            
        Returns:
            bool: 调度是否成功
        """
        def schedule_next():
            try:
                if self._check_config(task_type):
                    self.logger.info(f"执行{task_type}任务")
                    task_func()
                else:
                    self.logger.info(f"{task_type}任务配置不满足执行条件")
            except Exception as e:
                self.logger.error(f"{task_type}任务执行出错: {str(e)}")
            
            # 重新调度下一次执行
            if task_type in self.timers and self.timers[task_type] is not None:
                delay = self._calculate_delay(hour, minute)
                self.timers[task_type] = threading.Timer(delay, schedule_next)
                self.timers[task_type].start()
        
        # 取消现有定时器（如果存在）
        self.cancel_task(task_type)
        
        # 启动新的定时器
        delay = self._calculate_delay(hour, minute)
        self.timers[task_type] = threading.Timer(delay, schedule_next)
        self.timers[task_type].start()
        self.logger.info(f"{task_type}任务已调度，将在 {hour}:{minute} 执行")
        return True
    
    def schedule_national_debt(self, hour: int = 15, minute: int = 10) -> bool:
        """
        调度国债逆回购任务
        
        Args:
            hour: 执行小时，默认15
            minute: 执行分钟，默认10
            
        Returns:
            bool: 调度是否成功
        """
        return self._schedule_task(
            "national_debt",
            hour,
            minute,
            self.qmt.buyReverseRepo
        )
    
    def schedule_new_stock(self, hour: int = 10, minute: int = 10) -> bool:
        """
        调度新股打新任务
        
        Args:
            hour: 执行小时，默认10
            minute: 执行分钟，默认10
            
        Returns:
            bool: 调度是否成功
        """
        return self._schedule_task(
            "new_stock",
            hour,
            minute,
            self.qmt.autoBuyNewStock
        )
    
    def schedule_new_bond(self, hour: int = 10, minute: int = 10) -> bool:
        """
        调度新债打新任务
        
        Args:
            hour: 执行小时，默认10
            minute: 执行分钟，默认10
            
        Returns:
            bool: 调度是否成功
        """
        return self._schedule_task(
            "new_bond",
            hour,
            minute,
            self.qmt.autoBuyconvertibleBond
        )
    
    def cancel_task(self, task_type: str) -> bool:
        """
        取消指定类型的任务
        
        Args:
            task_type: 要取消的任务类型
            
        Returns:
            bool: 是否成功取消
        """
        if task_type in self.timers and self.timers[task_type] is not None:
            self.timers[task_type].cancel()
            self.timers[task_type] = None
            self.logger.info(f"{task_type}任务已取消")
            return True
        return False
    
    def cancel_all_tasks(self) -> bool:
        """
        取消所有任务
        
        Returns:
            bool: 是否成功取消所有任务
        """
        for task_type in list(self.timers.keys()):
            self.cancel_task(task_type)
        self.logger.info("所有定时任务已取消")
        return True 