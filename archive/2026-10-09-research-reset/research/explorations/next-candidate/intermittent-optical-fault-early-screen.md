# 间歇光故障与反复保护切换：早筛排除

日期：2026-10-07。依据已确认的 Research Brief，仅做小规模方向早筛；不是正式 corpus、GAP、HYP 或 IDEA，也不是 novelty 判断。

## 直觉问题

间歇性光层信号退化使业务在工作/保护光路之间反复切换。同步训练可能比一次较长但稳定的降速更容易受到反复中断影响。于是设想让光层等待恢复、防抖与训练状态协同决策。

## 已有证据和强替代方案

- ITU-T G.798.2（2026）对光媒质层保护说明：为了防止间歇故障导致保护开关频繁动作，已规定/描述 wait-to-restore（WTR）机制；故“防止光层反复切换”不是未被考虑的问题。[ITU-T 正式文本](https://www.itu.int/epublications/en/publication/itu-t-g-798-2-2026-02-characteristics-of-optical-transport-network-hierarchy-equipment-functional-blocks-media)。
- OpenAI 的 MRC 系统报告训练网络链路 flap 会影响同步训练，并展示在其数据中心网络中快速绕开链路故障、使部分链路 flap 对任务无可测影响。这证明任务侧后果和强系统替代方案同时存在，但**不是广域 EON 的实测证据**。[工程报告](https://openai.com/index/mrc-supercomputer-networking/)。
- EON 中 QoT 退化后的路由与调制自适应已有实验研究，不能将其当作空白。[JLT 2013 原论文](https://opg.optica.org/jlt/abstract.cfm?uri=jlt-31-4-664)。

## 早筛决定

**REJECT 当前表述。** WTR/防抖负责光层稳定性，快速多径负责部分任务连续性；仅将训练阶段或任务优先级加入 WTR 参数，不足以证明算网双向耦合，更难与既有故障后跨层恢复形成独立论文叙事。没有证据表明在目标广域 EON 中，这些强基线仍因某个光层特有约束而失败。

这不是“间歇光故障不重要”或“没有相关研究”的结论。只有出现明确的、WTR 和任务侧绕障都处理不了的光层可行域冲突及可观察任务损失，才值得重开。
