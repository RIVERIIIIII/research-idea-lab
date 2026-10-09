# 从光层到任务损失：证据先行早筛

日期：2026-10-09。仅做小规模探索；不改正式 corpus、GAP/HYP/IDEA 或人的既有决定。未检索到某种工作不等于它不存在。

## 已核实的证据边界

1. **光层异常能够穿透到数据传输层，但并非每次异常都如此。** [OpTel（NSDI 2022）](https://www.usenix.org/system/files/nsdi22-paper-miao.pdf)第 4.1 节/Fig. 9 的受控光纤损耗实验显示：当接收功率跌过门限，post-FEC BER、帧错误和 CRC 丢包上升；在未越过门限时，物理层指标变差却未影响数据传输。其腾讯骨干网数据统计了短时 optical events，但没有报告这些事件造成的大模型任务损失。不能把受控实验结果冒充每次生产事件的后果。
2. **部分故障的真实光层范围可能细于光纤段。** [IMC 2016 骨干网测量](https://people.csail.mit.edu/ghobadi/papers/failures_imc_2016.pdf)区分光段级与部分波长/通道级的故障；这为光层故障建模提供依据，但没有直接给出 AI 任务指标，也不足以证明算网联合决策优于既有保护。
3. **强保护机制可能消除任务可见的切换损失。** [JOCN 2026 OTN 训练现场试验](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-18-5-492)报告其特定配置下 hitless 主备切换不降低 pipeline-parallel training efficiency；[JOCN 2026 WSON 实验](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-18-9-C173)报告实验室和现网的亚 50 ms 光层保护，但公开摘要不提供可独立核查的训练迭代损失数据。这两篇不能推论所有网络/故障都无任务损失。
4. **算网可靠部署已有直接先例。** [JOCN 2024 RAR-based DMT](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-16-5-527)以节点/链路故障可能中断训练环为动机，联合考虑算力、波长和可靠性；仅添加训练工作负载或故障标签不足以表明独立贡献。
5. **“光资源负载改变硬故障风险”目前主要是模型证据。** [JOCN 2015](https://opg.optica.org/jocn/abstract.cfm?uri=jocn-7-3-A482)提出随平均占用等工作条件变化的器件可靠性*估计模型*；[Optical Switching and Networking 2019](https://www.sciencedirect.com/science/article/pii/S1573427718300663)已研究据此进行可靠性感知 RWA。当前未核实运营网中“增加波长负载 → EDFA 实际硬故障率提高”的因果测量，也未见由训练放置带来的独立任务收益。

## 本轮判定

**不新增候选。** OpTel 的光层→丢包实验可作为未来任务后果假设的基础，但它自身不证明 AI 任务损失；“短时光异常＋训练”接近已早筛的间歇故障/诊断线索。负载驱动 EDFA 故障风险尚欠现实校准，且可靠性感知光路选择已有强基线。没有 AI 任务现场实测**不是单独的一票否决项**；关键仍是能否提出可检验的任务后果，并展示光层特有约束与算网联合决策相对强基线的必要性。

`IDEA-002` 继续 ON HOLD。下一轮应优先核对**事件级光层—数据传输层—任务指标**的完整证据，或提出能被强保护方案直接推翻的最小场景；不从“故障＋AI”关键词直接造 IDEA。
