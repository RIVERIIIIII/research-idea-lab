from typing import List
import random
import networkx as nx
from events import FailureEvent
from result import LOGGER
from common_utils import EVENT_TYPE_NAMES
from performance_collector import get_performance_collector

class FailureManager:
    """
    Manages failure event generation and scheduling for the simulation.
    Handles node and link failures and their recovery.
    Expects the graph to have 'compute_available', 'storage_available', and 'bandwidth_available' attributes.
    """
    def __init__(self, config: dict, G: nx.Graph, resource_scheduler=None):
        self.config = config
        self.G = G
        self.resource_scheduler = resource_scheduler

    def set_resource_scheduler(self, resource_scheduler):
        """设置资源调度器，用于访问服务事件注册表"""
        self.resource_scheduler = resource_scheduler

    def generate_failure_events(self) -> List[FailureEvent]:
        """Generate node and link failure events based on config."""
        num_failures = self.config['num_failures']
        failure_types = self.config['failure_types']
        node_prob = failure_types['node']['probability']
        link_prob = failure_types['link']['probability']
        node_rate = failure_types['node']['rate']
        link_rate = failure_types['link']['rate']
        node_mean_duration = failure_types['node']['mean_duration']
        link_mean_duration = failure_types['link']['mean_duration']
        num_node_failures = int(num_failures * node_prob)
        num_link_failures = num_failures - num_node_failures
        events = []
        if num_node_failures > 0:
            events += self._generate_failure_events(num_node_failures, 'node', event_id_start=1000, rate_lambda=node_rate, mean_duration=node_mean_duration)
        if num_link_failures > 0:
            events += self._generate_failure_events(num_link_failures, 'link', event_id_start=2000, rate_lambda=link_rate, mean_duration=link_mean_duration)
        return events

    def _generate_failure_events(self, num_events: int, failure_type: str, event_id_start: int = 0, rate_lambda: float = 0.05, mean_duration: float = 10.0) -> List[FailureEvent]:
        """Generate node or link failure events as a Poisson process."""
        events = []
        arrival_time = 0.0
        node_ids = [n for n, data in self.G.nodes(data=True) if data.get('type') == 'datacenter']
        link_pairs = list(self.G.edges())
        for i in range(num_events):
            inter_arrival = random.expovariate(rate_lambda)
            arrival_time += inter_arrival
            duration = random.expovariate(1.0 / mean_duration)
            if failure_type == 'node':
                failed_node = random.choice(node_ids)
                events.append(FailureEvent(
                    event_id_start + i, 'failure', arrival_time, failure_type, failed_node=failed_node, duration=duration
                ))
            else:
                failed_link = list(random.choice(link_pairs))
                events.append(FailureEvent(
                    event_id_start + i, 'failure', arrival_time, failure_type, failed_link=failed_link, duration=duration
                ))
        return events

    def _apply_node_failure(self, env, event):
        """应用节点故障，返回受影响的节点和保存的状态"""
        node = event.failed_node
        self.G.nodes[node]['failed'] = True
        saved_compute = self.G.nodes[node]['compute_available']
        saved_storage = self.G.nodes[node]['storage_available']
        self.G.nodes[node]['compute_available'] = 0
        self.G.nodes[node]['storage_available'] = 0
        LOGGER.info(f'{env.now:.2f}: 故障事件 {event.event_id} 发生，节点 {node} 故障，持续时间 {event.duration:.2f}')
        return node, saved_compute, saved_storage

    def _apply_link_failure(self, env, event):
        """应用链路故障，返回受影响的链路和保存的状态"""
        u, v = event.failed_link
        link = tuple(sorted((u, v)))
        self.G.edges[u, v]['failed'] = True
        saved_bw = self.G.edges[u, v]['bandwidth_available']
        self.G.edges[u, v]['bandwidth_available'] = 0
        LOGGER.info(f'{env.now:.2f}: 故障事件 {event.event_id} 发生，链路 {u}-{v} 故障，持续时间 {event.duration:.2f}')
        return link, saved_bw

    def _get_affected_events(self, failed_resource, resource_type='node'):
        """获取受故障影响的服务事件ID集合"""
        affected_events = set()
        if not self.resource_scheduler:
            return affected_events

        registry = self.resource_scheduler.service_event_registry
        if resource_type == 'node' and failed_resource in registry['nodes']:
            affected_events.update(registry['nodes'][failed_resource])
        elif resource_type == 'link' and failed_resource in registry['links']:
            affected_events.update(registry['links'][failed_resource])
        return affected_events

    def _handle_affected_event(self, env, event, event_id, blocked):
        """处理单个受影响的服务事件"""
        registry = self.resource_scheduler.service_event_registry
        if event_id not in registry['events']:
            return

        event_resources = registry['events'][event_id]
        service_event = event_resources['event']
        service_event.allocated = False
        blocked.append(service_event)

        event_type_str = EVENT_TYPE_NAMES.get(event_resources['type'], event_resources['type'])
        failure_desc = f"节点 {event.failed_node} 故障" if event.failure_type == 'node' else f"链路 {event.failed_link[0]}-{event.failed_link[1]} 故障"
        LOGGER.info(f'{env.now:.2f}: {event_type_str} {service_event.event_id} 因{failure_desc}影响，任务阻塞')

        # 释放事件占用的资源
        paths = getattr(service_event, 'paths', [])
        if event_resources['type'] == 'distributed_training':
            self.resource_scheduler.release_distributed_training_resources(service_event, paths)
        elif event_resources['type'] == 'inference_service':
            self.resource_scheduler.release_inference_service_deployment_resources(service_event, paths)
        elif event_resources['type'] == 'inference_request':
            path = getattr(service_event, 'path', [])
            self.resource_scheduler.release_inference_request_resources(service_event, path)

    def _recover_node(self, env, event, saved_compute, saved_storage):
        """恢复节点状态"""
        node = event.failed_node
        self.G.nodes[node]['failed'] = False
        self.G.nodes[node]['compute_available'] = saved_compute
        self.G.nodes[node]['storage_available'] = saved_storage
        LOGGER.info(f'{env.now:.2f}: 故障事件 {event.event_id} 恢复，节点 {node} 恢复正常')
        
        # ✅ 新增：触发等待任务重试
        if self.resource_scheduler:
            self.resource_scheduler._trigger_waiting_tasks()

    def _recover_link(self, env, event, saved_bw):
        """恢复链路状态"""
        u, v = event.failed_link
        self.G.edges[u, v]['failed'] = False
        self.G.edges[u, v]['bandwidth_available'] = saved_bw
        LOGGER.info(f'{env.now:.2f}: 故障事件 {event.event_id} 恢复，链路 {u}-{v} 恢复正常')
        
        # ✅ 新增：触发等待任务重试
        if self.resource_scheduler:
            self.resource_scheduler._trigger_waiting_tasks()

    def failure_process(self, env, event, completed, blocked):
        """
        SimPy process for node or link failure events.
        """
        try:
            # 等待故障到达时间
            if event.arrival_time > env.now:
                yield env.timeout(event.arrival_time - env.now)

            # 应用故障并获取受影响的事件
            if event.failure_type == 'node' and event.failed_node is not None:
                node, saved_compute, saved_storage = self._apply_node_failure(env, event)
                affected_events = self._get_affected_events(node, 'node')
            elif event.failure_type == 'link' and event.failed_link is not None:
                link, saved_bw = self._apply_link_failure(env, event)
                affected_events = self._get_affected_events(link, 'link')
            else:
                affected_events = set()
                saved_compute = saved_storage = saved_bw = None

            # 处理受影响的服务事件
            if self.resource_scheduler and affected_events:
                for event_id in list(affected_events):
                    self._handle_affected_event(env, event, event_id, blocked)

            # 记录故障指标
            collector = get_performance_collector()
            failed_resource = str(event.failed_node) if event.failure_type == 'node' else f"{event.failed_link[0]}-{event.failed_link[1]}"
            collector.record_failure_metrics(
                failure_id=event.event_id,
                failure_type=event.failure_type,
                failed_resource=failed_resource,
                arrival_time=event.arrival_time,
                duration=event.duration,
                affected_events=list(affected_events)
            )

            # 等待故障持续时间
            yield env.timeout(event.duration)

            # 恢复故障状态
            if event.failure_type == 'node' and event.failed_node is not None:
                self._recover_node(env, event, saved_compute, saved_storage)
            elif event.failure_type == 'link' and event.failed_link is not None:
                self._recover_link(env, event, saved_bw)

        except Exception as e:
            LOGGER.error(f"Failure process error: {e}")

    def schedule_failures(self, env, failure_events, completed, blocked):
        """Schedule all failure events in the SimPy environment."""
        for fe in failure_events:
            env.process(self.failure_process(env, fe, completed, blocked)) 