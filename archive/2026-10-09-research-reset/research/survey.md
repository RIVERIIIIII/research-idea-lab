# 广域算力光网络生存性：当前 selected corpus 综述

> 本文依据已确认的 `research/research-brief.md`，用于把当前小规模正式 corpus 组织成可追溯的研究版图。它不是 comprehensive literature review、complete state of the art、research gap 或 novelty 判断。

## Scope & Coverage

- `selected.jsonl` 当前有 12 篇论文；本轮已有结构化 note、实际纳入 survey 的论文为 5 篇，年份范围 2018–2025。
- coverage roles（可重叠）：`foundational` 2 篇、`representative` 4 篇、`recent` 1 篇、`conflicting` 1 篇、`limited` 1 篇。
- evidence levels：3 篇 `full_text`、1 篇 `abstract_only`、1 篇 `metadata_only`。
- 当前覆盖：光层软故障恢复、软故障演化预测、区域相关故障概率建模、健康网络中的跨 DC LLM 训练优化，以及“训练资源弹性可能替代网络恢复”的待核实入口。
- 7 篇 selected papers 尚未生成 note，不能进入本轮实质综合；原有 001–003 卡片属于早期 pipeline-validation 数据，不属于当前 selected corpus，因此不纳入。

## Research Problems

当前材料把“光网络故障如何影响并保障 AI 任务”拆成四个相邻层次：

1. **故障后的光层恢复**：软故障使 QoT 恶化时，通过调制与频谱重配置保持高优先级连接。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E001] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
2. **故障前的预测与维修**：从 BER 序列预测 EDFA 退化，在硬故障前且不过度保守地触发维护。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E001] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E002]
3. **相关故障的风险表达**：用 PSRLG 描述灾害造成的联合链路/节点失效，并计算路径存活和资源集合联合失效概率。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E001] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002]
4. **光网络约束下的训练效率**：在跨 DC 光传送网中，让流水线并行适应带宽、时延和 HBM 约束。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E001] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]

资源弹性可能构成第五个层次，即算力侧直接移除不可用 worker/DC；但当前 note 为 `metadata_only`，无法确认其故障语义、网络假设和效果，不能支持肯定结论。[@openalex-w3037519745#E001] [@openalex-w3037519745#E002]

## Method Taxonomy

### 1. 反应式光层重配置

- **核心机制**：更稳健调制格式与跨业务等级频谱共享；规划阶段 ILP RSA，运行阶段在线 RSA。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
- **适用条件**：EON、不同速率保障等级、低优先级业务可让渡频谱。
- **证据边界**：当前只有摘要；成本改善仅是作者 claim，不能补写实验规模和效果量。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E003]

### 2. 预测式软故障维护

- **核心机制**：encoder-decoder LSTM 从 BER 序列预测未来约 4 天的退化轨迹。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E002] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E004]
- **代表证据**：单光路仿真中，预测方案在硬故障前 4 天、5.32% QoT margin 触发维修；固定阈值提前 42–65 天或在硬故障后动作。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E006]
- **边界**：只覆盖 EDFA gain degradation 和单光路场景。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E008]

### 3. 概率式相关故障建模

- **核心机制**：随机区域故障模型、PSRLG 术语、CFP/FP 离线预计算与查询结构。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002]
- **代表证据**：7 个光骨干拓扑与地震数据评估显示，不同故障基数的概率区间存在重叠，只按失效链路数量筛场景可能失真。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E003] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E005]
- **边界**：这是风险输入，不包含 AI 训练状态或任务恢复代价。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008]

### 4. 健康网络下的算网协同训练优化

- **核心机制**：非阻塞通信与计算—通信重叠；依据计算、HBM、跨 DC 时延和带宽联合选择训练配置。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]
- **代表证据**：3 区域、64 个 Ascend 910B NPU 上运行 Llama-2 13B/72B；相对 1F1B，作者报告最高约 78.91% bubble reduction 和平均约 9.1% iteration-time improvement。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E003] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E005]
- **边界**：没有注入软故障、硬中断或区域故障。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

### 5. 算力侧资源弹性（待核实）

当前只有题名和书目信息。它被保留用于检验“直接抛弃不可用 DC/worker 是否足够”，但取得全文前不能描述其方法或把它作为反证。[@openalex-w3037519745#E001] [@openalex-w3037519745#E002]

## Method Evolution

当前材料不足以建立可靠的领域演进时间线。按年份只能观察到：2018 年有软故障后的频谱共享恢复，2021 年出现概率化区域相关故障模型，2022 年讨论退化预测与维修时机，2025 年把光网络带宽约束纳入跨 DC LLM 训练配置。

**综合推断（synthesis/inference）**：这些工作可排列为“故障风险/状态感知 → 光层控制 → 任务运行”的控制链，但现有论文没有共同实现这条闭环，也没有证据证明它们存在直接技术继承。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E002] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]

