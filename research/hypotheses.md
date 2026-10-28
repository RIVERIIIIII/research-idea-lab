# Candidate Hypotheses

## Scope & Status

- inputs: research/research-brief.md（CONFIRMED）、research/gaps.md、research/survey.md、research/task-properties.md、research/stage3-mapping-audit.md。
- validation boundary: 以下是可检验的机制假设，不是论文事实、已验证收益或创新贡献。现有文献为能力与约束提供基础，新关系通过后续分析/验证判断。
- 仅生成一项，不为候选数量凑数。已完成首轮有界 back-check，HYP-001 的 decision 为 REVISE；修订机制仍待检验和补充回查。

## HYP-001 — 可变迁移数据量与软故障后的光资源恢复是否相互改变决策

- hypothesis_id: HYP-001
- title: 可变迁移数据量与软故障后的光资源恢复是否相互改变决策
- statement: 在地理分布式分片推理遭遇光层软故障、源端状态仍可访问、目标参数/显存可用，且恢复资源受连续频谱与调制可达性约束的条件下，按实际张量维度调整 KV 直传与 activation 重计算的分配，可能改变所需光连接及频谱分配；联合考虑该反馈，相比先独立恢复网络带宽再运行已有迁移策略，可在部分资源紧张情形下减少含控制、状态准备及重计算代价的服务恢复总时间。预期差异来自可传数据量和光资源可行集合相互影响，而非增加 GPU/频谱或降低既有业务保障。
- derived_from: [GAP-002]
- research_problem: 软故障恢复与状态迁移的联合可行性是否存在不能由固定带宽输入完整表达的反馈？若有，何时足以抵消联合协调与状态准备成本？
- rationale: EdgeFlow 把端点带宽作为给定输入，任务分配会改变传输量；EON 的频谱连续性、调制和故障态 QoT 限制光连接配置。可变传输量可能改变为满足恢复时间所需的频谱，而新配置可能改变目标及传输/重算分界。这是跨论文推断，待验证。
- supporting_evidence:
  - [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E003] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E004] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E005] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E006]
  - [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001] [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E002] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E002]
  - [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E012] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013]
- counter_evidence:
  - EdgeFlow 已联合目标选择和传输/重算分界，不能把这两个变量本身当新增机制。[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E005] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E006]
  - 网络感知成本 oracle 已可影响实例选择，固定光连接上的带宽/延迟感知很可能被普通调度完整表达。[@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E001] [@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E002]
  - 既有 BSR 和软故障共享已可降级带宽、保最低速率并进行客户层协调，不能把资源让渡或业务感知本身当贡献。[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013]
- assumptions:
  - 选定一种分片推理部署，其业务确实使用可编排 EON 光连接；这是拟研究场景，尚非本轮已验证部署事实。
  - 软故障后源端仍存活且可达，所需 KV 或历史 activations 可访问；不能获得时，相关动作不可行。
  - 目标已有可用模型参数、显存与计算资源，或将准备这些资源的全部代价计入；不假定免费副本和空闲 GPU。
  - 按实际模型的 KV 头数、精度、分片与层差异计算数据量/算量，不继承“activation 必为 KV 的一半”的通用假设。
  - 可执行的光层动作仅限设备/控制接口支持的路由、连续频槽与调制调整；配置时延、QoT 和其他连接保障均计入。
  - 将迁移一致性和生成暂停方式明确为模型前提；未知部分不当成已经实现的能力。
- mechanism_chain:
  - classical_problem: 光层软故障造成 QoT/有效容量退化，需恢复连接并维持服务约定。
  - classical_scheme_and_decision: 选择满足 QoT 的调制和频谱，必要时按既有等级让渡资源；任务迁移随后依据已恢复带宽选择目标和直传/重算分界。
  - limiting_condition_and_boundary: 独立控制把带宽需求或恢复后的带宽当固定输入，在需求可由任务动作改变时可能错过某些可行配置；固定需求在原场景仍合理。
  - task_property_evidence_and_control_conditions: 可由 KV 直传与 activation 重计算改变迁移数据量，但需源状态和目标参数/计算资源可用。
  - decision_change_and_causal_link: 传输量变化→满足相同时间/服务约束所需容量变化→连续频槽、路由与调制选择可能变化→目标/分界的代价再变化。四个箭头均为待验证关系，不是既有结果。
  - expected_benefit_and_source: 在离散光资源可行性受限且重计算较便宜时，可能减少恢复排队/资源争用和总恢复时间；该收益可能为零，也可能被准备与协调成本抵消。
- quality_checks:
  - property_authenticity: 迁移直传/重算选择已有正文基础；真实部署映射及 activation 可用性是需要核验的前提。
  - mechanism_effectiveness: 必须展示目标/分界与光路/连续频谱选择的相互变化；只更换故障后带宽参数不算验证新关系。
  - net_benefit_and_costs: 计入 activations 保存、参数准备、显存、计算争用、光路配置、通信握手、迁移暂停及协调成本。公平比较净服务恢复时间，不只比较搬运时间。
  - prior_art_risk: 光网络 NFV/VM 服务迁移、计算感知恢复、可重计算通信与灵活带宽编排均可能直接覆盖；尚无新颖性结论。
