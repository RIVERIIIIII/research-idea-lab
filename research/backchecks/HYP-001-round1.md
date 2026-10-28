# HYP-001 首轮定向回查（2026-10-10）

- scope: 当前 CONFIRMED Brief；源端状态可用的软故障后推理恢复。
- decision: REVISE
- meaning: 收窄后值得继续调查，不代表有效性或新颖性成立。
- coverage: OpenAlex 四组查询、每组最多 3 条，得到 12 条，无接口错误；原始查询及结果见同目录 HYP-001-search-run.json 与 HYP-001-candidates.jsonl。另经网页定向查询和参考文献追踪核对下表。不是完整系统综述。
- isolation: 未将回查新记录写入正式 candidates/selected，未分配正式笔记序号。

## 最近邻与证据边界

| 工作 / 标识 | 本轮实际读取 | 已覆盖的机制 | 对假设的影响 |
|---|---|---|---|
| EdgeFlow；paper_id: doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226 | 既有 032，E003–E006 | 选择目标及 KV/activation 分界；带宽给定 | 迁移、重计算及目标联合选择本身不能作为新增机制 |
| Efficient Routing and Bandwidth Assignment for Inter-Data-Center Live Virtual-Machine Migrations；paper_id: doi-c7fe628fcfa2a8e60d83506d89684e59b26afe081e3bc6b5ad5b115ee35f2c04；DOI 10.1364/JOCN.9.000B12 | 出版社摘要，abstract_only；作者 PDF 本轮网页访问失败 | 脏页重复传输关联迁移时间和资源占用；联合路由与带宽配置 | 宽泛的“可变数据量与网络分配互相影响”已有相邻基础；尚不能据摘要判断连续频谱/QoT 细节 |
| Low-Latency Edge LLM Handover via Joint KV Cache Transfer and Token Prefill；paper_id: arxiv-2603.28018 | v1 HTML §II、§III 开头，partial_text | §II 式(4)、(11)联合 prefill 长度与多用户回传速率；同参数目标，切换后暂停流式生成 | “传输/重计算与网络速率联合优化”已经有直接 LLM 工作；token prefill 不等于 EdgeFlow 的 activation 投影重建 |
| Pallas: A Proactive KV Cache Migration Framework for LLM Inference in AI-RAN；paper_id: doi-89dffb3ebd183eb2362c0aa847b1304e52a09d0cdcbf29c30bd87d623b576e9a | arXiv:2608.16477v1 HTML §1–4.1，partial_text | 预测切换前重建历史前缀，同时同步新生成 KV；按有效 goodput 选择准备窗口 | 提前准备与通信/计算重叠也须作为替代机制；移动切换不等于光层故障 |

BC-E001（abstract_only）：doi-c7fe628fcfa2a8e60d83506d89684e59b26afe081e3bc6b5ad5b115ee35f2c04，出版社 Abstract，支持上表的 VM 机制描述，不支持尚未读取的物理层细节。

BC-E002（partial_text）：arxiv-2603.28018，§II-A–II-B 式(4)、(11)，支持已有联合分界与回传分配；§II-A 假设同模型参数且暂停生成。未复核其全局最优证明或仿真结果。

BC-E003（partial_text）：Pallas 上述稳定 paper_id，§3–4.1，支持提前准备和实测 goodput 输入。未将相关工作段对 ctHO 的评价替代 ctHO 原文证据；未复核性能倍数。

## 一手来源

- VM：[出版社摘要](https://opg.optica.org/jocn/abstract.cfm?origin=search&uri=jocn-9-3-B12)。
- ctHO：[作者预印本 v1](https://arxiv.org/html/2603.28018v1)。
- Pallas：[作者预印本 v1](https://arxiv.org/html/2608.16477v1)。

## 决策依据与修订

原假设的宽泛反馈关系不足以区分已有工作，因此 REVISE；没有证据要求整条物理关系为假，也不因目前未检索到完全相同标题而 KEEP。

修订后只检验一个更具体的问题：在源端状态可用、目标资源可用的光层软故障恢复中，KV/activation 表示选择能否跨越连续频槽、调制可达性及故障态 QoT 形成的可行性边界，从而改变恢复光路；光路选择又能否改变表示/目标选择，并在公平资源预算和全部成本下改善服务恢复时间？这仍是待检验关系，不能仅靠增加光约束宣布贡献。

必须加入的强对照：给定网络容量下的 ctHO 类联合重建/速率调度（按各自可执行状态表示比较）；EdgeFlow 自适应迁移；同动作集合的交替协调或联合最优参考；仅光恢复并原地续服务。模型并不兼容时明确差异，不能直接移植性能数字。

## 尚未完成的核查

1. VM 论文正文及其他 EON 服务迁移工作是否已包含同等离散可行性反馈；摘要不足以判定没有。
2. NFV recovery strategies for critical services after massive failures in optical networks（DOI 10.1016/j.osn.2024.100790）目前只作摘要级线索，待正文核验具体恢复变量。
3. Memory-aware and spectrum-efficient co-scheduling for large model training over heterogeneous optical WANs（DOI 10.1016/j.yofte.2026.104704）为邻近训练/频谱联合机制线索，待正文核验；期刊卷期标为 2026 年 11 月，在线首发日期未核实，不因卷期在当前日期之后而自动排除。
4. activation 可访问成本、迁移一致性及光配置时延仍未解决。

## 下一步最小检验

先构造一个明确标为合成的有限光资源例子，枚举目标、表示选择与可执行光配置，并与同预算强对照比较。检查选择是否互相改变、是否依赖频谱连续性/QoT、扣除重计算和配置成本后是否仍有净收益。没有差异就进一步修订或 REJECT；有差异只能证明机制可发生，仍须正文 prior-art 核查和人工 Review。
