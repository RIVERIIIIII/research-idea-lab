import random
import networkx as nx
from typing import List, Dict, Tuple, Optional
from itertools import combinations
from result import LOGGER
from common_utils import CrossDomainCalculator, NetworkResourceCalculator, LocalPerformanceCalculator, WavelengthSelector, extract_event_config
from performance_collector import get_performance_collector


class ResourceSelectionConfig:
    """资源选择算法配置常量"""
    DEFAULT_WAVELENGTH_CAPACITY = 100.0  # 默认波长容量 (Gbps)
    MAX_WAVELENGTH_SEARCH = 20  # 最大波长搜索数量
    MAX_DATA_PARALLELISM = 100  # 最大数据并行度
    MAX_DC_SEARCH_OFFSET = 5  # 数据中心搜索范围偏移量
    SINGLE_DC_STRATEGY = True  # 是否启用单点优先策略
    



class ResourceSelection:
    """
    资源选择模块，实现基于Level指标的两种算法
    """

    def __init__(self, G, config=None):
        self.G = G
        self.config = config or ResourceSelectionConfig()
        self.level_calculator = CrossDomainCalculator()
        self.path_calculator = NetworkResourceCalculator(G)
        self.wavelength_selector = WavelengthSelector(G)
        self.perf_calculator = LocalPerformanceCalculator()



    def get_wavelength_capacity(self, path=None):
        """
        从图G中获取波长容量

        Args:
            path: 可选的路径，用于获取特定路径的波长容量

        Returns:
            float: 波长容量（Gbps）
        """
        if path and len(path) >= 2:
            u, v = path[0], path[1]
            if self.G.has_edge(u, v):
                wavelength_channels = self.G.edges[u, v].get('wavelength_channels', [])
                for channel in wavelength_channels:
                    if channel.status == 0:
                        return float(channel.bandwidth.replace('G', ''))
        return self.config.DEFAULT_WAVELENGTH_CAPACITY
    
    def get_total_available_gpus(self) -> int:
        """
        获取当前所有可用数据中心的GPU资源总量
        
        Returns:
            int: 总可用GPU数量
        """
        total = 0
        for node_id, node_data in self.G.nodes(data=True):
            if node_data.get('type') == 'datacenter' or node_data.get('is_co_location', False):
                total += node_data.get('available_gpu', 0)
        return total
    
    def calculate_gpus_per_dc(self, selected_dcs: List[int], N_req: int, p: int, t: int) -> Dict[int, int]:
        """
        计算每个选中的数据中心应分配的GPU数量
        
        Args:
            selected_dcs: 选中的数据中心列表
            N_req: 总GPU需求（必须是 p*t 的整数倍）
            p: 流水线并行度
            t: 张量并行度
        
        Returns:
            Dict[int, int]: 数据中心ID到分配GPU数量的映射
        """
        unit = p * t
        
        dc_available = {dc_id: self.G.nodes[dc_id]['available_gpu'] for dc_id in selected_dcs}
        
        sorted_dcs = sorted(selected_dcs, key=lambda dc_id: dc_available[dc_id])
        
        total_available = sum(dc_available.values())
        if total_available < N_req:
            from Graph_update import ComputeResourceError
            raise ComputeResourceError(None, N_req, total_available)
        
        gpus_per_dc = {dc_id: 0 for dc_id in selected_dcs}
        remaining_gpus = N_req
        
        for dc_id in sorted_dcs:
            if remaining_gpus <= 0:
                break
            max_possible = dc_available[dc_id] // unit * unit
            if max_possible > 0:
                allocate = min(max_possible, remaining_gpus)
                gpus_per_dc[dc_id] = allocate
                remaining_gpus -= allocate
        
        return gpus_per_dc
    
    def _get_available_datacenters(self):
        """获取所有可用的数据中心"""
        return [n for n, data in self.G.nodes(data=True)
                if (data.get('type') == 'datacenter' or data.get('is_co_location', False))
                and not data.get('failed', False)
                and 'available_gpu' in data]

    def _handle_single_dc_result(
        self,
        selected_dc: int,
        gpus_per_dc: Dict[int, int],
        N_req: int,
        p: int,
        t: int,
        event,
        algorithm_name: str,
        start_time: float) -> Tuple[List[int], Dict[int, int], Dict, int, float, float, Dict]:
        """
        处理单DC场景的结果     
        Args:
            selected_dc: 已选中的数据中心ID
            gpus_per_dc: 每个DC分配的GPU数量字典
            N_req: 总GPU需求
            p: 流水线并行度
            t: 张量并行度
            event: 事件对象
            algorithm_name: 算法名称（用于性能记录和日志前缀）
            start_time: 算法开始时间（用于计算执行时间）
        
        Returns:
            Tuple: (selected_dcs, gpus_per_dc, communication_paths, n_wave, required_bw, jct, selected_wavelengths)
        """
        import time
        
        selected_dcs = [selected_dc]
        communication_paths = {}
        n_wave = 0
        selected_wavelengths = {}
        required_bw = 0.0
        
        # 使用 calculate_local_execution_time 计算单DC场景的JCT
        data_parallel = N_req // (p * t)
        exec_time_result = self.perf_calculator.calculate_local_execution_time(
            event, selected_dc, data_parallel, data_parallel
        )
        t_sol = exec_time_result['t_sol']
        
        # 计算迭代次数
        config = extract_event_config(event, data_parallel=data_parallel)
        tokens_count = int(config['tokens'] * 1e12)
        iterations = tokens_count // (config['global_batch_size'] * config['sequence_length'])
        
        # 计算JCT
        jct = t_sol * iterations
        
        # 单DC场景下，Level值设为无穷大（无跨域通信损失）
        level = float('inf')
        
        LOGGER.info(f"[{algorithm_name}] 单DC场景，跳过通信资源分配，DC: {selected_dc}, JCT: {jct:.4f}")
        
        # 记录算法性能指标
        execution_time = time.time() - start_time
        collector = get_performance_collector()
        collector.record_algorithm_metrics(
            algorithm_name=algorithm_name,
            execution_time=execution_time,
            level_value=level,
            jct=jct,
            cost_c=0.0,
            num_wavelengths=0,
            num_dcs=1,
            total_gpus=N_req,
            event_id=getattr(event, 'event_id', -1)
        )
        
        LOGGER.info(f"[{algorithm_name}] 执行时间: {execution_time:.4f}秒")
        return (selected_dcs, gpus_per_dc, communication_paths, n_wave, required_bw, jct, selected_wavelengths)

    def _calculate_k_min(self, sorted_dcs, N_req):
        """计算理论最少需要的数据中心数量"""
        cumulative_gpus = 0
        k_min = 0
        for dc in sorted_dcs:
            cumulative_gpus += self.G.nodes[dc]['available_gpu']
            k_min += 1
            if cumulative_gpus >= N_req:
                break
        return k_min

    def _evaluate_dc_combination(self, dc_combination, N_req, p, t, event):
        """
        评估一个DC组合，返回最佳Level值、JCT、波长数和波长选择结果

        Returns:
            Tuple[float, float, int, Dict, Dict[int, int], Dict[Tuple[int, int], List[int]], float]: 
            (最佳Level值, 最佳JCT, 最佳波长数, 波长选择结果, 每个DC的GPU分配, 通信路径, 所需带宽)
            波长选择结果: {path_key: [wavelength_ids]}
        """
        dc_list = list(dc_combination)
        paths = self.path_calculator.calculate_all_pair_paths(dc_list)
        if paths is None:
            LOGGER.debug(f"DC组合 {dc_combination} 没有可用路径")
            return (-float('inf'), float('inf'), 1, {}, {}, {}, 0.0)

        LOGGER.debug(f"评估DC组合: {dc_list}, 路径数={len(paths)}")

        bottleneck_bw = self.path_calculator.calculate_bottleneck_bw(paths)
        max_level = -float('inf')
        jct = float('inf')
        best_n_wave = 1
        best_selected_wavelengths = {}
        best_required_bw = 0.0

        # 预计算循环不变量，移出循环以减少重复计算
        first_path = paths.get((dc_list[0], dc_list[1])) if len(dc_list) > 1 else None
        current_wavelength_capacity = self.get_wavelength_capacity(first_path)
        gpus_per_dc = self.calculate_gpus_per_dc(dc_list, N_req, p, t)
        data_parallel = N_req // (p * t)

        LOGGER.debug(f"瓶颈带宽={bottleneck_bw}, 单波长容量={current_wavelength_capacity}")

        for n_wave in range(1, self.config.MAX_WAVELENGTH_SEARCH + 1):
            required_bw = n_wave * current_wavelength_capacity
            event.bandwidth_gbps = required_bw

            # 检查总带宽是否足够
            if required_bw > bottleneck_bw:
                LOGGER.debug(f"n_wave={n_wave}: 所需带宽{required_bw}超过瓶颈带宽{bottleneck_bw}")
                continue

            # 调用波长选择函数，不仅检查连续性，还实际选择波长
            success, selected_wavelengths, reason = self.wavelength_selector.select_for_paths(paths, n_wave)
            if not success:
                LOGGER.debug(f"n_wave={n_wave}: 波长选择失败: {reason}")
                continue

            LOGGER.debug(f"n_wave={n_wave}: 波长选择成功: {selected_wavelengths}")

            metrics = self.level_calculator.calculate_performance_metrics(
                event, dc_list, data_parallel, n_wave, paths, gpus_per_dc, self.G, self.perf_calculator
            )
            current_level = metrics['level']
            current_jct = metrics['jct']
            LOGGER.debug(f"n_wave={n_wave}: Level值={current_level:.8f}, JCT={current_jct:.8f}")

            #存在膝点，level下降即推出波长循环
            if current_level > max_level:
                max_level = current_level
                jct = current_jct
                best_n_wave = n_wave
                best_selected_wavelengths = selected_wavelengths
                best_required_bw = required_bw
                LOGGER.debug(f"n_wave={n_wave}: 更新最佳Level值={max_level:.8f},此时JCT={jct:.8f}")
            else:
                LOGGER.debug(f"n_wave={n_wave}: Level值={current_level:.8f}，未提升最佳Level")
                LOGGER.debug(f"DC组合 {dc_list} 评估完成: 最佳Level={max_level:.8f}, 最佳波长数={best_n_wave}, 此时JCT={jct:.8f}")
                return (max_level, jct, best_n_wave, best_selected_wavelengths, gpus_per_dc, paths, best_required_bw)
        return (max_level, jct, best_n_wave, best_selected_wavelengths, gpus_per_dc, paths, best_required_bw)

    def _select_wavelengths_baseline(self, paths: Dict, max_wavelengths: int = 8) -> Tuple[int, Dict]:
        """
        基准算法的波长分配逻辑
        优先分配max_wavelengths个波长，不足时分配所有剩余可用波长

        Args:
            paths: DC之间的通信路径字典
            max_wavelengths: 最大波长分配数量（默认8个）

        Returns:
            Tuple[int, Dict]: (实际分配的波长数量, 波长选择结果)
            波长选择结果: {path_key: [wavelength_ids]}
        """
        if not paths:
            return 0, {}

        # 尝试分配max_wavelengths个波长
        success, selected_wavelengths, reason = self.wavelength_selector.select_for_paths(
            paths, max_wavelengths
        )

        if success:
            LOGGER.debug(f"基准算法成功分配 {max_wavelengths} 个波长")
            return max_wavelengths, selected_wavelengths

        # 如果8个波长不足，尝试分配更少波长
        LOGGER.debug(f"分配 {max_wavelengths} 个波长失败: {reason}，尝试分配更少波长")

        for n_wave in range(max_wavelengths - 1, 0, -1):
            success, selected_wavelengths, reason = self.wavelength_selector.select_for_paths(
                paths, n_wave
            )
            if success:
                LOGGER.debug(f"基准算法成功分配 {n_wave} 个波长")
                return n_wave, selected_wavelengths

        LOGGER.warning("基准算法未能分配到任何波长")
        return 0, {}

    def _allocate_gpus_greedy(
        self,
        ordered_dcs: List[int],
        N_req: int,
        p: int,
        t: int,
        algorithm_name: str) -> Tuple[List[int], Dict[int, int]]:
        """
        通用的贪心GPU分配函数
        
        按给定的DC顺序进行贪心分配，直至满足任务所需资源量。
        
        Args:
            ordered_dcs: 已按所需顺序排列的DC列表
            N_req: 总GPU需求
            p: 流水线并行度
            t: 张量并行度
            algorithm_name: 算法名称（用于日志）
        
        Returns:
            Tuple[List[int], Dict[int, int]]: (选中的DC列表, 每个DC分配的GPU数量)
        """
        unit = p * t
        
        valid_dcs = [dc for dc in ordered_dcs if self.G.nodes[dc]['available_gpu'] >= unit]
        
        if not valid_dcs:
            LOGGER.warning(f"[{algorithm_name}] 没有数据中心拥有足够的GPU支持一个DP组（需要至少 {unit} 个GPU）")
            return [], {}
        
        selected_dcs = []
        gpus_per_dc = {}
        remaining_gpus = N_req
        
        LOGGER.info(f"[{algorithm_name}] 开始分配，需求: {N_req}, 最小单位: {unit}")
        
        for dc in valid_dcs:
            if remaining_gpus <= 0:
                break
            
            available = self.G.nodes[dc]['available_gpu']
            max_allocatable = (available // unit) * unit
            
            if max_allocatable <= 0:
                continue
            
            allocate = min(max_allocatable, remaining_gpus)
            allocate = (allocate // unit) * unit
            
            if allocate >= unit:
                selected_dcs.append(dc)
                gpus_per_dc[dc] = allocate
                remaining_gpus -= allocate
                LOGGER.debug(f"[{algorithm_name}] DC {dc}: 可用 {available}, 分配 {allocate}, 剩余需求 {remaining_gpus}")
        
        total_allocated = sum(gpus_per_dc.values())
        if total_allocated < N_req:
            LOGGER.warning(f"[{algorithm_name}] 资源分配不完整: 需求 {N_req}, 已分配 {total_allocated}")
            return [], {}
        
        LOGGER.info(f"[{algorithm_name}] 选择的数据中心: {selected_dcs}, 分配详情: {gpus_per_dc}")
        
        return selected_dcs, gpus_per_dc

    def Random_Fit(self, N_req: int, event, p, t) -> Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
        """
        基线算法：Random-Fit随机装箱算法
        
        随机打乱数据中心顺序，然后按打乱后的顺序贪心选择，
        直至满足任务所需资源量。
        
        波长分配规则：在最短路径的剩余波长资源中选择可用波长。
        
        Args:
            N_req: 总GPU需求
            event: 包含任务配置参数的事件对象
            p: 流水线并行度
            t: 张量并行度
            
        Returns:
            Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
            (选中的数据中心列表, 每个DC分配的GPU数量, DC之间的通信路径字典, 分配的波长数量, 所需带宽, JCT, 波长选择结果)
        """
        import time
        start_time = time.time()
        LOGGER.info(f"[Random-Fit] 开始执行，总GPU需求: {N_req}")
        
        all_dcs = self._get_available_datacenters()
        
        # 随机打乱DC顺序（Random-Fit核心：随机排序）
        shuffled_dcs = all_dcs.copy()
        random.shuffle(shuffled_dcs)
        
        # 调用通用贪心分配函数
        selected_dcs, gpus_per_dc = self._allocate_gpus_greedy(
            shuffled_dcs, N_req, p, t, 'Random-Fit'
        )
        
        if not selected_dcs:
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 单DC场景：调用通用处理函数
        if len(selected_dcs) == 1:
            return self._handle_single_dc_result(
                selected_dc=selected_dcs[0],
                gpus_per_dc=gpus_per_dc,
                N_req=N_req,
                p=p,
                t=t,
                event=event,
                algorithm_name='Random-Fit',
                start_time=start_time
            )
        
        # 5. 获取通信路径
        communication_paths = self.path_calculator.calculate_all_pair_paths(list(selected_dcs))
        
        # 6. 波长分配
        n_wave, selected_wavelengths = self._select_wavelengths_baseline(communication_paths, max_wavelengths=8)
        
        if n_wave == 0 and len(selected_dcs) > 1:
            LOGGER.warning("[Random-Fit] 波长分配失败")
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 7. 计算性能指标
        data_parallel = N_req // (p * t)
        metrics = self.level_calculator.calculate_performance_metrics(
            event, selected_dcs, data_parallel, n_wave, communication_paths, gpus_per_dc, self.G, self.perf_calculator
        )
        level = metrics['level']
        jct = metrics['jct']
        
        # 8. 计算所需带宽
        first_path = next(iter(communication_paths.values())) if communication_paths else None
        wavelength_capacity = self.get_wavelength_capacity(first_path)
        required_bw = n_wave * wavelength_capacity
        event.bandwidth_gbps = required_bw
        
        LOGGER.info(f"[Random-Fit] 完成，DC: {selected_dcs}, 波长: {n_wave}, Level: {level:.4f}, JCT: {jct:.4f}")
        
        # 9. 记录算法性能指标
        execution_time = time.time() - start_time
        collector = get_performance_collector()
        collector.record_algorithm_metrics(
            algorithm_name='Random-Fit',
            execution_time=execution_time,
            level_value=level,
            jct=jct,
            cost_c=self.level_calculator.calculate_cost_c(communication_paths, n_wave) if communication_paths else 0.0,
            num_wavelengths=n_wave,
            num_dcs=len(selected_dcs),
            total_gpus=N_req,
            event_id=getattr(event, 'event_id', -1)
        )
        
        LOGGER.info(f"[Random-Fit] 执行时间: {execution_time:.4f}秒")
        return (selected_dcs, gpus_per_dc, communication_paths, n_wave, required_bw, jct, selected_wavelengths)

    def First_Fit(self, N_req: int, event, p, t) -> Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
        """
        基线算法：First-Fit首次适应算法
        
        无需对资源进行排序，直接按资源列表顺序选择资源，
        直至满足任务所需资源量。
        
        波长分配逻辑与Best_Fit和Worst_Fit算法保持完全一致。
        
        Args:
            N_req: 总GPU需求
            event: 包含任务配置参数的事件对象
            p: 流水线并行度
            t: 张量并行度
            
        Returns:
            Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
            (选中的数据中心列表, 每个DC分配的GPU数量, DC之间的通信路径字典, 分配的波长数量, 所需带宽, JCT, 波长选择结果)
        """
        import time
        start_time = time.time()
        LOGGER.info(f"[First-Fit] 开始执行，总GPU需求: {N_req}")
        
        all_dcs = self._get_available_datacenters()
        
        # 不进行排序，直接使用原始顺序（First-Fit核心：首次适应）
        # 调用通用贪心分配函数
        selected_dcs, gpus_per_dc = self._allocate_gpus_greedy(
            all_dcs, N_req, p, t, 'First-Fit'
        )
        
        if not selected_dcs:
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 单DC场景：调用通用处理函数
        if len(selected_dcs) == 1:
            return self._handle_single_dc_result(
                selected_dc=selected_dcs[0],
                gpus_per_dc=gpus_per_dc,
                N_req=N_req,
                p=p,
                t=t,
                event=event,
                algorithm_name='First-Fit',
                start_time=start_time
            )
        
        # 5. 获取通信路径
        communication_paths = self.path_calculator.calculate_all_pair_paths(list(selected_dcs))
        
        # 6. 波长分配
        n_wave, selected_wavelengths = self._select_wavelengths_baseline(communication_paths, max_wavelengths=8)
        
        if n_wave == 0 and len(selected_dcs) > 1:
            LOGGER.warning("[First-Fit] 波长分配失败")
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 7. 计算性能指标
        data_parallel = N_req // (p * t)
        metrics = self.level_calculator.calculate_performance_metrics(
            event, selected_dcs, data_parallel, n_wave, communication_paths, gpus_per_dc, self.G, self.perf_calculator
        )
        level = metrics['level']
        jct = metrics['jct']
        
        # 8. 计算所需带宽
        first_path = next(iter(communication_paths.values())) if communication_paths else None
        wavelength_capacity = self.get_wavelength_capacity(first_path)
        required_bw = n_wave * wavelength_capacity
        event.bandwidth_gbps = required_bw
        
        LOGGER.info(f"[First-Fit] 完成，DC: {selected_dcs}, 波长: {n_wave}, Level: {level:.4f}, JCT: {jct:.4f}")
        
        # 9. 记录算法性能指标
        execution_time = time.time() - start_time
        collector = get_performance_collector()
        collector.record_algorithm_metrics(
            algorithm_name='First-Fit',
            execution_time=execution_time,
            level_value=level,
            jct=jct,
            cost_c=self.level_calculator.calculate_cost_c(communication_paths, n_wave) if communication_paths else 0.0,
            num_wavelengths=n_wave,
            num_dcs=len(selected_dcs),
            total_gpus=N_req,
            event_id=getattr(event, 'event_id', -1)
        )
        
        LOGGER.info(f"[First-Fit] 执行时间: {execution_time:.4f}秒")
        return (selected_dcs, gpus_per_dc, communication_paths, n_wave, required_bw, jct, selected_wavelengths)

    def Worst_Fit(self, N_req: int, event, p, t) -> Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
        """
        基线算法一：Worst-Fit-Greedy装箱算法（最小化DC数量）
        
        基于Worst-Fit装箱思想，优先选择资源最多的数据中心，
        目标是用最少的DC数量满足任务需求，从而减少跨域通信开销。但是没有考虑最优解。
        
        核心思想：
        1. 按GPU容量降序排序所有可用DC
        2. 贪心选择：依次选择资源最多的DC，直到满足需求
        3. 确保每个DC分配的资源至少为一个DP组(p*t)
        
        Args:
            N_req: 总GPU需求
            event: 包含任务配置参数的事件对象
            p: 流水线并行度
            t: 张量并行度
            
        Returns:
            Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
            (选中的数据中心列表, 每个DC分配的GPU数量, DC之间的通信路径字典, 分配的波长数量, 所需带宽, JCT, 波长选择结果)
        """
        import time
        start_time = time.time()
        LOGGER.info(f"[Worst-Fit] 开始执行，总GPU需求: {N_req}")
        
        all_dcs = self._get_available_datacenters()
        
        # 按GPU容量降序排序（FFD核心：降序排序）
        sorted_dcs = sorted(all_dcs, key=lambda dc: self.G.nodes[dc]['available_gpu'], reverse=True)
        
        # 调用通用贪心分配函数
        selected_dcs, gpus_per_dc = self._allocate_gpus_greedy(
            sorted_dcs, N_req, p, t, 'Worst-Fit'
        )
        
        if not selected_dcs:
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 单DC场景：调用通用处理函数
        if len(selected_dcs) == 1:
            return self._handle_single_dc_result(
                selected_dc=selected_dcs[0],
                gpus_per_dc=gpus_per_dc,
                N_req=N_req,
                p=p,
                t=t,
                event=event,
                algorithm_name='Worst-Fit',
                start_time=start_time
            )
        
        # 5. 获取通信路径
        communication_paths = self.path_calculator.calculate_all_pair_paths(list(selected_dcs))
        
        # 6. 波长分配
        n_wave, selected_wavelengths = self._select_wavelengths_baseline(communication_paths, max_wavelengths=8)
        
        if n_wave == 0 and len(selected_dcs) > 1:
            LOGGER.warning("[Worst-Fit] 波长分配失败")
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 7. 计算性能指标
        data_parallel = N_req // (p * t)
        metrics = self.level_calculator.calculate_performance_metrics(
            event, selected_dcs, data_parallel, n_wave, communication_paths, gpus_per_dc, self.G, self.perf_calculator
        )
        level = metrics['level']
        jct = metrics['jct']
        
        # 8. 计算所需带宽
        first_path = next(iter(communication_paths.values())) if communication_paths else None
        wavelength_capacity = self.get_wavelength_capacity(first_path)
        required_bw = n_wave * wavelength_capacity
        event.bandwidth_gbps = required_bw
        
        LOGGER.info(f"[Worst-Fit] 完成，DC: {selected_dcs}, 波长: {n_wave}, Level: {level:.4f}, JCT: {jct:.4f}")
        
        # 9. 记录算法性能指标
        execution_time = time.time() - start_time
        collector = get_performance_collector()
        collector.record_algorithm_metrics(
            algorithm_name='Worst-Fit',
            execution_time=execution_time,
            level_value=level,
            jct=jct,
            cost_c=self.level_calculator.calculate_cost_c(communication_paths, n_wave) if communication_paths else 0.0,
            num_wavelengths=n_wave,
            num_dcs=len(selected_dcs),
            total_gpus=N_req,
            event_id=getattr(event, 'event_id', -1)
        )
        
        LOGGER.info(f"[Worst-Fit] 执行时间: {execution_time:.4f}秒")
        return (selected_dcs, gpus_per_dc, communication_paths, n_wave, required_bw, jct, selected_wavelengths)

    def Best_Fit(self, N_req: int, event, p, t) -> Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
        """
        基线算法二：Least-Resource-First（最小资源优先）
        
        采用Best-Fit装箱思想，与Worst-fit相反，优先选择资源最少的数据中心，
        目标是减少资源碎片，优先消耗小容量DC。
        
        核心思想：
        1. 按GPU容量升序排序所有可用DC
        2. 贪心选择：依次选择资源最少的DC，直到满足需求
        3. 确保每个DC分配的资源至少为一个DP组(p*t)
        4. 目标是减少资源碎片
        
        Args:
            N_req: 总GPU需求
            event: 包含任务配置参数的事件对象
            p: 流水线并行度
            t: 张量并行度
            
        Returns:
            Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
            (选中的数据中心列表, 每个DC分配的GPU数量, DC之间的通信路径字典, 分配的波长数量, 所需带宽, JCT, 波长选择结果)
        """
        import time
        start_time = time.time()
        LOGGER.info(f"[Best-Fit] 开始执行，总GPU需求: {N_req}")
        
        all_dcs = self._get_available_datacenters()
        
        # 按GPU容量升序排序（核心：优先选择资源最少的DC）
        sorted_dcs = sorted(all_dcs, key=lambda dc: self.G.nodes[dc]['available_gpu'])
        
        # 调用通用贪心分配函数
        selected_dcs, gpus_per_dc = self._allocate_gpus_greedy(
            sorted_dcs, N_req, p, t, 'Best-Fit'
        )
        
        if not selected_dcs:
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 单DC场景：调用通用处理函数
        if len(selected_dcs) == 1:
            return self._handle_single_dc_result(
                selected_dc=selected_dcs[0],
                gpus_per_dc=gpus_per_dc,
                N_req=N_req,
                p=p,
                t=t,
                event=event,
                algorithm_name='Best-Fit',
                start_time=start_time
            )
        
        # 5. 获取通信路径
        communication_paths = self.path_calculator.calculate_all_pair_paths(list(selected_dcs))
        
        # 6. 波长分配
        n_wave, selected_wavelengths = self._select_wavelengths_baseline(communication_paths, max_wavelengths=8)
        
        if n_wave == 0 and len(selected_dcs) > 1:
            LOGGER.warning("[Best-Fit] 波长分配失败")
            return ([], {}, {}, 0, 0.0, float('inf'), {})
        
        # 7. 计算性能指标
        data_parallel = N_req // (p * t)
        metrics = self.level_calculator.calculate_performance_metrics(
            event, selected_dcs, data_parallel, n_wave, communication_paths, gpus_per_dc, self.G, self.perf_calculator
        )
        level = metrics['level']
        jct = metrics['jct']
        
        # 8. 计算所需带宽
        first_path = next(iter(communication_paths.values())) if communication_paths else None
        wavelength_capacity = self.get_wavelength_capacity(first_path)
        required_bw = n_wave * wavelength_capacity
        event.bandwidth_gbps = required_bw
        
        LOGGER.info(f"[Best-Fit] 完成，DC: {selected_dcs}, 波长: {n_wave}, Level: {level:.4f}, JCT: {jct:.4f}")
        
        # 9. 记录算法性能指标
        execution_time = time.time() - start_time
        collector = get_performance_collector()
        collector.record_algorithm_metrics(
            algorithm_name='Best-Fit',
            execution_time=execution_time,
            level_value=level,
            jct=jct,
            cost_c=self.level_calculator.calculate_cost_c(communication_paths, n_wave) if communication_paths else 0.0,
            num_wavelengths=n_wave,
            num_dcs=len(selected_dcs),
            total_gpus=N_req,
            event_id=getattr(event, 'event_id', -1)
        )
        
        LOGGER.info(f"[Best-Fit] 执行时间: {execution_time:.4f}秒")
        return (selected_dcs, gpus_per_dc, communication_paths, n_wave, required_bw, jct, selected_wavelengths)

    def min_cross_domain_penalty(self, N_req: int, event, p, t) -> Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
        """
        算法一：最小化跨域损失算法
        
        通过遍历所有DC组合，选择Level值最大的组合，实现跨域损失最小化。

        Args:
            N_req: 总GPU需求
            event: 包含任务配置参数的事件对象
            p: 流水线并行度
            t: 张量并行度

        Returns:
            Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
            (选中的数据中心列表, 每个DC分配的GPU数量, DC之间的通信路径字典, 分配的波长数量, 所需带宽, JCT, 波长选择结果)
            波长选择结果: {path_key: [wavelength_ids]}
        """
        import time
        start_time = time.time()
        LOGGER.info(f"[minPenalty] 开始执行，总GPU需求: {N_req}")

        all_dcs = self._get_available_datacenters()

        # 1. 尝试单点优先策略
        if self.config.SINGLE_DC_STRATEGY:
            single_dc_candidates = [dc for dc in all_dcs if self.G.nodes[dc]['available_gpu'] >= N_req]
            if single_dc_candidates:
                single_dc_candidates.sort(key=lambda dc: self.G.nodes[dc]['available_gpu'])
                selected_dc = single_dc_candidates[0]
                gpus_per_dc = {selected_dc: N_req}
                LOGGER.info(f"[minPenalty] 单点优先策略成功，选择DC: {selected_dc}")
                
                # 调用统一的单DC结果处理方法（内部已记录性能指标）
                return self._handle_single_dc_result(
                    selected_dc=selected_dc,
                    gpus_per_dc=gpus_per_dc,
                    N_req=N_req,
                    p=p,
                    t=t,
                    event=event,
                    algorithm_name='minPenalty',
                    start_time=start_time
                )

        # 2. 确定搜索起点
        sorted_dcs = sorted(all_dcs, key=lambda dc: self.G.nodes[dc]['available_gpu'], reverse=True)
        k_min = self._calculate_k_min(sorted_dcs, N_req)
        LOGGER.info(f"[minPenalty] 剩余资源理论最少需要 {k_min} 个DC")

        # 3. 基数递增搜索
        best_level = -float('inf')
        best_dcs = None
        best_n_wave_overall = 1
        best_selected_wavelengths_overall = {}
        best_jct = float('inf')
        best_gpus_per_dc = {}
        best_paths = {}
        best_required_bw = 0.0
        max_k = min(len(all_dcs), k_min + self.config.MAX_DC_SEARCH_OFFSET)

        for k in range(k_min, max_k + 1):
            threshold = p * t
            candidate_dcs = [dc for dc in sorted_dcs if self.G.nodes[dc]['available_gpu'] >= threshold]
            LOGGER.info(f"[minPenalty] 在{len(candidate_dcs)}个候选DC中寻找最优 {k} 个DC的组合")
            if len(candidate_dcs) < k:
                LOGGER.debug(f"[minPenalty] 候选DC数量不足 {k} 个，跳过")
                continue

            for dc_combination in combinations(candidate_dcs, k):
                total_gpus = sum(self.G.nodes[dc]['available_gpu'] for dc in dc_combination)
                if total_gpus < N_req:
                    continue

                max_level, jct, best_n_wave, selected_wavelengths, gpus_per_dc, paths, required_bw = self._evaluate_dc_combination(
                    dc_combination, N_req, p, t, event
                )
                LOGGER.debug(f"[minPenalty] DC组合 {dc_combination}: Level={max_level:.4f}, 波长={best_n_wave}, JCT={jct:.4f}")
                if max_level > best_level:
                    best_level = max_level
                    best_dcs = list(dc_combination)
                    best_n_wave_overall = best_n_wave
                    best_selected_wavelengths_overall = selected_wavelengths
                    best_jct = jct
                    best_gpus_per_dc = gpus_per_dc
                    best_paths = paths
                    best_required_bw = required_bw

            if best_dcs is not None:
                LOGGER.info(f"[minPenalty] 在 {k} 个DC的组合中找到最优解，DC: {best_dcs}，Level: {best_level:.4f}, JCT: {best_jct:.4f}")
                break

        if best_dcs is None:
            LOGGER.warning(f"[minPenalty] 未能找到可行解")
            return ([], {}, {}, 0, 0.0, float('inf'), {})

        LOGGER.info(f"[minPenalty] 执行完成，选择的数据中心: {best_dcs}，最佳波长数: {best_n_wave_overall}")

        event.bandwidth_gbps = best_required_bw

        execution_time = time.time() - start_time
        
        # 记录算法性能指标
        collector = get_performance_collector()
        collector.record_algorithm_metrics(
            algorithm_name='minPenalty',
            execution_time=execution_time,
            level_value=best_level,
            jct=best_jct,
            cost_c=self.level_calculator.calculate_cost_c(best_paths, best_n_wave_overall) if best_paths else 0.0,
            num_wavelengths=best_n_wave_overall,
            num_dcs=len(best_dcs),
            total_gpus=N_req,
            event_id=getattr(event, 'event_id', -1)
        )
        
        LOGGER.info(f"[minPenalty] 执行时间: {execution_time:.4f}秒")
        return (best_dcs, best_gpus_per_dc, best_paths, best_n_wave_overall, best_required_bw, best_jct, best_selected_wavelengths_overall)
    
    def select_datacenters_optimal(self, p: int, t: int, T_dead: float, event) -> Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]:
        """
        算法二：满足DDL的最少计算资源算法
        
        通过二分搜索找到满足截止时间约束的最小数据并行度。

        Args:
            p: 流水线并行度
            t: 张量并行度
            T_dead: 截止时间
            event: 包含任务配置参数的事件对象
            
        Returns:
            Tuple[List[int], Dict[int, int], Dict[Tuple[int, int], List[int]], int, float, float, Dict]: 
            (选中的数据中心列表, 每个DC分配的GPU数量, DC之间的通信路径字典, 分配的波长数量, 所需带宽, JCT, 波长选择结果)
        """
        import time
        start_time = time.time()
        LOGGER.info(f"[algorithm2] 开始执行，截止时间: {T_dead}")
        
        # 1. 估算资源下界
        N_min_theory, d_min = self.perf_calculator.estimate_resource_bound(event, T_dead, data_parallel=1)
        LOGGER.info(f"[algorithm2] 估算的最小GPU数量: {N_min_theory}, 最小数据并行度: {d_min}")

        # 2. 二分搜索
        EMPIRICAL_MULTIPLIER = 2
        max_d_physical = int(self.get_total_available_gpus() / (p * t))
        max_d = min(d_min * EMPIRICAL_MULTIPLIER, max_d_physical)

        L = d_min
        R = max_d
        Best = None
        best_level = -float('inf')
        best_d = 0

        # 二分搜索循环（支持动态扩展右边界）
        while True:
            while L <= R:
                d_try = (L + R) // 2
                LOGGER.info(f"[algorithm2] 尝试数据并行度: {d_try} (搜索范围: [{L}, {R}])")

                N_req = p * t * d_try

                # 调用算法一，查找最优的DC组合和波长数
                # 注意：min_cross_domain_penalty 内部已记录性能数据
                result = self.min_cross_domain_penalty(
                    N_req=N_req,
                    event=event,
                    p=p,
                    t=t
                )
                selected_dcs = result[0]
                gpus_per_dc = result[1]
                communication_paths = result[2]
                best_n_wave = result[3]
                required_bw = result[4]
                jct = result[5]
                best_selected_wavelengths = result[6]

                if not selected_dcs:
                    LOGGER.info(f"[algorithm2] 数据并行度 {d_try} 未能找到可行解，增加d")
                    L = d_try + 1
                    continue

                if jct <= T_dead:
                    LOGGER.info(f"[algorithm2] 数据并行度 {d_try}，JCT: {jct:.2f} 满足截止时间 {T_dead}")
                    Best = (selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, best_selected_wavelengths)
                    best_d = d_try
                    R = d_try - 1
                else:
                    LOGGER.info(f"[algorithm2] 数据并行度 {d_try}，JCT: {jct:.2f} 不满足截止时间 {T_dead}，增加d")
                    L = d_try + 1

            if Best is None and R < max_d_physical:
                LOGGER.info(f"[algorithm2] 扩展右边界: {max_d} -> {min(max_d * 2, max_d_physical)}")
                L = max_d + 1
                max_d = min(max_d * 2, max_d_physical)
                R = max_d
                continue

            break

        execution_time = time.time() - start_time
        
        if Best is not None:
            selected_dcs, gpus_per_dc, communication_paths, best_n_wave, required_bw, jct, best_selected_wavelengths = Best
            
            # 记录算法性能指标（只在最终结果处记录一次）
            collector = get_performance_collector()
            collector.record_algorithm_metrics(
                algorithm_name='algorithm2',
                execution_time=execution_time,
                level_value=0.0,  # algorithm2 不计算 level
                jct=jct,
                cost_c=self.level_calculator.calculate_cost_c(communication_paths, best_n_wave) if communication_paths else 0.0,
                num_wavelengths=best_n_wave,
                num_dcs=len(selected_dcs) if selected_dcs else 0,
                total_gpus=best_d * p * t,
                event_id=getattr(event, 'event_id', -1)
            )
            
            LOGGER.info(f"[algorithm2] 完成，最小数据并行度: {best_d}, DC: {selected_dcs}, 波长: {best_n_wave}, JCT: {jct:.2f}")
            LOGGER.info(f"[algorithm2] 执行时间: {execution_time:.4f}秒")
            return Best
        
        LOGGER.warning(f"[algorithm2] 未能找到满足截止时间的解")
        LOGGER.info(f"[algorithm2] 执行时间: {execution_time:.4f}秒")
        return ([], {}, {}, 0, 0.0, float('inf'), {})