import simpy
import random
import json
import os
import time
import networkx as nx
import traceback
from typing import Optional, Dict, Any, List
from Graph_update import GraphUpdater, ResourceAllocationError
from resource_selection import ResourceSelection
from events import (DistributedTrainingEvent)
from result import LOGGER
from performance_collector import get_performance_collector


class TaskQueue:
    """任务等待队列管理器
    
    当资源不足时，任务进入等待队列，在资源释放时触发重试。
    使用优先级队列，按等待时间排序（等待越久优先级越高）。
    """
    
    def __init__(self, env):
        """初始化任务队列
        
        Args:
            env: SimPy 环境
        """
        self.env = env
        self.waiting_queue = []  # 等待中的任务列表
        
    def add_to_waiting(self, event, reason, existing_task_info=None):
        """将任务加入等待队列
        
        Args:
            event: 分布式训练事件对象
            reason: 进入等待队列的原因
            existing_task_info: 如果是重试任务，传入原有的 task_info 以保留 retry_count
            
        Returns:
            Dict: 任务信息字典
        """
        if existing_task_info:
            # 保留原有的重试计数
            task_info = existing_task_info
            task_info['reason'] = reason
            task_info['last_retry_time'] = self.env.now
            # 注意：不修改 waiting_since，以便计算总等待时间
            # 修复：将任务重新添加回队列（重试失败后需要重新等待）
            if task_info not in self.waiting_queue:
                self.waiting_queue.append(task_info)
                # 按等待时间排序（等待越久优先级越高）
                self.waiting_queue.sort(key=lambda x: x['waiting_since'])
        else:
            # 首次进入等待队列
            task_info = {
                'event': event,
                'arrival_time': event.arrival_time,
                'waiting_since': self.env.now,
                'reason': reason,
                'retry_count': 0,
                'last_retry_time': self.env.now
            }
            self.waiting_queue.append(task_info)
            # 按等待时间排序（等待越久优先级越高）
            self.waiting_queue.sort(key=lambda x: x['waiting_since'])
        
        return task_info
        
    def get_next_retry_task(self):
        """获取下一个应该重试的任务（等待时间最长的）
        
        Returns:
            Dict: 任务信息字典，如果队列为空则返回 None
        """
        if self.waiting_queue:
            return self.waiting_queue.pop(0)
        return None
    
    def is_empty(self):
        """检查队列是否为空"""
        return len(self.waiting_queue) == 0
    
    def size(self):
        """获取队列大小"""
        return len(self.waiting_queue)
    

