# 光层软故障对大模型训练影响：讨论性假设

Status: HUMAN_REVIEWED

## Scope

本文件记录一次小规模定向调研，用于回答：在硬中断发生前，渐进式光层软故障可能通过什么机制影响分布式训练？

- 执行 5 条定向检索式。
- 原始结果 19 条，去重后 19 条。
- OpenAlex 返回 13 条，Semantic Scholar 返回 6 条；arXiv 本次受到 HTTP 429 限制。
- 结果保存在本目录的 `data/` 中，未写入正式 `papers/candidates.jsonl` 或 `papers/selected.jsonl`。
- 以下均为待讨论假设，不是创新性结论。

## Observed Evidence

1. 光层软故障可表现为物理层退化和 QoT/BER 恶化，并可用于提前发现 SLA 风险或硬故障风险。
   - [BER Degradation Detection and Failure Identification in Elastic Optical Networks](https://opg.optica.org/jlt/abstract.cfm?uri=jlt-35-21-4595)
   - [Soft Failure Localization During Commissioning Testing and Lightpath Operation](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-10-1-A27)
2. 更鲁棒的调制格式可恢复 QoT，但可能需要更多频谱；优先级流量扩谱还可能挤占低优先级连接。
   - [Exploiting Spectrum Sharing for Soft Failure Recovery](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-10-8-653)
3. 多层网络中的调制格式自适应可降低错误，但可能降低虚链路及其承载业务的容量。
   - [Autonomic Disaggregated Multilayer Networking](https://opg.optica.org/abstract.cfm?uri=jocn-10-5-482)
4. 预 FEC 指标与后 FEC 误码不是同一层面的量；因此，光层指标恶化并不自动等于上层已经出现丢包或吞吐下降。
   - [Information Rates and post-FEC BER Prediction](https://arxiv.org/abs/1611.09738)
5. 分布式训练对慢链路、网络拥塞和通信尾延迟敏感；可预测的资源变化也可以触发训练侧提前调整。
   - [GREYHOUND](https://www.usenix.org/conference/atc25/presentation/wu-tianyuan)
   - [Parcae](https://www.usenix.org/conference/nsdi24/presentation/duan)

## Discussion Hypotheses

### DISC-SF-0 — 零假设：软故障在硬中断前对训练不可见

**Statement**

如果 QoT/预 FEC BER 的恶化仍能被 FEC 完全掩蔽，且网络控制器没有实施改变业务容量的动作，则训练在硬中断前不会出现可观测的吞吐或迭代时间退化。

**Why it matters**

这意味着不能把“当前训练性能下降”作为研究问题的默认前提。研究只能围绕未来中断风险及动作时机展开。

**Falsification**

在没有容量调整或路径切换时，训练层已经稳定出现吞吐、collective latency 或 iteration time 恶化。

### DISC-SF-1 — 容量退化假设（当前最有直接依据）

**Statement**

当控制器通过降低调制阶数等方式维持 QoT、但同时降低虚链路可用容量时，通信受限的分布式训练会在硬中断前出现通信时间和迭代时间增长；因此，“光路仍可用”不等于“训练性能未受损”。

**Optical-computing coupling**

光层恢复动作决定容量变化，训练并行结构和通信占比决定该变化对任务完成时间的放大程度。

**Falsification**

实际设备能够在目标软故障范围内始终保持原始客户侧速率，或容量下降对目标训练任务没有可测影响。

**Confidence for investigation**: HIGH

### DISC-SF-2 — 频谱挤占与多任务影响假设

**Statement**

当受损高优先级连接通过扩展频谱维持速率时，影响可能从该训练任务转移到共享光网络中的其他任务：低优先级连接被降速、阻塞或重路由，从而造成跨任务完成时间恶化。

**Optical-computing coupling**

联合问题不是单流恢复，而是根据训练任务状态与业务代价决定有限频谱应由谁承担退化。

**Risk**

若训练状态不会改变最优资源分配，本问题会退化为已有的优先级频谱共享，仅仅替换业务标签。

**Falsification**

网络始终有足够空闲频谱，或静态业务优先级已经足以得到相同决策。

**Confidence for investigation**: MEDIUM

### DISC-SF-3 — 预测窗口与训练动作时机假设

**Statement**

即使软故障尚未造成当前训练性能下降，预测到的硬故障时间窗口仍可能使系统在损失较低的训练状态执行 checkpoint、并行策略调整、迁移或光路切换，从而减少中断后的重算和恢复代价。

**Optical-computing coupling**

光层提供风险与剩余时间信息，训练层提供随时间变化的动作代价；联合决策的价值来自“何时、以何种方式处理”，而不只是是否恢复光路。

**Evidence boundary**

当前证据分别支持光故障可提前预测，以及训练可利用可预测资源变化主动调整；尚未发现直接证明二者联合机制有效的工作。

**Falsification**

光层能够始终无损、瞬时恢复，或任何提前训练动作的代价都不低于硬故障后的期望损失。

**Confidence for investigation**: MEDIUM

## Current Recommendation

- 保留 `DISC-SF-0` 作为必须检验的基线。
- 优先讨论 `DISC-SF-1`：它具有最清楚的“光层动作 → 业务容量 → 训练性能”因果链。
- 将 `DISC-SF-3` 作为不依赖“当前已经变慢”的替代叙事。
- `DISC-SF-2` 仅在多任务共享频谱且训练状态确实影响资源决策时继续保留。

这些假设均未经过完整文献回查，不能据此声称 novelty 或 innovation。

## Human Review Decision

- `DISC-SF-0`: BASELINE — 保留为必须检验的零假设。
- `DISC-SF-1`: KEEP — 继续调研容量退化路径。
- `DISC-SF-2`: KEEP — 继续调研频谱挤占与多任务影响路径。
- `DISC-SF-3`: REJECT — 当前轮次不再研究预测窗口与训练动作时机路径。

KEEP 仅表示假设值得进一步调研，不代表已经形成创新点或通过创新性审查。
