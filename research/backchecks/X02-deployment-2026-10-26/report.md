# X02：推理依赖什么连接，何时值得改变服务站点

日期：2026-10-26。定向证据回查；不改变正式 corpus、GAP/HYP decision、置信度或候选状态，不宣称创新性。当前范围遵循 CONFIRMED Research Brief。

## 本轮回答

**有证据支持：跨站推理确实存在持续通信依赖；光网络原端点恢复受资源可行性限制；改变服务站点可以增加恢复选择。尚未建立：某种真实光故障必然要求采用 EdgeFlow 式迁移。**

证据分三层：①推理系统部署/原型中实际存在的数据流；②光网络故障与经典服务恢复机制；③把两者连接起来的跨层推导。③不能冒充①中的光故障实测。

## 1. 什么连接受损会影响正在运行的推理

| 连接对象 | 受影响的工作 | 证据与限制 |
|---|---|---|
| 客户端/接入网关—解码站点 | 用户收不到后续 token；服务器可能仍在计算。恢复连接不等于迁移计算状态 | P/D-Serve 的持续流式响应支持这一依赖。是否由某条光路承载，需另给算网映射 |
| 跨站模型分段：客户端与远程模型块之间 | 每轮生成需传递激活值；相应路径不可用可能使生成停顿 | Petals 的真实跨地域实验与故障恢复机制支持。不能据此声称商业跨城光网已发生该故障 |
| 跨站 Prefill—Decode 的 KV 交付连接 | 影响尚未完成 KV 交接的请求及其首 token/切换；**KV 已完整到达且本地解码的请求，不一定再依赖此连接** | PrfaaS 的跨集群交付设计；PDD 还有本地 Relay Decode，可以边生成边交付。两者均不是光故障恢复实测 |

这里的“光连接”必须落实为：**哪两个业务端点的数据流，映射到哪些光路/承载路径，故障后还剩什么备用资源。** 光纤断裂可能影响多条光路；一条光路受损也可能已被下层保护屏蔽。不能把“光纤有故障”直接写成“推理请求中断”。

历史运营网络故障研究记录了跨数据中心长途链路问题及光保护可能引出的上层扰动，但没有 LLM 请求日志。它支持故障链的网络部分，不能提供本课题所需的现代推理中断概率或统一恢复时间。[E07]

## 2. 已有原端点光恢复为何可能不足

这里“原端点恢复”指维持服务所在站点，重建到该站点的连接；不等于等待物理光纤修好。

| 情况 | 判断 |
|---|---|
| 保护路径可迅速切换，且恢复后的性能满足业务要求 | 优先恢复连接；迁移可能徒增停顿、状态传输和资源竞争 |
| 拓扑上有绕行路，但缺少可分配波长/容量 | 原端点恢复仍可能失败；这是已有光云迁移研究明确处理的情形 [E05] |
| 连接重建可行，但完成太晚或恢复后的性能不满足请求要求 | 是值得建模的条件；本轮文献未证明它在目标生产推理部署中的发生频率，须作为待核验前提 |
| 已有可达且状态可用的备份站点 | 应比较直接启用备份，不能默认必须搬运原站点 KV [E06] |
| 原站点不可达，状态又只保存在原站点 | 不能假设 EdgeFlow 式在线状态搬运可执行；需另有可达副本、客户端历史或重算输入 |

“恢复不了原站点就换站点”已是经典机制。2016 年研究已经计入状态体积、传输速率和迁移停顿；2021 年 SCORE 已区分原站点恢复、备份启用、向第三站点迁移。不能把这些概念本身当作新贡献。[E05–E06]

## 3. 迁移何时才有价值

以下是基于证据的**研究推导，不是已验证的性能结论**。至少同时检查：

1. **有必要**：原端点恢复不可行，或其请求损失/时延明显更差。
2. **搬得动**：旧状态可读取且传输路径可达；否则明确改为从副本/客户端记录重建，不能混称源端迁移。
3. **接得住**：目标有兼容模型、计算和显存，迁移通路及迁移后的服务通路均能配置。
4. **来得及且值得**：把故障检测、决策、光配置、状态准备/传输/重建、切换和客户端重连全部计入后，仍优于可用替代方案。

若故障检测后业务还允许停顿 H，可先以 T_move ≤ H 检查迁移方案；原端点方案同样计算 T_same。T_move 不能只用“KV 字节数/带宽”。若两者均超时，迁移未必满足连续性目标；若两者均可行，需比较请求损失、恢复后性能及网络/计算成本。具体 SLO、H 和代价权衡均未由本轮证据确定。

**反例必须保留**：切断用户到 A 的路径，不代表 A 到 B 也断；但若同一割集同时隔离 A，迁移也可能被阻断。必须画出三类路径：用户到旧站点、状态源到新站点、用户到新站点，不能只画第一条。

最低比较基线：原端点保护/恢复、预存状态备份启用、可达源的在线迁移、从其他记录重建，以及请求终止/重试。仅将新请求重定向，不等于恢复已有会话。

## 4. 本轮原文证据索引

下列 E 编号仅在本报告命名空间 `X02-DEP-20261026` 内有效，不占正式 evidence/note sequence。已检索记录的稳定 paper_id 见 reading-selected.jsonl；不新建正式卡片。

