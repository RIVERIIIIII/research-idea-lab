import networkx as nx
from typing import List, Dict, Tuple, Optional, Set
from result import LOGGER

# ========== 常量定义 ==========

# 数据类型字节数映射常量
DATA_TYPE_BYTES = {
    "fp32": 4,
    "fp16": 2,
    "bf16": 2,
    "fp8": 1
}

# 事件类型名称映射（用于日志显示）
EVENT_TYPE_NAMES = {
    'distributed_training': '分布式训练',
    'inference_service': '推理服务部署',
    'inference_request': '推理请求',
    'failure': '故障事件'
}

# GPU性能映射字典
GPU_PERFORMANCE_MAP = {
    'NVIDIA_A100': {
        'Flops_fp8': 624,
        'Flops_fp16': 312,
        'Flops_fp32': 156,
        'memory_GiB': 80
    },
    'NVIDIA_H100': {
        'Flops_fp8': 1979,
        'Flops_fp16': 989,
        'Flops_fp32': 330,
        'memory_GiB': 80
    },
    'NVIDIA_V100': {
        'Flops_fp8': 0,
        'Flops_fp16': 125,
        'Flops_fp32': 62,
        'memory_GiB': 32
    },
    'NVIDIA_A40': {
        'Flops_fp8': 0,
        'Flops_fp16': 150,
        'Flops_fp32': 75,
        'memory_GiB': 48
    },
    'NVIDIA_L40S': {
        'Flops_fp8': 864,
        'Flops_fp16': 432,
        'Flops_fp32': 165,
        'memory_GiB': 48
    },
    'AMD_MI300X': {
        'Flops_fp8': 2615,
        'Flops_fp16': 1307,
        'Flops_fp32': 327,
        'memory_GiB': 192
    }
}

# 物理常量
SPEED_OF_LIGHT_FIBER = 2 * 10**8  # 光纤中的光速 (米/秒)

# 计算常量
LEVEL_COST_COEFFICIENT = 1e4  # Level计算中的代价系数

# 默认GPU算力 (TFLOPS)
DEFAULT_GPU_FLOPS = {
    "fp8": 312,
    "fp16": 312,
    "fp32": 156
}

# 默认带宽值 (TB/s)
DEFAULT_BW_INTRA = 1.8   # NVLink 5.0 = 1.8 TB/s
DEFAULT_BW_INTER = 0.1   # 800Gb/s = 100GB/s = 0.1TB/s


# ========== 工具类 ==========

class DataTypeUtil:
    """
    数据类型工具类
    统一处理数据类型相关的转换和验证
    """

    @staticmethod
    def get_bytes_per_param(data_type: Optional[str]) -> int:
        """
        获取每种数据类型的字节数

        Args:
            data_type: 数据类型 (fp32, fp16, bf16, fp8)

        Returns:
            int: 每个参数的字节数，默认为2 (fp16)
        """
        if data_type is None:
            return 2
        return DATA_TYPE_BYTES.get(data_type.lower(), 2)


class GPUManager:
    """
    GPU性能管理类
    封装GPU性能数据的查询和管理
    """

    # GPU型号别名映射
    _MODEL_ALIASES = {
        'a100': 'NVIDIA_A100',
        'h100': 'NVIDIA_H100',
        'mi300x': 'AMD_MI300X',
        'l40s': 'NVIDIA_L40S',
        'v100': 'NVIDIA_V100',
        'a40': 'NVIDIA_A40'
    }

    def __init__(self):
        self._cache: Dict[str, float] = {}

    def normalize_model_name(self, model: str) -> str:
        """
        规范化GPU型号名称

        Args:
            model: GPU型号名称

        Returns:
            str: 规范化的型号名称
        """
        normalized = model.upper().replace(" ", "_")
        if normalized in GPU_PERFORMANCE_MAP:
            return normalized
        # 尝试别名
        simple = normalized.split("_")[-1].lower()
        return self._MODEL_ALIASES.get(simple, 'NVIDIA_A100')

    def get_flops(self, model: str, precision: str = "fp16") -> float:
        """
        获取GPU算力

        Args:
            model: GPU型号
            precision: 精度类型 (fp8, fp16, fp32)

        Returns:
            float: GPU算力 (TFLOPs)
        """
        normalized = self.normalize_model_name(model)
        cache_key = f"{normalized}_{precision.lower()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        key = f"Flops_{precision.lower()}"
        flops = GPU_PERFORMANCE_MAP.get(normalized, {}).get(key)
        if flops is None or flops == 0:
            flops = DEFAULT_GPU_FLOPS.get(precision.lower(), 312)

        self._cache[cache_key] = flops
        return flops

    def get_memory(self, model: str) -> int:
        """
        获取GPU显存大小

        Args:
            model: GPU型号

        Returns:
            int: 显存大小 (GiB)
        """
        normalized = self.normalize_model_name(model)
        return GPU_PERFORMANCE_MAP.get(normalized, {}).get('memory_GiB', 80)


