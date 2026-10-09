# Candidate Research Ideas

## Scope & Decision Gate

- 输入：`research/hypotheses.md` 及 `research/backchecks/` 中对应回查。
- 只有 `KEEP` 或 `REVISE` 的 hypothesis 可以进入本文件。
- `HYP-001`：`REVISE`，进入候选。
- `HYP-002`：`REJECT`，保留历史记录但不生成 candidate idea。
- `DISC-HYP-A`：经人工初始 KEEP；四篇 closest work 全文核查后收紧为 `REVISE`，保留并更新 `IDEA-002`。
- 本文件输出只表示值得人工讨论的候选，不表示 novelty、confirmed contribution 或正式创新点。

## IDEA-001 — 预测软故障窗口内的训练状态感知跨层动作选择

- **idea_id**：`IDEA-001`
- **title**：预测软故障窗口内的训练状态感知跨层动作选择
- **statement**：研究在光层渐进 QoT 退化可提前预测时，训练运行状态是否会改变“光层频谱/调制重配置、训练侧配置适应或暂不动作”的选择边界，以及这种状态感知选择是否能相对网络侧独立恢复和训练侧独立自适应降低任务级完成时间损失，同时保持相同 QoT 保障。
- **derived_from**：[`HYP-001`, `GAP-001`]
- **core_problem**：现有工作分别能够预测软故障、执行光层恢复、让训练适应网络带宽或在 WAN churn 下自愈，但当前定向结果没有闭合“预测窗口中何时选择哪一层动作”的任务级决策关系。
- **proposed_relation_or_mechanism**：把预测的 QoT/BER 演化作为未来网络状态，把训练阶段/剩余工作特征作为动作代价条件；研究重点是跨层动作的选择边界，而不是简单把预测器与训练调度器串联。
- **supporting_evidence**：
  - 软故障预测能够产生约 4 天的动作窗口，并在单光路场景中改善维修时机。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E004] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E006]
  - 光层存在调制/频谱共享等可执行恢复动作。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
  - GeoPipe 表明训练配置可读取光网络约束，且带宽与训练性能并非简单线性关系。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E006]
- **closest_prior_work**：
  - `BC-H1-001`：软故障演化预测；缺少训练状态和联合动作。
  - `BC-H1-004`：CD-CBA；覆盖训练—光网络资源分配，但没有软故障预测。
  - `BC-H1-005`：Learning In Chaos；覆盖 WAN churn 下训练自愈，但没有光层 QoT/频谱机制。
  - 详细比较见 `research/backchecks/HYP-001.md`。
- **difference_from_prior_work**：候选不主张重新设计故障预测器、普通训练调度器或静态优先级恢复；待核查差异是训练状态是否改变预测软故障窗口内跨层动作的决策边界，并要求与网络侧独立和训练侧独立方案同时比较。
- **counter_evidence**：
  - 静态业务等级频谱共享可能已经足够保障关键连接。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
  - GeoPipe/CD-CBA 类训练—光网联合分配可能已经吸收带宽变化，使额外故障状态收益有限。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]
  - Learning In Chaos 和资源弹性路线可能通过训练侧自愈直接绕过光层动作；当前需要全文比较其适用故障模型。
- **uncertainty**：Semantic Scholar 本轮不可用；关键 back-check 工作尚未全文精读；训练状态变量和软故障对任务级指标的实际影响仍未被当前 evidence 确认。
- **back_check_summary**：HYP-001 共检索 67 条 raw、60 条唯一结果；关键比较集中包含 0 DIRECT、7 PARTIAL、3 ADJACENT。决策为 `REVISE`，候选已收缩到跨层动作选择边界。
- **confidence**：`MEDIUM`
- **status**：`POTENTIAL_CANDIDATE`
- **human_review**：`REJECT`。该 validation 候选对应后续讨论中的预测窗口/训练动作时机分支 `DISC-SF-3`，已由人明确淘汰，不再作为当前活跃候选。

## IDEA-002 — 不可绕行软故障容量缺口下的训练任务级频谱牺牲协调

