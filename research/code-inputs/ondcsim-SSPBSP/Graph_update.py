import networkx as nx
from typing import List, Optional
from result import LOGGER
from performance_collector import get_performance_collector

# --- Custom Exceptions ---
class ResourceAllocationError(Exception):
    """Base exception for resource allocation errors."""
    pass

class ComputeResourceError(ResourceAllocationError):
    """Exception raised when compute resources are insufficient or unavailable."""
    def __init__(self, dc_id, required, available):
        super().__init__(f"Insufficient compute resources at DC {dc_id}: required {required}, available {available}")
        self.dc_id = dc_id
        self.required = required
        self.available = available

class BandwidthResourceError(ResourceAllocationError):
    """Exception raised when bandwidth resources are insufficient or unavailable."""
    def __init__(self, src, dst, required, available=None):
        if available is not None:
            super().__init__(f"Insufficient bandwidth from {src} to {dst}: required {required}, available {available}")
        else:
            super().__init__(f"No available path from {src} to {dst}")
        self.src = src
        self.dst = dst
        self.required = required
        self.available = available

class PathNotFoundError(ResourceAllocationError):
    """Exception raised when no network path is available between nodes."""
    def __init__(self, src, dst):
        super().__init__(f"No path found from {src} to {dst}")
        self.src = src
        self.dst = dst