## Cross-Paper Comparison

| 路线 | 输入/假设 | 输出 | 目标 | 评价环境 | 关键边界 |
| --- | --- | --- | --- | --- | --- |
| 反应式重配置 | 软故障已检测；业务可分级 | 调制、频谱、RSA | 恢复 QoT 与高优先级速率 | 摘要级 | 未显示 AI 状态进入决策 [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E004] |
| 预测式维护 | BER 时序、单 EDFA 退化 | 未来 BER、维修时间 | 避免过早/过晚维修 | 6 节点 EON 单光路仿真 | 多光路与其他故障未覆盖 [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E008] |
| PSRLG | 灾害分布、拓扑、强度—距离关系 | 联合失效/路径存活概率 | 表达相关故障风险 | 7 拓扑及地震数据 | 地域外推近似；无任务效用 [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E007] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008] |
| GeoPipe | 计算、HBM、跨 DC 时延/带宽 | 训练配置 | 缩短迭代时间、减少 bubble | 3 区域 64 NPU | 只验证健康网络 [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008] |
| 资源弹性 | 未核实 | 未核实 | 未核实 | metadata only | 不能判断能否替代光层恢复 [@openalex-w3037519745#E002] |

这些路线不是统一排行榜：前三条分别处理故障后的控制、故障前的预测和相关风险；GeoPipe 处理任务侧对网络约束的适应。

## Known Limitations

### 作者明确承认

- 软故障预测只研究单光路 EDFA 增益退化，并提出研究多光路依赖、其他软故障和预测不确定性；非平稳数据还可能需要重新训练。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E007] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E008]
- PSRLG 的欧洲危险估计使用意大利数据拟合关系作为 first approximation，并依赖灾害模型假设。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E007]
- GeoPipe 将训练 scheduler 与光网络 control plane 的更紧密集成及动态资源编排列为未来工作。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E007]
- 频谱共享摘要未列出 limitation；资源弹性论文尚无全文证据，均不能代为补写。

### 综合推断（synthesis/inference）

- 当前证据分别给出“预测故障”“量化相关风险”“执行光层重配置”和“让训练适应网络带宽”的局部能力，但没有一篇纳入论文同时闭合故障风险、光层动作与 AI 任务损失。这是 corpus 结构观察，不代表领域中不存在此类工作。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E009] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E004] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]
- “直接抛弃不可用 DC”是否足够仍未解决：资源弹性全文尚待核实，而区域故障可能同时改变剩余算力、训练拓扑和光路风险。[@openalex-w3037519745#E002] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E005]

## Traceable Survey Findings

### SURV-001 — 软故障预测、光层恢复与训练适应尚未在当前证据中形成同一控制闭环

- **status**：`inferred`
- **statement**：当前纳入材料分别提供软故障演化预测、调制/频谱恢复和训练对跨 DC 带宽的适应，但尚未在同一已读证据中验证训练运行状态是否会改变预测软故障窗口内的跨层动作选择。
- **evidence**：[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E004] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

### SURV-002 — 相关故障风险与训练拓扑的联合关系在当前已读材料中未闭合

- **status**：`inferred`
- **statement**：PSRLG 材料能够计算相关资源失效和路径存活概率，训练材料能够表达跨 DC 网络约束，但当前已读卡片尚未验证风险如何改变训练拓扑与光保护的共同选择。
- **evidence**：[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E003] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

## Open Questions

以下只是待核查问题，不是正式 research gap 或候选创新点：

1. 光层退化预测的提前量如何映射为训练可感知的动作窗口？训练阶段、checkpoint 代价或剩余迭代时间是否改变最佳动作？[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E004] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E009]
2. PSRLG 风险能否进入算力放置、训练拓扑与光路保护的联合目标，而不只用于网络可用性查询？[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E006] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008]
3. 软故障下，按静态业务等级让渡频谱与按训练状态分配频谱有何实质差异？[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E004]
4. GeoPipe 的带宽—训练性能映射在 QoT 退化、重路由或部分容量损失时是否仍成立？[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E006] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]
5. 资源弹性方案能否在不破坏训练正确性或显著增加完成时间的前提下移除不可用 DC，以及何时仍需要光层恢复？该问题必须先补齐全文。[@openalex-w3037519745#E001] [@openalex-w3037519745#E002]

## Coverage Limitations

- 本轮实际使用 5 篇论文，规模不足以代表完整领域；另有 7 篇 selected paper 尚待结构化阅读。
- 软故障恢复只有摘要级证据，资源弹性只有 metadata，不能可靠定量比较。
- 当前缺少足够的训练故障实验、推理/Multi-Agent、光保护、checkpoint/迁移以及直接冲突实证。
- 当前集合偏向训练与光网络控制，尚不能比较训练、推理和 Multi-Agent 的故障敏感性。
- 不能从当前集合未出现某种机制推断其不存在，也不能据此声称 open question 具有 novelty。
