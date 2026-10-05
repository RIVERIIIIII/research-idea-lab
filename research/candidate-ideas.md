# Candidate Research Ideas

## Scope & Decision Gate

- 输入：`research/hypotheses.md`、`research/backchecks/HYP-001.md`、`research/backchecks/HYP-002.md`。
- 只有 `KEEP` 或 `REVISE` 的 hypothesis 可以进入本文件。
- `HYP-001`：`REVISE`，进入候选。
- `HYP-002`：`REJECT`，保留历史记录但不生成 candidate idea。
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

## Rejected Hypotheses

- `HYP-002`：`REJECT`。区域故障下联合计算/服务放置与光保护已有多项高度接近工作；当前训练 workload 差异不足以支持 candidate idea。详见 `research/backchecks/HYP-002.md`。

## Human Review Gate

`IDEA-001` 必须经过人工讨论和关键 prior work 全文核查后，才能决定是否进入正式科研分析。系统不得自行宣布其为创新点。
