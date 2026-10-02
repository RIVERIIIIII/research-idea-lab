# Project Workflow

所有研究类工作优先读取 `research/research-brief.md`。它定义研究范围，是文献流程的上游约束，但不是 Skill。

工作流：

```text
Human + Codex
-> Research Brief
-> Human Confirmation
-> literature-search
-> paper-deep-note
-> survey-writer
-> research-gap-finder
-> hypothesis
```

## Human Confirmation Gate

- Research Brief 的状态只能是 `DRAFT` 或 `CONFIRMED`，默认 `DRAFT`。
- 只有人明确确认研究范围后，才能把状态改为 `CONFIRMED`。
- 状态不是 `CONFIRMED` 时，不得正式构建或批量更新 `candidates.jsonl` 与 `selected.jsonl`，不得声称完成正式 literature review。
- `DRAFT` 状态允许小规模 exploratory search，用于澄清概念或讨论方向；结果不构成正式 corpus。
- 当前 3 篇论文、notes 和 survey 仅为 pipeline validation 数据，不得反向限定新的 Research Brief。

## DRAFT Discussion Behavior

Research Brief 为 `DRAFT` 时，先帮助人收敛问题，不立即启动正式搜索，也不一次性替人决定研究方向。按以下顺序逐步讨论：

```text
Research Area
-> 真正关注的现象/矛盾
-> Core Problem
-> Research Questions
-> Why It Matters
-> In Scope / Out of Scope
-> Valid Research Problem Criteria 检查
-> 人明确确认
-> CONFIRMED
```

可以指出问题过宽、过窄、预设解法、只是技术组合、缺乏研究价值或难以验证，但最终范围由人确认。不要因为项目旧题目或 validation corpus 默认新方向必须沿用原方案。

## Identity and Note Files

- 论文唯一身份始终是 frontmatter/JSONL 中的稳定 `paper_id`。
- note 文件名采用 `{sequence}-{filesystem-safe-title}.md`，仅供人类阅读。
- sequence 首次分配后不变；文件名、sequence 或标题 slug 均不得替代 `paper_id` 参与 evidence、survey、gap 或 hypothesis 引用。
