# DISC-SF-1 / DISC-SF-2 论文叙事成立性评估

Status: HUMAN_KEEP_BACKCHECKED

## Search Scope

本轮只核查已由人工 KEEP 的两个方向，不构建正式 corpus。

- `DISC-SF-1`：5 条 query，OpenAlex 返回 30 条；Semantic Scholar 因 HTTP 429 未返回。
- `DISC-SF-2`：5 条 query，OpenAlex 原始返回 40 条，去重后 38 条。
- 定向网页检索补查了 soft failure recovery、训练感知光网络资源分配和分布式训练调度。
- “未检索到直接工作”不等于“直接工作不存在”。

## Closest Existing Work

### Optical soft-failure side

`Exploiting Spectrum Sharing for Soft Failure Recovery`（JOCN 2018）已经研究：软故障后通过更鲁棒调制恢复 QoT；高优先级光路可以扩展频谱并挤占低优先级光路。其业务差异主要由静态 rate guarantee / priority 表达。

### Training-aware optical allocation side

- `Accelerating model synchronization for distributed machine learning in an optical wide area network`（JOCN 2022）联合考虑训练 job 信息、光拓扑、波长和带宽分配，但不以 soft failure 为场景。
- `Resource Allocation in Flexible-Bandwidth Fine-Grained Optical Transport Networks for Geo-Distributed Machine Learning`（IEEE IoT-J 2025）已考虑任务依赖、优先级、带宽调整和 task completion ratio，但不以 soft-failure-induced QoT / modulation transition 为核心。
- `CD-CBA`（JOCN 2026）已经根据 pipeline-parallel training 的 communication-bound 状态分配光网络频谱，以降低 bubble、迭代时间和阻塞，但未在已获得的摘要中建模 soft failure recovery。
- `Memory-aware and spectrum-efficient co-scheduling for large model training over heterogeneous optical WANs`（OFT 2026）已经联合内存约束、训练负载与 EON 频谱分配，但未在已获得的材料中研究 soft failure recovery。

## Key Assessment

`DISC-SF-1` 与 `DISC-SF-2` 不宜包装成两个独立研究问题：

- `DISC-SF-1` 描述软故障恢复动作导致容量变化及训练性能退化，是问题机制。
- `DISC-SF-2` 描述在有限频谱下由哪些业务承担降速或频谱让渡，是决策冲突。

二者合并后才更接近一篇完整论文。

## Candidate Paper-level Hypothesis

### DISC-HYP-A — 训练关键性驱动的光层软故障恢复

**Statement**

在多训练任务共享弹性光网络的场景中，当软故障迫使受损光路改变调制格式并触发扩谱或降速时，按静态业务优先级选择频谱受让者/牺牲者，可能无法最小化训练损失；利用同步训练的通信瓶颈、flow-to-job 依赖和当前任务关键性联合选择调制、频谱与速率调整，可能在满足 QoT 的同时降低加权迭代时间或任务完成时间。

**Optical-layer core**

- soft-failure-induced modulation transition；
- QoT constraint；
- routing / spectrum / rate reconfiguration；
- spectrum continuity / contiguity；
- 频谱扩展与业务降速之间的选择。

**Computing-network coupling**

训练层不负责解决光故障，而是提供“同样的带宽损失对不同 flow/job 的实际代价”。同步屏障、pipeline bubble 或关键通信路径可能使该代价呈非线性，因而不能仅用静态业务优先级表达。

**Why this may be a complete paper story**

1. **现象**：软故障后的光层自适应可以保持连接，却造成容量变化或频谱挤占。
2. **矛盾**：QoT 恢复与有限频谱竞争；保护一条光路可能损害其他训练流。
3. **现有边界**：soft-failure spectrum sharing 使用静态业务等级；训练感知光资源分配主要研究正常/拥塞条件，尚未在本轮材料中看到二者在软故障恢复中的直接联合。
4. **研究问题**：如何利用训练通信依赖度量降速代价，并联合决定调制、频谱和速率调整。
5. **可验证结果**：与静态优先级、纯光层最小频谱代价、纯训练感知带宽分配比较 QoT 满足率、频谱占用、阻塞率、iteration time 和 JCT。

**Falsification conditions**

- 静态优先级与训练关键性高度一致，联合信息不改变恢复决策；
- 训练性能对研究范围内的容量变化近似线性，普通 weighted bandwidth allocation 已足够；
- soft failure 恢复时始终有充足备用频谱，不存在受让者/牺牲者选择；
- 训练感知方法不能在相同 QoT 和频谱预算下显著改善训练指标；
- 后续回查发现已有工作已经联合建模相同 failure model、training semantics 和 optical decision variables。

**Current confidence for further investigation**: MEDIUM

## Main Risk

最大的风险不是“有没有算法可做”，而是问题可能退化为：

> 将现有 soft-failure spectrum sharing 的静态优先级，替换为训练任务权重。

要避免这一点，必须证明训练依赖产生了静态优先级无法表达的结构性决策，例如：

- 同步屏障使最慢关键流决定整个 iteration；
- 同一个 job 的多条流必须协调降速，单流局部最优不等于 job 最优；
- pipeline 不同通信边的带宽损失对 bubble 的影响不同；
- 牺牲非关键流可能不影响当前 iteration，而轻微损害关键流会放大整个 job 的完成时间。

如果不存在上述至少一种结构，本候选应被 REJECT，而不是仅靠“大模型训练”标签继续。

## Human Review Questions

1. 是否接受“多训练任务共享 EON，soft failure 后存在扩谱/降速选择”作为目标系统模型？
2. 是否接受将核心问题限定为训练关键性驱动的 modulation + spectrum + rate 联合恢复？
3. 你的设备/仿真条件是否能表达 soft-failure-induced QoT 变化和调制格式切换？
4. 是否有可获得的训练通信 trace 或可信的 iteration-time / bubble 模型用于评价？

本文件只证明该问题具有形成论文叙事的可能性，不证明 novelty。

## Human Decision and Back-check

- Human decision：`KEEP`（2026-10-05）。
- Targeted back-check：`research/backchecks/DISC-HYP-A.md`。
- Initial metadata-level decision：`KEEP`，confidence `MEDIUM`。
- Four-closest-work full-text audit：`REVISE`，confidence `MEDIUM`。
- 修订边界：只讨论 QoT-aware rerouting 无法提供足够残余带宽、soft-failure modulation fallback 形成不可避免容量缺口的场景；必须证明 QoT/调制可行域与训练依赖共同造成静态等级、GARA 类 task priority 或 CD-CBA 类 communication-bound allocation 无法表达的跨作业牺牲决策，否则应 REJECT。
- Minimal problem validation：`research/investigations/soft-failure-training-impact/minimal-problem-validation.md`，结果 `CONDITIONAL_PASS`。
- Synthetic stability check：`research/investigations/soft-failure-training-impact/minimal-stability-check.md`，结果 `PASS`（81 个邻近组合中 23 个产生更优组合决策；仅表示结构稳定，不是现实网络实验）。
