# 中文精读卡模板

```markdown
---
schema_version: "1.0"
note_sequence: "001"
paper_id: "..."
title: "..."
source_url: "..."
pdf_url: "..."
input_coverage: "full_text" # full_text | partial_text | abstract_only | title_only
evidence_level: "full_text" # full_text | partial_text | abstract_only | metadata_only
created_at: "..."
updated_at: "..."
---

# 论文精读卡：标题

## Input Coverage

- evidence_level：
- 输入边界：

## Metadata

- paper_id：
- title：
- authors：
- year：
- venue：
- DOI：
- arXiv：
- source URL：

## Research Question

## Motivation

## Method

## Experimental Setup

- 数据集 / workload：
- topology / system scale：
- baselines：
- metrics：
- 未明确提供的信息：

## Key Findings

## Limitations

优先记录 `author_limitation`；模型判断必须另行标为 `model_inference`。

## Evidence Items

### E001

`[@paper_id#E001]`

- type: paper_claim
- statement: ...
- locator:
  - page: null
  - section: null
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: null

## Model Inference

仅汇总 `type: model_inference` 的内容，并引用对应 evidence item。

## Research Inspiration

允许提出后续可讨论的启发，但必须标为模型推断，不得宣称 novel。

## Reading Priority

- 标签：值得精读 / 值得速读 / 可暂缓
- 理由：
```

说明：

- 文件路径为 `papers/notes/{sequence}-{filesystem-safe-title}.md`；文件名仅供人类阅读。
- `note_sequence` 首次分配后保持不变，论文身份仍由 `paper_id` 决定。
- 输入不足时保留结构并明确未知项，不为了填满模板而虚构。
- `input_coverage` 保留现有 data contract 字段；当 `evidence_level` 为
  `metadata_only` 时，将 `input_coverage` 记为 `title_only`。
- evidence item 编号在单篇 note 内唯一且稳定；编辑时追加，不重排。
- 正文中的重要判断使用 `[@paper_id#E001]` 形式引用本 note 的 evidence item。
