#!/usr/bin/env python3
"""
测试拓扑加载脚本
"""

# 设置matplotlib后端为Agg，支持非交互式环境
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from topology_OTN import TopologyManager
from result import LOGGER

def draw_topology(G):
    """
    绘制拓扑图，显示节点和链路信息
    使用地理布局显示美国节点位置
    Args:
        G: 网络拓扑图
    """
    LOGGER.info(f"开始绘制拓扑图...")
    # 设置节点颜色映射
    node_colors = []
    for node_id, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'unknown')
        if node_type == 'access':
            node_colors.append('#77dd77')  # 浅绿色
        elif node_type == 'aggregation':
            node_colors.append('#99ccee')  # 浅蓝色
        elif node_type == 'core':
            node_colors.append('#ff6961')  # 浅红色
        elif node_type == 'datacenter':
            node_colors.append('#9370db')  # 浅紫色
        else:
            node_colors.append('#d3d3d3')  # 浅灰色

    # 设置节点大小
    node_sizes = []
    for node_id, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'unknown')
        if node_type == 'datacenter':
            node_sizes.append(400)  # 数据中心节点更大
        else:
            node_sizes.append(200)  # 其他节点更小

    # 设置边颜色映射
    edge_colors = []
    for u, v, attrs in G.edges(data=True):
        edge_type = attrs.get('type', 'unknown')
        if edge_type == 'access':
            edge_colors.append('#228B22')  # 深绿色
        elif edge_type == 'aggregation':
            edge_colors.append('#1E90FF')  # 深蓝色
        elif edge_type == 'core':
            edge_colors.append('#DC143C')  # 深红色
        else:
            edge_colors.append('#808080')  # 深灰色

    # 设置边宽
    edge_widths = []
    for u, v, attrs in G.edges(data=True):
        bandwidth = attrs.get('capacity_Gbps', 0)
        # 根据带宽设置边宽，带宽越大边越宽
        edge_widths.append(min(bandwidth / 1000, 3.0))  # 最大边宽3.0

    # 设置画布大小（美国地图横向较长，使用16:10比例）
    plt.figure(figsize=(20, 14))

    # 使用地理布局：基于节点经纬度进行定位
    pos = {}
    lons = []
    lats = []

    # 收集所有节点的经纬度
    for node_id, attrs in G.nodes(data=True):
        lat = attrs.get('lat', 0.0)
        lon = attrs.get('lon', 0.0)
        # 如果节点没有经纬度信息，使用默认布局
        if lat == 0.0 and lon == 0.0:
            continue
        lons.append(lon)
        lats.append(lat)

    # 如果存在有效经纬度数据，使用地理布局
    if lons and lats:
        # 计算经纬度范围
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)

        # 添加边距
        lon_margin = (max_lon - min_lon) * 0.15 if max_lon > min_lon else 5
        lat_margin = (max_lat - min_lat) * 0.15 if max_lat > min_lat else 5

        min_lon -= lon_margin
        max_lon += lon_margin
        min_lat -= lat_margin
        max_lat += lat_margin

        # 将经纬度转换为平面坐标
        for node_id, attrs in G.nodes(data=True):
            lat = attrs.get('lat', 0.0)
            lon = attrs.get('lon', 0.0)
            if lat != 0.0 or lon != 0.0:
                # 归一化到 [0, 1] 范围
                x = (lon - min_lon) / (max_lon - min_lon) if max_lon > min_lon else 0.5
                y = (lat - min_lat) / (max_lat - min_lat) if max_lat > min_lat else 0.5
                pos[node_id] = (x, y)

    # 对于没有经纬度的节点，使用spring_layout计算位置
    nodes_without_geo = [n for n in G.nodes() if n not in pos]
    if nodes_without_geo:
        subG = G.subgraph(nodes_without_geo)
        sub_pos = nx.spring_layout(subG, k=0.5, iterations=50, seed=42)
        # 将子图位置放置在主图右侧
        for node_id, (x, y) in sub_pos.items():
            pos[node_id] = (x + 1.2, y)

    # 绘制节点
    nx.draw_networkx_nodes(G, pos,
                           node_color=node_colors,
                           node_size=node_sizes,
                           alpha=0.8,
                           edgecolors='#333333',
                           linewidths=1)

    # 绘制边
    nx.draw_networkx_edges(G, pos,
                           edge_color=edge_colors,
                           width=edge_widths,
                           alpha=0.8)

    # 添加节点标签（显示节点ID和名称）
    node_labels = {}
    for node_id, attrs in G.nodes(data=True):
        name = attrs.get('name', str(node_id))
        node_labels[node_id] = f"{node_id}:{name}"

    # 根据节点Y坐标智能调整标签位置
    label_pos = {}
    for node_id, (x, y) in pos.items():
        # 上方节点标签向下偏移，下方节点标签向上偏移
        if y > 0.7:
            label_pos[node_id] = (x, y - 0.05)  # 上方节点，标签向下
        else:
            label_pos[node_id] = (x, y + 0.05)  # 下方节点，标签向上

    # 绘制节点标签，带白色背景框
    nx.draw_networkx_labels(G, label_pos, node_labels,
                            font_size=9,
                            font_weight='bold',
                            font_color='#1a1a1a',
                            bbox=dict(boxstyle='round,pad=0.3',
                                     facecolor='white',
                                     edgecolor='gray',
                                     alpha=0.9,
                                     linewidth=1))
    
    # 添加边标签（显示链路ID、带宽信息和长度信息）
    edge_labels = {}
    for u, v, attrs in G.edges(data=True):
        link_id = attrs.get('id', f'{u}-{v}')
        total_wavelengths = attrs.get('total_wavelengths', 0)
        
        # 获取单个波长的带宽
        wavelength_bandwidth = '100G'  # 默认值
        if 'wavelength_channels' in attrs and attrs['wavelength_channels']:
            wavelength_bandwidth = attrs['wavelength_channels'][0].bandwidth
        
        # 获取链路长度
        length_km = attrs.get('length_km', 0)
        
        # 格式化带宽信息为 "波长数*带宽" 格式
        bandwidth_info = f"{total_wavelengths}*{wavelength_bandwidth}"
        
        # edge_labels[(u, v)] = f"ID: {link_id}\n{bandwidth_info}\nLength: {length_km} km"
        edge_labels[(u, v)] = f"{bandwidth_info}\nLength: {length_km} km"
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, font_weight='bold', font_color='#333333', rotate=False)
    
    # 设置图形标题
    plt.title('OTN Network Topology', fontsize=14, fontweight='bold')
    
    # 创建图例
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Access Node', markerfacecolor='#77dd77', markersize=10, markeredgecolor='#333333', markeredgewidth=1),
        plt.Line2D([0], [0], marker='o', color='w', label='Aggregation Node', markerfacecolor='#99ccee', markersize=10, markeredgecolor='#333333', markeredgewidth=1),
        plt.Line2D([0], [0], marker='o', color='w', label='Core Node', markerfacecolor='#ff6961', markersize=10, markeredgecolor='#333333', markeredgewidth=1),
        plt.Line2D([0], [0], marker='o', color='w', label='Datacenter', markerfacecolor='#9370db', markersize=10, markeredgecolor='#333333', markeredgewidth=1),
        plt.Line2D([0], [0], color='#228B22', lw=2, label='Access Link'),
        plt.Line2D([0], [0], color='#1E90FF', lw=2, label='Aggregation Link'),
        plt.Line2D([0], [0], color='#DC143C', lw=2, label='Core Link')
    ]
    plt.legend(handles=legend_elements, loc='best', fontsize=10)
    
    # 隐藏坐标轴
    plt.axis('off')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('topology_visualization.png', dpi=300, bbox_inches='tight')
    LOGGER.info(f"拓扑图已保存为 topology_visualization.png")

    # 显示图形
    plt.show()

