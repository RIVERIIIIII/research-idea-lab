# SRLG 相邻分支：定向早筛

## 范围

依据已确认的 `research/research-brief.md`，只检验三个可能形成独立问题的 SRLG 分支。此处不是正式 corpus、系统综述或 novelty 结论；不写入 `papers/candidates.jsonl`、`papers/selected.jsonl` 或 `research/candidate-ideas.md`。判断标准是：光层特有约束、AI 任务级后果、算网双向耦合、相对强基线的非平凡差异。

## 1. 训练阶段感知的分时备份频谱

**假设性问题：** 同一 SRLG 同时切断多条训练光路时，备份光路不能凭“不同工作故障不会同时发生”而共享同一资源；若通信峰值在时间上错开，是否可以在故障后通过训练调度与光层保护的联合决策，减少预留频谱且不延长训练完成时间？这仍是待证明的机制，不是已观察事实。

**直接先例（全文已核对）：** Cai 等，*Robust Time-Shared Backup Strategy for Training of Large Models in Cloud-Edge Optical Networks*，INFOCOM Workshops 2025，DOI `10.1109/INFOCOMWKSHPS65812.2025.11152930`（[IEEE 正式页面](https://ieeexplore.ieee.org/document/11152930/)；用户提供的 6 页 PDF）。第 2 页 Sec. II-A 明确提出两个训练请求 A/B 在错开的时间块复用同一备份光路上的频谱槽，图 3–4 给出机制；第 4 页 Sec. III-A/B 将 DNN 切分点、六阶段训练时间、计算容量、工作/备份路径和频谱槽纳入模型；第 5 页 Sec. IV-A 再次规定“共享备份链路且传输时间块不重叠”即可共享频谱。故“利用训练空闲期错峰共享备份频谱并联合计算/光路资源”的核心表述已被直接覆盖。

**仍未覆盖但未证明有价值的边界：** 该文工作/备份路径要求 link-disjoint（第 4 页表 I），结论声明保障任意**单链路**故障（第 6 页）；第 6 页图 8 虽画出不同数量的 failed links，但未给出 SRLG 成员、同一共因事件或同故障激活的备份资源竞争模型。不能据此声称它已处理 SRLG；同样不能仅因没有写 SRLG 就断言“SRLG 版本”是创新点。另有 2026 年 *Joint spectrum-time sharing maximization scheme with shared-path protection for elastic optical data center networks*，其[出版商摘要](https://www.sciencedirect.com/science/article/pii/S1068520026000945)明确研究依据光路释放时间复用共享保护频谱。

**技术风险：** 若设想需要按训练迭代频繁重配光路/频谱，控制与光交换时间可能抵消收益。必须将预留的光层资源与故障后更细粒度的业务复用区分，不能把分组层的时间复用直接当作频谱节省。

**早筛决定：REJECT 当前表述（不晋升候选）。** Cai 等已经实现该方向的主体机制。仅把单链路故障改成 SRLG 输入，很可能只是故障集合扩展；若要重开，必须先展示同一 SRLG 同时失效时，现有时间块共享策略在哪个明确约束下失败，以及新的算网联合决策为何不能靠增加 SRLG-disjoint 条件或普通训练重排解决。这里的“很可能”是模型判断，不是论文结论。

## 2. SRLG 后保留健康 DC 的算网联合渐进恢复

**假设性问题：** 一个区域性 SRLG 故障后保留未损坏 DC 的算力，随光网络修复逐步重新放置训练任务和恢复连接。

**强反证：** [*Progressive Recovery of Virtual Infrastructure Services in Optical Cloud Networks After Large Disasters*（OFC 2016）](https://opg.optica.org/abstract.cfm?URI=OFC-2016-W1B.6)和[*Joint Progressive Recovery of Optical Network and Datacenters After Large-Scale Disasters*（OFC 2017）](https://opg.optica.org/abstract.cfm?uri=ofc-2017-Tu3E.5)已经明确研究光网与数据中心的灾后渐进恢复；此外已有[灾后 essential/global re-provisioning 比较](https://opg.optica.org/abstract.cfm?uri=jocn-7-5-392)。本项目已发表工作又覆盖故障后训练的算网联合恢复。

**早筛决定：REJECT 当前表述。** “不要丢弃健康算力”本身是自然基线，不足以支持独立贡献。除非发现上述方法无法表达的光层/训练特定约束，否则不继续投入。

## 3. 不确定 SRLG 的定位与自适应保护

**假设性问题：** 共享风险关系不完全已知时，利用遥测和任务性能反馈更新风险判断，再联合调整光层保护与算力运行。

**强反证：** [*Failure Localization for Shared Risk Link Groups in All-Optical Mesh Networks Using Monitoring Trails*（JLT 2011）](https://ieeexplore.ieee.org/document/5739499/)覆盖 SRLG 定位；[*Differentiated Quality-of-Protection Provisioning with Probabilistic SRLG in Flexi-Grid Optical Networks*（2013）](https://opg.optica.org/abstract.cfm?uri=acpc-2013-AF2G.8)覆盖概率型 SRLG 保护。把训练性能症状作为额外反馈，若不能证明它改变光层风险识别或联合决策的可行性，目前只是已有组件叠加。它也与现有软故障诊断讨论方向高度接近。

**早筛决定：LOW PRIORITY / HOLD。** 暂不作为独立 SRLG 候选。只有提出可观测且可验证的反馈闭环，并经强基线比较后再重开。

## 总结

三个分支目前都不应晋升为 `IDEA-*`：分时备份的核心机制已被 Cai 等论文直接覆盖；保留健康 DC 的渐进恢复按当前表述被既有工作覆盖；不确定 SRLG 方向缺少相对定位与概率保护的独特机制。此结论只是在有限检索下的资源分配决定，不等于证明这些方向没有研究空间。
