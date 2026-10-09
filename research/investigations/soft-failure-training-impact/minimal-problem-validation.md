# IDEA-002 最小问题成立性验证

Status: `CONDITIONAL_PASS`

Synthetic stability check: `PASS`。在 81 个邻近合成组合中，23 个出现不同且更优的 job-group-aware 选择；差异集中于 2 个恢复 FS blocks 的中等稀缺区间（23/27）。详见 `minimal-stability-check.md`。

## Purpose

本文件只验证修订后的 `IDEA-002` 是否存在一个自然、可证伪、能够形成论文闭环的问题结构。不证明 novelty，不设计完整算法，也不扩大文献集合。

## Revised Problem Boundary

只考虑同时满足以下条件的场景：

1. 光层 soft failure 使受损光路 QoT 下降。
2. QoT-aware rerouting 已优先执行，但备选路径无法同时满足 QoT 与残余带宽需求。
3. 更稳健调制可以维持连接，却需要额外连续频谱；现有频谱不足以无损恢复所有流。
4. 多个同步训练作业共享受影响的 EON 资源，必须选择哪些流获得恢复频谱、哪些流临时降速。
5. 评价目标是 iteration time、pipeline bubble 或 JCT，而不只是恢复连接数、光路速率或静态业务等级。

只要第 2 或第 3 条不成立，问题就应交给快速重路由或普通光资源分配，不属于本候选。

## Minimal Counterexample

### Optical state

- 多条训练光路经过同一拥塞的 EON 区域。
- soft failure 使这些光路必须从高阶调制切换到更稳健调制。
- 每恢复一条流的原始速率，需要额外获得一个固定大小的连续 FS block。
- 受 spectrum continuity、contiguity 和当前占用限制，只能恢复两条流；其余流必须降速。
- 所有可行备选路径均已检查：或者 QoT 不满足，或者没有足够连续残余频谱。

这不是“有路却不重路由”，而是重路由无法消除后的剩余恢复冲突。

### Training jobs

设有两个同等级训练作业：

- `Job A`：当前 iteration 的同步屏障同时依赖两条受损流 `A1`、`A2`。两条流都恢复时，通信阶段从 80 ms 降至 40 ms；只恢复其中一条时，另一条仍决定屏障，通信阶段保持 80 ms。
- `Job B`：当前 pipeline 的关键边只有一条受损流 `B1`。恢复 `B1` 可使该 iteration 从 100 ms 降至 70 ms。
- 当前频谱预算只能恢复两条流。

候选决策如下：

| 选择 | Job A 改善 | Job B 改善 | 总任务级改善 |
| --- | ---: | ---: | ---: |
| `B1 + A1` | 0 ms | 30 ms | 30 ms |
| `B1 + A2` | 0 ms | 30 ms | 30 ms |
| `A1 + A2` | 40 ms | 0 ms | 40 ms |

该例表明，单流优先级或逐流即时边际收益可能先选择 `B1`，随后剩余一个 FS block 无法解除 `Job A` 的同步屏障；跨流、跨作业协调则可能选择 `A1 + A2`。决定性结构不是“训练流更重要”，而是同一作业多个流之间存在互补关系。

数值只用于展示可证伪结构，不是实验结果，也不证明现实网络中该情形常见。

## Can Existing Strategies Express It?

### Static rate class

如果 `A1`、`A2`、`B1` 属于相同 rate-guaranteed class，静态 gold/bronze 等级不能表达 `A1 + A2` 的组合收益。若人为把 `A1/A2` 预先设为更高等级，则只是把答案提前写入标签，无法适应 iteration 状态变化。

结论：不能稳定表达该最小反例。

### Per-flow weighted bandwidth utility

若目标是各流带宽收益的可加权和，恢复 `A1` 或 `A2` 会被错误地赋予独立收益；真实 barrier loss 是 `max`/组合函数。只有把完整 job dependency 写入 utility，才能表达该例。

结论：普通可加 per-flow utility 不足；job-level utility 可以表达，但这正是候选必须证明的结构。

### CD-CBA-like allocation

CD-CBA 已能把 `A1`、`A2`、`B1` 标为 communication-bound，并据此增加 FS；但已读方法主要按请求反馈增减 FS，没有研究 soft-failure QoT/调制可行域下、多个作业争夺不足恢复频谱时的组合牺牲选择。

风险：CD-CBA 可被扩展为全局 job-level optimizer。如果该扩展只需替换目标函数或增加一个 failure flag，候选贡献会偏弱。

