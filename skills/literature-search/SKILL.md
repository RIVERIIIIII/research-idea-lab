---
name: literature-search
description: Search, expand, normalize, deduplicate, lightly screen, and download academic papers from arXiv, Semantic Scholar, and OpenAlex when building candidates.jsonl and selected.jsonl for the research-idea-lab workflow. Do not use for deep paper analysis, surveys, gap finding, hypotheses, or novelty conclusions.
---

# Literature Search

Build the bounded literature set used by this project. Before running scripts,
read `docs/data-contract.md`; it is the authoritative schema and identity
contract.

## Inputs and outputs

Accept a research topic, research question, keywords, explicit search queries,
and optional seed-paper identifiers. Write:

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
