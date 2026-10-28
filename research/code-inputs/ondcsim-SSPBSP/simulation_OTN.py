#!/usr/bin/env python3

import os
import argparse
from result import LOGGER, init_logger, get_log_level
from datetime import datetime

import simpy
from topology_OTN import TopologyManager
from service import ServiceManager
from failure import FailureManager
from result import ResultManager
from topology_visualization import draw_topology
from performance_collector import get_performance_collector, reset_performance_collector
from visualization import PerformanceVisualizer

# --- Main Simulation Entry ---
def main():
    # --- Parse Command Line Arguments ---
    parser = argparse.ArgumentParser(description='OTN Network Simulation')
    parser.add_argument('--topology', '-t', type=str, default='data/nsfnet_topology.yaml',
                       help='Path to the topology configuration file (default: data/nsfnet_topology.yaml)')
    parser.add_argument('--datacenters', '-d', type=str, default='data/datacenters_OTN.yaml',
                       help='Path to the datacenters configuration file (default: data/datacenters_OTN.yaml)')
    parser.add_argument('--logfile', '-l', type=str, default='simulation.log',
                       help='Path to the log file (default: simulation.log)')
    parser.add_argument('--log-level','--ll', type=str, default='INFO',
                       help='Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--no-console-log', action='store_true',
                       help='Disable console log output')
    parser.add_argument('--algorithm', '-a', type=str, default='algorithm2',
                       choices=['algorithm2', 'Worst-Fit', 'Best-Fit', 'Random-Fit', 'First-Fit'],
                       help='选择要运行的算法 (默认: algorithm2)')
    parser.add_argument('--task-sequence-file', type=str, default=None,
                       help='预定义任务序列文件路径，用于确保不同算法使用相同的任务场景')
    parser.add_argument('--save-task-sequence', action='store_true',
                       help='保存本次仿真生成的任务序列到文件')
    
    args = parser.parse_args()
    
    # 处理日志文件路径
    if args.logfile == parser.get_default('logfile'):
        # 如果使用默认日志文件名，则生成带时间戳的文件名
        # 创建 logs 文件夹（如果不存在）
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 构造完整的日志文件路径
        args.logfile = os.path.join(logs_dir, f'{timestamp}_simulation.log')
    
    # 初始化日志系统
    log_level = get_log_level(args.log_level)
    init_logger(log_level=log_level, log_file=args.logfile, enable_console=not args.no_console_log)
    
    # --- Topology and Resource Initialization ---
    topo_mgr = TopologyManager(args.topology, args.datacenters)
    G = topo_mgr.get_graph()
    LOGGER.debug(f"Network nodes: {list(G.nodes)}")

    # 可视化图形
    #draw_topology(G)

    # 加载服务配置、故障配置
    service_config = topo_mgr.load_service_config()
    failure_cfg = topo_mgr.load_failure_config()

    # 【先初始化性能收集器】确保后续模块获取正确的实例
    reset_performance_collector()
    perf_collector = get_performance_collector(result_dir="result", algorithm_name=args.algorithm)

    # --- Run Simulation ---
    # 先创建 SimPy 环境，以便传递给 ServiceManager
    env = simpy.Environment()
    completed = []
    blocked = []

    # 然后初始化服务管理器、故障管理器和结果管理器
    service_mgr = ServiceManager(G, env, algorithm=args.algorithm)
    failure_mgr = FailureManager(failure_cfg, G)
    failure_mgr.set_resource_scheduler(service_mgr.graph_updater)  # 设置资源调度器，以便访问服务事件注册表
    result_mgr = ResultManager()

    # 生成故障事件
    failure_events = failure_mgr.generate_failure_events()
    # print(failure_events,end='\n')

    # 调度故障事件
    failure_mgr.schedule_failures(env, failure_events, completed, blocked)

    # 调度服务事件
    service_mgr.schedule_services(env, service_config, completed, blocked,
                                  task_sequence_file=args.task_sequence_file,
                                  save_task_sequence=args.save_task_sequence)

    env.run()

    # 收集并打印基本指标
    metrics = result_mgr.collect_basic_metrics(completed, blocked)
    result_mgr.print_metrics(metrics)
    if completed:
        LOGGER.info(f"前5个完成事件类型: {[event.event_type for event in completed[:5]]}")
    
    # 导出性能数据
    LOGGER.info("--- 正在导出性能数据 ---")
    exported_files = perf_collector.finalize()
    LOGGER.info(f"性能数据文件:")
    for file_type, file_path in exported_files.items():
        LOGGER.info(f"  {file_type}: {file_path}")
    
    # 生成可视化图表
    LOGGER.info("--- 正在生成可视化图表 ---")
    try:
        visualizer = PerformanceVisualizer(result_dir="result")
        json_file = exported_files.get('json', '')
        if json_file:
            generated_figures = visualizer.generate_all_visualizations(json_file)
            LOGGER.info(f"可视化图表:")
            for fig_name, fig_path in generated_figures.items():
                if fig_path:
                    LOGGER.info(f"  {fig_name}: {fig_path}")
    except Exception as e:
        LOGGER.warning(f"生成可视化图表时出错: {e}")

if __name__ == "__main__":
    main()
