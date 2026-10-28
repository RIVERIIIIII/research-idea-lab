# 第一阶段：经典光网络生存性机制表

## Scope & Coverage

Research Brief 为 `CONFIRMED`。当前覆盖 10 篇 selected 文献：1 篇 full_text、9 篇 partial_text、0 篇 abstract_only。补充 EON 综述使用带批注作者草稿，具体版本边界见笔记。此表为阶段一机制整理，不构成完整 literature review；尚未生成任务特性、gap、hypothesis 或创新性结论。

检索和筛选范围见 [阶段一检索报告](stage1-literature-search-report.md)。文献原文事实标为 supported，跨文献解释标为 inferred。supported 表示有可定位来源，不表示已独立实验证实。

## Research Problems

- **SURV-001** — status: supported。保护/恢复时间、控制粒度、资源专用/共享是不同分类轴，不应把“共享”当作与“保护”相对的概念。evidence: [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E001] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001]；derived_from: []。
- **SURV-002** — status: supported。保护的是指定故障集合下的连接/容量；单链路、单管道与多故障的保障范围不同。evidence: [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001]；derived_from: []。
- **SURV-003** — status: inferred。判断恢复至少应分别检查路径可达、资源可分配、故障状态 QoT、控制完成时间与服务约定，不能用单一“备份存在”代替。evidence: [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E003] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E002]；derived_from: [SURV-001, SURV-002]。

## Method Taxonomy

用五个维度描述每个方案：①何时决定路由和预留；②链路局部还是端到端；③专用还是共享；④是否预连接；⑤保障故障集合及恢复服务水平。它们可以组合，不是互斥方案名单。这是本报告的组织方式（综合推断），不是某篇论文提出的统一 taxonomy。evidence: [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E001] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001] [@doi-b5315866469261c081250bcdcf5fa7eef701933a1b79fb009fe7d265824076b9#E002] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E002]。

## Classical Mechanism Map

| 编号 / 经典问题 | 方案与原有决策 | 成立条件 / 风险模型 | 共享条件、成本与适用边界 | 证据 |
|---|---|---|---|---|
| M01 快速备用接管 | 1+1 双路发送、接收选择；1:1 故障后切换 | 备用通路与资源需可用；二者运行方式不同 | 1:1 可让低优先级业务使用备用；不能把“专用”一律写成双路同时发送 | [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E001] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001] |
| M02 故障局部绕行 | 链路保护在故障两端旁路；端到端路径保护重新连接原端点 | 绕行路由与波长可行，切换节点需存活 | 粒度改变路由空间与通知距离；不能固定宣称某类在所有设备上最快 | [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E003] |
| M03 降低备份预留 | SBPP 在兼容的故障情形间复用备份资源 | 本例为单链路故障，主备不相交 | 主路径不会被同一受保故障同时击中时，备份才可复用同一波长 | [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] |
| M04 故障后按现状恢复 | 动态寻找路由、预留并配置 | 剩余容量/波长可行且控制网络可工作 | 不足时可能失败；需计入搜索、信令与交叉连接时间 | [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E002] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E003] |
| M05 共享且减少实时切换 | p-cycle/FIPP 与 PXT 利用预连接结构；PXT 禁止分支点 | 不相交与共享兼容之外，还需交叉连接兼容 | 环/无分支结构限制路由；本组文献不支持所有系统均在 50 ms 内恢复的实测结论 | [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E002] [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E003] [@doi-b5315866469261c081250bcdcf5fa7eef701933a1b79fb009fe7d265824076b9#E001] [@doi-b5315866469261c081250bcdcf5fa7eef701933a1b79fb009fe7d265824076b9#E002] |
| M06 物理共因故障 | 管道/SRLG 约束同时用于主备选择与备份波长共享 | 已知物理风险映射；此文主要为单管道故障 | 逻辑链路不相交不够；主路径共管道时不能争用同一备用波长 | [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E002] |
| M07 容量不足下保留服务 | BSR：FBGR/PBGR 预定并预留恢复容量，BER 故障后按可用资源分配 | 可调光路、客户 committed/excess rate、端到端一致且连续频隙 | PBGR 不足承诺容量即失败；BER 不预留，不能与 PBGR 混为同一保证；UNI/映射/policing 需协调 | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E007] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] |
| M08 故障后的信号可用性 | 对不同主备激活状态实施 QoT 鲁棒 RSA | 指定单链路/SRLG 集合与物理损伤模型 | 正常态 QoT 不等于切换后 QoT；保障可能增加频谱需求、降低共享 | [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E002] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E003] |
| M09 避免多层重复恢复 | 通过层间恢复职责与 holdoff 协调升级 | 各层恢复机制及触发关系明确 | 等待下层恢复与更早启动上层之间有时间权衡；不等于大模型任务控制已被研究 | [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E003] |

