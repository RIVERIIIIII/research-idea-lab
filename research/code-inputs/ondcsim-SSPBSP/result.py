#!/usr/bin/env python3
import logging
from typing import List, Dict, Any
from events import Event

# 日志相关功能
LOGGER = logging.getLogger('算力网络调度')

def get_log_level(level_str):
    """将字符串日志级别转换为 logging 常量
    
    Args:
        level_str: 日志级别字符串，如 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        
    Returns:
        int: 对应的 logging 常量
    """
    return getattr(logging, level_str.upper())

def init_logger(log_level=logging.DEBUG, log_file=None, enable_console=False):
    """初始化日志系统
    
    Args:
        log_level: 日志级别，默认为DEBUG
        log_file: 日志文件路径，默认为None（不输出到文件）
        enable_console: 是否启用控制台输出，默认为False
    """
    # 移除LOGGER已有的处理器，避免重复添加
    for handler in LOGGER.handlers[:]:
        LOGGER.removeHandler(handler)
    
    # 设置LOGGER日志级别
    LOGGER.setLevel(log_level)
    
    # 定义统一的日志格式
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # 添加文件处理器
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        LOGGER.addHandler(fh)
    
    # 添加控制台处理器
    if enable_console:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        LOGGER.addHandler(ch)

# 结果管理功能
class ResultManager:
    """
    Manages collection and reporting of simulation results and metrics.
    """
    def __init__(self):
        self.metrics = {}

    def collect_basic_metrics(self, completed: List[Event], blocked: List[Event]) -> Dict[str, Any]:
        """Collect basic metrics: counts of completed/blocked events by type."""
        metrics: Dict[str, Any] = {'completed': {}, 'blocked': {}}
        for e in completed:
            metrics['completed'][e.event_type] = metrics['completed'].get(e.event_type, 0) + 1
        for e in blocked:
            metrics['blocked'][e.event_type] = metrics['blocked'].get(e.event_type, 0) + 1
        metrics['total_completed'] = int(len(completed))
        metrics['total_blocked'] = int(len(blocked))
        self.metrics = metrics
        return metrics

    def print_metrics(self, metrics: Dict[str, Any] = None):
        if metrics is None:
            metrics = self.metrics
        # Define all possible event types
        all_event_types = ['distributed_training']
        LOGGER.info("--- Simulation Metrics ---")
        LOGGER.info(f"Total completed events: {metrics.get('total_completed', 0)}")
        LOGGER.info(f"Total blocked events: {metrics.get('total_blocked', 0)}")
        LOGGER.info("Completed by type:")
        # Print all event types, including those with 0 completed
        for event_type in all_event_types:
            count = metrics.get('completed', {}).get(event_type, 0)
            LOGGER.info(f"  {event_type}: {count}")
        LOGGER.info("Blocked by type:")
        # Print all event types, including those with 0 blocked
        for event_type in all_event_types:
            count = metrics.get('blocked', {}).get(event_type, 0)
            LOGGER.info(f"  {event_type}: {count}")
