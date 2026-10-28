# 光层特有约束驱动的问题早筛（二）

## 范围

2026-10-07；依照已确认的 `research/research-brief.md`，只检查两个与已发表故障后训练恢复不同的机制。不更新正式论文 corpus、gap、hypothesis 或 `IDEA-*`。下面的“能否表达”判断属于模型推断，不是先例论文的作者结论。

## A. 故障修复后频谱碎片化与训练恢复

**直觉问题：** 光纤修好后，网络聚合空闲容量足够，但频谱槽不连续，原训练光路无法按原速率回迁；可否联合选择光路整理与训练配置，以减少任务完成时间？最小例子是某链路有 4 个空闲槽却分成 4 个单槽空洞，无法满足连续 3 槽的光路请求。这个例子证明碎片约束不是普通 WAN 总带宽约束，但不证明联合方法具有独立贡献。

**直接光层先例：** [AFRO](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-7-1-49)专门研究链路故障修复后的光路重优化与频谱碎片；[在线多域频谱整理](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-7-1-a7)和[低中断 make-before-break 整理](https://opg.optica.org/abstract.cfm?uri=ECOC-2011-Mo.2.K.3)覆盖光层动作及其扰动控制。

**直接算网先例：** `CD-CBA` 的全文卡 `papers/notes/009-CD-CBA-cross-domain-communication-bound-aware-resource-allocation.md` 已记录：它读取 pipeline 任务关键性，在频谱 continuity/contiguity/availability 约束下调整 FS 数量及候选路径，并以迭代时间、GPU bubble 和请求阻塞率评价。[@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E002] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E003] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E004]

**早筛：REJECT 当前表述。** 它把已研究的故障修复后整理和已研究的训练感知频谱分配并列，尚未指出一个两者都不能表达的训练配置/光层决策。进一步考虑“何时整理以避开训练关键阶段”也可能只是给整理动作加业务时窗；当前没有独立贡献证据。它还与已发表的故障后算网恢复过近。

## B. 跨域信息受限下的训练生存路由

**直觉问题：** 多个光网络域不共享内部 SRLG/频谱/QoT 细节时，如何保证跨域训练关键流在故障后的可恢复性，并联合调整训练放置？

**强先例：** [跨域相关故障生存路由](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-10-8-C39)已在域汇总信息下估计主备路径同失效概率并选路；[跨域可生存虚拟拓扑映射](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-8-6-408)已在分层控制平面中处理虚拟节点/链路的单光链路故障生存性；[多实体 network-cloud recovery](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-17-9-D53)进一步覆盖多主体协作恢复。`CD-CBA` 已将训练 communication-bound 状态接入多 DC 光路/FS 分配，但不研究故障。[@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E001] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E011]

**早筛：REJECT 当前表述。** “跨域信息受限 + 训练”目前只是把训练关键流送入成熟跨域生存路由/虚拟映射模型；未找到训练依赖强制改变信息交换量、风险约束或算力放置可行域的最小反例。要重开必须先证明这些模型在获得相同任务依赖和效用时仍无法处理的约束，而不是仅换目标权重。

## 结果

本轮没有新的 `IDEA-*`。这是避免把文献空白或关键词组合误认成独立论文问题的早筛结果。当前活跃的 `IDEA-002` 保持不变；仍需验证其现实发生条件和相对强基线的独立价值。
