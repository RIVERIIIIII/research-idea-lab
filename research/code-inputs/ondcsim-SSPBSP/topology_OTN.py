import yaml
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from math import radians, sin, cos, sqrt, atan2
import networkx as nx
from result import LOGGER
from common_utils import GPU_PERFORMANCE_MAP

@dataclass
class FGOTNSlots:
    total_slots: int
    available_slots: int
    occupied_slots: int

@dataclass
class ODU0:
    odu0_id: int
    bandwidth: str
    status: int
    fg_otn_slots: FGOTNSlots

    support_fg_otn: bool

@dataclass
class WavelengthChannel:
    wavelength_id: int
    bandwidth: str
    status: int
    odu0_list: List[ODU0]

@dataclass
class Node:
    id: int
    name: str
    type: str
    wavelength_num: int
    add_drop_capability: int
    fg_otn_support: bool
    oduk_support: bool
    wavelength_support: bool
    lat: float = 0.0
    lon: float = 0.0
    datacenter_id: int = 0

@dataclass
class Link:
    id: int
    src: int
    dst: int
    type: str
    length_km: float
    attenuation: float
    dispersion: float
    osnr: float
    total_wavelengths: int
    fg_otn_support: bool
    oduk_support: bool
    wavelength_support: bool
    wavelength_channels: List[WavelengthChannel]
    used_wavelengths: int = 0

@dataclass
class Storage:
    type: str
    capacity_GiB: int
    free_GiB: int
    bandwidth_GiBps: int

@dataclass
class Memory:
    type: str
    capacity_GiBps: int
    free_GiBps: int
    bandwidth_GiBps: int

@dataclass
class Server:
    GPU_num: int
    GPU_type: str
    storage: Storage
    memory: Memory

@dataclass
class Network:
    type: str
    topology: str
    bw_intra: float = 1.8  # 机内带宽 (TB/s) - NVLink 5.0
    bw_inter: float = 0.1   # 机间带宽 (TB/s) - 800Gb/s

@dataclass
class BackgroundTasks:
    enabled: bool = False
    gpu_min_ratio: float = 0.0
    gpu_max_ratio: float = 0.0
    random_seed: int = None

