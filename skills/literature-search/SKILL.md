---
name: literature-search
description: Search, expand, normalize, deduplicate, lightly screen, and download academic papers from arXiv, Semantic Scholar, and OpenAlex when building candidates.jsonl and selected.jsonl from a human-confirmed research brief. Do not use for deep paper analysis, surveys, gap finding, hypotheses, or novelty conclusions.
---

# Literature Search

Build the bounded literature set used by this project. Before running scripts,
read `research/research-brief.md`, then `docs/data-contract.md`. The brief is the
authoritative scope constraint; the data contract is the authoritative schema
and identity contract.

## 共享机制推导规范

使用本 Skill 时读取 [生存性机制发现方法](../../docs/mechanism-discovery.md)，按其中的分阶段职责执行；不得越过本 Skill 的输出边界。

## Human Confirmation Gate

- Read the exact value under `## Status` in `research/research-brief.md`.
- Formal corpus construction is allowed only when the status is `CONFIRMED`.
- When the status is `DRAFT`, do not batch-create or batch-update
  `papers/candidates.jsonl` or `papers/selected.jsonl` and do not claim a formal
  literature review is complete.
- A bounded exploratory lookup is allowed in `DRAFT` only to clarify a concept,
  test terminology, or check whether a class of work exists. Keep it separate
  from the formal corpus and describe it as exploratory.
- During `DRAFT`, use bounded source-specific lookup commands or read-only API
  calls; do not invoke unified `scripts/search_papers.py`, which enforces the
  confirmation gate before writing the formal JSONL files.
- Only the human may authorize changing the brief from `DRAFT` to `CONFIRMED`.

## Inputs and outputs

Accept a research topic, research question, keywords, explicit search queries,
and optional seed-paper identifiers that remain within the confirmed Research
Brief. For a formal run, write:

- `papers/candidates.jsonl`: canonical searched/expanded and screened records.
- `papers/selected.jsonl`: the selected subset using identical records and
  `paper_id` values.
- `papers/.cache/pdfs/{paper_id}.pdf`: temporary PDFs for selected papers only.

Run scripts from the project root with absolute script paths when practical.
Use `python3`; no third-party runtime dependency is required.

## Workflow

1. Turn the topic/question/keywords into a small set of complementary queries,
   or pass explicit `--query` values. Keep query wording in the run report.
2. Run `scripts/search_papers.py` against `arxiv,s2,openalex`. Keep result limits
   bounded per source and inspect reported source failures.
3. When seed papers are supplied, pass identifiers accepted by Semantic Scholar
   (for example `ARXIV:...`, `DOI:...`, or an S2 paper ID). The script adds the
   seed and performs citation, reference, and related-paper expansion.
4. Let the script normalize records, merge cross-source metadata, preserve
   provenance, and deduplicate using the project contract.
5. Review lightweight screening results. Low citation count alone is never an
   exclusion reason. The script auto-labels recent work by year and accepts
   explicit `--coverage-role PAPER_ID=role[,role]` annotations for grounded
   `foundational`, `representative`, `conflicting`, or `limited` judgments.
6. Download selected PDFs, when needed, with `scripts/download_papers.py`.

When several papers first enter `selected.jsonl` together, preserve that first-
entry order for later note-sequence assignment; do not use citation rank or a
later display sort to renumber notes.

Typical bounded run:

```bash
python3 skills/literature-search/scripts/search_papers.py \
  --topic "failure recovery for distributed training" \
  --query "geo-distributed training failure recovery optical networks" \
  --max-results-per-source 10 \
  --select-count 5
```

Seed expansion can be added with repeated `--seed` flags. Use `--expansion-limit`
to keep each citation/reference/related branch small.

## Screening and evidence limits

- Screening uses title/abstract query overlap, metadata completeness, modest
  citation context, recency, and PDF availability. Citation count is never the
  only criterion.
- `recent` may be assigned mechanically from `--recent-since`. Other coverage
  roles require a defensible title/abstract or user-provided judgment.
- Records not selected in a bounded run are `deferred`, not declared irrelevant.
- Preserve conflicting results and metadata conflicts for human review.
- Search coverage is evidence about the current search set only. Never infer
  “not found = does not exist,” and never make a novelty conclusion.

## Responsibilities and exclusions

This skill is responsible only for search, seed expansion, deduplication,
metadata normalization, lightweight screening, and PDF retrieval. It does not
perform deep reading, survey writing, research-gap analysis, hypothesis
generation, experiment design, or novelty assessment.

## 检索组织与回查

在已确认范围内分别组织经典生存性机制与任务特性两条检索线；不以是否同时出现 optical 与 LLM 作为入选必要条件。检索计划说明每组 query 用于补充哪类知识，覆盖经典方法、成立条件、任务特性证据及相邻领域机制；沿用现有 coverage_roles，不新增 JSONL 枚举。

执行 targeted back-check 时，查询应覆盖同问题、同机制、同义词、相邻应用与简单替代方案。使用现有脚本的输出参数将候选、入选、报告及下载记录写入 research/backchecks/ 下的独立路径；先检查脚本参数，不能使用会写入正式 corpus 的默认输出。回查发现相似方案时记录其覆盖范围和剩余差异，不由检索环节判断 novelty。