class WavelengthSelector:
    """
    波长选择器
    负责为光路选择满足波长连续性要求的波长
    """

    def __init__(self, G):
        self.G = G

    def select_for_paths(
        self,
        paths: Dict[Tuple[int, int], List[int]],
        n_wave: int) -> Tuple[bool, Dict[Tuple[int, int], List[int]], str]:
        """
        为多条路径选择满足波长连续性的波长

        波长连续性要求：
        1. 单条路径内部的所有链路必须使用相同编号的波长
        2. 不同路径之间如果共享链路，不能使用相同的波长

        Args:
            paths: 路径字典，key为(src, dst)元组，value为路径节点列表
            n_wave: 每条路径需要的波长数量

        Returns:
            Tuple[bool, Dict, str]:
                - bool: 是否所有路径都成功选择波长
                - Dict: {path_key: [wavelength_ids]} 路径到波长列表的映射
                - str: 失败原因（如果失败）
        """
        if not paths or n_wave <= 0:
            return False, {}, f"路径为空或n_wave={n_wave}无效"

        LOGGER.debug(f"开始为{len(paths)}条路径选择波长，每条路径需要{n_wave}个波长")

        selected_wavelengths = {}
        link_allocated_wavelengths: Dict[Tuple[int, int], Set[int]] = {}

        for (src, dst), path in paths.items():
            # 跳过反向路径（与正向路径共享相同的物理链路）
            if (dst, src) in paths and src > dst:
                LOGGER.debug(f"跳过反向路径: ({src}, {dst})")
                continue

            success, wavelengths, reason = self._select_for_single_path(
                path, n_wave, link_allocated_wavelengths
            )

            if not success:
                LOGGER.debug(f"路径 ({src}, {dst}) 波长选择失败: {reason}")
                return False, {}, f"路径 ({src}, {dst}) 选择失败: {reason}"

            link_key = (src, dst)
            selected_wavelengths[link_key] = wavelengths

            # 更新链路已分配波长记录
            for u, v in zip(path[:-1], path[1:]):
                edge_key = tuple(sorted((u, v)))
                if edge_key not in link_allocated_wavelengths:
                    link_allocated_wavelengths[edge_key] = set()
                link_allocated_wavelengths[edge_key].update(wavelengths)

            LOGGER.debug(f"路径 ({src}, {dst}) 选择波长: {wavelengths}")

        LOGGER.debug(f"所有路径波长选择成功，共选择{len(selected_wavelengths)}条路径的波长")
        return True, selected_wavelengths, ""

    def _select_for_single_path(
        self,
        path: List[int],
        n_wave: int,
        link_allocated_wavelengths: Dict[Tuple[int, int], Set[int]]) -> Tuple[bool, List[int], str]:
        """
        为单条路径选择满足波长连续性的波长，考虑已分配的波长

        Args:
            path: 路径节点列表
            n_wave: 需要的波长数量
            link_allocated_wavelengths: 已分配的波长记录

        Returns:
            Tuple[bool, List[int], str]: (是否成功, 选择的波长ID列表, 失败原因)
        """
        if not path or len(path) < 2:
            return False, [], f"路径无效: {path}"

        if n_wave <= 0:
            return False, [], f"n_wave必须大于0: {n_wave}"

        LOGGER.debug(f"为路径 {path} 选择{n_wave}个波长（考虑已分配波长）")

        # 获取路径上所有链路都可用的波长（交集），排除已分配的波长
        available_wavelengths = None

        for u, v in zip(path[:-1], path[1:]):
            if not self.G.has_edge(u, v):
                return False, [], f"链路 ({u}, {v}) 不存在"

            wavelength_channels = self.G.edges[u, v].get('wavelength_channels', [])
            if not wavelength_channels:
                return False, [], f"链路 ({u}, {v}) 没有波长通道"

            # 获取该链路上状态为0（可用）的波长ID
            link_available = {
                ch.wavelength_id for ch in wavelength_channels
                if ch.status == 0
            }

            # 排除该链路上已被其他路径分配的波长
            edge_key = tuple(sorted((u, v)))
            if edge_key in link_allocated_wavelengths:
                allocated = link_allocated_wavelengths[edge_key]
                link_available -= allocated
                LOGGER.debug(f"链路 ({u}, {v}) 排除已分配波长 {allocated}，剩余可用: {link_available}")

            LOGGER.debug(f"链路 ({u}, {v}) 可用波长: {link_available}")

            if available_wavelengths is None:
                available_wavelengths = link_available
                LOGGER.debug(f"初始化可用波长集合: {available_wavelengths}")
            else:
                old_count = len(available_wavelengths)
                available_wavelengths &= link_available
                new_count = len(available_wavelengths)
                LOGGER.debug(f"取交集后可用波长: {available_wavelengths} (从{old_count}个减少到{new_count}个)")

            if not available_wavelengths:
                return False, [], f"路径上链路 ({u}, {v}) 处无共同可用波长（考虑已分配波长）"

        # 检查是否有足够的可用波长
        if len(available_wavelengths) < n_wave:
            return False, [], f"路径上只有{len(available_wavelengths)}个共同可用波长，需要{n_wave}个，波长资源不足"

        # 选择前n_wave个波长（按ID排序）
        selected_wavelengths = sorted(list(available_wavelengths))[:n_wave]

        LOGGER.debug(f"路径 {path} 成功选择波长: {selected_wavelengths}")
        return True, selected_wavelengths, ""


# ========== 三类划分核心功能类 ==========

