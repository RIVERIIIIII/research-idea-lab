#!/usr/bin/env python3
"""
可视化模块 - 用于生成仿真性能数据的可视化图表

功能：
1. 算法性能对比图（Level值、JCT、执行时间）
2. 资源利用率时间序列图
3. 服务完成/阻塞分布图
4. 综合性能仪表板
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# 尝试导入matplotlib，如果不可用则提供降级方案
try:
    import matplotlib.pyplot as plt
    import matplotlib
    import matplotlib.font_manager as fm
    from matplotlib.ticker import MaxNLocator
    matplotlib.use('Agg')  # 使用非交互式后端
    
    # 重建字体缓存以确保识别系统字体
    try:
        fm._load_fontmanager(try_read_cache=False)
    except Exception:
        pass
    
    # 配置中文字体支持 - 使用matplotlib能识别的字体
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib未安装，可视化功能将不可用")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

from result import LOGGER


class PerformanceVisualizer:
    """
    性能数据可视化器
    """
    
    def __init__(self, result_dir: str = "result"):
        """
        初始化可视化器
        
        Args:
            result_dir: 结果文件根目录
        """
        self.result_dir = Path(result_dir)
        self.figures_dir = self.result_dir / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，无法生成可视化图表")
    
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
    
    def load_performance_data(self, json_file: str) -> Dict[str, Any]:
        """
        从JSON文件加载性能数据
        
        Args:
            json_file: JSON文件路径
            
        Returns:
            Dict: 性能数据字典
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def plot_algorithm_comparison(self, data: Dict[str, Any], save_path: Optional[str] = None) -> str:
        """
        绘制算法性能指标图（单算法仿真模式）
        包含所有事件类型，单DC成功事件和阻塞事件以特殊标记显示

        Args:
            data: 性能数据字典
            save_path: 保存路径，默认自动生成

        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过算法性能图生成")
            return ""

        algorithm_metrics = data.get('algorithm_metrics', [])

        if not algorithm_metrics:
            LOGGER.warning("没有算法性能数据可供可视化")
            return ""

        # 获取算法名称
        algorithm_name = data.get('simulation_info', {}).get('algorithm_name', 'unknown')

        # 提取指标数据和event_id
        event_ids = [m['event_id'] for m in algorithm_metrics]
        level_values = [m['level_value'] for m in algorithm_metrics]
        jct_values = [m['jct'] for m in algorithm_metrics]
        execution_times = [m['execution_time'] for m in algorithm_metrics]
        num_wavelengths = [m['num_wavelengths'] for m in algorithm_metrics]

        # 使用统一的状态判断逻辑区分事件类型
        # 三种状态：success_multi_dc, success_single_dc, blocked
        event_statuses = [self._classify_event_status(l, j) for l, j in zip(level_values, jct_values)]
        
        # 分类事件索引
        multi_dc_indices = [i for i, status in enumerate(event_statuses) if status == 'success_multi_dc']
        single_dc_indices = [i for i, status in enumerate(event_statuses) if status == 'success_single_dc']
        blocked_indices = [i for i, status in enumerate(event_statuses) if status == 'blocked']

        # 提取各类事件的event_id
        multi_dc_event_ids = [event_ids[i] for i in multi_dc_indices]
        single_dc_event_ids = [event_ids[i] for i in single_dc_indices]
        blocked_event_ids = [event_ids[i] for i in blocked_indices]

        # 使用seaborn配色方案
        if SEABORN_AVAILABLE:
            colors = sns.color_palette("deep")
            multi_dc_color = colors[0]
            single_dc_color = 'gold'
            blocked_color = colors[3]
        else:
            multi_dc_color = '#1f77b4'
            single_dc_color = 'gold'
            blocked_color = '#d62728'

        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'算法性能指标 - {algorithm_name}', fontsize=18, fontweight='bold', y=0.98)

        # 1. Level值图表
        ax = axes[0, 0]
        # 绘制多DC成功事件的Level值
        if multi_dc_event_ids:
            multi_dc_levels = [level_values[i] for i in multi_dc_indices]
            ax.plot(multi_dc_event_ids, multi_dc_levels, '-o', color=multi_dc_color, 
                   label='多DC事件', markersize=5, linewidth=1.5, alpha=0.8)
            # 添加平均线（仅多DC场景）
            avg_level = np.mean(multi_dc_levels)
            ax.axhline(avg_level, color='green', linestyle='--', linewidth=2, 
                      alpha=0.7, label=f'平均值: {avg_level:.4f}')
        
        # 绘制单DC成功事件（使用星形标记，显示在y=0位置）
        if single_dc_event_ids:
            ax.scatter(single_dc_event_ids, [0]*len(single_dc_event_ids), 
                      marker='*', color=single_dc_color, s=200, edgecolors='black',
                      linewidths=1, label='单DC场景(Level=∞)', zorder=10)
        
        # 绘制阻塞事件
        if blocked_event_ids:
            blocked_levels = [0] * len(blocked_event_ids)  # 阻塞事件显示在y=0
            ax.scatter(blocked_event_ids, blocked_levels, color=blocked_color, marker='x', 
                      s=120, linewidths=2, label='阻塞事件', zorder=5)
        
        ax.set_xlabel('事件ID', fontsize=11)
        ax.set_ylabel('Level值', fontsize=11)
        ax.set_title('Level值变化趋势', fontsize=13, fontweight='bold')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(loc='best', framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')

        # 2. JCT图表（转换为小时显示，更易读）
        ax = axes[0, 1]
        # 所有成功事件（多DC和单DC）都显示JCT
        all_success_indices = multi_dc_indices + single_dc_indices
        all_success_event_ids = multi_dc_event_ids + single_dc_event_ids
        if all_success_event_ids:
            all_success_jcts = [jct_values[i] / 3600 for i in all_success_indices]  # 转换为小时
            # 按event_id排序
            sorted_pairs = sorted(zip(all_success_event_ids, all_success_jcts))
            sorted_event_ids, sorted_jcts = zip(*sorted_pairs) if sorted_pairs else ([], [])
            ax.plot(sorted_event_ids, sorted_jcts, '-s', color='#2ca02c', 
                   label='成功事件', markersize=5, linewidth=1.5, alpha=0.8)
            # 添加平均线
            if sorted_jcts:
                avg_jct = np.mean(sorted_jcts)
                ax.axhline(avg_jct, color='orange', linestyle='--', linewidth=2, 
                          alpha=0.7, label=f'平均值: {avg_jct:.1f}h')
        
        # 阻塞事件的JCT为0
        if blocked_event_ids:
            ax.scatter(blocked_event_ids, [0]*len(blocked_event_ids), color=blocked_color, marker='x', 
                      s=120, linewidths=2, label='阻塞事件', zorder=5)
        
        ax.set_xlabel('事件ID', fontsize=11)
        ax.set_ylabel('JCT (小时)', fontsize=11)
        ax.set_title('任务完成时间(JCT)', fontsize=13, fontweight='bold')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(loc='best', framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')

        # 3. 执行时间图表
        ax = axes[1, 0]
        # 所有成功事件显示执行时间
        if all_success_event_ids:
            all_success_exec_times = [execution_times[i] for i in all_success_indices]
            sorted_pairs = sorted(zip(all_success_event_ids, all_success_exec_times))
            sorted_event_ids, sorted_exec_times = zip(*sorted_pairs) if sorted_pairs else ([], [])
            ax.plot(sorted_event_ids, sorted_exec_times, '-^', color='#ff7f0e', 
                   label='成功事件', markersize=5, linewidth=1.5, alpha=0.8)
            # 添加平均线
            if sorted_exec_times:
                avg_exec = np.mean(sorted_exec_times)
                ax.axhline(avg_exec, color='purple', linestyle='--', linewidth=2, 
                          alpha=0.7, label=f'平均值: {avg_exec:.4f}s')
        
        # 阻塞事件也可能有执行时间（算法尝试执行的时间）
        if blocked_event_ids:
            blocked_exec_times = [execution_times[i] for i in blocked_indices]
            ax.scatter(blocked_event_ids, blocked_exec_times, color=blocked_color, marker='x', 
                      s=120, linewidths=2, label='阻塞事件', zorder=5)
        
        ax.set_xlabel('事件ID', fontsize=11)
        ax.set_ylabel('执行时间 (秒)', fontsize=11)
        ax.set_title('算法执行时间', fontsize=13, fontweight='bold')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(loc='best', framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')

        # 4. 波长数量图表
        ax = axes[1, 1]
        # 多DC成功事件显示波长数量
        if multi_dc_event_ids:
            multi_dc_waves = [num_wavelengths[i] for i in multi_dc_indices]
            ax.plot(multi_dc_event_ids, multi_dc_waves, '-d', color='#9467bd', 
                   label='多DC事件', markersize=5, linewidth=1.5, alpha=0.8)
            # 添加平均线
            avg_waves = np.mean(multi_dc_waves)
            ax.axhline(avg_waves, color='teal', linestyle='--', linewidth=2, 
                      alpha=0.7, label=f'平均值: {avg_waves:.1f}')
        
        # 单DC成功事件波长数量为0，使用特殊标记
        if single_dc_event_ids:
            ax.scatter(single_dc_event_ids, [0]*len(single_dc_event_ids), 
                      marker='*', color=single_dc_color, s=200, edgecolors='black',
                      linewidths=1, label='单DC场景(波长=0)', zorder=10)
        
        # 阻塞事件
        if blocked_event_ids:
            blocked_waves = [num_wavelengths[i] for i in blocked_indices]
            ax.scatter(blocked_event_ids, blocked_waves, color=blocked_color, marker='x', 
                      s=120, linewidths=2, label='阻塞事件', zorder=5)
        
        ax.set_xlabel('事件ID', fontsize=11)
        ax.set_ylabel('波长数量', fontsize=11)
        ax.set_title('波长使用数量', fontsize=13, fontweight='bold')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(loc='best', framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')

        # 添加统计摘要文本框（区分三种状态）
        total_success = len(multi_dc_event_ids) + len(single_dc_event_ids)
        stats_text = f"统计摘要: 多DC成功 {len(multi_dc_event_ids)} 个, 单DC成功 {len(single_dc_event_ids)} 个, 阻塞 {len(blocked_event_ids)} 个"
        if event_ids:
            stats_text += f"\n阻塞率: {len(blocked_event_ids)/len(event_ids)*100:.1f}%"
        fig.text(0.5, 0.01, stats_text, ha='center', fontsize=11, 
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

        plt.tight_layout(rect=[0, 0.03, 1, 0.96])

        if save_path is None:
            timestamp = data.get('simulation_info', {}).get('start_time', '').replace(':', '-')
            save_path = self.figures_dir / f"{timestamp}_algorithm_metrics.png"

        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        LOGGER.info(f"算法性能图已保存: {save_path}")
        return str(save_path)
    
    def _extract_resource_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从性能数据中提取资源利用率数据
        
        Args:
            data: 性能数据字典
            
        Returns:
            Dict: 包含timestamps, all_gpu_utils, all_bw_utils, all_wave_utils的字典
        """
        resource_snapshots = data.get('resource_snapshots', [])
        
        if not resource_snapshots:
            return {'timestamps': [], 'all_gpu_utils': {}, 'all_bw_utils': {}, 'all_wave_utils': {}}
        
        timestamps = [s['timestamp'] for s in resource_snapshots]
        
        all_gpu_utils = {}
        all_bw_utils = {}
        all_wave_utils = {}
        
        for snapshot in resource_snapshots:
            for dc_id, util in snapshot.get('gpu_utilization', {}).items():
                if dc_id not in all_gpu_utils:
                    all_gpu_utils[dc_id] = []
                all_gpu_utils[dc_id].append(util * 100)
            
            for link, util in snapshot.get('bandwidth_utilization', {}).items():
                if link not in all_bw_utils:
                    all_bw_utils[link] = []
                all_bw_utils[link].append(util * 100)
            
            for link, util in snapshot.get('wavelength_utilization', {}).items():
                if link not in all_wave_utils:
                    all_wave_utils[link] = []
                all_wave_utils[link].append(util * 100)
        
        return {
            'timestamps': timestamps,
            'all_gpu_utils': all_gpu_utils,
            'all_bw_utils': all_bw_utils,
            'all_wave_utils': all_wave_utils
        }
    
    def plot_gpu_utilization_timeline(self, data: Dict[str, Any], save_path: Optional[str] = None) -> str:
        """
        绘制GPU利用率趋势图
        
        Args:
            data: 性能数据字典
            save_path: 保存路径
            
        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过GPU利用率图生成")
            return ""
        
        resource_data = self._extract_resource_data(data)
        timestamps = resource_data['timestamps']
        all_gpu_utils = resource_data['all_gpu_utils']
        
        if not timestamps or not all_gpu_utils:
            LOGGER.warning("没有GPU利用率数据可供可视化")
            return ""
        
        # 将时间戳转换为相对时间（从第一个时间戳开始计算）
        base_timestamp = timestamps[0] if timestamps else 0
        relative_timestamps = [t - base_timestamp for t in timestamps]
        
        # 创建独立图表
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle('GPU利用率趋势', fontsize=16, fontweight='bold')
        
        # 使用seaborn配色
        if SEABORN_AVAILABLE:
            colors = sns.color_palette("husl", len(all_gpu_utils))
        else:
            colors = plt.cm.tab10.colors
        
        # 绘制各DC的GPU利用率
        for idx, (dc_id, utils) in enumerate(sorted(all_gpu_utils.items())):
            if len(utils) == len(timestamps):
                ax.plot(relative_timestamps, utils, label=f'DC {dc_id}', 
                       color=colors[idx % len(colors)], linewidth=1.5, marker='o', markersize=4, alpha=0.8)
        
        # 计算并绘制平均GPU利用率
        if all_gpu_utils:
            avg_gpu = [sum(vals) / len(vals) for vals in zip(*all_gpu_utils.values())]
            ax.plot(relative_timestamps, avg_gpu, 'k-', linewidth=3, label='平均利用率', alpha=0.9)
        
        ax.set_xlabel('相对时间 (秒)', fontsize=12)
        ax.set_ylabel('GPU利用率 (%)', fontsize=12)
        ax.legend(loc='upper right', fontsize=9, ncol=2, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 105)
        
        # 添加统计摘要文本框
        all_gpu_vals = [v for utils in all_gpu_utils.values() for v in utils]
        stats_text = f"平均: {np.mean(all_gpu_vals):.1f}%  |  峰值: {np.max(all_gpu_vals):.1f}%  |  最小: {np.min(all_gpu_vals):.1f}%"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        if save_path is None:
            timestamp = data.get('simulation_info', {}).get('start_time', '').replace(':', '-')
            save_path = self.figures_dir / f"{timestamp}_gpu_utilization.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        LOGGER.info(f"GPU利用率图已保存: {save_path}")
        return str(save_path)
    
    def plot_bandwidth_utilization_timeline(self, data: Dict[str, Any], save_path: Optional[str] = None) -> str:
        """
        绘制带宽利用率趋势图
        
        Args:
            data: 性能数据字典
            save_path: 保存路径
            
        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过带宽利用率图生成")
            return ""
        
        resource_data = self._extract_resource_data(data)
        timestamps = resource_data['timestamps']
        all_bw_utils = resource_data['all_bw_utils']
        
        if not timestamps or not all_bw_utils:
            LOGGER.warning("没有带宽利用率数据可供可视化")
            return ""
        
        # 将时间戳转换为相对时间
        base_timestamp = timestamps[0] if timestamps else 0
        relative_timestamps = [t - base_timestamp for t in timestamps]
        
        # 创建独立图表
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle('带宽利用率趋势', fontsize=16, fontweight='bold')
        
        # 按平均利用率排序，选择Top 10链路
        avg_bw_per_link = {link: sum(utils)/len(utils) for link, utils in all_bw_utils.items()}
        top_links = sorted(avg_bw_per_link.keys(), key=lambda x: avg_bw_per_link[x], reverse=True)[:10]
        
        # 使用seaborn配色
        if SEABORN_AVAILABLE:
            colors = sns.color_palette("husl", len(top_links))
        else:
            colors = plt.cm.tab10.colors
        
        # 绘制各链路的带宽利用率
        for idx, link in enumerate(top_links):
            utils = all_bw_utils[link]
            if len(utils) == len(timestamps):
                ax.plot(relative_timestamps, utils, label=f'链路 {link}', 
                       color=colors[idx % len(colors)], linewidth=1.5, marker='s', markersize=4, alpha=0.8)
        
        # 计算并绘制平均带宽利用率
        if all_bw_utils:
            avg_bw = [sum(vals) / len(vals) for vals in zip(*all_bw_utils.values())]
            ax.plot(relative_timestamps, avg_bw, 'k-', linewidth=3, label='平均利用率', alpha=0.9)
        
        ax.set_xlabel('相对时间 (秒)', fontsize=12)
        ax.set_ylabel('带宽利用率 (%)', fontsize=12)
        ax.legend(loc='upper right', fontsize=9, ncol=2, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 105)
        
        # 添加统计摘要文本框
        all_bw_vals = [v for utils in all_bw_utils.values() for v in utils]
        stats_text = f"平均: {np.mean(all_bw_vals):.1f}%  |  峰值: {np.max(all_bw_vals):.1f}%  |  最小: {np.min(all_bw_vals):.1f}%"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        if save_path is None:
            timestamp = data.get('simulation_info', {}).get('start_time', '').replace(':', '-')
            save_path = self.figures_dir / f"{timestamp}_bandwidth_utilization.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        LOGGER.info(f"带宽利用率图已保存: {save_path}")
        return str(save_path)
    
    def plot_wavelength_utilization_timeline(self, data: Dict[str, Any], save_path: Optional[str] = None) -> str:
        """
        绘制波长利用率趋势图
        
        Args:
            data: 性能数据字典
            save_path: 保存路径
            
        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过波长利用率图生成")
            return ""
        
        resource_data = self._extract_resource_data(data)
        timestamps = resource_data['timestamps']
        all_wave_utils = resource_data['all_wave_utils']
        
        if not timestamps or not all_wave_utils:
            LOGGER.warning("没有波长利用率数据可供可视化")
            return ""
        
        # 将时间戳转换为相对时间
        base_timestamp = timestamps[0] if timestamps else 0
        relative_timestamps = [t - base_timestamp for t in timestamps]
        
        # 创建独立图表
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle('波长利用率趋势', fontsize=16, fontweight='bold')
        
        # 按平均利用率排序，选择Top 10链路
        avg_wave_per_link = {link: sum(utils)/len(utils) for link, utils in all_wave_utils.items()}
        top_links = sorted(avg_wave_per_link.keys(), key=lambda x: avg_wave_per_link[x], reverse=True)[:10]
        
        # 使用seaborn配色
        if SEABORN_AVAILABLE:
            colors = sns.color_palette("husl", len(top_links))
        else:
            colors = plt.cm.tab10.colors
        
        # 绘制各链路的波长利用率
        for idx, link in enumerate(top_links):
            utils = all_wave_utils[link]
            if len(utils) == len(timestamps):
                ax.plot(relative_timestamps, utils, label=f'链路 {link}', 
                       color=colors[idx % len(colors)], linewidth=1.5, marker='^', markersize=4, alpha=0.8)
        
        # 计算并绘制平均波长利用率
        if all_wave_utils:
            avg_wave = [sum(vals) / len(vals) for vals in zip(*all_wave_utils.values())]
            ax.plot(relative_timestamps, avg_wave, 'k-', linewidth=3, label='平均利用率', alpha=0.9)
        
        ax.set_xlabel('相对时间 (秒)', fontsize=12)
        ax.set_ylabel('波长利用率 (%)', fontsize=12)
        ax.legend(loc='upper right', fontsize=9, ncol=2, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 105)
        
        # 添加统计摘要文本框
        all_wave_vals = [v for utils in all_wave_utils.values() for v in utils]
        stats_text = f"平均: {np.mean(all_wave_vals):.1f}%  |  峰值: {np.max(all_wave_vals):.1f}%  |  最小: {np.min(all_wave_vals):.1f}%"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        if save_path is None:
            timestamp = data.get('simulation_info', {}).get('start_time', '').replace(':', '-')
            save_path = self.figures_dir / f"{timestamp}_wavelength_utilization.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        LOGGER.info(f"波长利用率图已保存: {save_path}")
        return str(save_path)
    
    def plot_resource_heatmap(self, data: Dict[str, Any], save_path: Optional[str] = None) -> str:
        """
        绘制资源利用率热力图
        
        Args:
            data: 性能数据字典
            save_path: 保存路径
            
        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE or not SEABORN_AVAILABLE:
            LOGGER.warning("matplotlib或seaborn未安装，跳过热力图生成")
            return ""
        
        resource_snapshots = data.get('resource_snapshots', [])
        
        if not resource_snapshots:
            LOGGER.warning("没有资源利用率数据可供可视化")
            return ""
        
        # 提取GPU利用率数据构建矩阵
        all_dc_ids = set()
        for snapshot in resource_snapshots:
            all_dc_ids.update(snapshot.get('gpu_utilization', {}).keys())
        
        all_dc_ids = sorted(all_dc_ids)
        
        if not all_dc_ids:
            LOGGER.warning("没有GPU利用率数据")
            return ""
        
        # 构建GPU利用率矩阵 (时间 x DC)
        gpu_matrix = []
        for snapshot in resource_snapshots:
            row = [snapshot.get('gpu_utilization', {}).get(dc_id, 0) * 100 for dc_id in all_dc_ids]
            gpu_matrix.append(row)
        
        gpu_matrix = np.array(gpu_matrix)
        
        # 创建热力图
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('资源利用率热力图', fontsize=16, fontweight='bold')
        
        # GPU利用率热力图
        ax = axes[0]
        if gpu_matrix.size > 0:
            sns.heatmap(gpu_matrix.T, ax=ax, cmap='YlOrRd', 
                       xticklabels=False, yticklabels=[f'DC {dc_id}' for dc_id in all_dc_ids],
                       cbar_kws={'label': '利用率 (%)'}, vmin=0, vmax=100)
            ax.set_xlabel('时间序列')
            ax.set_ylabel('数据中心')
            ax.set_title('GPU利用率热力图')
        
        # 带宽利用率热力图
        ax = axes[1]
        all_links = set()
        for snapshot in resource_snapshots:
            all_links.update(snapshot.get('bandwidth_utilization', {}).keys())
        
        all_links = sorted(all_links)[:10]  # 限制显示前10条链路
        
        if all_links:
            bw_matrix = []
            for snapshot in resource_snapshots:
                row = [snapshot.get('bandwidth_utilization', {}).get(link, 0) * 100 for link in all_links]
                bw_matrix.append(row)
            
            bw_matrix = np.array(bw_matrix)
            if bw_matrix.size > 0:
                sns.heatmap(bw_matrix.T, ax=ax, cmap='YlGnBu', 
                           xticklabels=False, yticklabels=[f'{link}' for link in all_links],
                           cbar_kws={'label': '利用率 (%)'}, vmin=0, vmax=100)
                ax.set_xlabel('时间序列')
                ax.set_ylabel('链路')
                ax.set_title('带宽利用率热力图 (Top 10链路)')
        else:
            ax.text(0.5, 0.5, '无带宽利用率数据', ha='center', va='center', fontsize=14)
            ax.set_title('带宽利用率热力图')
        
        plt.tight_layout()
        
        if save_path is None:
            timestamp = data.get('simulation_info', {}).get('start_time', '').replace(':', '-')
            save_path = self.figures_dir / f"{timestamp}_resource_heatmap.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        LOGGER.info(f"资源热力图已保存: {save_path}")
        return str(save_path)
    
    def plot_performance_dashboard(self, data: Dict[str, Any], save_path: Optional[str] = None,
                                     include_auxiliary: bool = False) -> str:
        """
        绘制综合性能仪表板（精简版，仅保留核心学术价值图表）
        
        学术价值说明：
        - 关键指标卡片：展示仿真整体统计，便于快速了解性能概况
        - Level值趋势：反映算法优化效果，是多算法对比的核心指标
        - JCT趋势：任务完成时间，直接影响用户体验，核心性能指标
        - 阻塞率统计：资源调度效率的关键度量
        
        已移除的冗余图表（缺乏对比意义）：
        - 执行时间分布：与任务规模强相关，单算法无对比价值
        - 波长使用分布：单算法分布无对比意义
        - DC使用分布：单算法分布无对比意义
        - GPU使用分布：可作为辅助信息，但不作为独立图表输出
        
        Args:
            data: 性能数据字典
            save_path: 保存路径
            include_auxiliary: 是否包含辅助信息图表（默认False）
            
        Returns:
            str: 保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，跳过仪表板生成")
            return ""
        
        summary = data.get('summary', {})
        sim_info = summary.get('simulation_info', {})
        service_stats = summary.get('service_statistics', {})
        
        # 根据是否包含辅助图表调整布局
        if include_auxiliary:
            fig = plt.figure(figsize=(18, 10))
            gs = fig.add_gridspec(2, 4, hspace=0.3, wspace=0.3)
        else:
            fig = plt.figure(figsize=(16, 8))
            gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        fig.suptitle(f"仿真性能仪表板 - {sim_info.get('algorithm_name', 'Unknown')}", 
                    fontsize=16, fontweight='bold')
        
        # 1. 关键指标卡片 (顶部) - 核心学术价值：快速了解整体性能
        ax_kpi = fig.add_subplot(gs[0, :2] if not include_auxiliary else gs[0, :])
        ax_kpi.axis('off')
        
        kpi_text = (
            f"总事件数: {sim_info.get('total_events', 0)}    |    "
            f"完成数: {sim_info.get('completed_events', 0)}    |    "
            f"阻塞数: {sim_info.get('blocked_events', 0)}    |    "
            f"阻塞率: {sim_info.get('block_rate', 0)*100:.1f}%    |    "
            f"平均JCT: {service_stats.get('avg_jct', 0):.2f}s    |    "
            f"平均Level: {service_stats.get('avg_level', 0):.4f}"
        )
        ax_kpi.text(0.5, 0.5, kpi_text, ha='center', va='center', fontsize=13,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.5))
        
        algo_metrics = data.get('algorithm_metrics', [])
        # 使用统一的状态判断逻辑
        event_statuses = []
        if algo_metrics:
            level_values = [m['level_value'] for m in algo_metrics]
            jct_values = [m['jct'] for m in algo_metrics]
            event_statuses = [self._classify_event_status(l, j) for l, j in zip(level_values, jct_values)]
        
        # 分类事件索引
        multi_dc_indices = [i for i, status in enumerate(event_statuses) if status == 'success_multi_dc']
        single_dc_indices = [i for i, status in enumerate(event_statuses) if status == 'success_single_dc']
        blocked_indices = [i for i, status in enumerate(event_statuses) if status == 'blocked']
        
        # 2. Level值趋势 - 核心学术价值：算法优化效果的核心指标
        ax_level = fig.add_subplot(gs[1, 0])
        if algo_metrics:
            event_ids = [m['event_id'] for m in algo_metrics]
            level_values = [m['level_value'] for m in algo_metrics]
            
            # 多DC成功事件
            multi_dc_event_ids = [event_ids[i] for i in multi_dc_indices]
            multi_dc_levels = [level_values[i] for i in multi_dc_indices]
            
            # 单DC成功事件
            single_dc_event_ids = [event_ids[i] for i in single_dc_indices]
            
            # 阻塞事件
            blocked_event_ids = [event_ids[i] for i in blocked_indices]
            
            # 绘制多DC成功事件
            if multi_dc_event_ids:
                ax_level.plot(multi_dc_event_ids, multi_dc_levels, 'b-o', markersize=3, 
                             label='多DC事件', linewidth=1, alpha=0.8)
                ax_level.axhline(np.mean(multi_dc_levels), color='green', linestyle='--', 
                               alpha=0.7, label=f'平均: {np.mean(multi_dc_levels):.4f}')
            
            # 绘制单DC成功事件（星形标记）
            if single_dc_event_ids:
                ax_level.scatter(single_dc_event_ids, [0]*len(single_dc_event_ids), 
                               marker='*', color='gold', s=150, edgecolors='black',
                               linewidths=1, label='单DC场景(Level=∞)', zorder=10)
            
            # 绘制阻塞事件
            if blocked_event_ids:
                ax_level.scatter(blocked_event_ids, [0]*len(blocked_event_ids), c='red', marker='x', 
                               s=80, label='阻塞事件', zorder=5)
        
        ax_level.set_xlabel('事件ID')
        ax_level.set_ylabel('Level值')
        ax_level.set_title('Level值趋势（核心指标）')
        ax_level.legend(loc='upper right', fontsize=8)
        ax_level.grid(True, alpha=0.3)
        
        # 3. JCT趋势 - 核心学术价值：任务完成时间，用户体验的直接度量
        ax_jct = fig.add_subplot(gs[1, 1])
        if algo_metrics:
            jct_values = [m['jct'] for m in algo_metrics]
            event_ids = [m['event_id'] for m in algo_metrics]
            
            # 所有成功事件（多DC和单DC）
            all_success_indices = multi_dc_indices + single_dc_indices
            if all_success_indices:
                success_jcts = [jct_values[i] for i in all_success_indices]
                success_ids_jct = [event_ids[i] for i in all_success_indices]
                
                # 按event_id排序
                sorted_pairs = sorted(zip(success_ids_jct, success_jcts))
                sorted_ids, sorted_jcts = zip(*sorted_pairs) if sorted_pairs else ([], [])
                
                if sorted_ids:
                    ax_jct.plot(sorted_ids, sorted_jcts, 'g-s', markersize=3, 
                               label='成功事件', linewidth=1, alpha=0.8)
                    ax_jct.axhline(np.mean(sorted_jcts), color='orange', linestyle='--', 
                                 alpha=0.7, label=f'平均: {np.mean(sorted_jcts):.1f}s')
            
            # 阻塞事件JCT为0
            if blocked_event_ids:
                ax_jct.scatter(blocked_event_ids, [0]*len(blocked_event_ids), c='red', marker='x', 
                              s=80, label='阻塞事件', zorder=5)
        
        ax_jct.set_xlabel('事件ID')
        ax_jct.set_ylabel('JCT (秒)')
        ax_jct.set_title('任务完成时间(JCT)趋势（核心指标）')
        ax_jct.legend(loc='upper right', fontsize=8)
        ax_jct.grid(True, alpha=0.3)
        
        # 辅助信息图表（可选，默认不生成）
        if include_auxiliary and algo_metrics:
            # 辅助信息：GPU使用分布（仅作为辅助参考）
            ax_gpu = fig.add_subplot(gs[1, 2])
            gpus = [m['total_gpus'] for m in algo_metrics if m['total_gpus'] > 0]
            if gpus:
                ax_gpu.hist(gpus, bins=15, color='coral', edgecolor='black', alpha=0.7)
                ax_gpu.axvline(np.mean(gpus), color='blue', linestyle='--',
                             label=f'平均: {np.mean(gpus):.0f}')
                ax_gpu.legend(fontsize=8)
            ax_gpu.set_xlabel('GPU数量')
            ax_gpu.set_ylabel('频次')
            ax_gpu.set_title('GPU使用分布（辅助信息）')
            ax_gpu.grid(True, alpha=0.3)
            
            # 辅助信息：资源使用摘要
            ax_summary = fig.add_subplot(gs[1, 3])
            ax_summary.axis('off')
            
            # 计算辅助统计信息
            exec_times = [m['execution_time'] for m in algo_metrics if m['execution_time'] > 0]
            wavelengths = [m['num_wavelengths'] for m in algo_metrics if m['num_wavelengths'] > 0]
            dc_counts = [m['num_dcs'] for m in algo_metrics if m['num_dcs'] > 0]
            
            aux_text = "辅助统计信息:\n"
            if exec_times:
                aux_text += f"平均执行时间: {np.mean(exec_times):.4f}s\n"
            if wavelengths:
                aux_text += f"平均波长数: {np.mean(wavelengths):.1f}\n"
            if dc_counts:
                aux_text += f"平均DC数: {np.mean(dc_counts):.1f}\n"
            if gpus:
                aux_text += f"平均GPU数: {np.mean(gpus):.0f}"
            
            ax_summary.text(0.5, 0.5, aux_text, ha='center', va='center', fontsize=11,
                          bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.5))
        
        if save_path is None:
            timestamp = data.get('simulation_info', {}).get('start_time', '').replace(':', '-')
            suffix = "_full" if include_auxiliary else ""
            save_path = self.figures_dir / f"{timestamp}_performance_dashboard{suffix}.png"
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        LOGGER.info(f"性能仪表板已保存: {save_path}")
        return str(save_path)
    
    def generate_all_visualizations(self, json_file: str, 
                                      include_auxiliary: bool = False) -> Dict[str, str]:
        """
        从JSON文件生成所有可视化图表（精简版，仅保留核心学术价值图表）
        
        图表学术价值分类：
        
        【核心图表 - 默认生成】
        1. algorithm_comparison: 算法性能对比图
           - 学术价值：展示Level值、JCT、执行时间、波长使用等核心指标
           - 用途：多算法对比分析、论文核心图表
           
        2. gpu_utilization: GPU利用率时间序列图
           - 学术价值：反映资源调度效率，资源利用率的核心度量
           - 用途：资源管理效率分析
           
        3. bandwidth_utilization: 带宽利用率时间序列图
           - 学术价值：网络资源使用效率的关键指标
           - 用途：网络资源调度分析
           
        4. wavelength_utilization: 波长利用率时间序列图
           - 学术价值：光网络资源效率的核心度量
           - 用途：波长资源分配分析
           
        5. resource_heatmap: 资源热力图
           - 学术价值：资源使用时空分布的可视化
           - 用途：资源瓶颈识别、负载均衡分析
           
        6. performance_dashboard: 性能仪表板（精简版）
           - 学术价值：综合展示核心性能指标
           - 用途：快速性能概览、报告摘要
        
        【辅助图表 - 可选生成】
        - performance_dashboard_full: 包含辅助信息的完整仪表板
          - 辅助信息：执行时间分布、波长/DC/GPU使用分布
          - 学术价值：单算法场景下缺乏对比意义，仅作参考
        
        Args:
            json_file: 性能数据JSON文件路径
            include_auxiliary: 是否生成辅助信息图表（默认False）
            
        Returns:
            Dict: 生成的图表文件路径字典
        """
        if not MATPLOTLIB_AVAILABLE:
            LOGGER.warning("matplotlib未安装，无法生成可视化图表")
            return {}
        
        data = self.load_performance_data(json_file)
        
        generated_files = {}
        
        # ========== 核心图表生成（默认启用） ==========
        
        # 核心图表1: 算法性能对比图 - 展示Level值、JCT等核心指标
        try:
            generated_files['algorithm_comparison'] = self.plot_algorithm_comparison(data)
        except Exception as e:
            LOGGER.error(f"生成算法对比图失败: {e}")
        
        # 核心图表2-4: 资源利用率时间序列图 - 反映资源调度效率
        try:
            generated_files['gpu_utilization'] = self.plot_gpu_utilization_timeline(data)
        except Exception as e:
            LOGGER.error(f"生成GPU利用率图失败: {e}")
        
        try:
            generated_files['bandwidth_utilization'] = self.plot_bandwidth_utilization_timeline(data)
        except Exception as e:
            LOGGER.error(f"生成带宽利用率图失败: {e}")
        
        try:
            generated_files['wavelength_utilization'] = self.plot_wavelength_utilization_timeline(data)
        except Exception as e:
            LOGGER.error(f"生成波长利用率图失败: {e}")
        
        # 核心图表5: 资源热力图 - 资源使用时空分布
        try:
            generated_files['resource_heatmap'] = self.plot_resource_heatmap(data)
        except Exception as e:
            LOGGER.error(f"生成资源热力图失败: {e}")
        
        # 核心图表6: 性能仪表板（精简版，仅核心指标）
        try:
            generated_files['performance_dashboard'] = self.plot_performance_dashboard(
                data, include_auxiliary=False)
        except Exception as e:
            LOGGER.error(f"生成性能仪表板失败: {e}")
        
        # ========== 辅助图表生成（可选） ==========
        
        # 辅助图表: 完整仪表板（包含执行时间、波长/DC/GPU分布等辅助信息）
        # 注意：这些辅助信息在单算法场景下缺乏对比意义，仅作参考
        if include_auxiliary:
            try:
                generated_files['performance_dashboard_full'] = self.plot_performance_dashboard(
                    data, include_auxiliary=True)
            except Exception as e:
                LOGGER.error(f"生成完整性能仪表板失败: {e}")

        LOGGER.info(f"可视化图表生成完成，共 {len([v for v in generated_files.values() if v])} 个文件")
        return generated_files


def main():
    """
    命令行入口，用于从JSON文件生成可视化
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='生成仿真性能数据可视化')
    parser.add_argument('json_file', type=str, help='性能数据JSON文件路径')
    parser.add_argument('--output-dir', '-o', type=str, default='result/figures',
                       help='输出目录 (默认: result/figures)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json_file):
        print(f"错误: 文件不存在: {args.json_file}")
        return
    
    visualizer = PerformanceVisualizer(result_dir=os.path.dirname(args.output_dir))
    generated = visualizer.generate_all_visualizations(args.json_file)
    
    print("\n生成的可视化文件:")
    for name, path in generated.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
