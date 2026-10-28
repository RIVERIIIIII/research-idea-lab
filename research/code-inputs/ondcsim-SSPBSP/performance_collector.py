#!/usr/bin/env python3
"""
性能数据收集模块 - 用于收集和导出仿真性能指标

功能：
1. 收集算法执行性能指标（Level值、JCT、执行时间等）
2. 收集资源利用率指标（GPU、带宽、波长）
3. 收集服务质量指标（完成率、阻塞率、故障影响）
4. 支持JSON/CSV格式导出
5. 提供可视化数据接口
"""

import json
import csv
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
from result import LOGGER


@dataclass
class AlgorithmMetrics:
    """算法性能指标"""
    algorithm_name: str  # 算法名称: 'minPenalty' 或 'algorithm2'
    execution_time: float = 0.0  # 执行时间(秒)
    level_value: float = 0.0  # Level值
    jct: float = 0.0  # 任务完成时间（任务完成时间不能作为一个算法性能指标）
    cost_c: float = 0.0  # 代价C
    num_wavelengths: int = 0  # 波长数量
    num_dcs: int = 0  # 选中的数据中心数量
    total_gpus: int = 0  # 总GPU数量
    event_id: int = -1  # 关联的事件ID


@dataclass
class ResourceUtilization:
    """资源利用率指标"""
    timestamp: float
    gpu_utilization: Dict[int, float]  # 各DC的GPU利用率
    bandwidth_utilization: Dict[str, float]  # 各链路的带宽利用率
    wavelength_utilization: Dict[str, float]  # 各链路的波长利用率


@dataclass
class ServiceMetrics:
    """服务性能指标"""
    event_id: int
    event_type: str
    arrival_time: float
    start_time: float
    end_time: float
    allocated: bool
    blocked_reason: Optional[str] = None
    selected_dcs: List[int] = field(default_factory=list)
    gpus_per_dc: Dict[int, int] = field(default_factory=dict)
    required_bw: float = 0.0
    jct: float = 0.0
    level: float = 0.0


@dataclass
class FailureMetrics:
    """故障指标"""
    failure_id: int
    failure_type: str  # 'node' 或 'link'
    failed_resource: str  # 故障资源标识
    arrival_time: float
    duration: float
    affected_events: List[int] = field(default_factory=list)