class LocalPerformanceCalculator:
    """
    局域性能计算器
    负责分布式训练中的局域计算性能指标
    """

    def __init__(self):
        self.BW_v_intra = DEFAULT_BW_INTRA
        self.BW_v_inter = DEFAULT_BW_INTER
        self._gpu_manager = GPUManager()
        self._data_type_util = DataTypeUtil()

    def _get_bytes_per_param(self, data_type: Optional[str]) -> int:
        """获取数据类型对应的字节数"""
        return self._data_type_util.get_bytes_per_param(data_type)

    def calculate_flops_mb(
        self,
        model_params: float,
        tensor_parallel: int,
        pipeline_parallel: int,
        micro_batch_size: int,
        sequence_length: int) -> float:
        """计算微批次的FLOPs"""
        return (6 * model_params) / (tensor_parallel * pipeline_parallel) * micro_batch_size * sequence_length

    def calculate_local_comp_time(
        self,
        mini_batch_size: int,
        micro_batch_size: int,
        flops_mb: float,
        gpu_flops: float) -> float:
        """计算单次迭代的局域计算时间"""
        t_cp_mb = flops_mb / (gpu_flops * 1e12)
        return (mini_batch_size / micro_batch_size) * t_cp_mb

    def calculate_dp_comm_time(
        self,
        model_params: float,
        data_type: str,
        tensor_parallel: int,
        pipeline_parallel: int,
        data_parallel: int,
        bw_inter: float) -> float:
        """计算数据并行通信时间"""
        bytes_per_param = self._get_bytes_per_param(data_type)
        numerator = model_params * bytes_per_param * 2 * (data_parallel - 1)
        denominator = tensor_parallel * pipeline_parallel * data_parallel * bw_inter * 1e12
        return numerator / denominator

    def calculate_tp_comm_time(
        self,
        mini_batch_size: int,
        micro_batch_size: int,
        layers: int,
        tensor_parallel: int,
        sequence_length: int,
        hidden_dim: int,
        data_type: str,
        bw_intra: float) -> float:
        """计算张量并行通信时间"""
        bytes_per_param = self._get_bytes_per_param(data_type)
        numerator = layers * 4 * micro_batch_size * sequence_length * hidden_dim * bytes_per_param * 2 * (tensor_parallel - 1)
        denominator = tensor_parallel * bw_intra * 1e12
        t_tp_mb = numerator / denominator
        return (mini_batch_size / micro_batch_size) * t_tp_mb

    def calculate_pp_comm_time(
        self,
        mini_batch_size: int,
        micro_batch_size: int,
        sequence_length: int,
        hidden_dim: int,
        data_type: str,
        bw_inter: float) -> float:
        """计算流水线并行通信时间"""
        bytes_per_param = self._get_bytes_per_param(data_type)
        numerator = 2 * micro_batch_size * sequence_length * hidden_dim * bytes_per_param
        denominator = bw_inter * 1e12
        t_pp_mb = numerator / denominator
        return (mini_batch_size / micro_batch_size) * t_pp_mb

    def calculate_local_comm_time(self, t_dp: float, t_tp: float, t_pp: float) -> float:
        """计算局域通信时间"""
        return t_dp + t_tp + t_pp

    def calculate_local_bubble_time(
        self,
        pipeline_parallel: int,
        flops_mb: float,
        gpu_flops: float,
        local_tp_comm_time: float,
        local_pp_comm_time: float,
        num_micro_batches: int
    ) -> float:
        """
        计算局域气泡时间

        封装t_cp_mb、t_tp_mb、t_pp_mb的计算逻辑

        Args:
            pipeline_parallel: 流水线并行度
            flops_mb: 微批次的FLOPs
            gpu_flops: GPU算力(TFLOPs)
            local_tp_comm_time: 局域张量并行通信时间
            local_pp_comm_time: 局域流水线并行通信时间
            num_micro_batches: 微批次数量

        Returns:
            float: 局域气泡时间
        """
        # 计算单个微批次的各项时间
        t_cp_mb = flops_mb / (gpu_flops * 1e12)  # 单个微批次的计算时间
        t_tp_mb = local_tp_comm_time / num_micro_batches  # 单个微批次的张量并行通信时间
        t_pp_mb = local_pp_comm_time / num_micro_batches  # 单个微批次的流水线并行通信时间

        LOGGER.debug(f"单个微批次的计算时间: {t_cp_mb}")
        LOGGER.debug(f"单个微批次的张量并行通信时间: {t_tp_mb}")
        LOGGER.debug(f"单个微批次的流水线并行通信时间: {t_pp_mb}")

        return (pipeline_parallel - 1) * (t_cp_mb + t_tp_mb + t_pp_mb)

    def get_gpu_flops(self, gpu_model: str, precision: str = "fp16") -> float:
        """获取GPU算力"""
        LOGGER.debug(f"获取GPU算力: {gpu_model}, 精度: {precision}")
        flops = self._gpu_manager.get_flops(gpu_model, precision)
        LOGGER.debug(f"归一化GPU型号: {self._gpu_manager.normalize_model_name(gpu_model)}, 算力: {flops}")
        return flops

    def _validate_estimate_params(self, **params) -> bool:
        """验证资源估算参数"""
        required_params = ['model_params', 'tokens', 'sequence_length',
                          'T_dead', 'tensor_parallel', 'pipeline_parallel',
                          'global_batch_size', 'micro_batch_size', 'epochs']
        return all(params.get(p) is not None and params.get(p) > 0 for p in required_params)

    def _calculate_iterations(self, tokens: float, global_batch_size: int, sequence_length: int) -> int:
        """计算迭代次数"""
        tokens_count = int(tokens * 1e12)
        return tokens_count // (global_batch_size * sequence_length)

    def _calculate_speedup_factor(self, min_total_comp_time: float, T_dead: float) -> float:
        """计算所需的加速因子"""
        return min_total_comp_time / T_dead

    def estimate_resource_bound(self, event, T_dead: float, data_parallel: int = 1) -> Tuple[int, int]:
        """
        估算资源下界

        基于动态计算的global_batch_size进行资源估算：
        global_batch_size = mini_batch_size × data_parallel

        Args:
            event: 包含任务配置参数的事件对象
            T_dead: 截止时间(秒)
            data_parallel: 数据并行度，用于动态计算global_batch_size，默认为1

        Returns:
            Tuple[int, int]: (最小GPU数量, 最小数据并行度)
        """
        try:
            # 从event中提取配置（传入data_parallel以动态计算global_batch_size）
            config = extract_event_config(event, data_parallel=data_parallel)

            model_params = config['model_params']
            tokens = config['tokens']
            sequence_length = config['sequence_length']
            tensor_parallel = config['tensor_parallel']
            pipeline_parallel = config['pipeline_parallel']
            epochs = config.get('epochs', 1)
            precision = config.get('precision', 'fp16')
            gpu_model = 'a100'  # 默认使用A100
            mini_batch_size = config['mini_batch_size']
            micro_batch_size = config['micro_batch_size']
            global_batch_size = config['global_batch_size']  # 动态计算的值

            # 验证必需参数
            if not all([model_params, tokens, sequence_length, T_dead,
                       tensor_parallel, pipeline_parallel, mini_batch_size, micro_batch_size]):
                LOGGER.warning("为estimate_resource_bound提供的参数无效，使用默认值")
                return tensor_parallel * pipeline_parallel, 1

            # 基于动态global_batch_size计算迭代次数
            iterations = self._calculate_iterations(tokens, global_batch_size, sequence_length)
            LOGGER.debug(f"估算资源下界: global_batch_size={global_batch_size}, 迭代次数={iterations}")

            gpu_flops = self.get_gpu_flops(gpu_model, precision)
            model_params_actual = model_params * 1e9
            flops_mb = self.calculate_flops_mb(
                model_params_actual, tensor_parallel, pipeline_parallel,
                micro_batch_size, sequence_length
            )
            # 使用mini_batch_size计算本地计算时间
            local_comp_time = self.calculate_local_comp_time(
                mini_batch_size, micro_batch_size, flops_mb, gpu_flops
            )
            min_iter_time = local_comp_time
            min_total_comp_time = min_iter_time * iterations * epochs
            speedup_factor = self._calculate_speedup_factor(min_total_comp_time, T_dead)
            min_data_parallel = max(1, int(speedup_factor) + 1)
            min_gpu_count = tensor_parallel * pipeline_parallel * min_data_parallel

            return min_gpu_count, min_data_parallel

        except Exception as e:
            LOGGER.error(f"Error in estimate_resource_bound: {e}")
            # 返回默认值
            return 1, 1

    def calculate_local_execution_time(self, event, dc_id, data_parallel, local_dp=None, gpu_model=None):
        """
        计算单节点独立完成任务的执行时间和相关局域计算指标

        Args:
            event: 包含任务配置参数的事件对象
            dc_id: 选择的数据中心
            data_parallel: 总数据并行度（用于计算mini-batch大小）
            local_dp: 本地DP组数量（用于计算DC内部通信），默认为None（使用data_parallel）

        Returns:
            dict: 包含以下键的字典
                t_sol: 单节点独立完成任务的执行时间
                mini_batch_size: mini-BS大小
                num_micro_batches: 微批次数量
                flops_mb: 微批次的FLOPs
                local_comp_time: 局域计算时间
                local_comm_time: 局域通信时间
                local_bubble_time: 局域气泡时间
        """
        from common_utils import extract_event_config

        # 本地DP组数量，用于DC内部通信计算
        local_dp = local_dp if local_dp is not None else data_parallel
        # 从事件配置中获取参数（预计算批次值）
        config = extract_event_config(event, data_parallel=data_parallel)
        layers = config['layers']
        hidden_dim = config['hidden_dim']
        sequence_length = config['sequence_length']
        data_type = config['precision']
        gpu_model = gpu_model or 'NVIDIA_A100'
        micro_batch_size = config['micro_batch_size']
        tokens = config['tokens']
        pipeline_parallel = config['pipeline_parallel']
        tensor_parallel = config['tensor_parallel']
        model_params = config['model_params']

        # 使用预计算的批次值
        mini_batch_size = config['mini_batch_size']
        num_micro_batches = config['num_micro_batches']

        # 输出调试信息
        LOGGER.debug(f"模型层数: {layers}")
        LOGGER.debug(f"隐藏维度: {hidden_dim}")
        LOGGER.debug(f"序列长度: {sequence_length}")
        LOGGER.debug(f"数据类型: {data_type}")
        LOGGER.debug(f"微批次大小: {micro_batch_size}")
        LOGGER.debug(f"mini-BS: {mini_batch_size}, 微批次数量: {num_micro_batches}")
        LOGGER.debug(f"训练token数量: {tokens}T")
        LOGGER.debug(f"流水线并行度: {pipeline_parallel}")
        LOGGER.debug(f"张量并行度: {tensor_parallel}")
        LOGGER.debug(f"模型参数量: {model_params}B")

        # 单位转换
        model_params *= 1e9  # 从B转换为实际数量

        # 获取GPU算力
        gpu_flops = self.get_gpu_flops(gpu_model, data_type)
        LOGGER.debug(f"GPU算力: {gpu_flops}")

        # 计算微批次的FLOPs
        flops_mb = self.calculate_flops_mb(model_params, tensor_parallel, pipeline_parallel,
                                       micro_batch_size, sequence_length)
        LOGGER.debug(f"微批次的FLOPs: {flops_mb}")

        # 计算局域计算时间
        local_comp_time = self.calculate_local_comp_time(mini_batch_size, micro_batch_size,
                                                                      flops_mb, gpu_flops)
        LOGGER.debug(f"局域计算时间: {local_comp_time}")

        # 获取带宽参数（使用类中定义的默认值）
        bw_inter = self.BW_v_inter  # 机间带宽 (TB/s)
        bw_intra = self.BW_v_intra   # 机内带宽 (TB/s)
        LOGGER.debug(f"机间带宽: {bw_inter}, 机内带宽: {bw_intra}")

        # 计算单DC完成任务的局域通信时间（使用local_dp计算DC内部通信）
        local_dp_comm_time = self.calculate_dp_comm_time(model_params, data_type,
                                                                     tensor_parallel, pipeline_parallel,
                                                                     local_dp, bw_inter)
        LOGGER.debug(f"总数据并行度: {data_parallel}, 本地DP组数: {local_dp}, 局域数据并行通信时间: {local_dp_comm_time}")
        local_tp_comm_time = self.calculate_tp_comm_time(mini_batch_size, micro_batch_size,
                                                                     layers, tensor_parallel,
                                                                     sequence_length, hidden_dim,
                                                                     data_type, bw_intra)
        LOGGER.debug(f"张量并行度: {tensor_parallel}, 局域张量并行通信时间: {local_tp_comm_time}")

        local_pp_comm_time = self.calculate_pp_comm_time(mini_batch_size, micro_batch_size,
                                                                     sequence_length, hidden_dim,
                                                                     data_type, bw_inter)
        LOGGER.debug(f"流水线并行度: {pipeline_parallel}, 局域流水线并行通信时间: {local_pp_comm_time}")

        local_comm_time = self.calculate_local_comm_time(local_dp_comm_time, local_tp_comm_time, local_pp_comm_time)
        LOGGER.debug(f"局域通信时间: {local_comm_time}")

        # 计算局域气泡时间（使用封装后的方法）
        local_bubble_time = self.calculate_local_bubble_time(
            pipeline_parallel, flops_mb, gpu_flops,
            local_tp_comm_time, local_pp_comm_time, num_micro_batches
        )
        LOGGER.debug(f"局域气泡时间: {local_bubble_time}")

        # 计算单节点独立完成任务的执行时间
        t_sol = local_comp_time + local_comm_time + local_bubble_time

        # 将返回值封装为字典（只包含计算得出的关键参数）
        result = {
            't_sol': t_sol,
            'mini_batch_size': mini_batch_size,
            'num_micro_batches': num_micro_batches,
            'flops_mb': flops_mb,
            'local_comp_time': local_comp_time,
            'local_comm_time': local_comm_time,
            'local_bubble_time': local_bubble_time,
        }

        return result