if __name__ == "__main__":
    try:
        # 使用相对路径
        tm = TopologyManager('data/nsfnet_topology.yaml', 'data/datacenters_OTN.yaml')
        print('加载成功')
        print(f'节点数: {len(tm.nodes)}')
        print(f'链路数: {len(tm.links)}')
        
        # 打印第一个节点的信息
        if tm.nodes:
            print('\n第一个节点信息:')
            node = tm.nodes[0]
            print(f'ID: {node.id}, Name: {node.name}, Type: {node.type}')
            print(f'支持fgOTN: {node.fg_otn_support}, 支持ODUk: {node.oduk_support}, 支持波分: {node.wavelength_support}')
        
        # 打印第一个链路的信息
        if tm.links:
            print('\n第一个链路信息:')
            link = tm.links[0]
            print(f'ID: {link.id}, 源: {link.src}, 目标: {link.dst}, 类型: {link.type}')
            print(f'支持fgOTN: {link.fg_otn_support}, 支持ODUk: {link.oduk_support}, 支持波分: {link.wavelength_support}')
        
        # 打印第一个波长通道的信息
        if tm.links and tm.links[0].wavelength_channels:
            print('\n第一个波长通道信息:')
            channel = tm.links[0].wavelength_channels[0]
            print(f'通道ID: {channel.channel_id}, 带宽: {channel.bandwidth}, 一致性ID: {channel.consistency_id}')
            print(f'ODU0数量: {len(channel.odu0_list)}')
        
        # 测试图构建
        print('\n===== 图构建测试 =====')
        G = tm.get_graph()
        print(f'图中节点数: {G.number_of_nodes()}')
        print(f'图中边数: {G.number_of_edges()}')
        
        # 测试节点属性
        print('\n节点属性测试:')
        if G.number_of_nodes() > 0:
            node_id = list(G.nodes())[0]
            node_attrs = G.nodes[node_id]
            print(f'节点 {node_id} 属性:')
            print(f'  类型: {node_attrs.get("type")}')
            print(f'  支持fgOTN: {node_attrs.get("fg_otn_support")}')
            print(f'  支持ODUk: {node_attrs.get("oduk_support")}')
            print(f'  支持波分: {node_attrs.get("wavelength_support")}')
        
        # 测试边属性
        print('\n边属性测试:')
        if G.number_of_edges() > 0:
            edge = list(G.edges())[0]
            edge_attrs = G.edges[edge]
            print(f'边 {edge} 属性:')
            print(f'  类型: {edge_attrs.get("type")}')
            print(f'  支持fgOTN: {edge_attrs.get("fg_otn_support")}')
            print(f'  支持ODUk: {edge_attrs.get("oduk_support")}')
            print(f'  支持波分: {edge_attrs.get("wavelength_support")}')
            print(f'  总波长数: {edge_attrs.get("total_wavelengths")}')
            print(f'  已使用波长数: {edge_attrs.get("used_wavelengths")}')
            print(f'  总带宽: {edge_attrs.get("capacity_Gbps")} Gbps')
            print(f'  链路长度: {edge_attrs.get("length_km")} km (根据经纬度计算)')
            print(f'  波长通道数量: {len(edge_attrs.get("wavelength_channels", []))}')
            if len(edge_attrs.get("wavelength_channels", [])) > 0:
                print(f'  第一个波长通道的ODU0数量: {len(edge_attrs["wavelength_channels"][0].odu0_list)}')
        
        # 验证波长通道数量与total_wavelengths一致
        print('\n验证波长通道数量:')
        for link in tm.links:
            if len(link.wavelength_channels) != link.total_wavelengths:
                print(f'  链路 {link.id} 波长通道数量 {len(link.wavelength_channels)} 与 total_wavelengths {link.total_wavelengths} 不一致!')
            else:
                print(f'  链路 {link.id} 波长通道数量 {len(link.wavelength_channels)} 与 total_wavelengths {link.total_wavelengths} 一致')
        
        # 验证100G波长的ODU0数量为80个
        print('\n验证ODU0数量:')
        for link in tm.links:
            for channel in link.wavelength_channels:
                if channel.bandwidth == '100G' and len(channel.odu0_list) != 80:
                    print(f'  链路 {link.id} 波长通道 {channel.channel_id} (100G) ODU0数量 {len(channel.odu0_list)} 不是80个!')
                elif channel.bandwidth == '400G' and len(channel.odu0_list) != 320:
                    print(f'  链路 {link.id} 波长通道 {channel.channel_id} (400G) ODU0数量 {len(channel.odu0_list)} 不是320个!')
                else:
                    print(f'  链路 {link.id} 波长通道 {channel.channel_id} ({channel.bandwidth}) ODU0数量 {len(channel.odu0_list)} 正确')
        
        print('\n测试成功!')
        
        # 绘制拓扑图
        print('\n开始绘制拓扑图...')
        draw_topology(G)
        print('拓扑图绘制完成!')
        
    except Exception as e:
        print(f'加载失败: {e}')
        import traceback
        traceback.print_exc()
