#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTN拓扑配置文件生成器
支持生成星型、环形、网状等多种拓扑结构
"""

import yaml
import math
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ODU0Config:
    """ODU0配置类"""
    odu0_id: int
    bandwidth: str = "1.25G"
    status: int = 0  # 0-未占用，1-已占用
    consistency_id: int = 0
    support_fg_otn: bool = True
    fg_otn_slots: Dict = None
    
    def __post_init__(self):
        if self.fg_otn_slots is None:
            self.fg_otn_slots = {
                "total_slots": 119,
                "available_slots": 119,
                "occupied_slots": 0
            }


@dataclass
class WavelengthConfig:
    """波长通道配置类"""
    channel_id: int
    bandwidth: str
    status: int = 0  # 0-未占用，1-已占用
    consistency_id: int = 0
    odu0_list: List[ODU0Config] = None
    
    def __post_init__(self):
        if self.odu0_list is None:
            self.odu0_list = []
            # 根据带宽设置ODU0数量
            if self.bandwidth == "100G":
                # 100G波长包含80个ODU0
                for i in range(1, 81):
                    self.odu0_list.append(ODU0Config(odu0_id=i))
            elif self.bandwidth == "400G":
                # 400G波长包含320个ODU0
                for i in range(1, 321):
                    self.odu0_list.append(ODU0Config(odu0_id=i))
            elif self.bandwidth == "800G":
                # 800G波长包含640个ODU0
                for i in range(1, 641):
                    self.odu0_list.append(ODU0Config(odu0_id=i))
            else:
                # 默认100G
                for i in range(1, 81):
                    self.odu0_list.append(ODU0Config(odu0_id=i))


@dataclass
class NodeConfig:
    """节点配置类"""
    id: int
    name: str
    type: str  # access, aggregation, core
    wavelength_num: int
    add_drop_capability: int
    fg_otn_support: bool
    oduk_support: bool
    wavelength_support: bool
    lat: float = 0.0
    lon: float = 0.0


@dataclass
class LinkConfig:
    """链路配置类"""
    id: int
    src: int
    dst: int
    type: str  # access, aggregation, core, dc_to_otn, user_to_otn
    length_km: float
    attenuation: float = 0.22
    dispersion: float = 17.0
    osnr: float = 30.0
    total_wavelengths: int = 80
    fg_otn_support: bool = True
    oduk_support: bool = True
    wavelength_support: bool = True
    used_wavelengths: int = 0
    wavelength_channels: List[WavelengthConfig] = None
    
    def __post_init__(self):
        if self.wavelength_channels is None:
            self.wavelength_channels = []
            # 默认生成100G波长通道
            for i in range(1, self.total_wavelengths + 1):
                self.wavelength_channels.append(WavelengthConfig(channel_id=i, bandwidth="100G"))


class TopologyGenerator:
    """拓扑生成器基类"""
    
    def __init__(self, node_counts: Dict[str, int] = None, base_id: int = 2001, 
                 wavelength_num: int = 80, wavelength_bandwidth: str = "100G",
                 radius_km: float = 1000.0):
        """
        初始化拓扑生成器
        
        Args:
            node_counts: 各类型节点数量，格式: {"access": int, "aggregation": int, "core": int}
            base_id: 链路起始ID
            wavelength_num: 波长数量
            wavelength_bandwidth: 波长带宽
            radius_km: 拓扑半径(公里)
        """
        self.node_counts = node_counts or {"access": 10, "aggregation": 5, "core": 3}
        self.base_id = base_id
        self.wavelength_num = wavelength_num
        self.wavelength_bandwidth = wavelength_bandwidth
        self.radius_km = radius_km
        
        self.nodes: List[NodeConfig] = []
        self.links: List[LinkConfig] = []
        self.dc_to_otn_links: List[LinkConfig] = []
        self.user_to_otn_links: List[LinkConfig] = []
        
        # 读取数据中心信息
        self.datacenters = self.load_datacenters()
        self.users = self.generate_users()
        
    def load_datacenters(self) -> List[Dict]:
        """从文件加载数据中心信息"""
        try:
            with open("data/datacenters_OTN.yaml", "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("datacenters", [])
        except Exception as e:
            print(f"加载数据中心信息失败: {e}")
            # 返回默认数据中心
            return [
                {"id": 951, "name": "DC1"},
                {"id": 952, "name": "DC2"},
                {"id": 953, "name": "DC3"}
            ]
    
    def generate_users(self) -> List[Dict]:
        """生成用户节点信息"""
        users = []
        for i in range(1, 6):
            users.append({
                "id": 900 + i,
                "name": f"User{i}"
            })
        return users
    
    def generate_nodes(self, center_lat: float = 39.0, center_lon: float = 116.0, 
                      radius_km: float = None) -> List[NodeConfig]:
        """生成节点配置（子类需要重写此方法）"""
        raise NotImplementedError("子类必须实现此方法")
    
    def generate_links(self) -> List[LinkConfig]:
        """生成链路配置（子类需要重写此方法）"""
        raise NotImplementedError("子类必须实现此方法")
    
    def generate_dc_to_otn_links(self) -> List[LinkConfig]:
        """生成数据中心到OTN节点链路"""
        dc_links = []
        link_id = 8001  # 数据中心链路ID范围8000-8999
        
        # 选择所有access类型节点
        access_nodes = [node for node in self.nodes if node.type == "access"]
        
        if not access_nodes:
            # 如果没有access节点，选择所有节点
            access_nodes = self.nodes
        
        # 为每个数据中心生成到OTN节点的链路
        for dc in self.datacenters:
            # 随机选择一个OTN节点
            otn_node = random.choice(access_nodes)
            
            # 生成链路
            link = LinkConfig(
                id=link_id,
                src=dc["id"],
                dst=otn_node.id,
                type="access",  # 默认使用access类型
                length_km=random.uniform(5, 15),
                total_wavelengths=40,  # 数据中心链路默认40个波长
                fg_otn_support=True,
                osnr=35  # 数据中心链路OSNR更高
            )
            
            dc_links.append(link)
            link_id += 1
        
        return dc_links
    
    def generate_user_to_otn_links(self) -> List[LinkConfig]:
        """生成用户到OTN节点链路"""
        user_links = []
        link_id = 9001  # 用户链路ID范围9000-9999
        
        # 选择所有access类型节点
        access_nodes = [node for node in self.nodes if node.type == "access"]
        
        if not access_nodes:
            # 如果没有access节点，选择所有节点
            access_nodes = self.nodes
        
        # 为每个用户生成到OTN节点的链路
        for user in self.users:
            # 随机选择一个OTN节点
            otn_node = random.choice(access_nodes)
            
            # 生成链路
            link = LinkConfig(
                id=link_id,
                src=user["id"],
                dst=otn_node.id,
                type="access",  # 默认使用access类型
                length_km=random.uniform(3, 10),
                total_wavelengths=40,  # 用户链路默认40个波长
                fg_otn_support=True,
                osnr=35  # 用户链路OSNR更高
            )
            
            user_links.append(link)
            link_id += 1
        
        return user_links
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算两个地理坐标之间的距离（公里）"""
        # 简化的距离计算（使用球面近似）
        R = 6371.0  # 地球半径（公里）
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def generate_wavelength_channels(self, bandwidth: str = "100G", count: int = 80) -> List[WavelengthConfig]:
        """生成波长通道配置"""
        channels = []
        for i in range(1, count + 1):
            channels.append(WavelengthConfig(
                channel_id=i,
                bandwidth=bandwidth
            ))
        return channels
    
    def create_node(self, node_id: int, node_type: str, lat: float, lon: float) -> NodeConfig:
        """创建节点配置"""
        node_configs = {
            "access": {
                "name": f"OTN_ACCESS_{node_id}",
                "wavelength_num": 40,
                "add_drop_capability": 10,
                "fg_otn_support": True,
                "oduk_support": True,
                "wavelength_support": True
            },
            "aggregation": {
                "name": f"OTN_AGGREGATION_{node_id}",
                "wavelength_num": 60,
                "add_drop_capability": 15,
                "fg_otn_support": True,
                "oduk_support": True,
                "wavelength_support": True
            },
            "core": {
                "name": f"OTN_CORE_{node_id}",
                "wavelength_num": 80,
                "add_drop_capability": 20,
                "fg_otn_support": False,
                "oduk_support": True,
                "wavelength_support": True
            }
        }
        
        config = node_configs[node_type]
        return NodeConfig(
            id=node_id,
            type=node_type,
            lat=lat,
            lon=lon,
            **config
        )
    
    def to_yaml_dict(self) -> Dict:
        """转换为YAML字典格式"""
        # 确保节点和链路已经生成
        if not self.nodes:
            self.generate_nodes()
        if not self.links:
            self.generate_links()
        if not self.dc_to_otn_links:
            self.dc_to_otn_links = self.generate_dc_to_otn_links()
        if not self.user_to_otn_links:
            self.user_to_otn_links = self.generate_user_to_otn_links()
        
        # 合并所有链路
        all_links = self.links + self.dc_to_otn_links + self.user_to_otn_links
        
        return {
            "nodes": self.nodes,
            "links": self.links,
            "dc_to_otn_links": self.dc_to_otn_links,
            "user_to_otn_links": self.user_to_otn_links
        }
    
    def save_to_file(self, filename: str):
        """保存为YAML文件"""
        # 生成完整的配置字典
        config_data = self.to_yaml_dict()
        
        with open(filename, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write("# ======================\n")
            f.write("# 完整fgOTN仿真架构（光层+电层+fgOTN的粒度）\n")
            f.write("#ODU0-1.25G、ODU1-2.5G、ODU2-10G、ODU2e-10G、ODU3-40G、ODU4-100G、ODUflex-n*1.25G\n")
            f.write("#时隙，100G分为1.25G*80个ODU0，一个ODU0包含119*10M（fgTS），一个ODU1包含238*fgTS、一个ODU2包含952*fgTS、n*119fgTS\n")
            f.write("# ======================\n\n\n")
            
            # 写入模板定义
            f.write("# 接入网OTN节点模板\n")
            f.write("otn_access_template: &otn_access_template\n")
            f.write("  id: 0\n")
            f.write("  name: OTN_ACCESS\n")
            f.write("  type: access       # 节点类型：access（接入网）、aggregation（汇聚网）、core（省干传输）\n")
            f.write("  wavelength_num: 40        # 支持40个波长\n")
            f.write("  add_drop_capability: 10     # 上下路波长数\n")
            f.write("  fg_otn_support: true       # 支持fgOTN\n")
            f.write("  oduk_support: true         # 支持ODUk\n")
            f.write("  wavelength_support: true   # 支持波分\n\n")
            
            f.write("# 汇聚网OTN节点模板\n")
            f.write("otn_aggregation_template: &otn_aggregation_template\n")
            f.write("  id: 0\n")
            f.write("  name: OTN_AGGREGATION\n")
            f.write("  type: aggregation\n")
            f.write("  wavelength_num: 60        # 支持60个波长\n")
            f.write("  add_drop_capability: 15     # 上下路波长数\n")
            f.write("  fg_otn_support: true       # 支持fgOTN\n")
            f.write("  oduk_support: true         # 支持ODUk\n")
            f.write("  wavelength_support: true   # 支持波分\n\n")
            
            f.write("# 省干传输OTN节点模板\n")
            f.write("otn_core_template: &otn_core_template\n")
            f.write("  id: 0\n")
            f.write("  name: OTN_CORE\n")
            f.write("  type: core\n")
            f.write("  wavelength_num: 80        # 支持80个波长\n")
            f.write("  add_drop_capability: 20     # 上下路波长数\n")
            f.write("  fg_otn_support: false      # 不支持fgOTN\n")
            f.write("  oduk_support: true         # 支持ODUk\n")
            f.write("  wavelength_support: true   # 支持波分\n\n")
            
            f.write("# 用户节点模板定义\n")
            f.write("user_template: &user_template\n")
            f.write("  id: 0\n")
            f.write("  name: User\n\n")
            
            f.write("# ODU0模板定义\n")
            f.write("odu0_template: &odu0_template\n")
            f.write("  odu0_id: 0\n")
            f.write("  bandwidth: 1.25G\n")
            f.write("  status: 0           # ODU0状态：0-未占用，1-已占用\n")
            f.write("  fg_otn_slots:       # fgOTN时隙配置\n")
            f.write("    total_slots: 119     # 每个ODU0支持119个fgOTN时隙\n")
            f.write("    available_slots: 119 # 可用fgOTN时隙数\n")
            f.write("    occupied_slots: 0    # 已占用fgOTN时隙数\n")
            f.write("  consistency_id: 0      # ODU0一致性标识，用于保证ODU0在链路上的一致性\n")
            f.write("  support_fg_otn: true   # 是否支持fgOTN（仅接入和汇聚网节点支持）\n\n")
            
            f.write("# 100G波长通道模板\n")
            f.write("wavelength_100g_template: &wavelength_100g_template\n")
            f.write("  channel_id: 0\n")
            f.write("  bandwidth: 100G\n")
            f.write("  status: 0           #波长状态，默认可用,占用情况：0-未占用，1-已占用\n")
            f.write("  consistency_id: 0      # 波长一致性标识，用于保证波长在链路上的一致性\n")
            f.write("  odu0_list:             # 示例：id=1的ODU0配置\n")
            f.write("    - odu0_id: 1\n")
            f.write("      <<: *odu0_template\n\n")
            
            f.write("# 400G波长通道模板\n")
            f.write("wavelength_400g_template: &wavelength_400g_template\n")
            f.write("  channel_id: 0\n")
            f.write("  bandwidth: 400G\n")
            f.write("  status: 0          #波长状态，默认可用\n")
            f.write("  consistency_id: 0      # 波长一致性标识\n")
            f.write("  odu0_list:             # 示例：id=1的ODU0配置\n")
            f.write("    - odu0_id: 1\n")
            f.write("      <<: *odu0_template\n\n")
            
            f.write("# 接入网链路模板\n")
            f.write("link_access_template: &link_access_template\n")
            f.write("  id: 2000\n")
            f.write("  src: 0\n")
            f.write("  dst: 0\n")
            f.write("  type: access       # 链路类型：access（接入网）、aggregation（汇聚网）、core（省干传输）\n")
            f.write("  length_km: 0\n")
            f.write("  attenuation: 0.22\n")
            f.write("  dispersion: 17\n")
            f.write("  osnr: 35                      #dB\n")
            f.write("  total_wavelengths: 40         # 光纤总波长容量\n")
            f.write("  fg_otn_support: true          # 支持fgOTN\n")
            f.write("  oduk_support: true            # 支持ODUk\n")
            f.write("  wavelength_support: true      # 支持波分\n")
            f.write("  used_wavelengths: 0           # 已使用波长数\n")
            f.write("  wavelength_channels:          # 示例：id=1的波长通道配置\n")
            f.write("    - channel_id: 1\n")
            f.write("      <<: *wavelength_100g_template\n")
            f.write("      consistency_id: 1\n\n")
            
            f.write("# 汇聚网链路模板\n")
            f.write("link_aggregation_template: &link_aggregation_template\n")
            f.write("  id: 4000\n")
            f.write("  src: 0\n")
            f.write("  dst: 0\n")
            f.write("  type: aggregation\n")
            f.write("  length_km: 0\n")
            f.write("  attenuation: 0.22\n")
            f.write("  dispersion: 17\n")
            f.write("  osnr: 32                      #dB\n")
            f.write("  total_wavelengths: 60         # 光纤总波长容量\n")
            f.write("  fg_otn_support: true          # 支持fgOTN\n")
            f.write("  oduk_support: true            # 支持ODUk\n")
            f.write("  wavelength_support: true      # 支持波分\n")
            f.write("  used_wavelengths: 0           # 已使用波长数\n")
            f.write("  wavelength_channels:          # 示例：id=1的波长通道配置\n")
            f.write("    - channel_id: 1\n")
            f.write("      <<: *wavelength_100g_template\n")
            f.write("      consistency_id: 1\n\n")
            
            f.write("# 省干传输链路模板\n")
            f.write("link_core_template: &link_core_template\n")
            f.write("  id: 6000\n")
            f.write("  src: 0\n")
            f.write("  dst: 0\n")
            f.write("  type: core\n")
            f.write("  length_km: 0\n")
            f.write("  attenuation: 0.22\n")
            f.write("  dispersion: 17\n")
            f.write("  osnr: 30                      #dB\n")
            f.write("  total_wavelengths: 80         # 光纤总波长容量\n")
            f.write("  fg_otn_support: false         # 不支持fgOTN\n")
            f.write("  oduk_support: true            # 支持ODUk\n")
            f.write("  wavelength_support: true      # 支持波分\n")
            f.write("  used_wavelengths: 0           # 已使用波长数\n")
            f.write("  wavelength_channels:          # 示例：id=1的波长通道配置\n")
            f.write("    - channel_id: 1\n")
            f.write("      <<: *wavelength_100g_template\n")
            f.write("      consistency_id: 1\n\n")
            
            f.write("# 数据中心到OTN节点链路模板\n")
            f.write("dc_to_otn_template: &dc_to_otn_template\n")
            f.write("  id: 8000\n")
            f.write("  src: 0\n")
            f.write("  dst: 0\n")
            f.write("  type: access       # 默认使用接入网类型\n")
            f.write("  length_km: 5\n")
            f.write("  attenuation: 0.22\n")
            f.write("  dispersion: 17\n")
            f.write("  osnr: 35                      #dB\n")
            f.write("  total_wavelengths: 40         # 光纤总波长容量\n")
            f.write("  fg_otn_support: true          # 支持fgOTN\n")
            f.write("  oduk_support: true            # 支持ODUk\n")
            f.write("  wavelength_support: true      # 支持波分\n")
            f.write("  used_wavelengths: 0           # 已使用波长数\n")
            f.write("  wavelength_channels:          # 示例：id=1的波长通道配置\n")
            f.write("    - channel_id: 1\n")
            f.write("      <<: *wavelength_100g_template\n")
            f.write("      consistency_id: 1\n\n")
            
            f.write("# 用户到OTN节点链路模板\n")
            f.write("user_to_otn_template: &user_to_otn_template\n")
            f.write("  id: 9000\n")
            f.write("  src: 0\n")
            f.write("  dst: 0\n")
            f.write("  type: access       # 默认使用接入网类型\n")
            f.write("  length_km: 3\n")
            f.write("  attenuation: 0.22\n")
            f.write("  dispersion: 17\n")
            f.write("  osnr: 35                      #dB\n")
            f.write("  total_wavelengths: 40         # 光纤总波长容量\n")
            f.write("  fg_otn_support: true          # 支持fgOTN\n")
            f.write("  oduk_support: true            # 支持ODUk\n")
            f.write("  wavelength_support: true      # 支持波分\n")
            f.write("  used_wavelengths: 0           # 已使用波长数\n")
            f.write("  wavelength_channels:          # 示例：id=1的波长通道配置\n")
            f.write("    - channel_id: 1\n")
            f.write("      <<: *wavelength_100g_template\n")
            f.write("      consistency_id: 1\n\n")
            
            # 写入节点配置
            f.write("# --- OTN设备1-900（ROADM/OXC+OTN交换机）---\n")
            f.write("nodes:\n")
            
            for node in config_data["nodes"]:
                if node.type == "access":
                    f.write("  - <<: *otn_access_template\n")
                elif node.type == "aggregation":
                    f.write("  - <<: *otn_aggregation_template\n")
                elif node.type == "core":
                    f.write("  - <<: *otn_core_template\n")
                
                f.write(f"    id: {node.id}\n")
                f.write(f"    name: {node.name}\n")
            
            # 写入用户配置
            f.write("\n# --- 用户节点901-950 --- \n")
            f.write("users:\n")
            for user in self.users:
                f.write("  - <<: *user_template\n")
                f.write(f"    id: {user['id']}\n")
            
            # 写入链路配置
            f.write("\n# --- 链路配置2000-10000 --- \n")
            f.write("# 链路分配规则：\n")
            f.write("# 2000-3999：接入网链路（连接接入网节点到汇聚网节点）\n")
            f.write("# 4000-5999：汇聚网链路（连接汇聚网节点到省干传输节点）\n")
            f.write("# 6000-7999：省干传输链路（连接省干传输节点）\n")
            f.write("# 8000-8999：数据中心到OTN节点链路（连接数据中心到OTN节点）\n")
            f.write("# 9000-9999：用户到OTN节点链路（连接用户到OTN节点）\n\n")
            f.write("links:\n")
            
            # 写入普通链路
            for link in config_data["links"]:
                if link.type == "access" and link.src < 950 and link.dst < 950:
                    f.write("  - <<: *link_access_template\n")
                elif link.type == "aggregation" and link.src < 950 and link.dst < 950:
                    f.write("  - <<: *link_aggregation_template\n")
                elif link.type == "core" and link.src < 950 and link.dst < 950:
                    f.write("  - <<: *link_core_template\n")
                else:
                    continue  # 跳过数据中心和用户链路，后面单独写入
                
                f.write(f"    id: {link.id}\n")
                f.write(f"    src: {link.src}\n")
                f.write(f"    dst: {link.dst}\n")
                f.write(f"    length_km: {link.length_km}\n")
            
            # 写入数据中心到OTN节点链路
            f.write("\n# --- 数据中心到OTN节点链路配置8000-8999 ---\n")
            f.write("dc_to_otn_links:\n")
            for link in config_data["dc_to_otn_links"]:
                f.write("  - <<: *dc_to_otn_template\n")
                f.write(f"    id: {link.id}\n")
                f.write(f"    src: {link.src}\n")
                f.write(f"    dst: {link.dst}\n")
                f.write(f"    length_km: {link.length_km}\n")
            
            # 写入用户到OTN节点链路
            f.write("\n# --- 用户到OTN节点链路配置9000-9999 ---\n")
            f.write("user_to_otn_links:\n")
            for link in config_data["user_to_otn_links"]:
                f.write("  - <<: *user_to_otn_template\n")
                f.write(f"    id: {link.id}\n")
                f.write(f"    src: {link.src}\n")
                f.write(f"    dst: {link.dst}\n")
                f.write(f"    length_km: {link.length_km}\n")


class StarTopologyGenerator(TopologyGenerator):
    """星型拓扑生成器"""
    
    def generate_nodes(self, center_lat: float = 39.0, center_lon: float = 116.0, 
                      radius_km: float = None) -> List[NodeConfig]:
        """生成星型拓扑节点"""
        if radius_km is None:
            radius_km = self.radius_km
            
        self.nodes = []
        
        # 生成core节点作为中心
        core_lat, core_lon = center_lat, center_lon
        core_node = self.create_node(node_id=601, node_type="core", lat=core_lat, lon=core_lon)
        self.nodes.append(core_node)
        
        # 生成第二个core节点
        core_node2 = self.create_node(node_id=602, node_type="core", lat=center_lat + 1.0, lon=center_lon + 1.0)
        self.nodes.append(core_node2)
        
        # 生成aggregation节点围绕core节点
        aggregation_count = self.node_counts.get("aggregation", 3)
        for i in range(aggregation_count):
            angle = 2 * math.pi * i / aggregation_count
            distance = radius_km * 0.3
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            agg_lat = center_lat + lat_offset
            agg_lon = center_lon + lon_offset
            
            agg_node = self.create_node(node_id=300 + i + 1, node_type="aggregation", lat=agg_lat, lon=agg_lon)
            self.nodes.append(agg_node)
        
        # 生成access节点围绕aggregation节点
        access_count = self.node_counts.get("access", 10)
        aggregation_nodes = [node for node in self.nodes if node.type == "aggregation"]
        
        for i in range(access_count):
            agg_node = aggregation_nodes[i % len(aggregation_nodes)]
            
            angle = 2 * math.pi * i / access_count
            distance = radius_km * 0.6
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            access_lat = center_lat + lat_offset
            access_lon = center_lon + lon_offset
            
            access_node = self.create_node(node_id=i + 1, node_type="access", lat=access_lat, lon=access_lon)
            self.nodes.append(access_node)
        
        return self.nodes
    
    def generate_links(self) -> List[LinkConfig]:
        """生成星型拓扑链路"""
        if not self.nodes:
            raise ValueError("请先生成节点")
        
        self.links = []
        link_id = 2001
        aggregation_link_id = 4001
        core_link_id = 6001
        
        # 获取不同类型的节点
        core_nodes = [node for node in self.nodes if node.type == "core"]
        aggregation_nodes = [node for node in self.nodes if node.type == "aggregation"]
        access_nodes = [node for node in self.nodes if node.type == "access"]
        
        # Core到Aggregation的链路（汇聚网链路，ID范围4000-5999）
        for agg_node in aggregation_nodes:
            for core_node in core_nodes:
                distance = self.calculate_distance(
                    core_node.lat, core_node.lon,
                    agg_node.lat, agg_node.lon
                )
                
                link = LinkConfig(
                    id=aggregation_link_id,
                    src=core_node.id,
                    dst=agg_node.id,
                    type="aggregation",
                    length_km=distance,
                    total_wavelengths=60,
                    fg_otn_support=True,
                    osnr=32
                )
                self.links.append(link)
                aggregation_link_id += 1
        
        # Core节点之间的链路（省干传输链路，ID范围6000-7999）
        for i in range(len(core_nodes)):
            for j in range(i + 1, len(core_nodes)):
                distance = self.calculate_distance(
                    core_nodes[i].lat, core_nodes[i].lon,
                    core_nodes[j].lat, core_nodes[j].lon
                )
                
                link = LinkConfig(
                    id=core_link_id,
                    src=core_nodes[i].id,
                    dst=core_nodes[j].id,
                    type="core",
                    length_km=distance,
                    total_wavelengths=80,
                    fg_otn_support=False,
                    osnr=30
                )
                self.links.append(link)
                core_link_id += 1
        
        # Aggregation到Access的链路（接入网链路，ID范围2000-3999）
        for i, access_node in enumerate(access_nodes):
            agg_node = aggregation_nodes[i % len(aggregation_nodes)]
            
            distance = self.calculate_distance(
                agg_node.lat, agg_node.lon,
                access_node.lat, access_node.lon
            )
            
            link = LinkConfig(
                id=link_id,
                src=agg_node.id,
                dst=access_node.id,
                type="access",
                length_km=distance,
                total_wavelengths=40,
                fg_otn_support=True,
                osnr=35
            )
            self.links.append(link)
            link_id += 1
        
        return self.links


class RingTopologyGenerator(TopologyGenerator):
    """环形拓扑生成器"""
    
    def generate_nodes(self, center_lat: float = 39.0, center_lon: float = 116.0, 
                      radius_km: float = None) -> List[NodeConfig]:
        """生成环形拓扑节点"""
        if radius_km is None:
            radius_km = self.radius_km
            
        self.nodes = []
        
        # 生成core节点
        core_count = self.node_counts.get("core", 3)
        for i in range(core_count):
            angle = 2 * math.pi * i / core_count
            distance = radius_km * 0.8
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            core_lat = center_lat + lat_offset
            core_lon = center_lon + lon_offset
            
            core_node = self.create_node(node_id=600 + i + 1, node_type="core", lat=core_lat, lon=core_lon)
            self.nodes.append(core_node)
        
        # 生成aggregation节点
        aggregation_count = self.node_counts.get("aggregation", 5)
        for i in range(aggregation_count):
            angle = 2 * math.pi * i / aggregation_count
            distance = radius_km * 0.5
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            agg_lat = center_lat + lat_offset
            agg_lon = center_lon + lon_offset
            
            agg_node = self.create_node(node_id=300 + i + 1, node_type="aggregation", lat=agg_lat, lon=agg_lon)
            self.nodes.append(agg_node)
        
        # 生成access节点
        access_count = self.node_counts.get("access", 10)
        for i in range(access_count):
            angle = 2 * math.pi * i / access_count
            distance = radius_km * 0.2
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            access_lat = center_lat + lat_offset
            access_lon = center_lon + lon_offset
            
            access_node = self.create_node(node_id=i + 1, node_type="access", lat=access_lat, lon=access_lon)
            self.nodes.append(access_node)
        
        return self.nodes
    
    def generate_links(self) -> List[LinkConfig]:
        """生成环形拓扑链路"""
        if not self.nodes:
            raise ValueError("请先生成节点")
        
        self.links = []
        link_id = 2001
        aggregation_link_id = 4001
        core_link_id = 6001
        
        # 获取不同类型的节点
        core_nodes = [node for node in self.nodes if node.type == "core"]
        aggregation_nodes = [node for node in self.nodes if node.type == "aggregation"]
        access_nodes = [node for node in self.nodes if node.type == "access"]
        
        # Core节点环形连接（省干传输链路，ID范围6000-7999）
        for i in range(len(core_nodes)):
            current_node = core_nodes[i]
            next_node = core_nodes[(i + 1) % len(core_nodes)]
            
            distance = self.calculate_distance(
                current_node.lat, current_node.lon,
                next_node.lat, next_node.lon
            )
            
            link = LinkConfig(
                id=core_link_id,
                src=current_node.id,
                dst=next_node.id,
                type="core",
                length_km=distance,
                total_wavelengths=80,
                fg_otn_support=False,
                osnr=30
            )
            self.links.append(link)
            core_link_id += 1
        
        # Aggregation节点环形连接（汇聚网链路，ID范围4000-5999）
        for i in range(len(aggregation_nodes)):
            current_node = aggregation_nodes[i]
            next_node = aggregation_nodes[(i + 1) % len(aggregation_nodes)]
            
            distance = self.calculate_distance(
                current_node.lat, current_node.lon,
                next_node.lat, next_node.lon
            )
            
            link = LinkConfig(
                id=aggregation_link_id,
                src=current_node.id,
                dst=next_node.id,
                type="aggregation",
                length_km=distance,
                total_wavelengths=60,
                fg_otn_support=True,
                osnr=32
            )
            self.links.append(link)
            aggregation_link_id += 1
        
        # Access节点环形连接（接入网链路，ID范围2000-3999）
        for i in range(len(access_nodes)):
            current_node = access_nodes[i]
            next_node = access_nodes[(i + 1) % len(access_nodes)]
            
            distance = self.calculate_distance(
                current_node.lat, current_node.lon,
                next_node.lat, next_node.lon
            )
            
            link = LinkConfig(
                id=link_id,
                src=current_node.id,
                dst=next_node.id,
                type="access",
                length_km=distance,
                total_wavelengths=40,
                fg_otn_support=True,
                osnr=35
            )
            self.links.append(link)
            link_id += 1
        
        # Aggregation到Core的链路
        for agg_node in aggregation_nodes:
            for core_node in core_nodes:
                distance = self.calculate_distance(
                    agg_node.lat, agg_node.lon,
                    core_node.lat, core_node.lon
                )
                
                link = LinkConfig(
                    id=aggregation_link_id,
                    src=agg_node.id,
                    dst=core_node.id,
                    type="aggregation",
                    length_km=distance,
                    total_wavelengths=60,
                    fg_otn_support=True,
                    osnr=32
                )
                self.links.append(link)
                aggregation_link_id += 1
        
        # Access到Aggregation的链路
        for i, access_node in enumerate(access_nodes):
            agg_node = aggregation_nodes[i % len(aggregation_nodes)]
            
            distance = self.calculate_distance(
                access_node.lat, access_node.lon,
                agg_node.lat, agg_node.lon
            )
            
            link = LinkConfig(
                id=link_id,
                src=access_node.id,
                dst=agg_node.id,
                type="access",
                length_km=distance,
                total_wavelengths=40,
                fg_otn_support=True,
                osnr=35
            )
            self.links.append(link)
            link_id += 1
        
        return self.links


class MeshTopologyGenerator(TopologyGenerator):
    """网状拓扑生成器"""
    
    def __init__(self, node_counts: Dict[str, int] = None, base_id: int = 2001, 
                 connectivity: float = 0.5, wavelength_num: int = 80, 
                 wavelength_bandwidth: str = "100G", radius_km: float = 1000.0):
        super().__init__(node_counts, base_id, wavelength_num, wavelength_bandwidth, radius_km)
        self.connectivity = connectivity  # 连接密度（0-1）
    
    def generate_nodes(self, center_lat: float = 39.0, center_lon: float = 116.0, 
                      radius_km: float = None) -> List[NodeConfig]:
        """生成网状拓扑节点"""
        if radius_km is None:
            radius_km = self.radius_km
            
        self.nodes = []
        
        # 生成core节点
        core_count = self.node_counts.get("core", 3)
        for i in range(core_count):
            # 随机分布节点
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(radius_km * 0.6, radius_km)
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            core_lat = center_lat + lat_offset
            core_lon = center_lon + lon_offset
            
            core_node = self.create_node(node_id=600 + i + 1, node_type="core", lat=core_lat, lon=core_lon)
            self.nodes.append(core_node)
        
        # 生成aggregation节点
        aggregation_count = self.node_counts.get("aggregation", 5)
        for i in range(aggregation_count):
            # 随机分布节点
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(radius_km * 0.3, radius_km * 0.6)
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            agg_lat = center_lat + lat_offset
            agg_lon = center_lon + lon_offset
            
            agg_node = self.create_node(node_id=300 + i + 1, node_type="aggregation", lat=agg_lat, lon=agg_lon)
            self.nodes.append(agg_node)
        
        # 生成access节点
        access_count = self.node_counts.get("access", 10)
        for i in range(access_count):
            # 随机分布节点
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius_km * 0.3)
            
            lat_offset = distance * math.sin(angle) / 111.0
            lon_offset = distance * math.cos(angle) / (111.0 * math.cos(math.radians(center_lat)))
            
            access_lat = center_lat + lat_offset
            access_lon = center_lon + lon_offset
            
            access_node = self.create_node(node_id=i + 1, node_type="access", lat=access_lat, lon=access_lon)
            self.nodes.append(access_node)
        
        return self.nodes
    
    def generate_links(self) -> List[LinkConfig]:
        """生成网状拓扑链路"""
        if not self.nodes:
            raise ValueError("请先生成节点")
        
        self.links = []
        link_id = 2001
        
        # 生成所有可能的连接
        possible_links = []
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                node1 = self.nodes[i]
                node2 = self.nodes[j]
                
                # 计算距离
                distance = self.calculate_distance(
                    node1.lat, node1.lon,
                    node2.lat, node2.lon
                )
                
                possible_links.append((i, j, distance))
        
        # 按距离排序，优先连接较近的节点
        possible_links.sort(key=lambda x: x[2])
        
        # 根据连接密度选择链路
        num_links = int(len(possible_links) * self.connectivity)
        selected_links = possible_links[:num_links]
        
        # 生成唯一的链路ID
        for i, j, distance in selected_links:
            node1 = self.nodes[i]
            node2 = self.nodes[j]
            
            # 确定链路类型
            if node1.type == "core" and node2.type == "core":
                link_type = "core"
                total_wavelengths = 80
                fg_otn_support = False
                osnr = 30
                link_id_base = 6000
            elif (node1.type == "core" and node2.type == "aggregation") or \
                 (node1.type == "aggregation" and node2.type == "core"):
                link_type = "aggregation"
                total_wavelengths = 60
                fg_otn_support = True
                osnr = 32
                link_id_base = 4000
            elif (node1.type == "aggregation" and node2.type == "aggregation") or \
                 (node1.type == "aggregation" and node2.type == "access") or \
                 (node1.type == "access" and node2.type == "aggregation"):
                link_type = "aggregation"
                total_wavelengths = 60
                fg_otn_support = True
                osnr = 32
                link_id_base = 4000
            else:  # access到access
                link_type = "access"
                total_wavelengths = 40
                fg_otn_support = True
                osnr = 35
                link_id_base = 2000
            
            link = LinkConfig(
                id=link_id,
                src=node1.id,
                dst=node2.id,
                type=link_type,
                length_km=distance,
                total_wavelengths=total_wavelengths,
                fg_otn_support=fg_otn_support,
                osnr=osnr
            )
            self.links.append(link)
            link_id += 1
        
        return self.links