class CrossDomainCalculator:
    """
    跨域计算计算器
    负责跨域通信相关的计算，包括Level指标、Cost计算、跨域通信时间
    """

    def __init__(self):
        self._data_type_util = DataTypeUtil()

    def calculate_level(self, t_save: float, t_extra: float, cost_c: float = 0.0) -> float:
        """
        计算Level值

        Args:
            t_save: 平均节省的计算时间
            t_extra: 跨域额外开销（通信时间 + 气泡时间）
            cost_c: 总代价 C(V_co) = Σ(n_wave * |path|)

        Returns:
            float: Level值
        """
        denominator = t_extra + cost_c
        if denominator == 0:
            return float('inf')
        return t_save / denominator

    def _get_wavelength_capacity_from_graph(self, graph, paths: Dict[Tuple[int, int], List[int]]) -> float:
        """
        从图中获取波长容量

        Args:
            graph: networkx图对象
            paths: 通信路径字典

        Returns:
            float: 波长容量（Gbps）
        """
        if not paths:
            return 100.0  # 默认值

        # 获取第一条路径的前两个节点
        first_path = next(iter(paths.values()), None)
        if first_path and len(first_path) >= 2:
            u, v = first_path[0], first_path[1]
            if graph.has_edge(u, v):
                wavelength_channels = graph.edges[u, v].get('wavelength_channels', [])
                for channel in wavelength_channels:
                    if hasattr(channel, 'status') and channel.status == 0:
                        bandwidth_str = channel.bandwidth if hasattr(channel, 'bandwidth') else '100G'
                        return float(bandwidth_str.replace('G', ''))
        return 100.0  # 默认值

    def calculate_cost_c(
        self,
        paths: Dict[Tuple[int, int], List[int]],
        n_wave: int = 1) -> float:
        """
        计算总代价 C(V_co) = Σ(n_wave * |path|)

        Args:
            paths: 路径字典
            n_wave: 每个路径使用的波长数

        Returns:
            float: 总代价 C(V_co)
        """
        if not paths:
            return 0.0

        total_cost = 0.0
        unique_paths = set()

        for src, dst in paths:
            if (dst, src) not in unique_paths:
                path = paths[(src, dst)]
                path_length = len(path) - 1
                total_cost += n_wave * path_length
                unique_paths.add((src, dst))

        return total_cost*LEVEL_COST_COEFFICIENT 

    def calculate_cross_domain_comm_time(
        self,
        model_params: float,
        data_type: str,
        num_dcs: int,
        aggregate_bw: float,
        path_length: float) -> float:
        """
        计算跨域单路径DP通信时间

        Args:
            model_params: 模型参数量 (Φ)
            data_type: 数据类型 (fp_x)
            num_dcs: 数据中心数量 (|V_co|)
            aggregate_bw: 聚合总带宽 (BW_(c_j))，单位：Gbps
            path_length: 路径总长度，单位：米

        Returns:
            float: 跨域单路径DP通信时间 (t_(c_j)^dp)
        """
        bytes_per_param = self._data_type_util.get_bytes_per_param(data_type)

        # 单位转换：model_params 单位是 B（十亿），需要转换为实际数量
        model_params_actual = model_params * 1e9

        # 计算数据传输时间（单位：秒）
        # data_size_gb: 数据量，单位GB
        # aggregate_bw: 带宽，单位Gbps，需要转换为GB/s (1 Gbps = 0.125 GB/s)
        data_size_gb = model_params_actual * bytes_per_param / (1024**3)
        aggregate_bw_gbps = aggregate_bw / 8  # Gbps -> GB/s
        transfer_time = data_size_gb / (aggregate_bw_gbps * num_dcs)
        LOGGER.debug(f"数据量: {data_size_gb:.2f} GB, 聚合带宽: {aggregate_bw} Gbps = {aggregate_bw_gbps} GB/s")
        LOGGER.debug(f"数据传输时间: {transfer_time:.4f} 秒")

        # 计算传播延迟（单位：秒）
        propagation_delay = path_length / SPEED_OF_LIGHT_FIBER
        LOGGER.debug(f"传播延迟: {propagation_delay:.6f} 秒")

        # 计算总通信时间
        total_comm_time = transfer_time + propagation_delay
        LOGGER.debug(f"总通信时间: {total_comm_time:.4f} 秒")

        return total_comm_time

    def calculate_performance_metrics(self, event, selected_dcs, data_parallel, n_wave, paths, gpus_per_dc, graph, local_perf_calculator):
        """
        计算性能指标，包括 JCT 和 Level

        Args:
            event: 包含任务配置参数的事件对象
            selected_dcs: 选择的数据中心
            data_parallel: 总的数据并行度
            n_wave: 波长数量
            paths: 通信路径
            gpus_per_dc: 每个数据中心分配的GPU数量
            graph: networkx图对象，用于获取路径长度
            local_perf_calculator: LocalPerformanceCalculator实例，用于计算本地执行时间

        Returns:
            dict: 包含各种性能指标的字典
        """
        from common_utils import extract_event_config

        # 从event中提取配置参数（data_parallel是全局DP）
        config = extract_event_config(event, data_parallel=data_parallel)
        model_params = config['model_params']
        pipeline_parallel = config['pipeline_parallel']
        tensor_parallel = config['tensor_parallel']
        data_type = config['precision']
        tokens = config['tokens']
        global_batch_size = config['global_batch_size']  # 动态计算的值
        sequence_length = config['sequence_length']

        # 计算迭代次数（基于动态计算的global_batch_size）
        # 迭代次数随data_parallel变化：DP越大，global_batch_size越大，迭代次数越少
        tokens_count = int(tokens * 1e12)
        iterations = tokens_count // (global_batch_size * sequence_length)
        LOGGER.debug(f"动态计算的global_batch_size: {global_batch_size}, 迭代次数: {iterations}")

        # 计算每个数据中心内部的DP组数量
        dp_groups_per_dc = []
        if gpus_per_dc:
            unit = pipeline_parallel * tensor_parallel
            for dc_id in selected_dcs:
                if dc_id in gpus_per_dc:
                    # 计算该数据中心内部的DP组数量
                    dp_group = gpus_per_dc[dc_id] // unit
                    dp_groups_per_dc.append(dp_group)
        LOGGER.debug(f"每个数据中心内部的DP组数量: {dp_groups_per_dc}")


        #计算多节点跨域单次迭代执行时间
        t_exe=0
        t_comm=0
        t_bubble=0 #恒为0
        t_sol_totals=[]
        LOGGER.debug(f"选择的数据中心: {selected_dcs}")
        for dc_id, dp_group in zip(selected_dcs, dp_groups_per_dc):
            #计算任务在一个节点独立完成的时间（单次迭代）
            LOGGER.debug(f"节点 {dc_id} 内部的DP组数量: {dp_group}")
            # 独立执行时：data_parallel = local_dp = dp_group
            t_sol = local_perf_calculator.calculate_local_execution_time(event, dc_id, dp_group, dp_group)['t_sol']
            LOGGER.debug(f"节点 {dc_id} 独立完成任务的时间: {t_sol}")
            config = extract_event_config(event, data_parallel=dp_group)
            global_batch_size = config['global_batch_size']  # 动态计算的值
            iterations_sol = tokens_count // (global_batch_size * sequence_length)
            LOGGER.debug(f"动态计算的global_batch_size: {global_batch_size}, 迭代次数: {iterations_sol}")
            t_sol_total = t_sol * iterations_sol
            t_sol_totals.append(t_sol_total)
            LOGGER.debug(f"节点 {dc_id} 独立完成任务的总时间: {t_sol_total}")

            # 协作执行时：data_parallel=总DP, local_dp=dp_group（该DC内部的DP组数）
            node_exe_time = local_perf_calculator.calculate_local_execution_time(event, dc_id, data_parallel, dp_group)['t_sol']
            LOGGER.debug(f"节点 {dc_id} 协作完成任务的时间: {node_exe_time}")
            # 找最慢的节点作为跨域执行时间
            if node_exe_time > t_exe:
                t_exe = node_exe_time
        t_exe_total=t_exe*iterations
        LOGGER.debug(f"跨域执行总时间: {t_exe_total}")

        # 计算节省的时间
        t_save = sum([t_sol_total-t_exe_total for t_sol_total in t_sol_totals]) / len(selected_dcs)
        LOGGER.debug(f"跨域节省时间: {t_save}")
        # 计算跨域通信时间
        if len(selected_dcs) > 1:
            # 从图中获取实际的波长容量（Gbps）
            wavelength_capacity = self._get_wavelength_capacity_from_graph(graph, paths)
            aggregate_bw = n_wave * wavelength_capacity
            LOGGER.debug(f"波长容量: {wavelength_capacity} Gbps, 跨域聚合带宽: {aggregate_bw} Gbps")

            # 计算单路径通信时间
            LOGGER.debug(f"跨域路径: {paths}")
            # 计算实际路径长度（米）
            path_lengths = []

            # 实现路径去重，确保往返路径仅被计算一次
            seen_paths = set()
            unique_paths = []

            # 遍历所有可用路径
            for (src, dst), path in paths.items():
                # 生成路径键，确保A→B和B→A被视为同一路径
                path_key = tuple(sorted((src, dst)))
                if path_key not in seen_paths:
                    seen_paths.add(path_key)
                    unique_paths.append((src, dst, path))

            LOGGER.debug(f"去重后的唯一路径: {unique_paths}")

            # 计算每个唯一路径的长度
            for src, dst, path in unique_paths:
                # 计算路径总长度（米）
                total_length = 0
                for j in range(len(path) - 1):
                    u, v = path[j], path[j+1]
                    if graph.has_edge(u, v):
                        # 从图中获取链路长度（公里），转换为米
                        length_km = graph.edges[u, v].get('length_km', 100)
                        total_length += length_km * 1000  # 转换为米
                        LOGGER.debug(f"链路 ({u}, {v}) 长度: {length_km} km")
                path_lengths.append(total_length)
                LOGGER.debug(f"路径 {src} -> {dst} 总长度: {total_length} 米")

            LOGGER.debug(f"跨域路径长度: {path_lengths} 米")

            # 计算每个路径的通信时延
            path_comm_times = []
            for path_length in path_lengths:
                # 计算该路径的单次数据跨域通信时延
                comm_time = self.calculate_cross_domain_comm_time(model_params, data_type, len(selected_dcs), aggregate_bw, path_length)
                path_comm_times.append(comm_time)
                LOGGER.debug(f"路径长度 {path_length} 米的通信时延: {comm_time} 秒")

            LOGGER.debug(f"所有路径的通信时延: {path_comm_times} 秒")

            # 基于木桶效应原理，选取最大值
            if path_comm_times:
                max_comm_time = max(path_comm_times)
                LOGGER.debug(f"最大单路径单次通信时延: {max_comm_time} 秒")

                # 计算跨域通信时间
                t_comm = 2 * (len(selected_dcs) - 1) * max_comm_time
                LOGGER.debug(f"最终跨域通信时间: {t_comm} 秒")
        else:
            t_comm = 0

        # 计算跨域额外时间
        t_extra =t_comm+t_bubble
        LOGGER.debug(f"单次迭代跨域额外时间: {t_extra}")

        t_extra_total=t_extra*iterations
        LOGGER.debug(f"任务跨域额外时间总时间: {t_extra_total}")

        # 计算代价
        cost_c = 0
        if paths:
            cost_c = self.calculate_cost_c(paths, n_wave)
        LOGGER.debug(f"任务跨域代价: {cost_c}")

        # 计算Level值
        level = self.calculate_level(t_save, t_extra_total, cost_c)
        # 计算JCT
        jct = t_exe_total+t_extra_total

        # 返回结果
        return {
            'cost_c': cost_c,
            'level': level,
            'jct': jct,
        }


