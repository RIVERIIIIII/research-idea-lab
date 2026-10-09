---
name: hypothesis
description: Generate grounded, specific, falsifiable candidate research hypotheses from existing GAP records and their evidence chain. Use after gap analysis; do not use for novelty conclusions, full experiment design, corpus expansion, or literature back-check execution.
license: MIT
metadata:
  author: archora; adapted for research-idea-lab
  version: "1.0-project"
---

# Hypothesis Generation

把已有 candidate gaps 转换为具体、可讨论且原则上可证伪的 candidate hypotheses。Hypothesis 是待验证判断，不是论文事实、正式创新点或 confirmed contribution。

## 共享机制推导规范

使用本 Skill 时读取 [生存性机制发现方法](../../docs/mechanism-discovery.md)，按其中的分阶段职责执行；不得越过本 Skill 的输出边界。

## 输入与输出

- 首先读取 `research/research-brief.md`，确认范围与有效问题标准。
- 主要读取 `research/gaps.md` 和 `research/survey.md`。
- 必要时读取 `papers/notes/*.md`，核对 evidence type、locator 和 counter-evidence。
- 遵循 `docs/data-contract.md` 的 ID 与 evidence chain。
- 输出 `research/hypotheses.md`。
- 始终读取 `references/hypothesis_template.md`。

不得绕过 GAP 从论文标题直接生成 hypothesis。每个 hypothesis 至少关联一个稳定 `GAP-...`，并保持：

```text
HYP -> GAP -> survey -> [@paper_id#E...] -> paper note -> source paper
```

## 工作流

1. 读取全部 candidate gaps，包括 evidence、counter-evidence、uncertainty、confidence 和 back-check requirement。
2. 只为能够形成具体关系和可否定预测的 GAP 生成 hypothesis；允许某个 GAP 不产生输出，不固定数量。
3. 明确条件、拟议关系或机制、比较对象和预期受影响指标。避免“可以研究 X”“结合 A+B”或“使用 AI 优化网络”。
4. 解释为何联合关系可能改变问题，而不只是拼接两个已有模块。
5. 继承并扩展 counter-evidence，列出会降低价值或使假设不成立的已有替代方法和条件。
6. 写出原则性的 falsification condition，但不设计完整实验 protocol。
7. 为每个 hypothesis 生成 3–6 条 targeted literature back-check queries；只保存，不执行。
8. 校验所有 evidence references、GAP IDs、必需字段和状态。

## Hypothesis 契约

稳定编号使用 `HYP-001`、`HYP-002`……；已发布编号不得因后续排序重排。每项至少包含：

- `hypothesis_id`
- `title`
- `statement`
- `derived_from`
- `research_problem`
- `rationale`
- `supporting_evidence`
- `counter_evidence`
- `assumptions`
- `falsifiability`
- `uncertainty`
- `back_check_queries`
- `confidence`
- `status`

另记录 `evidence_status: inferred`，与数据契约的 downstream 状态标签一致。

所有 hypothesis 的 `status` 默认为 `NEEDS_BACK_CHECK`。在 targeted back-check 和人工复核前，禁止使用 `novel`、`validated`、`innovation` 或 `confirmed contribution` 状态。

## 质量标准

- **Falsifiable**：说明什么观察会否定它；避免只写“X 可能影响 Y”。
- **Specific**：明确条件、关系/机制、比较基线和指标类别，但不扩展为完整实验方案。
- **Grounded**：supporting evidence 必须来自对应 GAP 已有 evidence chain；`unverified` 不能作为肯定支持。
- **Calibrated**：证据只提示“值得调查”，不能写成已经证明有效。
- **Counter-aware**：主动记录已有替代方法、潜在直接覆盖和可能使收益消失的条件。

## Confidence

- `HIGH`：当前内容中有多来源直接证据支持“值得进一步调查”。
- `MEDIUM`：存在部分支持，但关键关系依赖跨来源 inference。
- `LOW`：直接支持有限或 counter-evidence/coverage risk 较强，但仍有明确、可证伪的核查价值。

Confidence 不表示创新概率，也不应高于其来源 GAP，除非增加了新的可追溯 evidence；本 Skill 不新增文献证据。

## 职责边界

本 Skill 只完成 `GAP -> grounded + falsifiable candidate hypothesis -> back-check queries`。不得执行 queries、判断 novelty、生成最终 candidate innovation ideas、扩大 corpus、修改 Research Brief 或设计完整实验。

## 机制与收益推导

按 hypothesis_template 显式完成六步链条，重点解释传统条件、任务特性与决策改变之间的因果关系。既有 GAP 缺少经典机制或特性证据时，标记需要上游补证，不凭空补齐 hypothesis。

逐项检查特性真实性、机制有效性、净收益解释和 prior-art 风险。写出移除特性/禁止新增控制的反事实预测，以及收益消失或机制不成立的条件。比较应说明资源预算、故障与保障条件，区分机制收益、额外资源收益和保障放宽收益；只给原则性验证要求，不扩展为完整实验 protocol。
