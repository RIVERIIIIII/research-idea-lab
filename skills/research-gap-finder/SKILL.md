---
name: research-gap-finder
description: Identify evidence-linked candidate research gaps from a confirmed research brief, an existing survey, and paper notes. Use for limitation, conflict, assumption, coverage, or integration analysis; do not use for novelty claims, hypotheses, experiments, or literature search.
---

# Research Gap Finder

从现有 evidence 出发，识别值得进一步文献回查的候选 research gaps。目标是区分真实问题线索、工程集成机会和“文献读得还不够”造成的表面空白，而不是硬造创新点。

## 共享机制推导规范

使用本 Skill 时读取 [生存性机制发现方法](../../docs/mechanism-discovery.md)，按其中的分阶段职责执行；不得越过本 Skill 的输出边界。

## 输入与输出

- 上游范围：`research/research-brief.md`；必须先读取并确认状态为 `CONFIRMED`。
- 主要输入：`research/survey.md` 与其中实际纳入的 `papers/notes/*.md`。
- 身份与证据契约：`docs/data-contract.md`。
- 输出：`research/gaps.md`。
- 本 Skill 不启动检索，不补读未完成的 selected papers，不修改 Research Brief。

始终读取 `references/gap_analysis_template.md`。需要检查问题是否被正确界定时读取 `references/problem_framing_template.md`。

## 工作流

1. 概括输入范围、evidence levels 和 corpus limitations；小型或 validation corpus 必须明确降级结论强度。
2. 从 `paper_claim`、`experimental_evidence`、`author_limitation` 和 survey 的显式 synthesis 中提取 limitation、conflict、assumption 与 unresolved question。
3. 生成候选 gap 前先说明从 observed evidence 到 cross-paper synthesis 的推导；candidate gap 本身始终是 inference。
4. 对每个候选主动寻找当前 corpus 中的已解决、部分解决、冲突或“不重要”证据，写入 `counter_evidence`。
5. 依据 Research Brief 的范围和有效问题标准筛选；不满足者写入 `Rejected / Weak Gap Candidates`，不为凑数保留。
6. 校验所有 `[@paper_id#E...]` 引用能解析到 note；无法回溯的判断不得成为 candidate gap。

## Gap 类型

- `limitation-driven`：一个或多个工作明确承认的限制形成问题线索。
- `conflict-driven`：结论、假设、目标或方法间存在有证据的冲突。
- `assumption-driven`：方法依赖现实中可能不成立的强假设。
- `coverage-driven`：当前 corpus 对重要场景覆盖薄弱；必须设置 `back_check_needed: true`，且不得据此声称真实空白。
- `integration-driven`：已有工作分别覆盖问题链的不同部分。必须解释联合关系为何会改变问题、决策或评价目标；不能把 `A 做 X + B 做 Y` 直接当创新点。

## Candidate Gap 契约

稳定编号使用 `GAP-001`、`GAP-002`……；已发布编号后不得因排序变化而重排。每个 gap 至少包含：

- `gap_id`
- `title`
- `gap_type`
- `description`
- `why_it_may_matter`
- `evidence`
- `derived_from`
- `supporting_papers`
- `counter_evidence`
- `uncertainty`
- `back_check_needed`
- `confidence`

`confidence` 只能是 `HIGH`、`MEDIUM` 或 `LOW`，表示“当前 corpus 是否支持该问题值得进一步核查”，不表示 novelty。即使为 `HIGH`，也必须经过 targeted literature back-check。

## 证据层级

- **Observed Evidence**：论文陈述、实验结果或作者明确 limitation；逐项引用 evidence item。
- **Cross-paper Synthesis**：把多篇证据放在一起得到的综合观察；显式标记为 synthesis/inference。
- **Candidate Gap Inference**：在前两层之上提出的待核查问题；不得改写成 existing literature fact。

`model_inference` 可作为推理线索，但必须保留其类型并回溯其 `supports`，不能伪装成论文事实。`unverified` 只能降低置信度或提示回查，不能肯定支持 gap。

## 拒绝规则

以下情况默认进入 `Rejected / Weak Gap Candidates`：

- 只有“当前没有搜到”；
- 只是把两个热门关键词或技术名称拼接；
- 只是把业务标签替换为 AI/LLM，没有改变问题机制；
- 当前 corpus 已有直接或部分解法，而候选没有说明剩余问题；
- 研究意义、光层不可替代性或算网耦合不符合 Research Brief；
- 证据只来自 metadata、标题或无法解析的引用。

## 职责边界

本 Skill 只完成 `evidence → limitation/conflict/unresolved question → candidate gap`。不得生成 hypothesis、candidate innovation ideas、novelty conclusion、实验方案或 targeted literature back-check，也不得扩大 corpus。

## 机制机会分析

在生成 GAP 前，依据 survey 的经典机制表与任务特性表建立有证据的机会矩阵；不机械枚举所有组合。每个保留交叉项说明经典方案的受限条件、任务特性为何与该条件有关、可能改变的决策位置和仍需验证的关系。采用 gap_analysis_template 的新增结构；缺少关键证据时保留为待补证线索，不生成肯定支持的 GAP。

覆盖不足本身只触发回查，不构成机制机会。传统假设可以在原场景下合理；明确在哪些条件下才出现优化机会。通过③④⑤的连接解释待解决问题，但具体方案与可证伪预测留给 hypothesis。
