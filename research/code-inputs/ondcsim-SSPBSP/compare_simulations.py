#!/usr/bin/env python3
"""
算法对比仿真工具

功能：
1. 顺序运行多个算法的仿真
2. 确保使用相同的任务序列进行公平对比
3. 自动生成对比可视化图表
4. 导出统计对比报告

用法示例：

"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from result import LOGGER, init_logger
from multi_simulation_visualizer import MultiSimulationVisualizer


def run_simulation(algorithm: str,
                   task_sequence_file: Optional[str] = None,
                   save_task_sequence: bool = False,
                   random_seed: int = 42,
                   topology: str = 'data/nsfnet_topology.yaml',
                   datacenters: str = 'data/datacenters_OTN.yaml') -> str:
    """
    运行单次仿真

    Args:
        algorithm: 算法名称
        task_sequence_file: 任务序列文件路径
        save_task_sequence: 是否保存任务序列
        random_seed: 随机种子
        topology: 拓扑文件路径
        datacenters: 数据中心配置文件路径

    Returns:
        str: 生成的结果文件路径
    """
    cmd = [
        sys.executable,
        'simulation_OTN.py',
        '--algorithm', algorithm,
        '--topology', topology,
        '--datacenters', datacenters,
        '--log-level', 'INFO'
    ]

    if task_sequence_file:
        cmd.extend(['--task-sequence-file', task_sequence_file])

    if save_task_sequence:
        cmd.append('--save-task-sequence')

    LOGGER.info(f"运行仿真: algorithm={algorithm}, task_sequence={task_sequence_file}")

    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True
        )

        # 打印仿真输出日志
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    LOGGER.info(f"[{algorithm}] {line}")
        if result.stderr:
            for line in result.stderr.split('\n'):
                if line.strip():
                    LOGGER.warning(f"[{algorithm}] {line}")

        # 从输出中提取结果文件路径
        json_file = None
        for line in result.stdout.split('\n'):
            if 'json:' in line.lower():
                json_file = line.split(':', 1)[1].strip()
                break

        if json_file and os.path.exists(json_file):
            LOGGER.info(f"仿真完成: {algorithm} -> {json_file}")
            return json_file
        else:
            # 尝试在result/json_data目录中找到最新的文件
            result_dir = Path('result/json_data')
            if result_dir.exists():
                json_files = sorted(result_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True)
                if json_files:
                    latest_file = str(json_files[0])
                    LOGGER.info(f"找到最新结果文件: {latest_file}")
                    return latest_file

            LOGGER.error(f"未找到结果文件")
            return None

    except subprocess.CalledProcessError as e:
        LOGGER.error(f"仿真运行失败: {e}")
        if e.stdout:
            LOGGER.error(f"stdout: {e.stdout}")
        if e.stderr:
            LOGGER.error(f"stderr: {e.stderr}")
        return None


def compare_algorithms(algorithms: List[str],
                       random_seed: int = 42,
                       use_shared_task_sequence: bool = True,
                       topology: str = 'data/nsfnet_topology.yaml',
                       datacenters: str = 'data/datacenters_OTN.yaml') -> Dict[str, str]:
    """
    对比多个算法的性能

    Args:
        algorithms: 要对比的算法列表
        random_seed: 随机种子
        use_shared_task_sequence: 是否使用共享的任务序列
        topology: 拓扑文件路径
        datacenters: 数据中心配置文件路径

    Returns:
        Dict: {algorithm_name: result_file_path}
    """
    results = {}
    task_sequence_file = None

    # 如果需要共享任务序列，先运行第一个算法并保存任务序列
    if use_shared_task_sequence and len(algorithms) > 1:
        LOGGER.info("=" * 60)
        LOGGER.info(f"第一步: 运行 {algorithms[0]} 并保存任务序列")
        LOGGER.info("=" * 60)

        result_file = run_simulation(
            algorithm=algorithms[0],
            save_task_sequence=True,
            random_seed=random_seed,
            topology=topology,
            datacenters=datacenters
        )

        if result_file:
            results[algorithms[0]] = result_file
            # 从结果文件中提取任务序列文件路径
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                task_config = data.get('summary', {}).get('task_config', {})
                task_sequence_file = task_config.get('task_sequence_file')
                LOGGER.info(f"任务序列已保存: {task_sequence_file}")
            except Exception as e:
                LOGGER.warning(f"无法从结果文件中提取任务序列路径: {e}")
                # 使用默认路径
                task_sequence_file = f"data/task_sequences/task_sequence_{random_seed}.json"
        else:
            LOGGER.error("第一个算法运行失败，无法继续")
            return results

        # 运行剩余的算法，使用相同的任务序列
        for algo in algorithms[1:]:
            LOGGER.info("=" * 60)
            LOGGER.info(f"运行算法: {algo}")
            LOGGER.info("=" * 60)

            result_file = run_simulation(
                algorithm=algo,
                task_sequence_file=task_sequence_file,
                random_seed=random_seed,
                topology=topology,
                datacenters=datacenters
            )

            if result_file:
                results[algo] = result_file
            else:
                LOGGER.error(f"算法 {algo} 运行失败")

    else:
        # 独立运行每个算法
        for algo in algorithms:
            LOGGER.info("=" * 60)
            LOGGER.info(f"运行算法: {algo}")
            LOGGER.info("=" * 60)

            result_file = run_simulation(
                algorithm=algo,
                random_seed=random_seed,
                topology=topology,
                datacenters=datacenters
            )

            if result_file:
                results[algo] = result_file
            else:
                LOGGER.error(f"算法 {algo} 运行失败")

    return results


def generate_comparison_visualizations(result_files: Dict[str, str],
                                       output_dir: str = "result") -> Dict[str, str]:
    """
    生成对比可视化图表

    Args:
        result_files: {algorithm_name: result_file_path}
        output_dir: 输出目录

    Returns:
        Dict: 生成的图表文件路径字典
    """
    LOGGER.info("=" * 60)
    LOGGER.info("生成对比可视化图表")
    LOGGER.info("=" * 60)

    visualizer = MultiSimulationVisualizer(result_dir=output_dir)

    # 加载指定的仿真结果文件
    visualizer.load_specific_algorithms(result_files)

    # 生成所有对比图表
    generated_files = visualizer.generate_all_comparisons()

    # 生成统计报告
    report_path = visualizer.export_comparison_report()
    generated_files['report'] = report_path

    return generated_files


def print_comparison_summary(result_files: Dict[str, str], generated_files: Dict[str, str]):
    """打印对比结果摘要"""
    print("\n" + "=" * 60)
    print("算法对比完成")
    print("=" * 60)

    print("\n仿真结果文件:")
    for algo, file_path in result_files.items():
        print(f"  {algo}: {file_path}")

    print("\n生成的对比图表:")
    for name, file_path in generated_files.items():
        if file_path:
            print(f"  {name}: {file_path}")

    print("\n" + "=" * 60)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='算法对比仿真工具 - 运行多个算法并生成对比可视化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 对比多个算法（使用相同的任务序列）
  python compare_simulations.py --algorithms algorithm2 Worst-Fit Best-Fit

  # 使用不同的随机种子
  python compare_simulations.py --algorithms algorithm2 Worst-Fit --random-seed 123

  # 不使用共享任务序列（每个算法独立生成任务）
  python compare_simulations.py --algorithms algorithm2 Worst-Fit --no-shared-tasks
        """
    )

    parser.add_argument('--algorithms', '-a', nargs='+', required=True,
                       choices=['algorithm2', 'Worst-Fit', 'Best-Fit', 'Random-Fit', 'First-Fit'],
                       help='要对比的算法列表')
    parser.add_argument('--random-seed', '-s', type=int, default=42,
                       help='随机种子，用于确保结果可复现 (默认: 42)')
    parser.add_argument('--no-shared-tasks', action='store_true',
                       help='不使用共享任务序列，每个算法独立生成任务')
    parser.add_argument('--topology', '-t', type=str, default='data/nsfnet_topology.yaml',
                       help='拓扑配置文件路径')
    parser.add_argument('--datacenters', '-d', type=str, default='data/datacenters_OTN.yaml',
                       help='数据中心配置文件路径')
    parser.add_argument('--output-dir', '-o', type=str, default='result',
                       help='输出目录')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')

    args = parser.parse_args()

    # 初始化日志
    init_logger(log_level=getattr(__import__('logging'), args.log_level))

    LOGGER.info("=" * 60)
    LOGGER.info("开始算法对比仿真")
    LOGGER.info(f"算法: {args.algorithms}")
    LOGGER.info(f"随机种子: {args.random_seed}")
    LOGGER.info(f"使用共享任务序列: {not args.no_shared_tasks}")
    LOGGER.info("=" * 60)

    # 运行对比仿真
    result_files = compare_algorithms(
        algorithms=args.algorithms,
        random_seed=args.random_seed,
        use_shared_task_sequence=not args.no_shared_tasks,
        topology=args.topology,
        datacenters=args.datacenters
    )

    if not result_files:
        LOGGER.error("没有成功运行任何仿真")
        return

    # 生成对比可视化
    generated_files = generate_comparison_visualizations(
        result_files=result_files,
        output_dir=args.output_dir
    )

    # 打印摘要
    print_comparison_summary(result_files, generated_files)


if __name__ == "__main__":
    main()