def generate_topology(topology_type: str, node_counts: Dict[str, int], 
                     output_file: str, **kwargs) -> TopologyGenerator:
    """
    生成拓扑配置文件
    
    Args:
        topology_type: 拓扑类型（'star', 'ring', 'mesh'）
        node_counts: 各类型节点数量，格式: {"access": int, "aggregation": int, "core": int}
        output_file: 输出文件名
        **kwargs: 其他参数
    
    Returns:
        TopologyGenerator: 拓扑生成器实例
    """
    
    if topology_type.lower() == 'star':
        generator = StarTopologyGenerator(
            node_counts=node_counts,
            wavelength_num=kwargs.get('wavelength_num', 80),
            wavelength_bandwidth=kwargs.get('wavelength_bandwidth', "100G"),
            radius_km=kwargs.get('radius_km', 1000.0)
        )
    elif topology_type.lower() == 'ring':
        generator = RingTopologyGenerator(
            node_counts=node_counts,
            wavelength_num=kwargs.get('wavelength_num', 80),
            wavelength_bandwidth=kwargs.get('wavelength_bandwidth', "100G"),
            radius_km=kwargs.get('radius_km', 1000.0)
        )
    elif topology_type.lower() == 'mesh':
        generator = MeshTopologyGenerator(
            node_counts=node_counts,
            connectivity=kwargs.get('connectivity', 0.5),
            wavelength_num=kwargs.get('wavelength_num', 80),
            wavelength_bandwidth=kwargs.get('wavelength_bandwidth', "100G"),
            radius_km=kwargs.get('radius_km', 1000.0)
        )
    else:
        raise ValueError(f"不支持的拓扑类型: {topology_type}")
    
    # 生成节点和链路
    generator.generate_nodes()
    generator.generate_links()
    generator.dc_to_otn_links = generator.generate_dc_to_otn_links()
    generator.user_to_otn_links = generator.generate_user_to_otn_links()
    
    # 保存到文件
    generator.save_to_file(output_file)
    
    return generator


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description='OTN拓扑配置文件生成器')
    parser.add_argument('--type', type=str, required=True, 
                       choices=['star', 'ring', 'mesh'], 
                       help='拓扑类型')
    parser.add_argument('--access-nodes', type=int, default=10, 
                       help='接入网节点数量')
    parser.add_argument('--aggregation-nodes', type=int, default=5, 
                       help='汇聚网节点数量')
    parser.add_argument('--core-nodes', type=int, default=3, 
                       help='省干传输节点数量')
    parser.add_argument('--output', type=str, default='data/auto_topology.yaml', 
                       help='输出文件名')
    parser.add_argument('--connectivity', type=float, default=0.5,
                       help='网状拓扑连接密度(0-1)')
    parser.add_argument('--wavelength-num', type=int, default=80,
                       help='波长数量(默认:80)')
    parser.add_argument('--wavelength-bandwidth', type=str, default='100G',
                       choices=['100G', '400G', '800G'],
                       help='波长带宽(默认:100G)')
    parser.add_argument('--radius-km', type=float, default=1000.0,
                       help='拓扑半径(公里,默认:1000)')
    
    args = parser.parse_args()
    
    try:
        # 构建节点数量字典
        node_counts = {
            "access": args.access_nodes,
            "aggregation": args.aggregation_nodes,
            "core": args.core_nodes
        }
        
        if args.type == 'mesh':
            generator = generate_topology(args.type, node_counts, args.output, 
                                        connectivity=args.connectivity,
                                        wavelength_num=args.wavelength_num,
                                        wavelength_bandwidth=args.wavelength_bandwidth,
                                        radius_km=args.radius_km)
        else:
            generator = generate_topology(args.type, node_counts, args.output,
                                        wavelength_num=args.wavelength_num,
                                        wavelength_bandwidth=args.wavelength_bandwidth,
                                        radius_km=args.radius_km)
        
        print(f"成功生成{args.type}拓扑配置文件: {args.output}")
        print(f"节点数: {len(generator.nodes)}")
        print(f"链路数: {len(generator.links)}")
        print(f"数据中心到OTN链路数: {len(generator.dc_to_otn_links)}")
        print(f"用户到OTN链路数: {len(generator.user_to_otn_links)}")
        print(f"总链路数: {len(generator.links) + len(generator.dc_to_otn_links) + len(generator.user_to_otn_links)}")
        
    except Exception as e:
        print(f"生成拓扑配置文件时出错: {e}")
        import traceback
        traceback.print_exc()