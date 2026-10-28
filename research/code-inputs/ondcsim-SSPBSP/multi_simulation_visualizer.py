#!/usr/bin/env python3
"""
多仿真结果对比可视化模块

功能：
1. 从多个仿真结果文件中加载数据
2. 支持多算法性能对比可视化
3. 提供统计分析功能（平均值、方差、置信区间等）
4. 支持多种图表类型（折线图、柱状图、箱线图、散点图等）
"""

import json
import os
import glob
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# 尝试导入matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib
    import matplotlib.font_manager as fm
    matplotlib.use('Agg')

    try:
        fm._load_fontmanager(try_read_cache=False)
    except Exception:
        pass

    # IEEE会议论文图表标准常量
    IEEE_SINGLE_COLUMN_WIDTH = 3.5  # 单栏宽度（英寸）
    IEEE_DOUBLE_COLUMN_WIDTH = 7.0  # 双栏宽度（英寸）
    IEEE_SINGLE_COLUMN_HEIGHT = 2.6  # 单栏推荐高度
    IEEE_DOUBLE_COLUMN_HEIGHT = 3.5  # 双栏推荐高度

    # IEEE学术出版推荐配色（色盲友好，黑白打印可读）
    IEEE_COLORS = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5']

    # 配置中文字体支持 - 使用matplotlib能识别的字体
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # IEEE学术出版标准字体设置
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Noto Serif CJK SC']
    plt.rcParams['font.size'] = 9
    plt.rcParams['axes.titlesize'] = 10
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 8
    plt.rcParams['figure.titlesize'] = 10

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib未安装，可视化功能将不可用")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

from result import LOGGER


@dataclass
class AlgorithmComparisonData:
    """算法对比数据结构"""
    algorithm_name: str
    simulation_id: str
    level_values: List[float]
    jct_values: List[float]
    execution_times: List[float]
    block_rate: float
    completion_rate: float
    avg_jct: float
    avg_level: float


