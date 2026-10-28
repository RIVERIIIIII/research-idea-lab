# Datacenter & Optical Network Orchestration Simulator
## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Experiment
Edit the YAML files in `data/` to set up your network topology, datacenters, failure models, and service parameters.

### 3. Run the Simulation
```bash
python simulation_OTN.py
```

Simulation results and metrics will be printed to the console.
# 1. 运行单个算法仿真
```bash
python simulation_OTN.py --algorithm minPenalty
```
# 2. 运行算法对比（compare_simulations.py）
# 对比多个算法（使用相同任务序列，确保公平对比）
```bash
python compare_simulations.py --algorithms minPenalty Worst-Fit Best-Fit Random-Fit First-Fit
```

# 指定随机种子（确保结果可复现）
```bash
python compare_simulations.py --algorithms minPenalty Worst-Fit --random-seed 123
```

# 指定拓扑和数据中心配置
```bash
python compare_simulations.py --algorithms minPenalty Worst-Fit --topology data/nsfnet_topology.yaml --datacenters data/datacenters_OTN.yaml
```

# 指定输出目录和日志级别
```bash
python compare_simulations.py --algorithms minPenalty Worst-Fit --output-dir result --log-level DEBUG
```

# 3. 使用预定义任务序列
```bash
python simulation_OTN.py --algorithm algorithm2 --task-sequence-file data/task_sequences/task_sequence_42.json
```
# 4. 生成多仿真对比可视化
```bash
python multi_simulation_visualizer.py --result-dir result --pattern "*.json" --report
```
## Overview
This simulator models datacenter and inter-datacenter optical network orchestration, supporting event-driven simulation of compute, storage, and bandwidth allocation, as well as node/link failures. The architecture is modular, extensible, and fully YAML-configurable.

## Project Structure
```
ondcsim/
  data/
    nsfnet_topology.yaml      # NSFNET topology definition
    datacenters.yaml          # Datacenter locations and resources
    failures.yaml             # Failure event configuration
    service.yaml              # Service event simulation parameters
    simulator.yaml            # Global simulation parameters
  topology.py                # TopologyManager: loads and manages the network graph
  service.py                 # ServiceManager: handles all service event processes
  failure.py                 # FailureManager: handles failure event generation and processing
  result.py                  # ResultManager: collects and prints simulation metrics
  event.py                   # Event dataclasses and event generators
  simulation.py              # Main entry point
  common_utils.py            # Utility functions
```

## Configuration
All simulation parameters are set via YAML files in the `data/` directory:
- **nsfnet_topology.yaml**: Defines the network nodes and links.
- **datacenters.yaml**: Defines datacenter locations, compute, and storage.
- **failures.yaml**: Number, type, and rate of node/link failures.
- **service.yaml**: Number of events, arrival rates (lambda), and service rates (mu) for each service type.
- **simulator.yaml**: Global simulation parameters (e.g., simulation_end_time).


## 自动生成拓扑命令
# 生成星型拓扑
python3 generate_topology.py --type star --access-nodes 5 --aggregation-nodes 3 --core-nodes 2 --output data/test_topology.yaml

# 生成环形拓扑
python3 generate_topology.py --type ring --access-nodes 8 --aggregation-nodes 4 --core-nodes 3 --output data/ring_topology.yaml

# 生成网状拓扑
python3 generate_topology.py --type mesh --access-nodes 10 --aggregation-nodes 5 --core-nodes 3 --connectivity 0.6 --output data/mesh_topology.yaml

## Extending the Simulator
- **Add new event types**: Define new dataclasses in `event.py` and add processes in `service.py`.
- **Change topology/resources**: Edit the YAML files in `data/`.
- **Add new failure/repair models**: Extend `FailureManager` in `failure.py`.
- **Add analytics/visualization**: Extend `ResultManager` or use `plot_tools.py`.

## Notes
- The simulator is modular and can be extended for new event types, failure models, or analytics.
- All configuration is handled via YAML for easy experimentation.
- For advanced usage, see the docstrings in each module.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or contributions, please open an issue or pull request.