class NetworkResourceCalculator:
    """
    网络资源计算器
    负责路径计算、瓶颈带宽计算
    """

    def __init__(self, G):
        self.G = G

    def calculate_all_pair_paths(self, dcs: List[int]) -> Dict[Tuple[int, int], List[int]]:
        """计算数据中心集合内部所有节点对的路径"""
        paths = {}
        for i in range(len(dcs)):
            for j in range(i + 1, len(dcs)):
                src = dcs[i]
                dst = dcs[j]
                try:
                    path = self.find_path(src, dst)
                    paths[(src, dst)] = path
                    paths[(dst, src)] = path[::-1]
                except Exception as e:
                    LOGGER.warning(f"Failed to find path between {src} and {dst}: {e}")
                    return {}
        return paths

    def calculate_bottleneck_bw(self, paths: Dict[Tuple[int, int], List[int]]) -> float:
        """计算瓶颈带宽"""
        if not paths:
            return 0.0

        min_bw = float('inf')
        for path in paths.values():
            path_bw = min(
                self.G.edges[u, v]['bandwidth_available']
                for u, v in zip(path[:-1], path[1:])
            )
            if path_bw < min_bw:
                min_bw = path_bw

        return min_bw

    def _get_available_nodes(self) -> List:
        """获取所有可用节点"""
        return [
            n for n in self.G.nodes
            if not self.G.nodes[n].get('failed', False)
        ]

    def _get_available_edges(self) -> List[Tuple]:
        """获取所有可用边"""
        return [
            (u, v) for u, v in self.G.edges
            if not self.G.edges[u, v].get('failed', False)
        ]

    def _filter_nodes_by_type(self, nodes: List) -> Tuple[List, List]:
        """将节点分为计算节点和网络节点"""
        compute_nodes = [
            n for n in nodes
            if self.G.nodes[n].get('type') == 'datacenter'
        ]
        network_nodes = [
            n for n in nodes
            if self.G.nodes[n].get('type') != 'datacenter'
        ]
        return compute_nodes, network_nodes

    def find_path(self, src, dst):
        """找到从src到dst的最短路径"""
        available_nodes = self._get_available_nodes()
        available_edges = self._get_available_edges()
        compute_nodes, network_nodes = self._filter_nodes_by_type(available_nodes)

        # 构建子图
        if src in compute_nodes and dst in compute_nodes:
            intermediate_nodes = network_nodes + [src, dst]
            H_edges = [
                (u, v) for u, v in available_edges
                if u in intermediate_nodes and v in intermediate_nodes
            ]
            H = self.G.edge_subgraph(H_edges).copy()
            H = H.subgraph(intermediate_nodes)
        else:
            H = self.G.edge_subgraph(available_edges).copy()
            H = H.subgraph(available_nodes)

        path = nx.shortest_path(H, src, dst)
        return path