class MultiSimulationVisualizer:
    """
    多仿真结果对比可视化器
    支持从多个仿真结果文件中读取数据，进行综合对比分析
    """

    # 算法名称显示映射（用于图表显示）
    ALGORITHM_DISPLAY_NAMES = {
        'minPenalty': 'FC-CEM'
    }

    def __init__(self, result_dir: str = "result"):
        """
        初始化多仿真可视化器

        Args:
            result_dir: 结果文件根目录
        """
        self.result_dir = Path(result_dir)
        self.raw_dir = self.result_dir / "json_data"
        self.figures_dir = self.result_dir / "comparison_figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，无法生成可视化图表")

        # 存储加载的仿真数据
        self.simulation_data: Dict[str, List[Dict]] = {}

    def _get_display_name(self, algo_name: str) -> str:
        """获取算法的显示名称"""
        return self.ALGORITHM_DISPLAY_NAMES.get(algo_name, algo_name)

    def _classify_event_status(self, level_value: float, jct: float) -> str:
        """
        分类事件状态
        
        根据level值和JCT判断事件状态：
        - success_multi_dc: 多DC成功事件（level > 0 且有限）
        - success_single_dc: 单DC成功事件（level = 0 或 inf，但JCT > 0）
        - blocked: 阻塞事件（JCT = 0 或 level为异常值）
        
        Args:
            level_value: Level值
            jct: 任务完成时间
            
        Returns:
            str: 'success_multi_dc' | 'success_single_dc' | 'blocked'
        """
        # 阻塞事件：JCT为0，或level为-inf/nan
        if jct == 0 or np.isneginf(level_value) or np.isnan(level_value):
            return 'blocked'
        
        # 单DC成功事件：level为0或inf（单点策略），但JCT > 0表示任务成功执行
        if level_value == 0 or np.isinf(level_value):
            return 'success_single_dc'
        
        # 多DC成功事件：level > 0 且有限
        if level_value > 0:
            return 'success_multi_dc'
        
        return 'blocked'

    def load_simulation_files(self, pattern: str = "*.json") -> Dict[str, List[Dict]]:
        """
        加载所有符合条件的仿真结果文件

        Args:
            pattern: 文件匹配模式

        Returns:
            Dict: {algorithm_name: [simulation_data_list]}
        """
        if not self.raw_dir.exists():
            LOGGER.warning(f"结果目录不存在: {self.raw_dir}")
            return {}

        json_files = list(self.raw_dir.glob(pattern))
        LOGGER.info(f"找到 {len(json_files)} 个仿真结果文件")

        self.simulation_data = {}

        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 从文件中提取算法名称
                algo_name = data.get('simulation_info', {}).get('algorithm_name', 'unknown')

                if algo_name not in self.simulation_data:
                    self.simulation_data[algo_name] = []

                self.simulation_data[algo_name].append(data)
                LOGGER.info(f"已加载: {file_path.name} -> 算法: {algo_name}")

            except Exception as e:
                LOGGER.error(f"加载文件失败 {file_path}: {e}")

        # 统计信息
        for algo_name, data_list in self.simulation_data.items():
            LOGGER.info(f"算法 {algo_name}: {len(data_list)} 次仿真")

        return self.simulation_data

    def load_specific_algorithms(self, algorithm_files: Dict[str, str]) -> Dict[str, Dict]:
        """
        加载指定算法的仿真结果文件

        Args:
            algorithm_files: {algorithm_name: file_path}

        Returns:
            Dict: {algorithm_name: simulation_data}
        """
        self.simulation_data = {}

        for algo_name, file_path in algorithm_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if algo_name not in self.simulation_data:
                    self.simulation_data[algo_name] = []

                self.simulation_data[algo_name].append(data)
                LOGGER.info(f"已加载指定文件: {file_path} -> 算法: {algo_name}")

            except Exception as e:
                LOGGER.error(f"加载文件失败 {file_path}: {e}")

        return self.simulation_data

    def extract_algorithm_metrics(self, data: Dict) -> AlgorithmComparisonData:
        """
        从仿真数据中提取算法性能指标

        Args:
            data: 仿真数据字典

        Returns:
            AlgorithmComparisonData: 算法对比数据
        """
        sim_info = data.get('simulation_info', {})
        algo_metrics = data.get('algorithm_metrics', [])
        summary = data.get('summary', {})
        service_stats = summary.get('service_statistics', {})

        algo_name = sim_info.get('algorithm_name', 'unknown')
        sim_id = sim_info.get('simulation_id', 'unknown')

        return AlgorithmComparisonData(
            algorithm_name=algo_name,
            simulation_id=sim_id,
            level_values=[m.get('level_value', 0) for m in algo_metrics if m.get('level_value', float('inf')) < float('inf')],
            jct_values=[m.get('jct', 0) for m in algo_metrics if m.get('jct', float('inf')) < float('inf')],
            execution_times=[m.get('execution_time', 0) for m in algo_metrics],
            block_rate=sim_info.get('block_rate', 0),
            completion_rate=service_stats.get('completion_rate', 0),
            avg_jct=service_stats.get('avg_jct', 0),
            avg_level=service_stats.get('avg_level', 0)
        )

    def calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """
        计算统计指标

        Args:
            values: 数值列表

        Returns:
            Dict: 统计指标字典
        """
        if not values:
            return {
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0,
                "var": 0.0,
                "min": 0.0,
                "max": 0.0,
                "ci_95_lower": 0.0,
                "ci_95_upper": 0.0
            }

        arr = np.array(values)
        mean = np.mean(arr)
        n = len(arr)

        # 当只有一个值时，标准差和方差为0（避免Degrees of freedom <= 0警告）
        if n <= 1:
            std = 0.0
            var = 0.0
            ci_95 = 0.0
        else:
            std = np.std(arr, ddof=1)  # 样本标准差
            var = np.var(arr, ddof=1)
            ci_95 = 1.96 * std / np.sqrt(n)

        return {
            "mean": float(mean),
            "median": float(np.median(arr)),
            "std": float(std),
            "var": float(var),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "ci_95_lower": float(mean - ci_95),
            "ci_95_upper": float(mean + ci_95)
        }

    def generate_comparison_report(self) -> Dict[str, Any]:
        """
        生成算法对比统计报告

        Returns:
            Dict: 包含各算法统计指标的报告
        """
        report = {}

        for algo_name, data_list in self.simulation_data.items():
            algo_report = {
                "simulation_count": len(data_list),
                "metrics": {}
            }

            # 收集所有仿真的指标
            all_level_values = []
            all_jct_values = []
            all_execution_times = []
            all_block_rates = []
            all_completion_rates = []

            for data in data_list:
                metrics = self.extract_algorithm_metrics(data)
                all_level_values.extend(metrics.level_values)
                all_jct_values.extend(metrics.jct_values)
                all_execution_times.extend(metrics.execution_times)
                all_block_rates.append(metrics.block_rate)
                all_completion_rates.append(metrics.completion_rate)

            # 计算统计指标
            algo_report["metrics"]["level_value"] = self.calculate_statistics(all_level_values)
            algo_report["metrics"]["jct"] = self.calculate_statistics(all_jct_values)
            algo_report["metrics"]["execution_time"] = self.calculate_statistics(all_execution_times)
            algo_report["metrics"]["block_rate"] = self.calculate_statistics(all_block_rates)
            algo_report["metrics"]["completion_rate"] = self.calculate_statistics(all_completion_rates)

            report[algo_name] = algo_report

        return report

    def plot_algorithm_comparison_line(self, metric: str = "level_value",
                                        save_path: Optional[str] = None) -> str:
        """
        绘制算法对比折线图
        包含所有事件类型，单DC成功事件和阻塞事件以特殊标记显示
        
        Args:
            metric: 要对比的指标 ('level_value', 'jct', 'execution_time')
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过图表生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        fig, ax = plt.subplots(figsize=(IEEE_DOUBLE_COLUMN_WIDTH, IEEE_DOUBLE_COLUMN_HEIGHT))

        colors = IEEE_COLORS
        markers = ['o', 's', '^', 'D', 'v']

        # 用于统计单DC和阻塞事件数量
        single_dc_counts = {}
        blocked_counts = {}
        algo_execution_stats = {}

        # 先绘制所有算法的成功事件折线
        for idx, (algo_name, data_list) in enumerate(self.simulation_data.items()):
            color = colors[idx % len(colors)]
            marker = markers[idx % len(markers)]
            single_dc_counts[algo_name] = 0
            blocked_counts[algo_name] = 0
            display_name = self._get_display_name(algo_name)

            # 使用第一次仿真的数据绘制
            if data_list:
                data = data_list[0]
                algo_metrics = data.get('algorithm_metrics', [])

                # 使用统一的状态判断逻辑
                event_ids = list(range(len(algo_metrics)))
                level_values = [m.get('level_value', 0) for m in algo_metrics]
                jct_values = [m.get('jct', 0) for m in algo_metrics]
                event_statuses = [self._classify_event_status(l, j) for l, j in zip(level_values, jct_values)]
                
                # 分类事件索引
                multi_dc_indices = [i for i, status in enumerate(event_statuses) if status == 'success_multi_dc']
                single_dc_indices = [i for i, status in enumerate(event_statuses) if status == 'success_single_dc']
                blocked_indices = [i for i, status in enumerate(event_statuses) if status == 'blocked']
                
                # 记录统计数量
                single_dc_counts[algo_name] = len(single_dc_indices)
                blocked_counts[algo_name] = len(blocked_indices)

                if metric == 'level_value':
                    # 绘制多DC成功事件
                    if multi_dc_indices:
                        multi_dc_event_ids = [event_ids[i] for i in multi_dc_indices]
                        multi_dc_levels = [level_values[i] for i in multi_dc_indices]
                        ax.plot(multi_dc_event_ids, multi_dc_levels, marker=marker, linestyle='-',
                               label=f'{display_name}', color=color, markersize=6, linewidth=2)
                    
                    # 绘制单DC成功事件（星形标记）
                    if single_dc_indices:
                        single_dc_event_ids = [event_ids[i] for i in single_dc_indices]
                        ax.scatter(single_dc_event_ids, [0]*len(single_dc_event_ids), 
                                  marker='*', color='gold', s=150, edgecolors='black',
                                  linewidths=1, zorder=10)

                    ylabel = 'Level Value'
                    title = 'Level Value Comparison (Event ID)'

                elif metric == 'jct':
                    # 所有成功事件（多DC和单DC）都显示JCT
                    all_success_indices = multi_dc_indices + single_dc_indices
                    if all_success_indices:
                        success_event_ids = [event_ids[i] for i in all_success_indices]
                        success_values = [jct_values[i] / 3600 for i in all_success_indices]  # 转换为小时
                        # 按event_id排序
                        sorted_pairs = sorted(zip(success_event_ids, success_values))
                        sorted_ids, sorted_values = zip(*sorted_pairs) if sorted_pairs else ([], [])
                        ax.plot(sorted_ids, sorted_values, marker=marker, linestyle='-',
                               label=f'{display_name}', color=color, markersize=6, linewidth=2)

                    ylabel = 'JCT (hours)'
                    title = 'Job Completion Time (JCT) Comparison'

                elif metric == 'execution_time':
                    execution_times = [m.get('execution_time', 0) for m in algo_metrics]
                    algo_execution_stats[algo_name] = {
                        'mean': np.mean(execution_times) if execution_times else 0,
                        'std': np.std(execution_times) if execution_times else 0,
                        'count': len(execution_times)
                    }
                    all_success_indices = multi_dc_indices + single_dc_indices
                    if all_success_indices:
                        success_event_ids = [event_ids[i] for i in all_success_indices]
                        success_values = [execution_times[i] for i in all_success_indices]
                        # 按event_id排序
                        sorted_pairs = sorted(zip(success_event_ids, success_values))
                        sorted_ids, sorted_values = zip(*sorted_pairs) if sorted_pairs else ([], [])
                        ax.plot(sorted_ids, sorted_values, marker=marker, linestyle='-',
                               label=f'{display_name}', color=color, markersize=6, linewidth=2)

                    ylabel = 'Execution Time (s)'
                    title = 'Algorithm Execution Time Comparison'
                else:
                    continue

        # 绘制所有算法的阻塞事件标记（统一使用红色X）
        has_blocked = False
        for idx, (algo_name, data_list) in enumerate(self.simulation_data.items()):
            if data_list:
                data = data_list[0]
                algo_metrics = data.get('algorithm_metrics', [])

                event_ids = list(range(len(algo_metrics)))
                level_values = [m.get('level_value', 0) for m in algo_metrics]
                jct_values = [m.get('jct', 0) for m in algo_metrics]
                event_statuses = [self._classify_event_status(l, j) for l, j in zip(level_values, jct_values)]
                blocked_indices = [i for i, status in enumerate(event_statuses) if status == 'blocked']

                if blocked_indices:
                    has_blocked = True
                    blocked_event_ids = [event_ids[i] for i in blocked_indices]

                    if metric == 'level_value':
                        blocked_values = [0 for _ in blocked_indices]  # 阻塞事件显示为0
                    elif metric == 'jct':
                        blocked_values = [0 for _ in blocked_indices]  # 阻塞事件显示为0
                    elif metric == 'execution_time':
                        blocked_values = [algo_metrics[i].get('execution_time', 0) for i in blocked_indices]
                    else:
                        continue

                    # 绘制阻塞事件（红色X标记，使用edgecolor区分不同算法）
                    ax.scatter(blocked_event_ids, blocked_values, c='red', marker='x',
                              s=150, linewidths=2, zorder=10)

        # 构建图例
        handles, labels = ax.get_legend_handles_labels()
        
        # 如果有单DC场景，添加特殊图例（星形标记）
        if any(single_dc_counts.values()):
            from matplotlib.lines import Line2D
            single_dc_handle = Line2D([0], [0], marker='*', color='gold', linestyle='None',
                                      markersize=12, markerfacecolor='gold', 
                                      markeredgecolor='black', markeredgewidth=1,
                                      label='Single-DC Scenario (Level=∞)')
            handles.append(single_dc_handle)
            labels.append('Single-DC Scenario (Level=∞)')
        
        # 如果有阻塞事件，添加统一的图例项
        if has_blocked:
            from matplotlib.lines import Line2D
            blocked_handle = Line2D([0], [0], marker='x', color='red', linestyle='None',
                                    markersize=10, markeredgewidth=2, label='Blocked Event')
            handles.append(blocked_handle)
            labels.append('Blocked Event')

        ax.set_xlabel('Event ID', fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=10)
        ax.legend(handles, labels, loc='best', framealpha=0.9, fontsize=8)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(axis='both', which='major', labelsize=9)

        # 对于Level值，添加统计信息注释
        if metric == 'level_value':
            stats_text = []
            for algo_name in self.simulation_data.keys():
                if single_dc_counts[algo_name] > 0 or blocked_counts[algo_name] > 0:
                    parts = []
                    if single_dc_counts[algo_name] > 0:
                        parts.append(f"Single-DC: {single_dc_counts[algo_name]}")
                    if blocked_counts[algo_name] > 0:
                        parts.append(f"Blocked: {blocked_counts[algo_name]}")
                    display_name = self._get_display_name(algo_name)
                    stats_text.append(f"{display_name}: {', '.join(parts)}")
            
            if stats_text:
                ax.text(0.02, 0.02, '\n'.join(stats_text), transform=ax.transAxes,
                       fontsize=8, verticalalignment='bottom', 
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 对于执行时间，添加统计信息注释
        if metric == 'execution_time':
            stats_text = []
            for algo_name in self.simulation_data.keys():
                if algo_name in algo_execution_stats:
                    stats = algo_execution_stats[algo_name]
                    display_name = self._get_display_name(algo_name)
                    stats_text.append(f"{display_name}: Mean={stats['mean']:.3f}s, Std={stats['std']:.3f}s (n={stats['count']})")
            
            if stats_text:
                ax.text(0.02, 0.02, '\n'.join(stats_text), transform=ax.transAxes,
                       fontsize=8, verticalalignment='bottom', 
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_comparison_line_{metric}.png"

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        LOGGER.info(f"算法对比折线图已保存: {save_path}")
        return str(save_path)

    def plot_algorithm_comparison_bar(self, save_path: Optional[str] = None) -> str:
        """
        绘制算法平均JCT对比柱状图

        Args:
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过图表生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        algo_names = list(self.simulation_data.keys())
        avg_jct_values = []
        display_names = [self._get_display_name(name) for name in algo_names]

        for algo_name in algo_names:
            data_list = self.simulation_data[algo_name]
            if data_list:
                data = data_list[0]
                summary = data.get('summary', {})
                service_stats = summary.get('service_statistics', {})
                value = service_stats.get('avg_jct', 0)
                value = value / 86400 if value > 0 else 0
                avg_jct_values.append(value)

        # IEEE学术出版标准尺寸和配色
        fig, ax = plt.subplots(figsize=(IEEE_SINGLE_COLUMN_WIDTH, 2.8))

        # IEEE学术出版推荐配色
        colors = IEEE_COLORS
        bars = ax.bar(display_names, avg_jct_values, color=colors[:len(algo_names)],
                     edgecolor='black', linewidth=1, alpha=0.9)

        # 数值标签 - 显示在柱状图顶部
        for bar in bars:
            height = bar.get_height()
            label_text = f'{height:.2f}'
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   label_text,
                   ha='center', va='bottom', fontsize=9,
                   color='black')

        ax.set_ylabel('Average JCT (days)', fontsize=10)
        ax.grid(True, alpha=0.4, axis='y', linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)

        # 设置y轴上限，预留标签空间
        max_value = max(avg_jct_values) if avg_jct_values else 1
        ax.set_ylim(0, max_value * 1.15)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=9, width=0.75, length=4,
                      direction='in', top=True, right=True)
        ax.set_xticklabels(display_names, rotation=15, ha='center', fontsize=9)

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_comparison_bar.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"算法对比柱状图已保存: {save_path}")
        return str(save_path)

    def plot_blocking_analysis(self, save_path: Optional[str] = None) -> str:
        """
        绘制阻塞率对比图

        Args:
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过阻塞分析图生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        algo_blocking_stats = {}

        for algo_name, data_list in self.simulation_data.items():
            if not data_list:
                continue

            total_events = 0
            blocked_events = 0

            for data in data_list:
                service_metrics = data.get('service_metrics', [])
                for m in service_metrics:
                    total_events += 1
                    if not m.get('allocated', False):
                        blocked_events += 1

            algo_blocking_stats[algo_name] = {
                'total': total_events,
                'blocked': blocked_events,
                'block_rate': blocked_events / total_events if total_events > 0 else 0
            }

        if not algo_blocking_stats:
            LOGGER.warning("没有阻塞数据可供分析")
            return ""

        # IEEE学术出版标准尺寸
        fig, ax = plt.subplots(figsize=(IEEE_SINGLE_COLUMN_WIDTH, 2.8))

        algo_names = list(algo_blocking_stats.keys())
        display_names = [self._get_display_name(name) for name in algo_names]

        # IEEE学术出版推荐配色
        colors = IEEE_COLORS

        block_rates = [algo_blocking_stats[name]['block_rate'] * 100 for name in algo_names]
        total_counts = [algo_blocking_stats[name]['total'] for name in algo_names]
        blocked_counts = [algo_blocking_stats[name]['blocked'] for name in algo_names]
        x = np.arange(len(algo_names))

        bars = ax.bar(x, block_rates, color=colors[:len(algo_names)],
                     edgecolor='black', alpha=0.9, linewidth=1)
        ax.set_ylabel('Blocking Rate (%)', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(display_names, rotation=15, ha='center', fontsize=9)
        ax.grid(True, alpha=0.4, axis='y', linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=9, width=0.75, length=4,
                      direction='in', top=True, right=True)

        max_rate = max(block_rates) if block_rates else 0
        ax.set_ylim(0, max(max_rate * 1.35, 10))

        for bar, rate, total, blocked in zip(bars, block_rates, total_counts, blocked_counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + max_rate * 0.03,
                   f'{rate:.2f}%', ha='center', va='bottom', fontsize=9)
            ax.text(bar.get_x() + bar.get_width()/2, height + max_rate * 0.15,
                   f'({blocked}/{total})', ha='center', va='bottom', fontsize=8, color='gray')

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_blocking_analysis.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"阻塞分析图已保存: {save_path}")
        return str(save_path)

    def _extract_utilization_timeline(self, data: Dict, utilization_type: str) -> Tuple[List[float], List[float]]:
        """
        从仿真数据中提取资源利用率时间序列
        
        Args:
            data: 仿真数据字典
            utilization_type: 利用率类型 ('gpu' 或 'wavelength')
            
        Returns:
            Tuple: (相对时间列表, 平均利用率列表)
        """
        resource_snapshots = data.get('resource_snapshots', [])
        
        if not resource_snapshots:
            return [], []
        
        timestamps = []
        avg_utils = []
        
        for snapshot in resource_snapshots:
            timestamp = snapshot.get('timestamp', 0)
            timestamps.append(timestamp)
            
            if utilization_type == 'gpu':
                utils_dict = snapshot.get('gpu_utilization', {})
            elif utilization_type == 'wavelength':
                utils_dict = snapshot.get('wavelength_utilization', {})
            else:
                utils_dict = {}
            
            if utils_dict:
                avg_util = np.mean(list(utils_dict.values())) * 100
            else:
                avg_util = 0
            
            avg_utils.append(avg_util)
        
        if not timestamps:
            return [], []
        
        base_timestamp = timestamps[0]
        relative_timestamps = [t - base_timestamp for t in timestamps]
        
        return relative_timestamps, avg_utils


    def plot_gpu_utilization_summary_comparison(self, save_path: Optional[str] = None) -> str:
        """
        绘制各算法平均GPU利用率汇总对比图

        数据来源: resource_snapshots.gpu_utilization
        计算方法: 对每个时间点，计算所有DC的平均GPU利用率
        横坐标: 相对仿真时间（秒）
        纵坐标: GPU利用率（%）

        Args:
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过GPU利用率汇总对比图生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        # IEEE学术出版标准尺寸
        fig, ax = plt.subplots(figsize=(IEEE_DOUBLE_COLUMN_WIDTH, IEEE_DOUBLE_COLUMN_HEIGHT))

        # IEEE学术出版推荐配色
        colors = IEEE_COLORS
        markers = ['o', 's', '^', 'D', 'v']

        for idx, (algo_name, data_list) in enumerate(self.simulation_data.items()):
            if not data_list:
                continue

            data = data_list[0]
            timestamps, avg_utils = self._extract_utilization_timeline(data, 'gpu')
            display_name = self._get_display_name(algo_name)

            if timestamps and avg_utils:
                ax.plot(timestamps, avg_utils,
                       label=f'{display_name}',
                       color=colors[idx % len(colors)],
                       linewidth=2.0, marker=markers[idx % len(markers)],
                       markersize=6, alpha=0.95,
                       markeredgewidth=1.0,
                       markeredgecolor='white',
                       markevery=max(1, len(timestamps)//15))

        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('GPU Utilization (%)', fontsize=10)
        ax.legend(loc='upper right', fontsize=8, framealpha=0.95,
                 edgecolor='black', fancybox=False, shadow=False)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 105)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=9, width=0.75, length=4,
                      direction='in', top=True, right=True)

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_gpu_utilization_summary.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"GPU利用率汇总对比图已保存: {save_path}")
        return str(save_path)

    def plot_wavelength_utilization_summary_comparison(self, save_path: Optional[str] = None) -> str:
        """
        绘制各算法平均波长利用率汇总对比图

        数据来源: resource_snapshots.wavelength_utilization
        计算方法: 对每个时间点，计算所有链路的平均波长利用率
        横坐标: 相对仿真时间（秒）
        纵坐标: 波长利用率（%）

        Args:
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过波长利用率汇总对比图生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        # IEEE学术出版标准尺寸
        fig, ax = plt.subplots(figsize=(IEEE_DOUBLE_COLUMN_WIDTH, IEEE_DOUBLE_COLUMN_HEIGHT))

        # IEEE学术出版推荐配色
        colors = IEEE_COLORS
        markers = ['o', 's', '^', 'D', 'v']

        for idx, (algo_name, data_list) in enumerate(self.simulation_data.items()):
            if not data_list:
                continue

            data = data_list[0]
            timestamps, avg_utils = self._extract_utilization_timeline(data, 'wavelength')
            display_name = self._get_display_name(algo_name)

            if timestamps and avg_utils:
                ax.plot(timestamps, avg_utils,
                       label=f'{display_name}',
                       color=colors[idx % len(colors)],
                       linewidth=2.0, marker=markers[idx % len(markers)],
                       markersize=6, alpha=0.95,
                       markeredgewidth=1.0,
                       markeredgecolor='white',
                       markevery=max(1, len(timestamps)//15))

        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('Wavelength Utilization (%)', fontsize=10)
        ax.legend(loc='upper right', fontsize=8, framealpha=0.95,
                 edgecolor='black', fancybox=False, shadow=False)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 105)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=9, width=0.75, length=4,
                      direction='in', top=True, right=True)

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_wavelength_utilization_summary.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"波长利用率汇总对比图已保存: {save_path}")
        return str(save_path)

    def plot_gpu_utilization_summary_single_column(self, save_path: Optional[str] = None) -> str:
        """
        绘制各算法平均GPU利用率汇总对比图（单栏版本）

        数据来源: resource_snapshots.gpu_utilization
        计算方法: 对每个时间点，计算所有DC的平均GPU利用率
        横坐标: 相对仿真时间（秒）
        纵坐标: GPU利用率（%）
        尺寸: 单栏 (3.5" × 2.6")

        Args:
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过GPU利用率单栏汇总对比图生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        fig, ax = plt.subplots(figsize=(IEEE_SINGLE_COLUMN_WIDTH, IEEE_SINGLE_COLUMN_HEIGHT))

        colors = IEEE_COLORS
        markers = ['o', 's', '^', 'D', 'v']

        for idx, (algo_name, data_list) in enumerate(self.simulation_data.items()):
            if not data_list:
                continue

            data = data_list[0]
            timestamps, avg_utils = self._extract_utilization_timeline(data, 'gpu')
            display_name = self._get_display_name(algo_name)

            if timestamps and avg_utils:
                ax.plot(timestamps, avg_utils,
                       label=f'{display_name}',
                       color=colors[idx % len(colors)],
                       linewidth=1.5, marker=markers[idx % len(markers)],
                       markersize=4, alpha=0.95,
                       markeredgewidth=0.8,
                       markeredgecolor='white',
                       markevery=max(1, len(timestamps)//10))

        ax.set_xlabel('Time (s)', fontsize=9)
        ax.set_ylabel('GPU Utilization (%)', fontsize=9)
        ax.legend(loc='lower left', fontsize=7, framealpha=0.95,
                 edgecolor='black', fancybox=False, shadow=False)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 105)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=8, width=0.75, length=4,
                      direction='in', top=True, right=True)

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_gpu_utilization_summary_single_column.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"GPU利用率单栏汇总对比图已保存: {save_path}")
        return str(save_path)

    def plot_wavelength_utilization_summary_single_column(self, save_path: Optional[str] = None) -> str:
        """
        绘制各算法平均波长利用率汇总对比图（单栏版本）

        数据来源: resource_snapshots.wavelength_utilization
        计算方法: 对每个时间点，计算所有链路的平均波长利用率
        横坐标: 相对仿真时间（秒）
        纵坐标: 波长利用率（%）
        尺寸: 单栏 (3.5" × 2.6")

        Args:
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过波长利用率单栏汇总对比图生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        fig, ax = plt.subplots(figsize=(IEEE_SINGLE_COLUMN_WIDTH, IEEE_SINGLE_COLUMN_HEIGHT))

        colors = IEEE_COLORS
        markers = ['o', 's', '^', 'D', 'v']

        for idx, (algo_name, data_list) in enumerate(self.simulation_data.items()):
            if not data_list:
                continue

            data = data_list[0]
            timestamps, avg_utils = self._extract_utilization_timeline(data, 'wavelength')
            display_name = self._get_display_name(algo_name)

            if timestamps and avg_utils:
                ax.plot(timestamps, avg_utils,
                       label=f'{display_name}',
                       color=colors[idx % len(colors)],
                       linewidth=1.5, marker=markers[idx % len(markers)],
                       markersize=4, alpha=0.95,
                       markeredgewidth=0.8,
                       markeredgecolor='white',
                       markevery=max(1, len(timestamps)//10))

        ax.set_xlabel('Time (s)', fontsize=9)
        ax.set_ylabel('Wavelength Utilization (%)', fontsize=9)
        ax.legend(loc='upper right', fontsize=7, framealpha=0.95,
                 edgecolor='black', fancybox=False, shadow=False)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 105)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=8, width=0.75, length=4,
                      direction='in', top=True, right=True)

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_wavelength_utilization_summary_single_column.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"波长利用率单栏汇总对比图已保存: {save_path}")
        return str(save_path)

    def plot_gpu_utilization_statistics(self, save_path: Optional[str] = None) -> str:
        """
        绘制GPU利用率统计对比柱状图
        
        显示各算法的GPU利用率平均值和标准差
        横坐标: Algorithm
        纵坐标: GPU Utilization (%)
        
        Args:
            save_path: 保存路径
            
        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过GPU利用率统计图生成")
            return ""
        
        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""
        
        algo_stats = {}
        
        for algo_name, data_list in self.simulation_data.items():
            if not data_list:
                continue
            
            all_gpu_utils = []
            
            for data in data_list:
                resource_snapshots = data.get('resource_snapshots', [])
                for snapshot in resource_snapshots:
                    gpu_utils = snapshot.get('gpu_utilization', {})
                    if gpu_utils:
                        all_gpu_utils.extend(gpu_utils.values())
            
            if all_gpu_utils:
                algo_stats[algo_name] = {
                    'avg': np.mean(all_gpu_utils) * 100,
                    'std': np.std(all_gpu_utils) * 100
                }
        
        if not algo_stats:
            LOGGER.warning("没有GPU利用率数据可供对比")
            return ""

        # IEEE学术出版标准尺寸
        fig, ax = plt.subplots(figsize=(IEEE_SINGLE_COLUMN_WIDTH, 2.8))

        algo_names = list(algo_stats.keys())
        display_names = [self._get_display_name(name) for name in algo_names]

        # IEEE学术出版推荐配色
        colors = IEEE_COLORS

        gpu_avgs = [algo_stats[name]['avg'] for name in algo_names]
        gpu_stds = [algo_stats[name]['std'] for name in algo_names]

        bars = ax.bar(display_names, gpu_avgs, yerr=gpu_stds, capsize=3,
                     color=colors[:len(algo_names)], edgecolor='black', alpha=0.9, linewidth=1)

        ax.set_ylabel('GPU Utilization (%)', fontsize=10)
        ax.grid(True, alpha=0.4, axis='y', linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 105)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=9, width=0.75, length=4,
                      direction='in', top=True, right=True)
        ax.set_xticklabels(display_names, rotation=15, ha='center', fontsize=9)

        for bar, avg in zip(bars, gpu_avgs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                   f'{avg:.1f}%', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_gpu_utilization_statistics.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"GPU利用率统计图已保存: {save_path}")
        return str(save_path)

    def plot_wavelength_utilization_statistics(self, save_path: Optional[str] = None) -> str:
        """
        绘制波长利用率统计对比柱状图

        显示各算法的波长利用率平均值
        横坐标: Algorithm
        纵坐标: Wavelength Utilization (%)

        Args:
            save_path: 保存路径

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过波长利用率统计图生成")
            return ""

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return ""

        algo_stats = {}

        for algo_name, data_list in self.simulation_data.items():
            if not data_list:
                continue

            all_wave_utils = []

            for data in data_list:
                resource_snapshots = data.get('resource_snapshots', [])
                for snapshot in resource_snapshots:
                    wave_utils = snapshot.get('wavelength_utilization', {})
                    if wave_utils:
                        all_wave_utils.extend(wave_utils.values())

            if all_wave_utils:
                algo_stats[algo_name] = {
                    'avg': np.mean(all_wave_utils) * 100
                }

        if not algo_stats:
            LOGGER.warning("没有波长利用率数据可供对比")
            return ""

        # IEEE学术出版标准尺寸
        fig, ax = plt.subplots(figsize=(IEEE_SINGLE_COLUMN_WIDTH, 2.8))

        algo_names = list(algo_stats.keys())
        display_names = [self._get_display_name(name) for name in algo_names]

        # IEEE学术出版推荐配色
        colors = IEEE_COLORS

        wave_avgs = [algo_stats[name]['avg'] for name in algo_names]

        bars = ax.bar(display_names, wave_avgs,
                     color=colors[:len(algo_names)], edgecolor='black', alpha=0.9, linewidth=1)

        ax.set_ylabel('Wavelength Utilization (%)', fontsize=10)
        ax.grid(True, alpha=0.4, axis='y', linestyle='--', linewidth=0.75)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 105)

        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

        ax.tick_params(axis='both', which='major', labelsize=9, width=0.75, length=4,
                      direction='in', top=True, right=True)
        ax.set_xticklabels(display_names, rotation=15, ha='center', fontsize=9)

        for bar, avg in zip(bars, wave_avgs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                   f'{avg:.1f}%', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = self.figures_dir / f"{timestamp}_wavelength_utilization_statistics.png"

        plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        LOGGER.info(f"波长利用率统计图已保存: {save_path}")
        return str(save_path)

    def generate_all_comparisons(self) -> Dict[str, str]:
        """
        生成所有对比图表

        Returns:
            Dict: 生成的图表文件路径字典
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，无法生成可视化图表")
            return {}

        if not self.simulation_data:
            LOGGER.warning("没有仿真数据可供可视化")
            return {}

        generated_files = {}

        # 折线图对比
        try:
            generated_files['level_line'] = self.plot_algorithm_comparison_line('level_value')
            generated_files['jct_line'] = self.plot_algorithm_comparison_line('jct')
            generated_files['exec_time_line'] = self.plot_algorithm_comparison_line('execution_time')
        except Exception as e:
            LOGGER.error(f"生成折线图失败: {e}")

        # 柱状图对比
        try:
            generated_files['bar_comparison'] = self.plot_algorithm_comparison_bar()
        except Exception as e:
            LOGGER.error(f"生成柱状图失败: {e}")

        # 阻塞分析对比
        try:
            generated_files['blocking_analysis'] = self.plot_blocking_analysis()
        except Exception as e:
            LOGGER.error(f"生成阻塞分析图失败: {e}")
        
        # GPU利用率汇总对比（折线图）
        try:
            generated_files['gpu_utilization_summary'] = self.plot_gpu_utilization_summary_comparison()
        except Exception as e:
            LOGGER.error(f"生成GPU利用率汇总对比图失败: {e}")
        
        # 波长利用率汇总对比（折线图）
        try:
            generated_files['wavelength_utilization_summary'] = self.plot_wavelength_utilization_summary_comparison()
        except Exception as e:
            LOGGER.error(f"生成波长利用率汇总对比图失败: {e}")
        
        # GPU利用率统计对比（柱状图）
        try:
            generated_files['gpu_utilization_statistics'] = self.plot_gpu_utilization_statistics()
        except Exception as e:
            LOGGER.error(f"生成GPU利用率统计图失败: {e}")
        
        # 波长利用率统计对比（柱状图）
        try:
            generated_files['wavelength_utilization_statistics'] = self.plot_wavelength_utilization_statistics()
        except Exception as e:
            LOGGER.error(f"生成波长利用率统计图失败: {e}")

        # GPU利用率汇总对比（单栏折线图）
        try:
            generated_files['gpu_utilization_summary_single_column'] = self.plot_gpu_utilization_summary_single_column()
        except Exception as e:
            LOGGER.error(f"生成GPU利用率单栏汇总对比图失败: {e}")

        # 波长利用率汇总对比（单栏折线图）
        try:
            generated_files['wavelength_utilization_summary_single_column'] = self.plot_wavelength_utilization_summary_single_column()
        except Exception as e:
            LOGGER.error(f"生成波长利用率单栏汇总对比图失败: {e}")

        LOGGER.info(f"所有对比图表生成完成，共 {len([v for v in generated_files.values() if v])} 个文件")
        return generated_files

    def export_comparison_report(self, report_path: Optional[str] = None) -> str:
        """
        导出对比报告为JSON

        Args:
            report_path: 报告保存路径

        Returns:
            str: 报告文件路径
        """
        report = self.generate_comparison_report()

        if report_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = self.result_dir / f"{timestamp}_comparison_report.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        LOGGER.info(f"对比报告已导出: {report_path}")
        return str(report_path)


def main():
    """
    命令行入口
    """
    import argparse

    parser = argparse.ArgumentParser(description='多仿真结果对比可视化')
    parser.add_argument('--result-dir', '-r', type=str, default='result',
                       help='结果文件目录 (默认: result)')
    parser.add_argument('--pattern', '-p', type=str, default='*.json',
                       help='文件匹配模式 (默认: *.json)')
    parser.add_argument('--output-dir', '-o', type=str, default=None,
                       help='输出目录')
    parser.add_argument('--report', action='store_true',
                       help='生成统计报告')

    args = parser.parse_args()

    visualizer = MultiSimulationVisualizer(result_dir=args.result_dir)

    # 加载仿真文件
    visualizer.load_simulation_files(pattern=args.pattern)

    if not visualizer.simulation_data:
        print("未找到仿真数据文件")
        return

    # 生成对比图表
    generated = visualizer.generate_all_comparisons()

    print("\n生成的对比图表:")
    for name, path in generated.items():
        if path:
            print(f"  {name}: {path}")

    # 生成报告
    if args.report:
        report_path = visualizer.export_comparison_report()
        print(f"\n统计报告: {report_path}")


if __name__ == "__main__":
    main()