| M10 弹性频谱可行性 | 联合考虑路由、连续频槽、保护带与距离自适应调制 | 沿路频谱一致且每连接频槽连续；调制需满足可达性 | 空闲总量足够仍可能受碎片影响；草稿的简化可达性模型不能替代完整 QoT | [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001] [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E002] [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E003] |
| M11 双故障保护 | 每业务三条链路不相交光路；dedicated 1:1:1 同类别共享，mixed 另允许跨类别共享 | 静态需求、可调收发器、连续且沿路一致频谱、距离相关调制 | 按式(1)–(4)排除双故障争用组合；dedicated 不代表全部备份独占；非任意规模 SRLG 保障 | [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E003] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E004] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E005] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E006] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E007] |
| M12 软故障频谱让渡 | 更稳健调制并借用 bronze 频谱维持 gold 净速率 | 可配置收发器；bronze 最低速率、QoT 与频谱可行性仍需满足 | 规划固定最短路、设定 X dB 故障；保障等级及权重影响可让渡量 | [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E012] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E014] |

表中“成本与边界”包含基于所列条件的阅读者解释，不能直接转换成研究缺口。

## Task Property Map

阶段一不将客户层 SLA 等同 AI 任务性能。第二阶段任务证据另见 [任务特性表](task-properties.md)，交叉推断见 [机会分析](gaps.md)。

## Method Evolution

不按发表年份构造单线进化史。基础分类、物理风险、配置结构、带宽等级、故障态 QoT 是可并存的分析维度；当前材料不足以证明某路线全面取代另一条路线。

## Cross-Paper Comparison

- **SURV-004** — status: supported。不同论文的输入自由度不同：有的联合决定主备 RWA，有的先固定工作路由，有的允许按整数信道拆分恢复。比较结果时不能忽略这些差别。evidence: [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E001] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E003]；derived_from: []。
- **SURV-005** — status: inferred。容量共享至少需同时核对故障调用兼容与交换配置兼容；在含物理损伤的模型里还要检查激活后的 QoT。evidence: [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] [@doi-b5315866469261c081250bcdcf5fa7eef701933a1b79fb009fe7d265824076b9#E001] [@doi-b5315866469261c081250bcdcf5fa7eef701933a1b79fb009fe7d265824076b9#E002] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001]；derived_from: [SURV-002, SURV-003]。
- **SURV-006** — status: inferred。新模型相对基线的收益必须在相同故障集合、服务等级、资源预算及硬件条件下解释；降带宽、减少保障情形或增加资源都可能改变结果，不能直接归因于机制。evidence: [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E002] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E003] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E003]；derived_from: [SURV-003, SURV-004]。

## Known Limitations

### 作者明确边界

PXT 的无分支约束与双向、单位容量模型见其 §3.3；管道保护论文的静态需求、无波长转换与模型规模见其引言/模型；统一框架固定工作路径且允许整数信道拆分。以上是模型条件，未一律改写成作者“缺陷”。evidence: [@doi-b5315866469261c081250bcdcf5fa7eef701933a1b79fb009fe7d265824076b9#E003] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E003] [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E001]。

### 综合推断

不能预设经典机制“不认识业务”“都要求全带宽”或“只能处理独立单链路故障”。本组已含服务等级、物理共因风险、故障状态 QoT 和多层协调；这些都应成为后续比较基线。此项是对本组覆盖的解释，非全领域结论。evidence: [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E002] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E003]。

## Open Questions

仅列阅读待核验项，不登记为 GAP：

1. BSR 已补读：客户 SLS 经三种映射/policing 架构与 CNS/ENS 控制落地；AI 任务代价仍未研究。控制面仿真器约 1.05 s（含 1 s holding），不能等同真实光硬件或任务恢复时延。evidence: [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E010] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E011]。
2. 当代弹性光网中可调收发器、连续/连续块频谱和调制/距离约束如何具体限制共享与恢复？BSR 已补充一致与连续频隙、first-fit 及示例子载波/槽位关系；补充作者草稿已提供距离自适应 RSA 的条件证据（M10），最终版本尚未核验。evidence: [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E007]。
3. 软故障已补机制正文（M12）；双故障已核验共享判据与模型正文（M11），实验数值未复核。区域灾害、跨域信息隐藏及故障后重新保护，仍需代表正文证据；补充检索文件仅为线索，不自动纳入当前 corpus。
4. PXT 与 QoT 预印本和期刊版本之间的差异尚未逐项核验；不混用版本数值。

## Coverage Limitations

这是阶段一首批基线图谱，包含 M01–M12 的问题/机制位置，非互斥类别。尚未完成 exhaustive review、全套数学推导或性能复现。旧归档未作为默认输入，阶段一 10 篇均按本轮 Brief 重新筛选与核验；不基于“当前没找到”推断不存在。

阶段一已按有界覆盖收口，未核验项保留；任务特性与交叉分析另文记录，本报告不生成创新候选。

## BSR 全文补读更新

- **SURV-007** — status: supported。部分带宽保证与尽力恢复的资源预留和失败条件不同，不能仅以“压缩带宽”合并比较。evidence: [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006]；derived_from: [SURV-001, SURV-003]。
- **SURV-008** — status: inferred。BSR 的频谱节省同时伴随恢复带宽/服务保证变化；原论文资源量与恢复率还采用不同容量约束，不能把这些数值解释成相同保障下的纯算法收益。evidence: [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E008] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E013]；derived_from: [SURV-006, SURV-007]。