### GARA-like task/subtask allocation

GARA 已能编码 task/subtask order，并通过全局仿真评价 TCR，因此理论上可能发现 `A1 + A2` 的组合收益。它当前没有 soft-failure QoT、离散调制转换、FS continuity/contiguity 和频谱牺牲关系，但这些变量可以被加入。

风险：这是当前最强反证。如果加入光层故障可行域后直接复用 GARA 类框架即可解决，候选可能只是已有训练感知资源分配的场景扩展。

## Why the Problem Remains Optical

候选只有在以下变量直接决定可行解时才属于光通信问题：

- soft-failure-induced QoT degradation；
- modulation/FEC transition 对所需 FS 数量的离散改变；
- spectrum continuity 与 contiguity；
- 路径上的可用连续 FS block；
- 哪些相邻或共享资源的光路能够成为 spectrum victim；
- rerouting、modulation adaptation、spectrum borrowing 和 rate degradation 的动作优先关系。

若把这些约束替换成一个通用 WAN 总带宽预算后，方法与结论基本不变，则该候选不满足 Research Brief，应被拒绝。

## Paper-story Closure Check

| 组成 | 当前是否成立 | 内容 |
| --- | --- | --- |
| 现象 | 是 | soft failure 后连接仍可维持，但调制降级造成扩谱或降速。 |
| 矛盾 | 是 | 有限连续频谱不能恢复所有训练流，保护一条流会挤占其他流。 |
| 现有方法边界 | 部分成立 | 静态 class 不读训练依赖；训练感知方法未建模该故障可行域，但可能容易扩展。 |
| 研究问题 | 是 | 如何选择恢复频谱受益流与降速牺牲流，使 job-level loss 最小。 |
| 可建模性 | 是 | QoT/调制/FS 可行域与 barrier/pipeline DAG 可形成联合约束。 |
| baseline | 是 | 快速重路由、静态 class、per-flow utility、GARA-like、CD-CBA-like。 |
| 指标 | 是 | QoT satisfaction、恢复/阻塞、频谱占用、iteration time、bubble、JCT。 |
| 可证伪性 | 是 | 若训练依赖不改变选择，或现有训练感知分配达到同等结果，则否定。 |
| 独立贡献潜力 | 条件成立 | 取决于联合结构是否超出“给既有算法增加故障约束”。 |

## Rejection Conditions

满足任意一项，应拒绝或再次收缩：

1. 目标负载下几乎总能找到满足 QoT 和带宽的备选路径。
2. 调制降级后通常有足够空闲连续频谱，不需要牺牲其他流。
3. barrier/pipeline dependency 不会改变受益流或牺牲流选择。
4. GARA/CD-CBA 仅加入 QoT 与调制约束即可得到相同决策，无需新的问题结构。
5. 把 EON 换成普通 WAN bandwidth budget 后，模型和算法没有实质变化。
6. 组合协调的收益只出现在刻意构造的极端参数中。

## Decision

### `CONDITIONAL_PASS`

该问题能够形成一篇论文的基本叙事，且最小反例说明 job-level dependency 可能产生逐流优先级无法表达的组合决策。光层 QoT、调制与连续频谱约束也可以成为不可替代的可行域，而不是背景变量。

但目前还不能给出无条件 `PASS`，原因是 GARA 类全局 task/subtask allocation 可能通过加入故障约束直接吸收该问题。候选是否足以形成独立贡献，取决于能否证明：

> 光层故障产生的离散、路径相关频谱可行域，与训练 flow group 的非可加依赖联合后，形成了现有训练感知光资源分配不能通过简单改目标函数获得的决策结构。

## Smallest Next Check

不进行完整实验，只需做一个小规模可行性核查：

1. 在 1 个 EON topology、2–3 个训练 jobs 和 1 个 soft-failure scenario 中生成 modulation fallback 后的 FS 缺口。
2. 先执行 QoT-aware rerouting，确认仍存在至少一组无法无损恢复的流。
3. 比较静态 class、per-flow utility 与 job-group-aware selection 是否产生不同受益/牺牲集合。
4. 检查这种差异是否在多个相邻负载/故障强度下存在，而不是单点构造。

若该小检查通过，`IDEA-002` 可进入正式候选讨论；若不通过，应停止投入并返回其他方向。

该检查已完成：合成参数稳定性通过，但尚未验证真实 EON/QoT 场景中的出现频率，因此总体决定仍为 `CONDITIONAL_PASS`。