@dataclass
class Datacenter:
    type: str
    id: int
    name: str
    server_num: int
    server: Server
    network: Network
    co_location_node_id: int = 0
    background_tasks: BackgroundTasks = None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    使用 Haversine 公式计算两点间的地球表面距离

    Args:
        lat1: 起点纬度（度）
        lon1: 起点经度（度）
        lat2: 终点纬度（度）
        lon2: 终点经度（度）

    Returns:
        float: 两点间的距离（公里）
    """
    R = 6371  # 地球平均半径（公里）

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


class TopologyManager:
    """
    Manages the network topology, including loading from YAML, building the networkx graph,
    and initializing all resource attributes for nodes and edges.
    Also provides methods to load service and simulator configuration.
    """
    
    def __init__(self, topology_file: str, datacenter_file: str):
        self.topology_file = topology_file
        self.datacenter_file = datacenter_file
        self.nodes = []
        self.links = []
        self.dc_to_otn_links = []
        self.datacenters = []
        self.G = nx.Graph()
        self.load_topology()
        self.load_datacenters()
        self.build_graph()



    def load_topology(self):
        """
        加载网络拓扑配置
        """
        try:
            with open(self.topology_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                LOGGER.error(f"拓扑文件 {self.topology_file} 为空")
                raise ValueError(f"拓扑文件 {self.topology_file} 为空")
            
            # 验证必要字段
            if 'nodes' not in data:
                LOGGER.error(f"拓扑文件 {self.topology_file} 缺少 'nodes' 字段")
                raise ValueError(f"拓扑文件 {self.topology_file} 缺少 'nodes' 字段")
            
            if 'links' not in data:
                LOGGER.error(f"拓扑文件 {self.topology_file} 缺少 'links' 字段")
                raise ValueError(f"拓扑文件 {self.topology_file} 缺少 'links' 字段")
            
            # 加载节点
            self.nodes = []
            for node_data in data['nodes']:
                try:
                    # 处理 datacenter 字段，兼容旧格式
                    datacenter_id = node_data.pop('datacenter', 0)
                    node = Node(**node_data)
                    node.datacenter_id = datacenter_id
                    self.nodes.append(node)
                except Exception as e:
                    LOGGER.error(f"加载节点时出错: {node_data}, 错误: {e}")
                    raise
            
            # 创建节点ID到节点对象的映射，用于后续计算链路长度
            self.node_map = {node.id: node for node in self.nodes}

            # 处理links和dc_to_otn_links
            self.links = self._process_links(data.get('links', []), '链路')
            LOGGER.info(f"成功加载 {len(self.nodes)} 个节点和 {len(self.links)} 条链路")

            self.dc_to_otn_links = self._process_links(data.get('dc_to_otn_links', []), '数据中心到OTN节点链路')
            if self.dc_to_otn_links:
                LOGGER.info(f"成功加载 {len(self.dc_to_otn_links)} 条数据中心到OTN节点链路")
        except FileNotFoundError:
            LOGGER.error(f"拓扑文件 {self.topology_file} 不存在")
            raise
        except yaml.YAMLError as e:
            LOGGER.error(f"解析拓扑文件 {self.topology_file} 时出错: {e}")
            raise
        except Exception as e:
            LOGGER.error(f"加载拓扑文件 {self.topology_file} 时出错: {e}")
            raise



    def _process_links(self, links_data, link_type_name):
        """
        处理链路数据，动态生成wavelength_channels和odu0_list

        Args:
            links_data: 链路数据列表
            link_type_name: 链路类型名称（用于错误日志）

        Returns:
            List[Link]: 处理后的链路对象列表
        """
        links = []
        for link_data in links_data:
            try:
                total_wavelengths = link_data.get('total_wavelengths', 80)
                link_type = link_data.get('type', 'access')
                wavelength_channels = self._create_wavelength_channels(total_wavelengths, link_type)
                link_data['wavelength_channels'] = wavelength_channels
                links.append(Link(**link_data))
            except Exception as e:
                LOGGER.error(f"加载{link_type_name}时出错: {link_data}, 错误: {e}")
                raise
        return links

    def _create_wavelength_channels(self, total_wavelengths, link_type='access'):
        """
        创建波长通道列表
        
        Args:
            total_wavelengths: 波长通道总数
            link_type: 链路类型
            
        Returns:
            List[WavelengthChannel]: 生成的波长通道列表
        """
        # 根据链路类型确定默认带宽
        if link_type == 'core':
            default_bandwidth = '400G'
        else:
            default_bandwidth = '100G'
        
        wavelength_channels = []
        for wavelength_id in range(1, total_wavelengths + 1):
            bandwidth = default_bandwidth
            
            # 根据带宽确定ODU0数量
            if bandwidth == '100G':
                odu0_count = 80
            elif bandwidth == '400G':
                odu0_count = 320
            else:
                odu0_count = 80
            
            # 动态生成odu0_list
            odu0_list = []
            for odu0_id in range(1, odu0_count + 1):
                fg_otn_slots = FGOTNSlots(
                    total_slots=119,
                    available_slots=119,
                    occupied_slots=0
                )
                
                odu0 = ODU0(
                    odu0_id=odu0_id,
                    bandwidth='1.25G',
                    status=0,
                    fg_otn_slots=fg_otn_slots,
                    support_fg_otn=not link_type == 'core'
                )
                odu0_list.append(odu0)
            
            # 创建WavelengthChannel对象
            channel = WavelengthChannel(
                wavelength_id=wavelength_id,
                bandwidth=bandwidth,
                status=0,
                odu0_list=odu0_list
            )
            wavelength_channels.append(channel)
        
        return wavelength_channels


    def load_datacenters(self):
        """
        加载数据中心配置
        """
        try:
            with open(self.datacenter_file, 'r', encoding='utf-8') as f:
                dc_data = yaml.safe_load(f)
            
            if not dc_data:
                LOGGER.error(f"数据中心文件 {self.datacenter_file} 为空")
                raise ValueError(f"数据中心文件 {self.datacenter_file} 为空")
            
            if 'datacenters' not in dc_data:
                LOGGER.error(f"数据中心文件 {self.datacenter_file} 缺少 'datacenters' 字段")
                raise ValueError(f"数据中心文件 {self.datacenter_file} 缺少 'datacenters' 字段")
            
            self.datacenters = []
            for dc_dict in dc_data['datacenters']:
                try:
                    # 处理 co_location_node 字段，兼容旧格式
                    co_location_node_id = dc_dict.pop('co_location_node', 0)
                    
                    # 创建嵌套对象
                    storage = Storage(**dc_dict['server']['storage'])
                    memory = Memory(**dc_dict['server']['memory'])
                    server = Server(
                        GPU_num=dc_dict['server']['GPU_num'],
                        GPU_type=dc_dict['server']['GPU_type'],
                        storage=storage,
                        memory=memory
                    )
                    # 从配置中读取网络参数，包括带宽信息
                    network = Network(**dc_dict['network'])
                    
                    # 解析背景任务配置
                    bg_tasks = None
                    if 'background_tasks' in dc_dict:
                        bg_config = dc_dict['background_tasks']
                        gpu_util = bg_config.get('gpu_utilization', {})
                        bg_tasks = BackgroundTasks(
                            enabled=bg_config.get('enabled', False),
                            gpu_min_ratio=gpu_util.get('min_ratio', 0.0),
                            gpu_max_ratio=gpu_util.get('max_ratio', 0.0),
                            random_seed=bg_config.get('random_seed')
                        )
                    
                    # 创建数据中心对象
                    dc = Datacenter(
                        type=dc_dict['type'],
                        id=dc_dict['id'],
                        name=dc_dict['name'],
                        server_num=dc_dict['server_num'],
                        server=server,
                        network=network,
                        background_tasks=bg_tasks
                    )
                    dc.co_location_node_id = co_location_node_id
                    self.datacenters.append(dc)
                except Exception as e:
                    LOGGER.error(f"加载数据中心时出错: {dc_dict}, 错误: {e}")
                    raise
            
            LOGGER.info(f"成功加载 {len(self.datacenters)} 个数据中心")
        except FileNotFoundError:
            LOGGER.error(f"数据中心文件 {self.datacenter_file} 不存在")
            raise
        except yaml.YAMLError as e:
            LOGGER.error(f"解析数据中心文件 {self.datacenter_file} 时出错: {e}")
            raise
        except Exception as e:
            LOGGER.error(f"加载数据中心文件 {self.datacenter_file} 时出错: {e}")
            raise


    
    def _get_gpu_performance(self, gpu_type):
        """
        获取 GPU 性能参数
        
        Args:
            gpu_type: GPU 类型
            
        Returns:
            dict: GPU 性能参数字典
        """
        if gpu_type not in GPU_PERFORMANCE_MAP:
            gpu_type = 'NVIDIA_A100'
        return GPU_PERFORMANCE_MAP[gpu_type]

    def _calculate_datacenter_resources(self, dc):
        """
        计算数据中心资源，考虑背景任务占用
        
        Args:
            dc: 数据中心对象
            
        Returns:
            dict: 数据中心资源字典
        """
        import random
        gpu_perf = self._get_gpu_performance(dc.server.GPU_type)
        
        total_gpu = dc.server.GPU_num * dc.server_num
        total_compute_capacity = total_gpu * gpu_perf['Flops_fp16']
        total_storage_capacity = dc.server.storage.capacity_GiB * dc.server_num
        
        # 计算背景任务GPU占用
        available_gpu = total_gpu
        if dc.background_tasks and dc.background_tasks.enabled:
            min_ratio = dc.background_tasks.gpu_min_ratio
            max_ratio = dc.background_tasks.gpu_max_ratio
            if max_ratio > 0:
                # 使用种子确保多次运行占用一致
                seed = dc.background_tasks.random_seed
                if seed is not None:
                    # 结合DC ID生成确定性种子，确保每个DC有不同的占用
                    random.seed(seed + dc.id)
                occupied_ratio = random.uniform(min_ratio, max_ratio)
                occupied_gpu = int(total_gpu * occupied_ratio)
                available_gpu = total_gpu - occupied_gpu
                LOGGER.info(f"DC {dc.id} ({dc.name}): 背景任务占用 {occupied_gpu} GPU ({occupied_ratio:.1%}), 可用 {available_gpu} GPU")
        
        # 计算可用算力（按GPU比例）
        compute_available = total_compute_capacity * (available_gpu / total_gpu) if total_gpu > 0 else 0
        
        return {
            'compute_capacity': total_compute_capacity,
            'compute_available': compute_available,
            'storage_capacity': total_storage_capacity,
            'storage_available': total_storage_capacity,
            'gpu_type': dc.server.GPU_type,
            'gpu_count': total_gpu,
            'available_gpu': available_gpu,
            'server_count': dc.server_num,
            'storage_type': dc.server.storage.type,
            'memory_type': dc.server.memory.type,
            'network_type': dc.network.type,
            'bw_intra': dc.network.bw_intra,
            'bw_inter': dc.network.bw_inter,
            'gpu_flops_fp8': gpu_perf['Flops_fp8'],
            'gpu_flops_fp16': gpu_perf['Flops_fp16'],
            'gpu_flops_fp32': gpu_perf['Flops_fp32'],
            'gpu_memory_GiB': gpu_perf['memory_GiB']
        }

    def build_graph(self):
        """
        构建网络拓扑图
        """
        try:
            G = self.G
            
            # 构建节点映射
            node_to_dc_map = self._build_node_mappings()
            
            # 添加节点
            self._add_network_nodes(G, node_to_dc_map)
            self._add_datacenter_nodes(G)
            
            # 添加链路
            self._add_network_links(G)
            self._add_dc_to_otn_links(G)
            
            LOGGER.info(f"成功构建网络拓扑图，包含 {G.number_of_nodes()} 个节点和 {G.number_of_edges()} 条边")
        except Exception as e:
            LOGGER.error(f"构建网络拓扑图时出错: {e}")
            raise

    def _build_node_mappings(self):
        """
        构建节点映射关系
        
        Returns:
            dict: 网络节点到数据中心的映射
        """
        node_to_dc_map = {}
        for dc in self.datacenters:
            if dc.co_location_node_id > 0:
                node_to_dc_map[dc.co_location_node_id] = dc
        return node_to_dc_map

    def _add_network_nodes(self, G, node_to_dc_map):
        """
        添加网络节点
        
        Args:
            G: 网络拓扑图
            node_to_dc_map: 网络节点到数据中心的映射
        """
        for node in self.nodes:
            node_attrs = {
                'name': node.name,
                'type': node.type,
                'fg_otn_support': node.fg_otn_support,
                'oduk_support': node.oduk_support,
                'wavelength_support': node.wavelength_support,
                'wavelength_num': node.wavelength_num,
                'add_drop_capability': node.add_drop_capability,
                'lat': node.lat,
                'lon': node.lon,
                'datacenter_id': node.datacenter_id,
                'is_co_location': False
            }
            
            # 检查是否有共址的数据中心
            if node.id in node_to_dc_map:
                dc = node_to_dc_map[node.id]
                # 添加数据中心属性到网络节点
                dc_resources = self._calculate_datacenter_resources(dc)
                node_attrs.update(dc_resources)
                node_attrs['is_co_location'] = True
            
            G.add_node(node.id, **node_attrs)

    def _add_datacenter_nodes(self, G):
        """
        添加数据中心节点
        
        Args:
            G: 网络拓扑图
        """
        for dc in self.datacenters:
            if dc.co_location_node_id == 0 or dc.co_location_node_id not in self.node_map:
                # 数据中心作为独立节点
                dc_resources = self._calculate_datacenter_resources(dc)
                dc_attrs = {
                    'name': dc.name,
                    'type': 'datacenter',
                    'is_co_location': False
                }
                dc_attrs.update(dc_resources)
                G.add_node(dc.id, **dc_attrs)

    def _add_links(self, G, links):
        """
        添加链路到网络拓扑图
        
        Args:
            G: 网络拓扑图
            links: 链路列表
        """
        for link in links:
            length_km = link.length_km
            if length_km == 0:
                src_node = self.node_map.get(link.src)
                dst_node = self.node_map.get(link.dst)
                if src_node and dst_node:
                    length_km = haversine_distance(
                        src_node.lat, src_node.lon,
                        dst_node.lat, dst_node.lon
                    )
            
            total_capacity = 0
            for channel in link.wavelength_channels:
                if channel.status == 0:
                    bandwidth_value = float(channel.bandwidth.replace('G', ''))
                    total_capacity += bandwidth_value
            
            G.add_edge(link.src, link.dst, 
                       id=link.id,
                       type=link.type,
                       fg_otn_support=link.fg_otn_support,
                       oduk_support=link.oduk_support,
                       wavelength_support=link.wavelength_support,
                       capacity_Gbps=total_capacity, 
                       latency_ms=length_km * 0.005,
                       bandwidth_capacity=total_capacity, 
                       bandwidth_available=total_capacity,
                       wavelength_channels=link.wavelength_channels, 
                       total_wavelengths=link.total_wavelengths,
                       used_wavelengths=link.used_wavelengths,
                       length_km=length_km,
                       attenuation=link.attenuation,
                       dispersion=link.dispersion,
                       osnr=link.osnr)

    def _add_network_links(self, G):
        """
        添加网络链路
        
        Args:
            G: 网络拓扑图
        """
        self._add_links(G, self.links)

    def _add_dc_to_otn_links(self, G):
        """
        添加数据中心到OTN节点的链路
        
        Args:
            G: 网络拓扑图
        """
        if self.dc_to_otn_links:
            self._add_links(G, self.dc_to_otn_links)


    def get_graph(self):
        return self.G

    def get_datacenter_ids(self):
        return [dc.id for dc in self.datacenters]

    def get_nodes(self):
        return self.nodes

    def get_links(self):
        return self.links

    def get_datacenters(self):
        return self.datacenters

    def load_service_config(self, service_yaml_path: str = 'data/service.yaml'):
        """Load service event simulation parameters from YAML."""
        with open(service_yaml_path, 'r', encoding='utf-8') as f:
            service_cfg = yaml.safe_load(f)['service']
        return service_cfg
    
    def load_failure_config(self, failure_yaml_path: str = 'data/failures.yaml'):
        """Load failure simulation parameters from YAML."""
        with open(failure_yaml_path, 'r', encoding='utf-8') as f:
            failure_cfg = yaml.safe_load(f)['failures']
        # return failure_cfg['num_failures'],failure_cfg['failure_types']['node'],failure_cfg['failure_types']['link']
        return failure_cfg