- **idea_id**：`IDEA-002`
- **title**：不可绕行软故障容量缺口下的训练任务级频谱牺牲协调
- **statement**：研究在 QoT-aware rerouting 无法提供足够残余带宽、soft-failure-induced modulation transition 造成不可避免频谱缺口时，是否需要依据同步屏障、pipeline 关键边和 flow-to-job 依赖，跨训练作业协调恢复频谱受益流与降速牺牲流，并在相同 QoT 与频谱预算下相对静态 rate class、普通 task-priority allocation 和 communication-bound FS allocation 降低任务级损失。
- **derived_from**：[`DISC-HYP-A`, `GAP-003`]
- **core_problem**：现有软故障频谱共享已经按静态 rate class 选择频谱牺牲者；fgOTN 和 CD-CBA 已分别按同步任务优先级与 communication-bound 状态分配动态光带宽/FS。待验证问题只剩：在重路由不能消除的软故障容量缺口下，QoT/调制可行域与训练依赖的联合是否迫使系统做出既有两类方法都不能表达的跨作业牺牲决策。
- **proposed_relation_or_mechanism**：先排除存在足够 QoT/带宽备选路径的情形；对剩余不可避免容量缺口，将 flow 对 barrier/bubble/JCT 的边际影响映射为恢复代价，在 QoT、调制可达性、频谱连续/一致性和最低速率约束下联合选择扩谱、降速及受让/牺牲流。不能只给 CD-CBA 加 failure flag，也不能只把业务等级替换成训练权重。
- **supporting_evidence**：
  - 软故障后的鲁棒调制可能要求扩谱，并可由低等级光路让渡频谱。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E001] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
  - fgOTN 已证实同步依赖、task/subtask priority 与可调光带宽形成明确资源竞争。[@doi-9a31f9cf00c5424841e64b70a521325632ad9fa457e6ca856337d1e6ce735962#E003] [@doi-9a31f9cf00c5424841e64b70a521325632ad9fa457e6ca856337d1e6ce735962#E004]
  - CD-CBA 已证实 communication-bound labels 会改变 FS/路径分配及训练级指标。[@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E002] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E007]
- **closest_prior_work**：
  - `BC-DHA-001`：最接近的光层恢复工作，覆盖调制切换与频谱让渡，但使用静态业务等级。
  - `BC-DHA-003`：全文覆盖同步 GDML 的 task/subtask priority 与可调 fgOTN bandwidth。
  - `BC-DHA-004`：全文覆盖 communication-bound task labeling、动态 FS 增减和路径选择。
  - `BC-DHA-002`：全文给出约 2 μs 的 QoT/QoS-aware 快速重路由，是绕开本问题的强替代机制。
  - 详细比较见 `research/backchecks/DISC-HYP-A.md`。
- **difference_from_prior_work**：待核查差异限定为“重路由不可消除的 soft-failure QoT/调制容量缺口”与“跨训练作业 flow-to-job dependency”共同决定受益/牺牲流；一般 training-aware priority 或 CB-driven FS allocation 已被已有工作覆盖。
- **counter_evidence**：静态等级可能足够；GARA/CD-CBA 可能已吸收容量变化；约 2 μs 快速重路由可能避免容量缺口；如果只增加 failure state 而不改变决策结构，则候选不成立。
- **uncertainty**：Semantic Scholar 限流；其余相邻训练—光网工作尚未全部全文核查；不可绕行容量缺口出现频率与训练 trace/QoT 模型联合验证可行性尚未确认。
- **back_check_summary**：核心检索 96 条 raw、79 条去重记录；精确补查后共 91 条唯一 metadata records。关键比较仍为 0 DIRECT、6 PARTIAL、2 ADJACENT；四篇 closest work 全文核查后 decision 从人工初始 `KEEP` 收紧为 `REVISE`，confidence `MEDIUM`。
- **problem_validation**：最小反例结果为 `CONDITIONAL_PASS`；81 个邻近合成组合的稳定性核查中，23 个出现不同且更优的 job-group-aware 选择，且集中于中等频谱稀缺区间（23/27）。这排除了单点数值构造，但没有验证现实出现频率，GARA 类全局分配仍可能吸收该问题。详见 `research/investigations/soft-failure-training-impact/minimal-problem-validation.md` 与 `minimal-stability-check.md`。
- **confidence**：`MEDIUM`
- **status**：`POTENTIAL_CANDIDATE`

## Rejected Hypotheses

- `HYP-002`：`REJECT`。区域故障下联合计算/服务放置与光保护已有多项高度接近工作；当前训练 workload 差异不足以支持 candidate idea。详见 `research/backchecks/HYP-002.md`。

## Human Review Gate

当前唯一保留登记的候选是已收紧边界的 `IDEA-002`，但其**当前推进决定为暂停深入验证（ON HOLD）**，不是正在投入完整仿真的方向。四篇关键 prior work 已全文核查；“不可绕行容量缺口”的现实发生频率与独立论文价值仍待人工判断。最新讨论线索和推进优先级以 `research/current-status.md` 为准。系统不得自行宣布 `IDEA-002` 为创新点。
