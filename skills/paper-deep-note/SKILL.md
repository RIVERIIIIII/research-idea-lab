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
- 输出且只输出该论文的 `papers/notes/{sequence}-{filesystem-safe-title}.md`。
- 文件名只用于人类阅读；身份和引用始终使用 frontmatter 中的 `paper_id`。

开始前必须读取：

1. `research/research-brief.md`，作为研究范围的上游约束；`DRAFT` 时只处理人明确指定的 exploratory/pipeline-validation 材料。
2. `docs/data-contract.md`，作为身份、note 和 evidence reference 的唯一契约。
3. `references/note_template.md`，作为固定输出结构。
4. 需要判断阅读优先级时，再读取 `references/reading_guidelines.md`。

## Note filename

- `sequence` 是三位数字，按论文首次进入 selected corpus 的顺序分配。
- 新建 note 前先读取现有 note frontmatter 的 `note_sequence`。若有多个尚未建 note 的 selected papers，先按它们首次出现在 `selected.jsonl` 的顺序为整组分配后续号码，再处理目标论文；不得按处理顺序、引用量或后续排序重新编号。
- title slug 使用论文标题生成 filesystem-safe 名称，合理截断；规范见 `docs/data-contract.md`。
- 标题或文件名不是身份。更新 metadata 不得改变 `paper_id`、evidence ID 或 downstream reference。

## Evidence level

在 frontmatter 和 Metadata 中明确记录：

- `full_text`：PDF 全文可读取。
- `partial_text`：只读取了部分正文或 PDF 提取不完整。
- `abstract_only`：只有摘要。
- `metadata_only`：只有书目信息。

`evidence_level` 不得高于实际输入覆盖范围。摘要或 metadata 模式下，不得生成看似来自全文的实验设置、页码、章节、图表或结果。

## 工作流

1. 用 `paper_id` 在 `selected.jsonl` 中找到唯一记录，并定位 `{paper_id}.pdf` 缓存；不要通过 note 文件名匹配身份。
2. 判断 evidence level，并在笔记开头写明输入边界。
3. 提取研究问题、动机、方法、实验设置、关键结果、局限和研究启发。
4. 每个重要事实或判断建立稳定 evidence item；已有 `E001` 等编号不得在更新时重排。
5. 在正文相关判断后使用 `[@paper_id#E...]` 回溯证据项。
6. 写入 note 后检查 note_sequence、paper_id、类型枚举、引用目标、页码/章节和未知字段。

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
