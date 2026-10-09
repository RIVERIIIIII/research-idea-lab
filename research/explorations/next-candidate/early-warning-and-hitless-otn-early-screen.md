# 预警避障与 OTN 保护切换：两条线索的早筛

日期：2026-10-08。依据已确认的 Research Brief 做小规模 exploratory search；不改变正式 corpus、GAP、HYP、IDEA 或人的淘汰决定。这里的 REJECT 仅针对**当前问题表述**，不代表相关工作已被穷尽。

## 线索一：光纤故障预警后提前迁移训练任务

**待检验推断**：如果光纤传感提前发现可能发生的断纤，则在有限告警窗口内联合改变光路保护、任务放置或状态备份，可能避免训练中断。

**已知证据和强基线**：

- [OFC 2024 部署网光纤传感实验](https://opg.optica.org/abstract.cfm?uri=OFC-2024-Tu2J.6)检测并定位了埋地光缆旁的挖掘机与风镐扰动；其摘要没有证明可靠的故障发生预测、足够的预警提前量或 AI 任务收益。
- [JOCN 2017 预警数据备份](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-9-6-536)在假定的告警窗口内联合选择安全数据中心、备份路由和待备份数据量。
- [Computer Networks 2020 预警服务保护](https://doi.org/10.1016/j.comnet.2020.107419)已针对光纤及数据中心受灾，联合考虑请求重路由、请求改向与服务迁移。
- [HPDC 2020 预测触发 checkpoint/live migration](https://www.ornl.gov/publication/orchestrating-fault-prediction-live-migration-and-checkpointing)已有任务侧故障预测与状态保护的强基线；它不是光网研究，不能据此声称光网联合问题已完全解决。
- [Gemini（2023）](https://www.amazon.science/publications/gemini-fast-failure-recovery-in-distributed-training-with-in-memory-checkpoints)研究分布式训练的内存检查点与快速故障恢复，是训练状态保护的另一任务侧基线；不研究光纤故障预警。

**缺口与判定**：从“光纤扰动可检测”到“具有可信、足够长的在线预警窗口”仍缺证据；“预警后迁移任务和改光路”的主体决策已有直接光网—数据中心先例。这些先例**没有被核实为已评估训练状态或完成时间**，但只把服务换成训练任务也不足以形成一篇独立论文。**REJECT 当前表述，不创建候选。** 若未来要重开，须先有目标光网可操作的预警窗口，并指出 AI 任务状态和光层约束相互改变保护选择的具体情形。

## 线索二：OTN 主备切换的瞬时损失使跨 DC 训练停顿

**待检验推断**：光路故障倒换即使很快，也可能短时丢比特或丢包，使 pipeline-parallel 训练停顿；也许需要联合保护与训练状态调整。

**直接任务级反证与光层强基线**：

- [JOCN 2026 的 240 km 现场试验](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-18-5-492)报告其 PFC-assisted hitless 800G OTN 在主备路径倒换时使 pipeline-parallel training efficiency 不受倒换影响。该结论只适用于论文所测设置，不能外推为所有光网都无瞬时损失。论文的 52%→99.51% 比较是 **120 km 条件下 PFC 开/关**，不是故障切换的收益数值。
- [JLT 2020 无丢比特 OTN 保护实验](https://doi.org/10.1109/JLT.2020.2967510)将故障预测、主动维护和 bit-lossless protection 联用；构成直接光层替代方案。

**缺口与判定**：目前没有证明在目标广域算力光网中，强光保护之后仍有训练可观测损失；也没有展示为何任务状态必须参与光层保护选择。**REJECT 当前表述，不创建候选。** 这不否定其他设备、故障或保护方案可能存在切换损失，只是现有表述尚未通过候选门槛。

## 共同结论

这两条线索均不能仅凭“可能影响训练”晋升为 IDEA。它们还需要相对上述强基线的具体失效条件、可观察任务损失，以及算网统一决策或双向耦合的必要性。`IDEA-002` 仍为 ON HOLD；本次没有正式 novelty 判断或完整文献检索。
