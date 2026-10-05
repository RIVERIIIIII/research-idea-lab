# Research Gap Analysis

## Gap Analysis Scope

- **Research Brief**：`research/research-brief.md`，状态为 `CONFIRMED`。
- **Survey**：`research/survey.md`。
- **实际使用的 paper notes**：5 篇；只使用当前 survey 纳入的 004、005、007、012、015 卡片，不使用早期 pipeline-validation 的 001–003 卡片。
- **evidence levels**：3 篇 `full_text`、1 篇 `abstract_only`、1 篇 `metadata_only`。
- **corpus limitations**：当前 `selected.jsonl` 有 12 篇论文，尚有 7 篇未形成 note；软故障恢复只有摘要级证据，资源弹性只有 metadata；训练故障实验、推理/Multi-Agent、保护机制与 checkpoint/迁移覆盖不足。
- **用途声明**：本次仅验证 `survey + paper evidence → traceable candidate gaps`。下列 gap 均为待回查 inference，不是正式科研结论、创新点或 novelty claim。

## Candidate Gaps

### GAP-001 — 光层软故障预测窗口与训练状态之间缺少经验证的联合决策关系

- **gap_id**：`GAP-001`
- **title**：光层软故障预测窗口与训练状态之间缺少经验证的联合决策关系
- **gap_type**：`integration-driven`
- **description**：当前材料分别展示了软故障演化预测、故障后的频谱重配置，以及跨 DC LLM 训练对光网络带宽约束的适应；值得进一步核查的是，预测得到的退化时间窗口能否与训练阶段、剩余任务量或任务连续性共同决定光层动作，而不是始终采用固定业务等级或独立维修阈值。
- **why_it_may_matter**：如果训练状态会改变“立即维修、先重配置频谱、调整训练配置或等待”的相对代价，那么只优化 QoT margin 或健康网络下的迭代时间可能不能代表任务级连续性；该关系同时依赖 QoT/频谱等光层变量和训练运行状态，符合 Research Brief 的算网耦合边界。
- **derived_from**：[`SURV-001`]
- **supporting_papers**：`doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4`；`doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922`；`doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7`
- **back_check_needed**：`true`
- **confidence**：`MEDIUM`

#### Observed Evidence

1. 软故障预测论文使用 50 个历史/当前 BER 观测预测未来 70 步、约 4 天的退化轨迹，并在单光路实验中报告预测式维修相对固定阈值具有更低 QoT margin。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E004] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E006]
2. 作者明确将多光路依赖、其他软故障和预测不确定性列为未来工作。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E008]
3. 频谱共享论文提出按既定业务等级进行调制与频谱重配置，但摘要没有显示 AI 任务状态参与决策。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E004]
4. GeoPipe 已把计算、HBM、跨 DC 时延和带宽共同用于训练配置，并把 scheduler 与 optical control plane 的更紧密集成列为未来工作；其评估没有注入光网络故障。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E007] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

#### Cross-paper Synthesis

**综合推断（synthesis/inference）**：现有卡片分别提供了“何时可能发生硬故障”“光层可以怎样重配置”和“训练配置怎样响应网络带宽”的局部能力，但尚未在同一证据链中验证训练状态是否会改变软故障期间的最佳光层动作。该判断来自当前 corpus 的结构，不能推断领域中不存在相关工作。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E009] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

#### Candidate Gap Inference

候选 gap 是：**在可预测的光层软故障演化期间，任务状态是否构成选择光层维护/重配置与训练侧适应动作的必要决策变量。** 这是待核查问题，不是“现有研究没有做”的事实陈述。

#### Counter Evidence