# ========== 事件配置提取工具函数 ==========

def extract_event_config(event, validate=True, data_parallel=None):
    """
    从event对象中提取所有配置参数

    参数关系说明：
    - mini_batch_size: 固定配置值，每个数据并行组的批次大小
    - micro_batch_size: 固定配置值，每个微批次的大小
    - global_batch_size: 动态计算值 = mini_batch_size × data_parallel
    - num_micro_batches: 预计算值 = mini_batch_size // micro_batch_size

    Args:
        event: 包含模型配置和训练配置的事件对象
        validate: 是否验证必需字段
        data_parallel: 数据并行度，用于动态计算global_batch_size

    Returns:
        dict: 包含所有配置参数的字典

    Raises:
        KeyError: 当validate=True且缺少必需字段时
    """
    model_config = event.model_config
    training_config = event.training_config
    parallelism = model_config.get('parallelism', {})

    # 获取训练配置参数（mini_batch_size 和 micro_batch_size 是固定值）
    mini_batch_size = training_config.get('mini_batch_size')
    micro_batch_size = training_config.get('micro_batch_size')

    # 根据 data_parallel 动态计算 global_batch_size
    global_batch_size = None
    num_micro_batches = None
    if data_parallel is not None and mini_batch_size is not None and micro_batch_size is not None:
        global_batch_size = mini_batch_size * data_parallel
        num_micro_batches = mini_batch_size // micro_batch_size

    config = {
        # 模型配置
        'model_params': model_config.get('model_params'),
        'layers': model_config.get('layers'),
        'hidden_dim': model_config.get('hidden_dim'),
        'model_name': model_config.get('model_name'),

        # 并行度配置
        'tensor_parallel': parallelism.get('tensor_parallel'),
        'pipeline_parallel': parallelism.get('pipeline_parallel'),
        'data_parallel': parallelism.get('data_parallel'),

        # 训练配置
        'tokens': training_config.get('tokens'),
        'sequence_length': training_config.get('sequence_length'),
        'precision': training_config.get('precision'),
        'epochs': training_config.get('epochs'),
        'learning_rate': training_config.get('learning_rate'),

        # 批次相关配置（mini_batch_size 和 micro_batch_size 是固定值）
        'mini_batch_size': mini_batch_size,
        'micro_batch_size': micro_batch_size,

        # 动态计算的值
        'global_batch_size': global_batch_size,
        'num_micro_batches': num_micro_batches,
    }

    if validate:
        required_fields = ['model_params', 'tokens', 'mini_batch_size', 'sequence_length']
        for field in required_fields:
            if config[field] is None:
                raise KeyError(f"配置中缺少必需的字段: {field}")

    return config


# ========== 导出控制 ==========

__all__ = [
    # 常量
    'DATA_TYPE_BYTES',
    'GPU_PERFORMANCE_MAP',
    'EVENT_TYPE_NAMES',
    'SPEED_OF_LIGHT_FIBER',
    'LEVEL_COST_COEFFICIENT',
    'DEFAULT_GPU_FLOPS',
    'DEFAULT_BW_INTRA',
    'DEFAULT_BW_INTER',
    # 工具函数
    'extract_event_config',
    # 工具类
    'DataTypeUtil',
    'GPUManager',
    'WavelengthSelector',
    # 三类核心功能类
    'LocalPerformanceCalculator',
    'CrossDomainCalculator',
    'NetworkResourceCalculator',
]