class GraphUpdater:
    """
    Manages resource allocation for the simulation.
    Handles compute (GPU) and network (bandwidth) resource allocation and release.
    """
    def __init__(self, G, env=None):
        self.G = G
        self.env = env
        self.service_event_registry = {
            'nodes': {},  # 节点 ID -> 服务事件列表
            'links': {},  # (u, v) -> 服务事件列表
            'events': {}  # 事件 ID -> 事件详情和占用资源
        }
        
        # 采集初始资源状态快照
        collector = get_performance_collector()
        collector.record_resource_utilization(
            timestamp=0.0,
            G=self.G
        )

    # --- 波长分配辅助方法 ---
    def _mark_wavelengths_as_used(self, path, wavelength_ids):
        """
        将路径上的指定波长标记为已使用(status=1)

        波长连续性：路径上所有链路使用相同编号的波长

        Args:
            path: 路径节点列表，如 [1, 2, 3]
            wavelength_ids: 要标记的波长ID列表，如 [0, 1, 2]
        """
        if not path or len(path) < 2 or not wavelength_ids:
            LOGGER.warning(f"标记波长为已使用：无效参数 path={path}, wavelength_ids={wavelength_ids}")
            return

        LOGGER.debug(f"标记路径 {path} 上的波长 {wavelength_ids} 为已使用")

        for u, v in zip(path[:-1], path[1:]):
            if not self.G.has_edge(u, v):
                LOGGER.warning(f"链路 ({u}, {v}) 不存在，跳过")
                continue

            wavelength_channels = self.G.edges[u, v].get('wavelength_channels', [])
            marked_count = 0

            for ch in wavelength_channels:
                if ch.wavelength_id in wavelength_ids:
                    ch.status = 1  # 标记为已占用
                    marked_count += 1

            LOGGER.debug(f"链路 ({u}, {v}) 标记了 {marked_count} 个波长为已使用")

    def _mark_wavelengths_as_available(self, path, wavelength_ids):
        """
        将路径上的指定波长标记为可用(status=0)

        Args:
            path: 路径节点列表，如 [1, 2, 3]
            wavelength_ids: 要标记的波长ID列表，如 [0, 1, 2]
        """
        if not path or len(path) < 2 or not wavelength_ids:
            LOGGER.warning(f"标记波长为可用：无效参数 path={path}, wavelength_ids={wavelength_ids}")
            return

        LOGGER.debug(f"标记路径 {path} 上的波长 {wavelength_ids} 为可用")

        for u, v in zip(path[:-1], path[1:]):
            if not self.G.has_edge(u, v):
                LOGGER.warning(f"链路 ({u}, {v}) 不存在，跳过")
                continue

            wavelength_channels = self.G.edges[u, v].get('wavelength_channels', [])
            marked_count = 0

            for ch in wavelength_channels:
                if ch.wavelength_id in wavelength_ids:
                    ch.status = 0  # 标记为可用
                    marked_count += 1

            LOGGER.debug(f"链路 ({u}, {v}) 标记了 {marked_count} 个波长为可用")

    # --- 在给定路径上分配带宽 ---
    def update_bandwidth_path(self, path, required_bw):
        """
        在给定的路径上分配带宽。
        
        Args:
            path: 已经选好的路径
            required_bw: 所需带宽，单位：Gbps
        
        Returns:
            list: 分配的路径
            
        Raises:
            BandwidthResourceError: 如果路径上的带宽不足
        """
        # 检查路径是否有效
        if not path or len(path) < 2:
            raise ValueError("Invalid path provided")
        
        # 检查路径上的带宽是否足够
        for u, v in zip(path[:-1], path[1:]):
            if self.G.edges[u, v]['bandwidth_available'] < required_bw:
                raise BandwidthResourceError(path[0], path[-1], required_bw, self.G.edges[u, v]['bandwidth_available'])
        
        # 分配带宽
        for u, v in zip(path[:-1], path[1:]):
            self.G.edges[u, v]['bandwidth_available'] -= required_bw
            assert self.G.edges[u, v]['bandwidth_available'] >= 0, f"Bandwidth negative on edge {u}-{v}"
        
        return path

    def release_bandwidth_path(self, path, released_bw):
        """
        Release bandwidth along the given path.
        
        Args:
            path: The path to release bandwidth from
            released_bw: Bandwidth to release in Gbps
        """
        # 释放带宽
        for u, v in zip(path[:-1], path[1:]):
            self.G.edges[u, v]['bandwidth_available'] += released_bw
            assert self.G.edges[u, v]['bandwidth_available'] <= self.G.edges[u, v]['bandwidth_capacity'], f"Bandwidth exceeds capacity on edge {u}-{v}"

    # ---在一个DC分配GPU资源 ---
    def update_compute_resource(self, dc_id, required_gpus):
        """
        Args:
            dc_id: Datacenter ID
            required_gpus: Number of GPUs required
            
        Raises:
            ComputeResourceError: If insufficient compute resources are available
        """
        available = self.G.nodes[dc_id]['available_gpu']
        if available < required_gpus:
            raise ComputeResourceError(dc_id, required_gpus, available)
        
        self.G.nodes[dc_id]['available_gpu'] -= required_gpus
        assert self.G.nodes[dc_id]['available_gpu'] >= 0, f"Compute negative at DC {dc_id}"

    def release_compute_resource(self, dc_id, released_gpus):
        """
        Release GPU resources at a datacenter.
        
        Args:
            dc_id: Datacenter ID
            released_gpus: Number of GPUs to release
        """
        self.G.nodes[dc_id]['available_gpu'] += released_gpus
        assert self.G.nodes[dc_id]['available_gpu'] <= self.G.nodes[dc_id]['gpu_count'], f"Compute exceeds capacity at DC {dc_id}"

    # --- 分布式训练资源分配函数 ---
    def _log_resource_change(self, resource_type, resource_id, before, after, change, unit=""):
        """统一记录资源变化日志"""
        LOGGER.info(f"  {resource_type} {resource_id}: 可用{unit}={after} (变更前: {before}, 变更: {change})")

    def _log_gpu_allocation(self, gpus_per_dc, is_release=False):
        """记录GPU分配/释放日志"""
        action = "释放" if is_release else "分配"
        LOGGER.info(f"{action}后各数据中心可用GPU数量：")
        for dc_id, gpus in gpus_per_dc.items():
            available = self.G.nodes[dc_id]['available_gpu']
            before = available - (gpus if is_release else -gpus)
            self._log_resource_change("DC", dc_id, before, available, f"{action}: {gpus}")

    def _log_bandwidth_allocation(self, path, required_bw, is_release=False):
        """记录带宽分配/释放日志"""
        action = "释放" if is_release else "分配"
        LOGGER.info(f"{action}后路径 {path} 各链路带宽状态：")
        for u, v in zip(path[:-1], path[1:]):
            available = self.G.edges[u, v]['bandwidth_available']
            before = available - (required_bw if is_release else -required_bw)
            self._log_resource_change("链路", f"{u}-{v}", before, available, f"{action}: {required_bw}", "Gbps")

    def update_graph_resources(self, event, selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, selected_wavelengths=None):
        """
        为分布式训练事件分配计算资源和网络带宽。

        Args:
            event: DistributedTrainingEvent object
            selected_dcs: 选中的数据中心列表
            gpus_per_dc: 每个数据中心分配的GPU数量
            communication_paths: 数据中心之间的通信路径
            best_n_wave: 最佳波长数
            required_bw: 需要分配的带宽（波长数 × 单波长容量）
            selected_wavelengths: 波长选择结果 {path_key: [wavelength_ids]}，可选

        Returns:
            list: List of allocated paths between datacenters

        Raises:
            ComputeResourceError: 如果任何数据中心没有足够的GPU资源
            BandwidthResourceError: 如果任何数据中心对其他数据中心的带宽需求超过了可用带宽
        """
        allocated_dcs = []
        allocated_paths = []

        try:
            if not selected_dcs:
                raise ComputeResourceError(None, event.gpus_per_dc, 0)

            event.dc_list = selected_dcs
            event.gpus_per_dc = max(gpus_per_dc.values())

            # Step 1: 分配计算资源
            LOGGER.info(f"分配计算资源: {gpus_per_dc}")
            for dc_id, gpus in gpus_per_dc.items():
                self.update_compute_resource(dc_id, gpus)
                allocated_dcs.append(dc_id)
            self._log_gpu_allocation(gpus_per_dc, is_release=False)

            # Step 2: 分配波长和网络带宽
            LOGGER.info(f"使用最佳波长数: {best_n_wave} 进行波长分配，需要带宽: {required_bw} Gbps")
            # 去重：使用集合记录已处理的物理链路，避免往返路径重复分配
            processed_links = set()
            for (src, dst), path in communication_paths.items():
                # 生成链路键，确保A->B和B->A被视为同一条链路
                link_key = tuple(sorted((src, dst)))
                if link_key in processed_links:
                    LOGGER.debug(f"跳过重复路径: ({src}, {dst}) 已处理")
                    continue
                processed_links.add(link_key)

                # 如果有预选波长，使用预选波长；否则使用传统带宽分配
                if selected_wavelengths and link_key in selected_wavelengths:
                    wavelength_ids = selected_wavelengths[link_key]
                    self._mark_wavelengths_as_used(path, wavelength_ids)
                    LOGGER.info(f"路径 ({src}, {dst}) 标记波长为已使用: {wavelength_ids}")
                    # 同时更新带宽（波长分配也需要减少可用带宽）
                    self.update_bandwidth_path(path, required_bw)


                allocated_paths.append(path)
                self._log_bandwidth_allocation(path, required_bw, is_release=False)

            # Step 3: 记录服务事件与资源的关联关系
            event_resources = {
                'event': event,
                'type': 'distributed_training',
                'nodes': event.dc_list.copy(),
                'links': [],
                'gpus_per_dc': gpus_per_dc,
                'required_bw': required_bw,
                'selected_wavelengths': selected_wavelengths  # 记录波长选择结果
            }

            for path in allocated_paths:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    link = tuple(sorted((u, v)))
                    event_resources['links'].append(link)

            for dc_id in event.dc_list:
                if dc_id not in self.service_event_registry['nodes']:
                    self.service_event_registry['nodes'][dc_id] = []
                self.service_event_registry['nodes'][dc_id].append(event.event_id)

            for link in event_resources['links']:
                if link not in self.service_event_registry['links']:
                    self.service_event_registry['links'][link] = []
                self.service_event_registry['links'][link].append(event.event_id)

            self.service_event_registry['events'][event.event_id] = event_resources
            
            # 记录资源利用率
            collector = get_performance_collector()
            collector.record_resource_utilization(
                timestamp=self.env.now if self.env else 0.0,
                G=self.G
            )
            
            return allocated_paths

        except Exception as e:
            LOGGER.error(f"资源分配失败: {str(e)}")
            for path in allocated_paths:
                self.release_bandwidth_path(path, required_bw)
            for dc_id in allocated_dcs:
                if dc_id in gpus_per_dc:
                    self.release_compute_resource(dc_id, gpus_per_dc[dc_id])
            raise

    def _get_event_resources(self, event_id):
        """获取事件资源信息"""
        return self.service_event_registry['events'].get(event_id)

    def _cleanup_event_registry(self, event_id):
        """清理服务事件注册表"""
        event_resources = self._get_event_resources(event_id)
        if not event_resources:
            return

        for dc_id in event_resources['nodes']:
            if dc_id in self.service_event_registry['nodes']:
                self.service_event_registry['nodes'][dc_id] = [
                    eid for eid in self.service_event_registry['nodes'][dc_id]
                    if eid != event_id
                ]
                if not self.service_event_registry['nodes'][dc_id]:
                    del self.service_event_registry['nodes'][dc_id]

        for link in event_resources['links']:
            if link in self.service_event_registry['links']:
                self.service_event_registry['links'][link] = [
                    eid for eid in self.service_event_registry['links'][link]
                    if eid != event_id
                ]
                if not self.service_event_registry['links'][link]:
                    del self.service_event_registry['links'][link]

        del self.service_event_registry['events'][event_id]

    def release_graph_resources(self, event, paths):
        """
        Release resources for distributed training event.

        Args:
            event: DistributedTrainingEvent object
            paths: List of paths to release bandwidth from
        """
        event_resources = self._get_event_resources(event.event_id)
        if not event_resources:
            return

        gpus_per_dc = event_resources.get('gpus_per_dc', {})
        adjusted_bw = event_resources.get('required_bw', 100.0)
        selected_wavelengths = event_resources.get('selected_wavelengths', {})  # 获取波长选择结果

        # Release compute resources
        for dc_id in event.dc_list:
            gpus = gpus_per_dc.get(dc_id, event.gpus_per_dc)
            self.release_compute_resource(dc_id, gpus)
        self._log_gpu_allocation(gpus_per_dc, is_release=True)

        # Release wavelengths and network bandwidth
        # 去重：使用集合记录已处理的物理链路，避免往返路径重复释放
        processed_links = set()
        for path in paths:
            # 生成链路键，确保A->B和B->A被视为同一条链路
            if len(path) >= 2:
                link_key = tuple(sorted((path[0], path[-1])))
                if link_key in processed_links:
                    LOGGER.debug(f"跳过重复路径释放: {path} 已处理")
                    continue
                processed_links.add(link_key)

                # 如果有预选波长，释放波长；否则使用传统带宽释放
                if selected_wavelengths and link_key in selected_wavelengths:
                    wavelength_ids = selected_wavelengths[link_key]
                    self._mark_wavelengths_as_available(path, wavelength_ids)
                    LOGGER.info(f"路径 {link_key} 释放波长: {wavelength_ids}")
                    # 同时释放带宽
                    self.release_bandwidth_path(path, adjusted_bw)


                self._log_bandwidth_allocation(path, adjusted_bw, is_release=True)

        # Cleanup registry
        self._cleanup_event_registry(event.event_id)
        
        # 记录资源利用率
        collector = get_performance_collector()
        collector.record_resource_utilization(
            timestamp=self.env.now if self.env else 0.0,
            G=self.G
        )