- 光层已有按业务等级实施频谱共享和在线 RSA 的恢复路径，可能无需引入训练内部状态即可保障关键连接。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
- GeoPipe 已能根据跨 DC 带宽调整训练配置，训练侧适应可能吸收一部分容量变化，使额外联合控制收益有限。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E006]
- 资源弹性可能通过移除不可用 worker/DC 提供更简单的替代方案，但当前只有 metadata，不能确认。[@openalex-w3037519745#E002]

#### Uncertainty

- 当前没有直接证据量化软故障对 LLM 训练完成时间、正确性或连续性的影响。
- 频谱共享论文只有摘要，可能遗漏正文中的跨层讨论。
- 尚未处理的 selected papers 可能已经部分或直接覆盖联合控制。

#### Back-check Needed

需要定向核查：task-aware optical soft-failure control、proactive reconfiguration for distributed training、training-stage-aware network control、optical degradation-aware scheduling，以及能够反驳联合控制必要性的资源弹性工作。本阶段不执行该检索。

### GAP-002 — 区域相关故障风险尚未在当前证据中闭合到训练拓扑与光层保护的联合选择

- **gap_id**：`GAP-002`
- **title**：区域相关故障风险尚未在当前证据中闭合到训练拓扑与光层保护的联合选择
- **gap_type**：`integration-driven`
- **description**：当前材料能够计算相关链路/节点联合失效和路径存活概率，也能在健康网络中根据跨 DC 带宽调整训练配置；值得进一步核查的是，PSRLG 风险是否应同时影响训练实例/并行拓扑放置与光路保护，而非只作为网络可用性查询或事后恢复输入。
- **why_it_may_matter**：区域故障可能同时移除多条光路和多个算力站点。若训练拓扑与光路共享同一地理风险，独立优化可能形成隐含的共同失效点；但该重要性目前尚未由训练故障实验支持。
- **derived_from**：[`SURV-002`]
- **supporting_papers**：`doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250`；`doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7`
- **back_check_needed**：`true`
- **confidence**：`LOW`

#### Observed Evidence

1. PSRLG 工作建立了概率相关故障模型，可查询资源集合联合失效、节点断连和路径存活概率。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E006]
2. 不同故障基数的概率区间存在重叠，说明仅按失效链路数量刻画风险可能不充分。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E005]
3. GeoPipe 在 3 个区域部署 64 个 NPU，并使训练配置感知跨 DC 网络参数，但其测试没有覆盖区域或链路故障。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E003] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

#### Cross-paper Synthesis

**综合推断（synthesis/inference）**：当前证据链的一端能够表达区域相关风险，另一端能够表达训练对跨 DC 带宽的依赖，但没有在已读卡片中验证风险如何改变训练放置、并行拓扑和光保护的共同选择。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

#### Candidate Gap Inference

候选 gap 是：**概率相关故障风险是否会实质改变地理分布式训练拓扑与光层保护资源的联合选择。** 当前只能说明值得核查，不能说明尚无研究。

#### Counter Evidence

- PSRLG 模型已经支持路径存活和 VM placement 类可用性应用，可能直接扩展到算力放置，无需形成新的核心问题。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E006]
- GeoPipe 表明健康网络下训练配置已能利用网络约束；风险变量可能只是现有优化中的附加参数，而不会改变方法本质。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]
- 当前 selected corpus 中仍有区域故障韧性、灾害保护和光数据中心方向的论文尚未形成 note；它们可能构成直接覆盖。该项是 corpus 状态提醒，不作为论文事实。

#### Uncertainty

- 训练任务级损失在区域故障下尚无本 corpus 的实验支持。
- PSRLG 与 GeoPipe 的系统目标不同，把两者连接起来可能只是工程组合。
- 相关主题的 selected papers 尚未精读，因此当前置信度为 `LOW`。

#### Back-check Needed

必须定向核查 regional-failure-resilient virtual infrastructure mapping、disaster protection in optical DC networks、risk-aware geo-distributed training placement，以及 SRLG-aware compute-network co-optimization。本阶段不执行该检索。

## Rejected / Weak Gap Candidates

### 1. “把高优先级业务替换成 LLM 训练优先级”

- **rejection_reason**：只是标签替换；没有证明训练状态会改变光层机制、约束或目标，也缺少算力侧决策。
- **evidence_or_counter_evidence**：现有频谱共享方法已经按业务等级完成调制与 RSA 调整。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
- **disposition**：拒绝作为 gap；只有在训练状态形成不可替代的双向耦合后才可重新评估。

### 2. “为 LLM 重新设计一个光软故障检测器”

- **rejection_reason**：故障检测输入是 BER/光层退化，当前没有证据表明更换上层 workload 会改变检测问题；容易成为热门关键词拼接。
- **evidence_or_counter_evidence**：现有工作已使用 BER 序列预测 EDFA 退化并给出提前维修窗口。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E002] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E006]
- **disposition**：拒绝；研究对象应是检测结果如何改变算网决策，而不是给检测器加 LLM 标签。

### 3. “资源弹性已经证明可以直接丢弃不可用 DC”

- **rejection_reason**：当前卡片为 `metadata_only`，具体方法、故障模型、训练正确性与网络假设均未核实，不能从标题得出结论。
- **evidence_or_counter_evidence**：该信息已被标记为 `unverified`，只可作为反例核查入口。[@openalex-w3037519745#E001] [@openalex-w3037519745#E002]
- **disposition**：拒绝作为 gap 或结论；待后续 targeted back-check。

### 4. “区域相关故障在算力光网络中没有被研究”

- **rejection_reason**：这是由当前 corpus coverage 不足产生的无依据存在性判断；已有 PSRLG 工作明确研究相关故障，且 selected corpus 中还有直接相关论文尚未精读。
- **evidence_or_counter_evidence**：PSRLG 已对相关链路/节点故障及其概率查询建立模型。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E003]
- **disposition**：拒绝该绝对表述；仅保留 GAP-002 这一需要回查的具体联合关系。