| ID | 文献、版本与定位 | 可以支持什么；不能支持什么 |
|---|---|---|
| E01 | **Distributed Inference and Fine-tuning of Large Language Models Over The Internet**（Petals），[arXiv:2312.08361v1](https://arxiv.org/html/2312.08361v1)，§3.2、§4.2 | 跨地域分段推理、逐轮激活通信；断连后可用客户端保存的输入激活在替代服务器重建 KV。不是从失联源读取 KV，也不是光纤断裂实验 |
| E02 | **P/D-Serve: Serving Disaggregated Large Language Model at Scale**，[arXiv:2408.08147v1](https://arxiv.org/html/2408.08147v1)，摘要、§3.2、§3.4 | 有商业部署；故障处理明确未采用请求迁移，可能清理并结束已有响应。实例恢复不能当作原请求无缝恢复；其 region 不能自行解释成跨城市 |
| E03 | **Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter**，[arXiv:2604.15039v2](https://arxiv.org/html/2604.15039v2)，§3.1、§4.1 | 远程 Prefill 向本地解码交付 KV；有双集群 profiling，但文中吞吐/带宽结果来自测量数据驱动的模型。不是生产光故障恢复实验 |
| E04 | **PDD: Unleashing Economical and Flexible Heterogeneous LLM Inference via Cross-Datacenter Prefill-Decode Disaggregation**，[arXiv:2609.13161v1](https://arxiv.org/html/2609.13161v1)，架构、§4.1 | 本地 Relay Decode 可在跨站 KV 交付期间生成；双集群实验用 2×10Gbps 专线模拟跨数据中心连接。不能推断交付链路受损必使所有已生成请求停顿。HTML 日期与编号月份有冲突，不据此判断发表先后 |
| E05 | **Restoration in Optical Cloud Networks With Relocation and Services Differentiation**，JOCN 2016，[DOI:10.1364/JOCN.8.000100](https://doi.org/10.1364/JOCN.8.000100)，[作者稿](https://www.diva-portal.org/smash/get/diva2:925332/FULLTEXT01.pdf)，§III、Eq.(3)、HRP 算法（PDF 3–5页） | 单光纤链路故障后，HRP 先找有足够波长的原站点路径，再考虑其他有资源站点；计入迁移停顿。WDM 仿真，不是 LLM 实测；固定传输速率模型不能证明已覆盖 LLM 状态与光资源联合选择 |
| E06 | **Storage Protection with Connectivity and Processing Restoration for Survivable Cloud Services**（SCORE），ICCCN 2021，[DOI:10.1109/ICCCN52240.2021.9522324](https://doi.org/10.1109/ICCCN52240.2021.9522324)，[作者稿](https://research.chalmers.se/publication/526151/file/526151_Fulltext.pdf)，§III、Fig.3、§IV（含封面 PDF 4–7页） | 先恢复原站点，再启用预存一致存储的备份，最后向第三站点迁移；后者需状态传输可行。模型/仿真，不自动证明持续变化的 LLM KV 可直接按该假设复制 |
| E07 | **An Empirical Analysis of Intra- and Inter-Datacenter Network Failures for Geo-Distributed Services**，SIGMETRICS 2013 Extended Abstract，[微软原始出版记录](https://www.microsoft.com/en-us/research/publication/empirical-analysis-intra-inter-datacenter-network-failures-geo-distributed-services/)，[原文镜像](https://netman.aiops.org/~peidan/ANM2017/9.EventPrediction/ReadingList/network%20failures/sigmetircs13-An%20Empirical%20Analysis%20of%20Intra-%20and%20Inter-Datacenter.pdf)，§2、§3.2 | 运营网络日志说明跨站链路故障及光层事件与上层链路扰动的关系；缺少应用日志且部分故障原因难归因。文中引述的恢复耗时不能当现代光网络统一参数 |

## 5. 对 X02 的含义及后续最小工作

本轮更正了背景论证，但**不自动改写 HYP-001 的故障模型或推进候选**：

- EdgeFlow 的可达源迁移能力不能直接套到“源站点失联”。Petals 提供了另一种可恢复状态来源，也带来不同通信与存储代价。
- 若继续 X02，应先选定真实数据流：持续分段解码、用户流式连接，或 KV 交接。三者不能混成一种故障背景。
- 对选定场景画故障前后路径、状态位置和资源表；比较至少一种原端点恢复和一种已有备份恢复。用纸面反例检查迁移是否可行、是否有净收益，无须先搭完整仿真。
- 只有当任务状态/时限改变了**恢复端点、光路径、波长/频谱、容量或共享分配**，才继续论证光网络贡献。单独加速 KV 搬运不足以满足 Brief。
- 当前还缺目标部署的实际光承载映射、保护配置、故障后剩余容量与应用时限。若无法获得现场数据，可明确采用“实证任务架构 + 显式光网模型”的研究设定；不能标作完整生产故障案例。

## 检索与材料边界

使用项目 `skills/literature-search/SKILL.md` 完成检索/下载；本报告另作原文核验与机制推导。OpenAlex 两次运行分别返回20条、8条记录，**未宣称合计28篇独立论文**。查询、元数据与报错见 search-run*.json、exact-run.json 及隔离 JSONL。初次 DNS 失败保留；网络重试成功。网页补充检索及阅读入口见 web-search-log.md。

六篇定向下载成功五篇，2016作者稿超时；已通过网页 PDF 全文读取。2013镜像下载403，但网页工具可读取两页全文。下载文件 SHA256、页数见 pdf-manifest.json，抽取文本在 text/。未下载成功不伪称本地可用。

本轮没有修改正式 papers/candidates.jsonl、papers/selected.jsonl、note-registry.json 或既有卡片；工作区原有改动保持。本报告不替代完整系统综述或人工 prior-art 审查。
