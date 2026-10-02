---
name: survey-writer
description: Build a Chinese, evidence-linked survey from multiple paper notes in papers/notes/. Use when synthesizing a bounded selected-paper corpus into research problems, method taxonomy, evolution, comparisons, limitations, open questions, and coverage limits.
---

# Survey Writer

围绕一个研究主题组织多篇论文卡片，输出 `research/survey.md`。重点是梳理研究问题、方法路线、跨论文比较和当前局限，不按论文逐篇拼接摘要。

## 输入与输出

- 上游约束：`research/research-brief.md`；先读取它，再处理 corpus。
- 主要输入：`papers/notes/*.md`。
- 辅助输入：`papers/selected.jsonl`，用于核对稳定 `paper_id`、覆盖角色和集合边界。
- 输出：`research/survey.md`。
- 论文卡片是证据接口；按 frontmatter `paper_id` 识别论文，不把可读文件名当作身份。不要为了写综述而重新独立分析 PDF。

## 工作流

1. 读取 `research/research-brief.md`；若为 `DRAFT`，不得把现有 validation corpus 写成正式研究范围，并明确 survey 的暂定性质。
2. 读取 `docs/data-contract.md`，确认引用和证据类型约束。
3. 读取所有纳入综述的论文卡片，统计论文数、年份、coverage roles 和 evidence levels。
4. 始终读取 `references/survey_template.md`。
5. 依据 `references/comparison_dimensions.md` 选择当前材料有证据支持的比较维度。
6. 依据 `references/related_work_patterns.md` 按问题或方法路线组织文字。
7. 建立 research problem → method taxonomy → representative evidence → comparison → limitation/open question 的结构。
8. 校验所有 `[@paper_id]` 与 `[@paper_id#E...]` 引用能按 note frontmatter 解析，不能依赖文件名。

## 证据规则

- 已有工作的关键事实优先引用 evidence item：`[@paper_id#E001]`。
- 仅需指向整篇论文时可使用 `[@paper_id]`。
- 跨论文综合判断同时引用支持它的多个证据，并显式标记为 **综合推断（synthesis/inference）**。
- 保持 `paper_claim`、`experimental_evidence`、`author_limitation`、`model_inference` 和 `unverified` 的边界。
- 不把模型推断改写成论文原结论；不从 `abstract_only` 卡片推导全文实验细节。

## 输出规则

- 按问题和方法路线组织，不使用“Paper A / Paper B / Paper C”流水账。
- benchmark、dataset、topology、workload、baseline 和 metric 只总结卡片中明确记录的信息。
- 作者明确承认的局限与跨论文综合推断分开呈现。
- 证据不足时明确省略演进叙事或比较维度，不强行补全。
- 当前材料少或覆盖不全时，必须声明这是基于 selected corpus 的 pipeline-validation survey。

## 职责边界

本 Skill 不负责搜索、PDF 下载、单篇精读、research-gap 定义、hypothesis、候选创新点、novelty 判断或实验设计。禁止用“没有搜到”推断“不存在”，也不得声称当前材料构成 comprehensive literature review 或 complete state of the art。