class PerformanceCollector:
    """
    性能数据收集器 - 采用观察者模式收集仿真过程中的性能指标
    """

    def __init__(self, result_dir: str = "result", algorithm_name: str = "unknown"):
        """
        初始化性能收集器

        Args:
            result_dir: 结果文件保存的根目录
            algorithm_name: 本次仿真使用的算法名称，用于标识结果文件
        """
        self.simulation_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
        self.result_dir = Path(result_dir)
        self.algorithm_name = algorithm_name

        # 创建目录结构
        self._setup_directories()

        # 数据存储容器
        self.algorithm_metrics: List[AlgorithmMetrics] = []
        self.resource_snapshots: List[ResourceUtilization] = []
        self.service_metrics: List[ServiceMetrics] = []
        self.failure_metrics: List[FailureMetrics] = []

        # 统计计数器
        self.total_events = 0
        self.completed_events = 0
        self.blocked_events = 0

        # 任务配置信息（用于确保可复现性）
        self.task_config: Dict[str, Any] = {}

        LOGGER.info(f"性能收集器已初始化，仿真ID: {self.simulation_id}, 算法: {algorithm_name}")
    
    def _setup_directories(self):
        """创建结果目录结构"""
        subdirs = ['json_data', 'csv_exports', 'figures']
        for subdir in subdirs:
            (self.result_dir / subdir).mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"结果目录已创建: {self.result_dir}")
    
    def record_algorithm_metrics(self, 
                                  algorithm_name: str,
                                  execution_time: float,
                                  level_value: float,
                                  jct: float,
                                  cost_c: float = 0.0,
                                  num_wavelengths: int = 0,
                                  num_dcs: int = 0,
                                  total_gpus: int = 0,
                                  event_id: int = -1):
        """
        记录算法执行性能指标
        
        Args:
            algorithm_name: 算法名称 ('minPenalty' 或 'algorithm2')
            execution_time: 算法执行时间(秒)
            level_value: Level值
            jct: 任务完成时间
            cost_c: 代价C
            num_wavelengths: 波长数量
            num_dcs: 选中的数据中心数量
            total_gpus: 总GPU数量
            event_id: 关联的事件ID
        """
        metrics = AlgorithmMetrics(
            algorithm_name=algorithm_name,
            execution_time=execution_time,
            level_value=level_value,
            jct=jct,
            cost_c=cost_c,
            num_wavelengths=num_wavelengths,
            num_dcs=num_dcs,
            total_gpus=total_gpus,
            event_id=event_id
        )
        self.algorithm_metrics.append(metrics)
        LOGGER.debug(f"记录算法指标: {algorithm_name}, Level={level_value:.4f}, JCT={jct:.2f}")
    
    def record_resource_utilization(self,
                                     timestamp: float,
                                     G: Any):
        """
        记录资源利用率快照
        
        Args:
            timestamp: 时间戳
            G: 网络拓扑图对象
        """
        gpu_util = {}
        bw_util = {}
        wave_util = {}
        
        # 计算算力网络总GPU分配率
        # 修复：使用 is_co_location 属性识别数据中心节点
        for node_id, node_data in G.nodes(data=True):
            if node_data.get('is_co_location', False) or node_data.get('type') == 'datacenter':
                total_gpu = node_data.get('gpu_count')
                available_gpu = node_data.get('available_gpu')
                if total_gpu and total_gpu > 0:
                    gpu_util[node_id] = (total_gpu - available_gpu) / total_gpu
        
        # 计算带宽和波长利用率
        for u, v, edge_data in G.edges(data=True):
            link_key = f"{u}-{v}"
            
            # 带宽利用率
            bw_capacity = edge_data.get('bandwidth_capacity')
            bw_available = edge_data.get('bandwidth_available')
            if bw_capacity and bw_capacity > 0:
                bw_util[link_key] = (bw_capacity - bw_available) / bw_capacity
            
            # 波长利用率
            wavelength_channels = edge_data.get('wavelength_channels', [])
            if wavelength_channels:
                total_waves = len(wavelength_channels)
                used_waves = sum(1 for ch in wavelength_channels if ch.status == 1)
                wave_util[link_key] = used_waves / total_waves
        
        snapshot = ResourceUtilization(
            timestamp=timestamp,
            gpu_utilization=gpu_util,
            bandwidth_utilization=bw_util,
            wavelength_utilization=wave_util
        )
        self.resource_snapshots.append(snapshot)
    
    def record_service_metrics(self,
                                event_id: int,
                                event_type: str,
                                arrival_time: float,
                                start_time: float,
                                end_time: float,
                                allocated: bool,
                                blocked_reason: Optional[str] = None,
                                selected_dcs: Optional[List[int]] = None,
                                gpus_per_dc: Optional[Dict[int, int]] = None,
                                required_bw: float = 0.0,
                                jct: float = 0.0,
                                level: float = 0.0):
        """
        记录服务事件性能指标
        
        Args:
            event_id: 事件ID
            event_type: 事件类型
            arrival_time: 到达时间
            start_time: 开始时间
            end_time: 结束时间
            allocated: 是否成功分配
            blocked_reason: 阻塞原因
            selected_dcs: 选中的数据中心列表
            gpus_per_dc: 每个DC分配的GPU数量
            required_bw: 所需带宽
            jct: 任务完成时间
            level: Level值
        """
        metrics = ServiceMetrics(
            event_id=event_id,
            event_type=event_type,
            arrival_time=arrival_time,
            start_time=start_time,
            end_time=end_time,
            allocated=allocated,
            blocked_reason=blocked_reason,
            selected_dcs=selected_dcs or [],
            gpus_per_dc=gpus_per_dc or {},
            required_bw=required_bw,
            jct=jct,
            level=level
        )
        self.service_metrics.append(metrics)
        
        self.total_events += 1
        if allocated:
            self.completed_events += 1
        else:
            self.blocked_events += 1
    
    def record_failure_metrics(self,
                                failure_id: int,
                                failure_type: str,
                                failed_resource: str,
                                arrival_time: float,
                                duration: float,
                                affected_events: Optional[List[int]] = None):
        """
        记录故障事件指标
        
        Args:
            failure_id: 故障ID
            failure_type: 故障类型 ('node' 或 'link')
            failed_resource: 故障资源标识
            arrival_time: 到达时间
            duration: 持续时间
            affected_events: 受影响的事件ID列表
        """
        metrics = FailureMetrics(
            failure_id=failure_id,
            failure_type=failure_type,
            failed_resource=failed_resource,
            arrival_time=arrival_time,
            duration=duration,
            affected_events=affected_events or []
        )
        self.failure_metrics.append(metrics)
    
    def set_task_config(self, task_config: Dict[str, Any]):
        """
        设置任务配置信息，用于确保仿真可复现

        Args:
            task_config: 任务配置字典，包含random_seed、num_events、task_sequence等
        """
        self.task_config = task_config

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        获取汇总统计数据

        Returns:
            Dict: 包含各类统计指标的字典
        """
        summary = {
            "simulation_info": {
                "simulation_id": self.simulation_id,
                "algorithm_name": self.algorithm_name,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_events": self.total_events,
                "completed_events": self.completed_events,
                "blocked_events": self.blocked_events,
                "block_rate": self.blocked_events / self.total_events if self.total_events > 0 else 0.0
            },
            "task_config": self.task_config,
            "algorithm_statistics": self._calculate_algorithm_stats(),
            "resource_statistics": self._calculate_resource_stats(),
            "service_statistics": self._calculate_service_stats()
        }
        return summary
    
    def _calculate_algorithm_stats(self) -> Dict[str, Any]:
        """
        计算算法统计信息
        
        正确区分：
        - 多DC成功事件：level > 0 且有限
        - 单DC成功事件：level = 0 或 inf，但JCT > 0
        - 阻塞事件：JCT = 0 或 level为异常值
        """
        stats = {}

        algo_metrics = self.algorithm_metrics
        if algo_metrics:
            # 分类事件
            multi_dc_levels = []
            single_dc_count = 0
            blocked_count = 0
            all_success_jcts = []
            
            for m in algo_metrics:
                # 使用统一的状态判断逻辑
                if m.jct == 0:
                    blocked_count += 1
                elif m.level_value == 0 or m.level_value == float('inf'):
                    # 单DC成功事件
                    single_dc_count += 1
                    all_success_jcts.append(m.jct)
                elif m.level_value > 0 and m.level_value != float('inf'):
                    # 多DC成功事件
                    multi_dc_levels.append(m.level_value)
                    all_success_jcts.append(m.jct)
                else:
                    blocked_count += 1
            
            # 计算多DC场景的平均Level值
            avg_level = sum(multi_dc_levels) / len(multi_dc_levels) if multi_dc_levels else 0.0
            
            # 计算所有成功事件的平均JCT
            avg_jct = sum(all_success_jcts) / len(all_success_jcts) if all_success_jcts else 0.0
            
            stats[self.algorithm_name] = {
                "execution_count": len(algo_metrics),
                "avg_execution_time": sum(m.execution_time for m in algo_metrics) / len(algo_metrics),
                "avg_level": avg_level,
                "avg_jct": avg_jct,
                "avg_cost_c": sum(m.cost_c for m in algo_metrics) / len(algo_metrics),
                "avg_wavelengths": sum(m.num_wavelengths for m in algo_metrics) / len(algo_metrics),
                "avg_dcs": sum(m.num_dcs for m in algo_metrics) / len(algo_metrics),
                "avg_gpus": sum(m.total_gpus for m in algo_metrics) / len(algo_metrics),
                "multi_dc_count": len(multi_dc_levels),
                "single_dc_count": single_dc_count,
                "blocked_count": blocked_count
            }

        return stats
    
    def _calculate_resource_stats(self) -> Dict[str, Any]:
        """计算资源统计信息"""
        if not self.resource_snapshots:
            return {}
        
        # 计算平均利用率
        avg_gpu_util = {}
        avg_bw_util = {}
        avg_wave_util = {}
        
        for snapshot in self.resource_snapshots:
            for dc_id, util in snapshot.gpu_utilization.items():
                if dc_id not in avg_gpu_util:
                    avg_gpu_util[dc_id] = []
                avg_gpu_util[dc_id].append(util)
            
            for link, util in snapshot.bandwidth_utilization.items():
                if link not in avg_bw_util:
                    avg_bw_util[link] = []
                avg_bw_util[link].append(util)
            
            for link, util in snapshot.wavelength_utilization.items():
                if link not in avg_wave_util:
                    avg_wave_util[link] = []
                avg_wave_util[link].append(util)
        
        return {
            "avg_gpu_utilization": {k: sum(v)/len(v) for k, v in avg_gpu_util.items()},
            "avg_bandwidth_utilization": {k: sum(v)/len(v) for k, v in avg_bw_util.items()},
            "avg_wavelength_utilization": {k: sum(v)/len(v) for k, v in avg_wave_util.items()},
            "snapshot_count": len(self.resource_snapshots)
        }
    
    def _calculate_service_stats(self) -> Dict[str, Any]:
        """
        计算服务统计信息
        
        正确区分：
        - 完成事件：allocated=True（包括单DC和多DC成功事件）
        - 阻塞事件：allocated=False
        """
        if not self.service_metrics:
            return {}
        
        completed = [m for m in self.service_metrics if m.allocated]
        blocked = [m for m in self.service_metrics if not m.allocated]
        
        # 计算完成事件的平均JCT（包括单DC和多DC）
        avg_jct = sum(m.jct for m in completed) / len(completed) if completed else 0.0
        
        # 计算完成事件的平均Level值（排除inf值，只计算多DC场景）
        valid_levels = [m.level for m in completed 
                       if m.level > 0 and m.level != float('inf')]
        avg_level = sum(valid_levels) / len(valid_levels) if valid_levels else 0.0
        
        stats = {
            "total_services": len(self.service_metrics),
            "completed_count": len(completed),
            "blocked_count": len(blocked),
            "completion_rate": len(completed) / len(self.service_metrics) if self.service_metrics else 0.0,
            "avg_jct": avg_jct,
            "avg_level": avg_level,
            "avg_response_time": sum(m.start_time - m.arrival_time for m in completed) / len(completed) if completed else 0.0
        }
        
        return stats
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """
        导出所有性能数据为JSON格式

        Args:
            filename: 输出文件名，默认自动生成

        Returns:
            str: 输出文件的完整路径
        """
        if filename is None:
            timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{self.algorithm_name}_{self.simulation_id}.json"

        filepath = self.result_dir / 'json_data' / filename
        
        data = {
            "simulation_info": {
                "simulation_id": self.simulation_id,
                "algorithm_name": self.algorithm_name,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat()
            },
            "algorithm_metrics": [asdict(m) for m in self.algorithm_metrics],
            "resource_snapshots": [asdict(s) for s in self.resource_snapshots],
            "service_metrics": [asdict(m) for m in self.service_metrics],
            "failure_metrics": [asdict(m) for m in self.failure_metrics],
            "summary": self.get_summary_statistics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        LOGGER.info(f"性能数据已导出到JSON: {filepath}")
        return str(filepath)
    
    def export_summary_to_csv(self, filename: Optional[str] = None) -> str:
        """
        导出汇总统计数据为CSV格式

        Args:
            filename: 输出文件名，默认自动生成

        Returns:
            str: 输出文件的完整路径
        """
        if filename is None:
            timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_metrics_summary.csv"

        filepath = self.result_dir / 'csv_exports' / filename

        summary = self.get_summary_statistics()

        # 将嵌套字典展平
        flat_data = []
        flat_data.append({"metric": "simulation_id", "value": summary["simulation_info"]["simulation_id"]})
        flat_data.append({"metric": "algorithm_name", "value": summary["simulation_info"]["algorithm_name"]})
        flat_data.append({"metric": "total_events", "value": summary["simulation_info"]["total_events"]})
        flat_data.append({"metric": "completed_events", "value": summary["simulation_info"]["completed_events"]})
        flat_data.append({"metric": "blocked_events", "value": summary["simulation_info"]["blocked_events"]})
        flat_data.append({"metric": "block_rate", "value": summary["simulation_info"]["block_rate"]})

        # 算法统计 - 使用通用的 algorithm_ 前缀，而非具体的算法名称
        # 这样可以支持单算法仿真，也保持向后兼容
        for algo_name, algo_stats in summary.get("algorithm_statistics", {}).items():
            for key, value in algo_stats.items():
                flat_data.append({"metric": f"algorithm_{key}", "value": value})

        # 服务统计
        for key, value in summary.get("service_statistics", {}).items():
            flat_data.append({"metric": f"service_{key}", "value": value})

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["metric", "value"])
            writer.writeheader()
            writer.writerows(flat_data)

        LOGGER.info(f"汇总数据已导出到CSV: {filepath}")
        return str(filepath)
    
    def export_algorithm_comparison_csv(self, filename: Optional[str] = None) -> str:
        """
        导出算法性能数据为CSV格式，便于可视化
        单算法仿真模式下，移除algorithm_name列

        Args:
            filename: 输出文件名，默认自动生成

        Returns:
            str: 输出文件的完整路径
        """
        if filename is None:
            timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_algorithm_comparison.csv"

        filepath = self.result_dir / 'csv_exports' / filename

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 单算法仿真模式下，移除algorithm_name列
            writer.writerow([
                'event_id', 'execution_time', 'level_value',
                'jct', 'cost_c', 'num_wavelengths', 'num_dcs', 'total_gpus'
            ])

            for m in self.algorithm_metrics:
                writer.writerow([
                    m.event_id, m.execution_time, m.level_value,
                    m.jct, m.cost_c, m.num_wavelengths, m.num_dcs, m.total_gpus
                ])

        LOGGER.info(f"算法性能数据已导出到CSV: {filepath}")
        return str(filepath)
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """
        获取可视化所需的数据格式

        Returns:
            Dict: 适合直接传递给可视化库的数据结构
        """
        # 单算法仿真模式下，直接使用当前算法的数据
        return {
            "algorithm_metrics": {
                "algorithm_name": self.algorithm_name,
                "level_values": [m.level_value for m in self.algorithm_metrics],
                "jct_values": [m.jct for m in self.algorithm_metrics],
                "execution_times": [m.execution_time for m in self.algorithm_metrics],
                "cost_c_values": [m.cost_c for m in self.algorithm_metrics],
                "num_wavelengths": [m.num_wavelengths for m in self.algorithm_metrics],
                "event_ids": [m.event_id for m in self.algorithm_metrics]
            },
            "resource_timeline": {
                "timestamps": [s.timestamp for s in self.resource_snapshots],
                "gpu_utilization": [sum(s.gpu_utilization.values()) / len(s.gpu_utilization) if s.gpu_utilization else 0
                                   for s in self.resource_snapshots],
                "bandwidth_utilization": [sum(s.bandwidth_utilization.values()) / len(s.bandwidth_utilization)
                                         if s.bandwidth_utilization else 0
                                         for s in self.resource_snapshots]
            },
            "service_distribution": {
                "completed": self.completed_events,
                "blocked": self.blocked_events
            }
        }
    
    def finalize(self):
        """
        仿真结束时调用，导出所有数据
        
        Returns:
            Dict: 包含所有导出文件路径的字典
        """
        LOGGER.info("正在导出性能数据...")
        
        exported_files = {
            "json": self.export_to_json(),
            "summary_csv": self.export_summary_to_csv(),
            "algorithm_csv": self.export_algorithm_comparison_csv()
        }
        
        LOGGER.info("性能数据导出完成")
        return exported_files


# 全局性能收集器实例（单例模式）
_performance_collector: Optional[PerformanceCollector] = None


def get_performance_collector(result_dir: str = "result", algorithm_name: str = "unknown") -> PerformanceCollector:
    """
    获取全局性能收集器实例

    Args:
        result_dir: 结果文件保存的根目录
        algorithm_name: 本次仿真使用的算法名称

    Returns:
        PerformanceCollector: 性能收集器实例
    """
    global _performance_collector
    if _performance_collector is None:
        _performance_collector = PerformanceCollector(result_dir, algorithm_name)
    return _performance_collector


def reset_performance_collector():
    """重置全局性能收集器实例"""
    global _performance_collector
    _performance_collector = None