class ServiceManager:
    """
    Manages all service processes and event scheduling for the simulation.
    Focuses on SimPy event handling and delegates resource allocation to GraphUpdater.
    """
    SUPPORTED_ALGORITHMS = ('algorithm2', 'Worst-Fit', 'Best-Fit', 'Random-Fit', 'First-Fit')

    def __init__(self, G, env, algorithm: str = 'algorithm2'):
        if algorithm == 'minPenalty':
            raise ValueError("Algorithm 'minPenalty' has been disabled.")
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. Supported algorithms: {', '.join(self.SUPPORTED_ALGORITHMS)}"
            )
        self.G = G
        self.env = env
        self.algorithm = algorithm
        self.graph_updater = GraphUpdater(G, env)
        self.resource_selection = ResourceSelection(G)
        self.task_queue = TaskQueue(env)  # 新增：任务等待队列
        self.task_sequence: List[Dict[str, Any]] = []  # 存储生成的任务序列
        
        # 重试配置参数
        self.max_retry_attempts = 10  # 最大重试次数
        self.max_wait_time = float('inf')  # 最大等待时间（仿真时间单位）
        
        # 用于存储 completed 和 blocked 列表的引用
        self.completed = []
        self.blocked = []

    # 训练处理进程
    def distributed_training_service_process(self, env, event, completed, blocked):
        """
        SimPy process for distributed training events.

        Process flow:
        1. Call ResourceSelection for resource selection
        2. Call GraphUpdater for resource allocation
        3. Calculate completion time using fc_training.py
        4. Wait for completion time
        5. Release resources using GraphUpdater
        6. Add event to completed list
        """
        try:
            # Step 1：调用资源选择算法选择数据中心和路径
            algo_start_time = time.time()  # 记录算法开始时间，用于阻塞事件
            try:
                strategy = self.algorithm  # 使用全局配置的算法

                parallelism = event.model_config.get('parallelism', {})
                p = parallelism.get('pipeline_parallel')  # p是流水线并行
                t = parallelism.get('tensor_parallel')  # t是张量并行
                d = parallelism.get('data_parallel')
                T_dead = event.training_config.get('deadline') * 86400  # 天转换为秒

                # 根据策略选择调用不同的资源选择方法
                total_gpus = p * t * d

                if strategy == 'minPenalty':
                    raise ValueError("Algorithm 'minPenalty' has been disabled.")
                    # 使用算法一：最小化跨域损失算法（内部已记录性能指标）
                    selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, selected_wavelengths = self.resource_selection.min_cross_domain_penalty(
                        N_req=total_gpus,
                        event=event, p=p, t=t
                    )
                    
                elif strategy == 'algorithm2':
                    selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, selected_wavelengths = self.resource_selection.select_datacenters_optimal(
                        p=p,
                        t=t,
                        T_dead=T_dead,
                        event=event
                    )
                elif strategy == 'Worst-Fit':
                    selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, selected_wavelengths = self.resource_selection.Worst_Fit(
                        N_req=total_gpus,
                        event=event, p=p, t=t
                    )
                elif strategy == 'Best-Fit':
                    selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, selected_wavelengths = self.resource_selection.Best_Fit(
                        N_req=total_gpus,
                        event=event, p=p, t=t
                    )
                elif strategy == 'Random-Fit':
                    selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, selected_wavelengths = self.resource_selection.Random_Fit(
                        N_req=total_gpus,
                        event=event, p=p, t=t
                    )
                elif strategy == 'First-Fit':
                    selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, selected_wavelengths = self.resource_selection.First_Fit(
                        N_req=total_gpus,
                        event=event, p=p, t=t
                    )

                
                # Step 2：调用资源调度器进行资源分配
                paths = self.graph_updater.update_graph_resources(
                    event, selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, selected_wavelengths
                )
            except ResourceAllocationError as e:
                # 资源分配失败，需要检查重试限制
                # 注意：任务可能已经在 _trigger_waiting_tasks 中从队列取出，但 retry_count 已增加
                # 我们需要在 waiting_queue 中查找是否有相同 event_id 的任务
                existing_task_info = None
                for task in self.task_queue.waiting_queue:
                    if task['event'].event_id == event.event_id:
                        existing_task_info = task
                        break
                
                # 如果没有找到，说明这是首次失败或者任务已被取出重试
                # 在这种情况下，我们需要创建新的 task_info，但保留 retry_count
                # 由于无法直接获取，我们通过 event 属性来追踪
                if not existing_task_info:
                    # 检查 event 是否有 retry_count 属性
                    if hasattr(event, '_retry_count'):
                        # 创建一个新的 task_info，保留 retry_count
                        existing_task_info = {
                            'event': event,
                            'arrival_time': event.arrival_time,
                            'waiting_since': getattr(event, '_waiting_since', self.env.now),
                            'reason': '',
                            'retry_count': event._retry_count,
                            'last_retry_time': self.env.now
                        }
                
                task_info = self.task_queue.add_to_waiting(event, str(e), existing_task_info)
                retry_count = task_info['retry_count'] if task_info else 0
                wait_duration = self.env.now - task_info['waiting_since'] if task_info else 0
                
                # 检查是否超过最大重试次数
                if retry_count >= self.max_retry_attempts:
                    # 超过最大重试次数，标记为阻塞
                    self._record_blocked_event(
                        event, blocked, algo_start_time, 
                        f"Max retry attempts exceeded: {str(e)}"
                    )
                    LOGGER.warning(f'{self.env.now:.2f}: 任务 {event.event_id} 重试{retry_count}次失败，已达到最大重试次数，任务阻塞')
                    return
                
                # 检查是否超过最大等待时间
                if wait_duration > self.max_wait_time:
                    # 超过最大等待时间，标记为阻塞
                    self._record_blocked_event(
                        event, blocked, algo_start_time, 
                        f"Max wait time exceeded: {str(e)}"
                    )
                    LOGGER.warning(f'{self.env.now:.2f}: 任务 {event.event_id} 等待时间{wait_duration:.2f}超过最大限制，任务阻塞')
                    return
                
                # 未超过限制，进入等待队列等待下次重试
                if retry_count > 0:
                    LOGGER.info(f'{self.env.now:.2f}: 任务 {event.event_id} 第{retry_count}次重试失败，继续等待')
                else:
                    LOGGER.info(f'{self.env.now:.2f}: 分布式训练 {event.event_id} 资源不足，进入等待队列')
                return
            
            # 记录事件开始时间
            event.start_time = env.now
            event.allocated = True
            event.paths = paths
            
            # 打印训练开始日志
            LOGGER.info(f'{env.now:.2f}: 分布式训练 {event.event_id} 开始执行')

            # Step 3: 计算任务完成时间
            completion_time = jct
            LOGGER.info(f'{env.now:.2f}: 分布式训练 {event.event_id} 预计完成时间为 {completion_time:.2f} 秒')

            # Step 4: 等待任务完成
            yield env.timeout(completion_time)

            # 检查是否被故障处理标记为未分配，若是则提前退出
            if not event.allocated:
                return

            # 记录事件完成时间
            event.end_time = env.now
            LOGGER.info(f'{env.now:.2f}: 分布式训练 {event.event_id} 执行完成')
            
            # Step 5: 释放资源
            self.graph_updater.release_graph_resources(event, paths)
            LOGGER.info(f'{env.now:.2f}: 分布式训练 {event.event_id} 资源释放成功')
            
            # ✅ 新增：触发等待任务重试
            self._trigger_waiting_tasks()

            # Step 6: 将事件添加到已完成列表
            completed.append(event)

            # 记录服务性能指标
            collector = get_performance_collector()
            collector.record_service_metrics(
                event_id=event.event_id,
                event_type='distributed_training',
                arrival_time=event.arrival_time,
                start_time=event.start_time,
                end_time=event.end_time,
                allocated=True,
                selected_dcs=event.dc_list if hasattr(event, 'dc_list') else [],
                gpus_per_dc=getattr(event, 'gpus_per_dc', {}),
                required_bw=getattr(event, 'bandwidth_gbps', 0.0),
                jct=completion_time,
                level=getattr(event, 'level', 0.0)
            )

        except Exception as e:
            # 如果发生任何错误，将事件标记为失败并添加到阻塞列表
            event.allocated = False
            blocked.append(event)
            
            # 计算实际执行时间
            execution_time = time.time() - algo_start_time

            # 记录服务性能指标（异常阻塞）
            collector = get_performance_collector()
            collector.record_service_metrics(
                event_id=event.event_id,
                event_type='distributed_training',
                arrival_time=event.arrival_time,
                start_time=getattr(event, 'start_time', env.now),
                end_time=env.now,
                allocated=False,
                blocked_reason=f"Exception: {str(e)}",
                jct=0.0,
                level=0.0
            )

            # 记录算法性能指标（阻塞事件level和jct设置为0，但使用实际执行时间）
            collector.record_algorithm_metrics(
                algorithm_name=self.algorithm,
                execution_time=execution_time,
                level_value=0.0,
                jct=0.0,
                cost_c=0.0,
                num_wavelengths=0,
                num_dcs=0,
                total_gpus=0,
                event_id=event.event_id
            )

            LOGGER.error(f'{env.now:.2f}: 分布式训练 {event.event_id} 执行出错，任务阻塞')
            LOGGER.error(f'错误详情: {str(e)}')
            LOGGER.error(f'堆栈跟踪: {traceback.format_exc()}')
    
    def _create_task_sequence(self, num_events: int, arrival_rate: float,
                               model_configs: list,
                               random_seed: Optional[int] = None,
                               model_selection_mode: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        预生成任务序列，确保不同算法使用相同的任务场景

        Args:
            num_events: 事件数量
            arrival_rate: 到达率
            model_configs: 模型配置列表（包含内嵌的training_config）
            random_seed: 随机种子
            model_selection_mode: 模型选择模式（"random"或具体模型名称）

        Returns:
            List[Dict]: 任务序列，每个任务包含arrival_time、model_config、training_config
        """
        if random_seed is not None:
            random.seed(random_seed)

        task_sequence = []
        current_time = 0.0

        # 确定要使用的模型配置
        selected_model_config = None
        if model_selection_mode and model_selection_mode != "random":
            # 根据模型名称查找对应的配置
            for config in model_configs:
                if config.get('model_name') == model_selection_mode:
                    selected_model_config = config
                    LOGGER.info(f"模型选择模式: 固定使用 {model_selection_mode} 模型")
                    break
            if not selected_model_config:
                LOGGER.warning(f"未找到模型 {model_selection_mode}，将使用随机选择模式")
        
        for i in range(num_events):
            # 生成随机到达时间
            inter_arrival = random.expovariate(arrival_rate)
            current_time += inter_arrival

            # 选择模型配置
            if selected_model_config:
                # 使用固定的模型配置
                model_config = selected_model_config
            else:
                # 随机选择模型配置
                model_config = random.choice(model_configs)
            

            task_sequence.append({
                'event_id': i,
                'arrival_time': current_time,
                'model_config': model_config
            })

        return task_sequence

    def _save_task_sequence(self, task_sequence: List[Dict[str, Any]], filepath: str):
        """保存任务序列到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(task_sequence, f, indent=2, ensure_ascii=False)
        LOGGER.info(f"任务序列已保存到: {filepath}")

    def _load_task_sequence(self, filepath: str) -> List[Dict[str, Any]]:
        """从文件加载任务序列"""
        with open(filepath, 'r', encoding='utf-8') as f:
            task_sequence = json.load(f)
        LOGGER.info(f"任务序列已从文件加载: {filepath}，共 {len(task_sequence)} 个任务")
        return task_sequence

    # 训练到达进程
    def distributed_training_arrival_process(self, env, num_events, dc_ids, completed, blocked,
                                             arrival_rate, event_id_start=0, random_config=None,
                                             task_sequence: Optional[List[Dict]] = None,
                                             model_selection_mode: Optional[str] = None):
        """创建分布式训练事件event

        Args:
            env: SimPy environment
            num_events: Number of events to generate
            dc_ids: List of datacenter IDs
            completed: List to store completed events
            blocked: List to store blocked events
            arrival_rate: Arrival rate (events per second)
            event_id_start: Starting event ID
            random_config: Configuration for random events, including model_configs and training_configs
            task_sequence: 预生成的任务序列，如果提供则使用此序列而非随机生成
            model_selection_mode: 模型选择模式（"random"或具体模型名称）
        """
        # 从随机到达配置中提取模型配置
        model_configs = random_config.get('model_configs')

        # 如果有预生成的任务序列，使用它
        if task_sequence:
            for task in task_sequence:
                arrival_time = task['arrival_time']
                # 等待到达时间
                if arrival_time > env.now:
                    yield env.timeout(arrival_time - env.now)

                model_config = task['model_config']
                training_config = model_config.get('training_config')

                # 创建分布式训练事件
                event = DistributedTrainingEvent(
                    event_id_start + task['event_id'], 'distributed_training', env.now, [],
                    0,  # 每个DC的GPU数量
                    0,  # 所需带宽
                )

                # 为事件添加模型配置和训练配置
                event.model_config = model_config
                event.training_config = training_config
                LOGGER.info(f'时间 {env.now:.2f}，分布式训练事件 {event.event_id}到达（来自预定义序列）')
                # 调度分布式训练服务进程
                env.process(self.distributed_training_service_process(env, event, completed, blocked))
        else:
            # 原有的随机生成逻辑
            # 确定要使用的模型配置
            selected_model_config = None
            if model_selection_mode and model_selection_mode != "random":
                # 根据模型名称查找对应的配置
                for config in model_configs:
                    if config.get('model_name') == model_selection_mode:
                        selected_model_config = config
                        LOGGER.info(f"模型选择模式: 固定使用 {model_selection_mode} 模型")
                        break
                if not selected_model_config:
                    LOGGER.warning(f"未找到模型 {model_selection_mode}，将使用随机选择模式")
            
            for i in range(num_events):
                # 生成随机到达时间
                yield env.timeout(random.expovariate(arrival_rate))

                # 选择模型配置
                if selected_model_config:
                    # 使用固定的模型配置
                    model_config = selected_model_config
                else:
                    # 随机选择一个模型配置
                    model_config = random.choice(model_configs)

                # 从模型配置中获取内嵌的训练配置
                training_config = model_config.get('training_config')

                # 创建分布式训练事件
                event = DistributedTrainingEvent(
                    event_id_start + i, 'distributed_training', env.now, [],
                    0,  # 每个DC的GPU数量
                    0,  # 所需带宽
                )

                # 为事件添加模型配置和训练配置
                event.model_config = model_config
                event.training_config = training_config

                # 记录任务序列
                self.task_sequence.append({
                    'event_id': i,
                    'arrival_time': env.now,
                    'model_config': model_config
                })

                LOGGER.info(f'时间 {env.now:.2f}，分布式训练事件 {event.event_id}到达')
                # 调度分布式训练服务进程
                env.process(self.distributed_training_service_process(env, event, completed, blocked))
    
    def _record_blocked_event(self, event, blocked, algo_start_time, reason):
        """记录阻塞事件的性能指标
        
        Args:
            event: 事件对象
            blocked: 阻塞事件列表
            algo_start_time: 算法开始时间
            reason: 阻塞原因
        """
        event.allocated = False
        blocked.append(event)
        
        execution_time = time.time() - algo_start_time
        
        collector = get_performance_collector()
        collector.record_service_metrics(
            event_id=event.event_id,
            event_type='distributed_training',
            arrival_time=event.arrival_time,
            start_time=getattr(event, 'start_time', self.env.now),
            end_time=self.env.now,
            allocated=False,
            blocked_reason=reason,
            jct=0.0,
            level=0.0
        )
        
        collector.record_algorithm_metrics(
            algorithm_name=self.algorithm,
            execution_time=execution_time,
            level_value=0.0,
            jct=0.0,
            cost_c=0.0,
            num_wavelengths=0,
            num_dcs=0,
            total_gpus=0,
            event_id=event.event_id
        )
    
    def _select_model_config(self, model_configs, model_selection_mode):
        """根据选择模式选择模型配置
        
        Args:
            model_configs: 模型配置列表
            model_selection_mode: 模型选择模式（"random"或具体模型名称）
            
        Returns:
            选中的模型配置，如果为随机模式则返回 None
        """
        if not model_selection_mode or model_selection_mode == "random":
            return None
        
        for config in model_configs:
            if config.get('model_name') == model_selection_mode:
                LOGGER.info(f"模型选择模式: 固定使用 {model_selection_mode} 模型")
                return config
        
        LOGGER.warning(f"未找到模型 {model_selection_mode}，将使用随机选择模式")
        return None
    
    def _create_and_schedule_event(self, env, event_id, model_config, training_config, 
                                    completed, blocked, log_prefix=""):
        """创建并调度分布式训练事件
        
        Args:
            env: SimPy 环境
            event_id: 事件 ID
            model_config: 模型配置
            training_config: 训练配置
            completed: 完成事件列表
            blocked: 阻塞事件列表
            log_prefix: 日志前缀
            
        Returns:
            创建的事件对象
        """
        event = DistributedTrainingEvent(
            event_id, 'distributed_training', env.now, [], 0, 0
        )
        event.model_config = model_config
        event.training_config = training_config
        
        log_msg = f'时间 {env.now:.2f}，分布式训练事件 {event.event_id}到达'
        if log_prefix:
            log_msg += f'（{log_prefix}）'
        LOGGER.info(log_msg)
        
        env.process(self.distributed_training_service_process(env, event, completed, blocked))
        return event
    
    def _trigger_waiting_tasks(self):
        """触发等待队列中的任务重试
        
        在资源释放或故障恢复时调用，每次只重试一个任务。
        如果失败则回到队列，等待下次资源释放。
        """
        # 检查是否有等待的任务
        if self.task_queue.is_empty():
            return
        
        # 只取出一个任务重试
        task_info = self.task_queue.get_next_retry_task()
        if not task_info:
            return
        
        event = task_info['event']
        # 增加重试计数（在启动服务进程之前）
        task_info['retry_count'] += 1
        task_info['last_retry_time'] = self.env.now
        
        # 同步到 event 对象，以便在 distributed_training_service_process 中访问
        event._retry_count = task_info['retry_count']
        event._waiting_since = task_info['waiting_since']
        
        # 计算等待时间（从任务到达至今）
        wait_duration = self.env.now - task_info['waiting_since']
        
        # 从 event.model_config 中获取原始资源需求
        parallelism = event.model_config.get('parallelism', {})
        p = parallelism.get('pipeline_parallel', 1)
        t = parallelism.get('tensor_parallel', 1)
        d = parallelism.get('data_parallel', 1)
        total_gpus = p * t * d
        
        # 获取模型名称
        model_name = event.model_config.get('model_name', 'unknown')
        
        # 开始重试
        LOGGER.info(f'{self.env.now:.2f}: 任务 {event.event_id} 开始第{task_info["retry_count"]}次重试 '
                    f'(等待了{wait_duration:.2f}时间单位，GPU 需求：{total_gpus}, 模型：{model_name})')
        
        # 启动服务进程
        self.env.process(self.distributed_training_service_process(
            self.env, event, self.completed, self.blocked
        ))
        
        # 记录等待队列状态
        if not self.task_queue.is_empty():
            LOGGER.debug(f'{self.env.now:.2f}: 等待队列中仍有 {self.task_queue.size()} 个任务')
    
    def schedule_services(self, env, service_config, completed, blocked,
                          task_sequence_file: Optional[str] = None,
                          save_task_sequence: bool = False):
        """
        Schedule all service event arrivals in the SimPy environment.

        Args:
            env: SimPy environment
            service_config: Service configuration dictionary, including:
                - random_seed: Random seed for reproducibility
                - predefined_tasks_mode: Whether to enable hybrid mode (random + predefined tasks)
                - num_events: Number of random events for each service type
                - lambda: Arrival rates for each service type
                - mu: Service rates for each service type
                - random_event_config: Configuration for random events
                - predefined_tasks: List of predefined tasks
            completed: List to store completed events
            blocked: List to store blocked events
            task_sequence_file: 预定义任务序列文件路径
            save_task_sequence: 是否保存生成的任务序列
        """
        # 同步外部列表引用，确保等待队列重试时使用正确的列表
        self.completed = completed
        self.blocked = blocked

        # 初始化随机数生成器，确保可重复性
        random_seed = service_config.get('random_seed')
        if random_seed is not None:
            random.seed(random_seed)

        # 创建只包含数据中心的列表
        dc_ids = [n for n, data in self.G.nodes(data=True) if data.get('type') == 'datacenter']

        # 获取随机事件配置
        random_event_config = service_config.get('random_event_config', {})

        # 处理任务序列
        task_sequence = None
        if task_sequence_file and os.path.exists(task_sequence_file):
            task_sequence = self._load_task_sequence(task_sequence_file)

        # 调度随机到达事件
        if 'num_events' in service_config and 'lambda' in service_config:
            num_events_dict = service_config['num_events']
            lambda_dict = service_config['lambda']
            LOGGER.info(f'num_events_dict: {num_events_dict}, lambda_dict: {lambda_dict}')
            # 调度分布式训练事件
            if 'distributed_training' in num_events_dict:
                num_events = num_events_dict['distributed_training']
                arrival_rate = lambda_dict['distributed_training']
                dt_config = random_event_config.get('distributed_training', {})

                # 如果没有预定义任务序列且需要保存，则预生成任务序列
                if task_sequence is None and save_task_sequence:
                    model_configs = dt_config.get('model_configs', [])
                    # 获取模型选择模式
                    model_selection_mode = service_config.get('model_selection_mode', 'random')
                    task_sequence = self._create_task_sequence(
                        num_events, arrival_rate, model_configs, random_seed, model_selection_mode
                    )
                    # 保存任务序列
                    save_path = f"data/task_sequences/task_sequence_{random_seed or 'default'}.json"
                    self._save_task_sequence(task_sequence, save_path)
                    # 更新性能收集器中的任务配置
                    collector = get_performance_collector()
                    collector.set_task_config({
                        'random_seed': random_seed,
                        'num_events': num_events,
                        'arrival_rate': arrival_rate,
                        'task_sequence_file': save_path
                    })

                # 获取模型选择模式
                model_selection_mode = service_config.get('model_selection_mode', 'random')

                env.process(self.distributed_training_arrival_process(
                    env, num_events, dc_ids, completed, blocked,
                    arrival_rate, event_id_start=0, random_config=dt_config,
                    task_sequence=task_sequence,
                    model_selection_mode=model_selection_mode
                ))
