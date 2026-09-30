---
name: paper-deep-note
description: Produce a grounded Chinese deep-reading note for one selected academic paper from its metadata and preferably its PDF, preserving paper_id and evidence-item traceability. Do not use for surveys, gap finding, hypothesis generation, novelty claims, or experiment design.
---

# Paper Deep Note

处理一篇已入选论文，输出中文结构化精读卡。核心目标是准确区分论文陈述、实验支持、作者局限、模型推断和待核实信息。

## 输入与输出

- 从 `papers/selected.jsonl` 读取目标记录，不重新生成或修改 `paper_id`。
- 优先读取 `papers/.cache/pdfs/{paper_id}.pdf`。
- PDF 不存在时，可以调用现有 `skills/literature-search/scripts/download_papers.py`；不要实现新的下载器。
- 输出且只输出该论文的 `papers/notes/{paper_id}.md`。

开始前必须读取：

1. `docs/data-contract.md`，作为身份、note 和 evidence reference 的唯一契约。
2. `references/note_template.md`，作为固定输出结构。
3. 需要判断阅读优先级时，再读取 `references/reading_guidelines.md`。

## Evidence level

在 frontmatter 和 Metadata 中明确记录：

- `full_text`：PDF 全文可读取。
- `partial_text`：只读取了部分正文或 PDF 提取不完整。
- `abstract_only`：只有摘要。
- `metadata_only`：只有书目信息。

`evidence_level` 不得高于实际输入覆盖范围。摘要或 metadata 模式下，不得生成看似来自全文的实验设置、页码、章节、图表或结果。

## 工作流

1. 用 `paper_id` 在 `selected.jsonl` 中找到唯一记录并定位同名 PDF。
2. 判断 evidence level，并在笔记开头写明输入边界。
3. 提取研究问题、动机、方法、实验设置、关键结果、局限和研究启发。
4. 每个重要事实或判断建立稳定 evidence item；已有 `E001` 等编号不得在更新时重排。
5. 在正文相关判断后使用 `[@paper_id#E...]` 回溯证据项。
6. 写入 note 后检查 paper_id、类型枚举、引用目标、页码/章节和未知字段。

## 证据约束

只使用以下类型：

- `paper_claim`：论文明确陈述，但不自动视为已被证明的事实。
- `experimental_evidence`：论文报告的实验、数据或分析结果。
- `author_limitation`：作者明确承认的限制、边界或未来工作。
- `model_inference`：基于论文内容形成的解释或启发，必须在 `supports` 中引用其他 evidence items。
- `unverified`：当前输入无法核实的信息，不得用于肯定支持 gap 或假设。

禁止把 `model_inference` 混入作者结论。实验设置、数值、数据集、baseline、指标、图表和开源状态未明确出现时，写“未提供”或 `unverified`，不要补全。

## 职责边界

本 Skill 只负责单篇论文精读卡。不得写 survey、寻找 research gap、生成 hypothesis、判断创新性或设计完整实验。
