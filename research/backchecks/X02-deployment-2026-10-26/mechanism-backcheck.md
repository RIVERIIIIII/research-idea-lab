# 步骤5定向回查：哪些机制已有，哪些差异仍未确认

日期：2026-10-26。检索用项目 literature-search skill；事实核验与机制判断另记。所有新材料隔离，不进入正式corpus，不分配笔记序号。

## 有界检索与访问

- OpenAlex四组机制查询返回11条，查询/结果/错误记录见 mechanism-search-run.json、mechanism-candidates.jsonl；包含不相关噪声，不能解释为11篇相关论文。
- 两组新发现论文的精确题名查询返回4条，见 mechanism-direct-search-run.json、mechanism-direct-candidates.jsonl；其中两条对应下列预印本。两次结果不合并宣称独立论文总数。
- 另用网页按 optical + migration + recomputation / state transfer / compression / service restoration，以及VM论文精确题名追踪作者稿；发现新预印本后读取其arXiv固定v1原文。网页检索不是完备覆盖。
- VM作者稿下载HTTP403，网页直接访问失败；仅使用搜索引擎索引的作者稿正文片段，不能声称已完成全文阅读。此前 abstract_only 的历史记录不改写，新增片段范围单列。

下列M-E编号属于本文件命名空间 `X02-MECH-20261026`，不替代正式笔记evidence ID。

## 新核验的关键证据

| 局部ID / 稳定paper_id | 原文与实际读取位置 | 支持及限制 |
|---|---|---|
| M-E01 / doi-c7fe628fcfa2a8e60d83506d89684e59b26afe081e3bc6b5ad5b115ee35f2c04 | **Efficient Routing and Bandwidth Assignment for Inter-Data-Center Live Virtual-Machine Migrations**，JOCN2017，[作者仓储记录](https://re.public.polimi.it/handle/11311/1024646)、[作者稿](https://re.public.polimi.it/bitstream/11311/1024646/1/Ayoub_JOCN2017_v6.pdf)。索引正文§II–III及结论片段 | 已把脏页、重复传输、迁移时长与选路/带宽关联。§III片段明确每节点OEO、因此不考虑波长连续性。不是“可变迁移量与网络配置”普遍未研究的依据；也不能从该假设推出其他光迁移工作均不研究连续性。未读全稿、未复核结果 |
| M-E02 / doi-1fd5461d0403c7e09dfb1b84e0b4078d8b77b23b1bb76db46b7b3c8496a240d3 | **When Does Distributed AI Inference Need More Wide-Area Bandwidth? A Co-Design Evaluation of Optical, Packet, and Software Levers**，[arXiv:2608.14967v1](https://arxiv.org/html/2608.14967v1)，§2.1–2.3、§3.2–3.3、§4–7 | 已比较跨站状态传输/重算，给出光容量与请求调度两时间尺度设计。是分析模型及后续测量计划，非完成的生产推理光故障试验；不移植其带宽或时延数值作本场景参数 |
| M-E03 / doi-b854adbf9dcbd9d95586c1cb3df1eafc31cafadb44df0abfd5ca4d4cba705c05 | **An Optical KV Cache Network for Disaggregated LLM Serving**，[arXiv:2610.18444v1](https://arxiv.org/html/2610.18444v1)，§II、§III-A/B、Algorithm1、§IV-A | 已按prefill进度预订OCS端口/电路并复用现有电路。评估为集群仿真并使用测得的prefill成本模型；不是跨域故障下接替模型段。提前配光路和任务感知配置本身不能再当贡献 |
| M-E04 / document_id: draft-tan-ccamp-onco-problem-statement-00 | **Optical Networks and AI Computing Orchestration (ONCO) Problem Statement, Use Cases and Requirements**，[IETF固定版本](https://www.ietf.org/archive/id/draft-tan-ccamp-onco-problem-statement-00.html)，§4.2、§5 | 已提出为跨域KV迁移按需配置光通道及算网协同需求。是2026-07-06的个人Internet-Draft，work in progress，不能称为已发布标准、算法或实验结论。不照搬其“零抖动”等一般性宣称作为本项目保证 |

NFV recovery strategies for critical services after massive failures in optical networks（DOI:10.1016/j.osn.2024.100790）本轮仍仅核对[大学出版摘要](https://portal.fis.tum.de/de/publications/nfv-recovery-strategies-for-critical-services-after-massive-failu/)；不能据此判断其完整状态/路径控制变量。网页还出现专利与非学术条目，只作未核验线索，不用于肯定或排除机制。

## 与原有最近邻一起看的结果

| 工作 | 明确已有的部分 | 本轮不能确认的部分 |
|---|---|---|
| EdgeFlow，正式卡032 E003–E006 | 可达源的KV/activation分配与目标选择 | 是否和实际光保护/恢复控制联合实现；原文已读模型给定端点带宽 |
| Petals，上轮E01 | 客户端输入历史支持替代模型段恢复 | 不能把其已有恢复能力据为本课题贡献；光路配置机制未由上轮读取建立 |
| PR-SRD2016，上轮E05 | 光故障后原端点恢复与换站，计入状态传输开销 | 不能声称尚无服务迁移或迁移停顿模型 |
| SCORE2021，上轮E06 | 原端点、备份、第三站点恢复；状态来源可为主/备数据 | 不能把“多个状态来源”本身称为新增；需区分已有等价备份与计算重建记录 |
| ctHO / Pallas，HYP-001-round1 | 已有计算/传输联合、主动准备与重叠 | 非光故障不能直接否定或证明光层机制差异，但须作强替代 |
| 本轮M-E01–04 | 可变迁移代价、光路编排、推理进度驱动电路配置均有直接相邻工作 | “联合优化+推理+光网络”仍不足以划出贡献；具体剩余机制须继续检验 |

## 对步骤5的约束

可以形成待检验草案：**从不同的可用信息恢复同一会话状态，会改变临时状态连接的端点与持续服务连接的资源需求，进而影响光恢复计划。** 但这只是可能的机制差异位置，尚未通过同机制prior-art核查，尤其不能将SCORE的主/备来源选择漏掉。

时间尺度是必须检查的新反证：若选定光层动作无法在请求停顿预算内完成，逐请求临时配置可能不适用；应比较已有/预配置资源或不同控制粒度，不能为了保住方案任意放宽时限。M-E02的时间尺度是其设计设定，M-E03是另一类集群OCS，均不能作为所有广域光设备的统一耗时。

本轮未找到完整相同方案不证明新颖性；本文件不改变HYP-001 decision，也不生成最终candidate idea。