- comparison_conditions: 固定总频谱、GPU/显存预算、故障模型、原业务最低保障、状态正确性和可执行动作集合。比较适用的仅光层恢复并原地续推理、网络恢复后自适应 EdgeFlow，以及在同动作空间反复协调网络/任务的强替代；固定带宽一次性串行方案只能辅助解释，不能作为唯一基线。若更通用的联合最优解表达相同模型，不能把算法包装成新机制。
- counterfactual: 固定直传/重算分界或禁止改变光资源分配后，所声称的反馈收益应消失或减少；若只需更新单一带宽数值便能重现全部选择与收益，则光层机制主张削弱。
- benefit_disappearance_conditions:
  - 光资源充足，所有目标均可满足相同恢复需求，改变传输量不改变分配。
  - 重计算/activation 保存/参数准备远贵于传输，最优分界恒定。
  - 源端不可达或必要状态丢失，相关迁移动作根本不可执行。
  - 其他连接保障、配置时延或故障态 QoT 使新增配置不可行。
  - 原地重路由或同样信息下的简单交替协调已得到相同选择与净结果。
- falsifiability: 若在满足前提的资源紧张情形中，传输/重算选择不能改变光资源可行分配，或改变光分配不能反向影响任务决策，则核心反馈被否定；若虽有反馈，但扣除同预算下全部代价后无可解释改善，则净收益主张不成立；若现有工作已完整覆盖同问题/同控制/同约束，则新机制差异不成立。后者影响贡献判断，不表示物理关系必为假。
- uncertainty: 跨地域部署与可编排光连接的实际映射、状态一致性、activation 保存、参数准备和成本参数仍待核验。不能借“未搜到”宣称不存在已有方案。当前 confidence 仅表示值得检验的证据强度。
- back_check_queries:
  - "elastic optical network soft failure recovery computation aware service migration spectrum allocation"
  - "joint optical spectrum allocation virtual machine state migration recomputation bandwidth"
  - "KV cache migration activation recomputation network resource allocation optical"
  - "NFV optical network failure recovery migration routing spectrum joint optimization"
  - "communication computation tradeoff state reconstruction bandwidth allocation service recovery"
  - "alternating optimization optical network service migration flexible bandwidth resource allocation"
- confidence: LOW
- evidence_status: inferred
- decision: REVISE
- back_check_report: research/backchecks/HYP-001-round1.md
- revision: 宽泛的传输/重计算与网络分配联合优化已有相关工作；收窄为状态表示选择跨越连续频谱、调制与故障态 QoT 的可行性边界，并检验其净恢复价值。新增 ctHO 类联合重建/速率分配作为强对照。
- status: NEEDS_BACK_CHECK

## 未生成独立假设的线索

GAP-001：阶段 SLO 与频谱让渡仍须界定具体传输事件和计时点，避免把阶段名称直接变成业务权重。X03、X04 仍是待补证线索。未生成 candidate idea。HYP-001 首轮回查为 REVISE，修订后仍需最小机制检验、补充正文核查和人工 Review。

## HYP-001 最小检验更新（2026-10-10）

见 `research/checks/HYP-001/assessment.md`。合成枚举支持“选择可能相互影响”的条件性关系，但完整可行网络选项 oracle 可复现同一最优值，未通过光层机制额外价值的强对照。decision 维持 REVISE，confidence 维持 LOW。当前不生成 candidate；优先补最近邻光网络迁移正文，而非继续扩大这个一般联合优化模型。

## HYP-001 关联讨论补充（2026-10-26）

已按用户五步计划形成 [机制草案](backchecks/X02-deployment-2026-10-26/mechanism-draft.md) 与 [定向回查](backchecks/X02-deployment-2026-10-26/mechanism-backcheck.md)。讨论位置为：可从不同可用信息恢复同一模型段状态时，状态连接的端点/路径与持续服务光连接是否变化。Petals历史输入重放、EdgeFlow逐层activation投影、SCORE已有主/备数据来源必须分开，不能把已有能力直接称为本项目贡献。

本补充不替换上方软故障statement；新工作场景用单光纤故障作路径检查，不将其无声并入原假设。隔离证据也不伪装成正式corpus/GAP已纳入。decision仍REVISE，confidence仍LOW，status仍NEEDS_BACK_CHECK，不新增HYP编号或candidate。

对旧oracle判断的解释补充：完整配置oracle与联合枚举同值，是等价求解，不能单独证明或否定机制差异。旧例只优于弱顺序策略、没有真实原地恢复对照等局限仍在，仍不足以确认贡献。后续先做同场景强基线的纸面反例检验，再核对具体同机制覆盖。
