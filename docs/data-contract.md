# Research Idea Lab Data Contract

Version: `1.0`

This document defines the shared paper record, deduplication, paper-note, and
evidence-reference contracts used by the project. JSONL means one complete JSON
object per line, encoded as UTF-8. Unknown values use `null` (or `[]` for
multi-value fields); fabricated placeholders such as `"unknown"` are not used.

## 1. Paper identity

`paper_id` is the canonical, filesystem-safe identity used by every stage and
as the filename stem under `papers/notes/`.

### 1.1 Generation priority

When a paper is first added, use the first available identifier below:

1. DOI: `doi-` + SHA-256 of the normalized DOI.
2. arXiv ID: `arxiv-` + normalized arXiv ID, replacing `/` with `-`.
3. Semantic Scholar paper ID: `s2-` + lowercase Semantic Scholar paper ID.
4. OpenAlex work ID: `openalex-` + lowercase OpenAlex work ID without its URL
   prefix.
5. Metadata fallback: `meta-` + SHA-256 of
   `normalized_title|year_or_empty|normalized_first_author_or_empty`.

SHA-256 is lowercase hexadecimal. Prefixes make the identifier origin visible
and prevent collisions between identifier namespaces.

Normalization rules:

- DOI: trim whitespace, lowercase, remove `https://doi.org/`, `http://doi.org/`,
  `doi.org/`, and a leading `doi:`.
- arXiv ID: trim whitespace, lowercase, remove `arxiv:`, arXiv URL prefixes,
  `.pdf`, and the version suffix such as `v2`.
- OpenAlex ID: trim whitespace, lowercase, and remove
  `https://openalex.org/`.
- Title: Unicode NFKC, lowercase, collapse whitespace, normalize Unicode dash
  variants, and remove punctuation for matching/hash input only. The displayed
  `title` is not normalized destructively.
- Author used in fallback: Unicode NFKC, lowercase, collapse whitespace, and
  remove punctuation. Use the first listed author only.

### 1.2 Immutability and late identifiers

Once written to `candidates.jsonl`, `paper_id` is immutable. If a DOI or another
stronger identifier is discovered later, populate its identifier field but do
not rename `paper_id`, its note, or downstream references.

When two existing records are later found to represent one paper, preserve the
record already referenced downstream. Put the retired ID in
`alternate_paper_ids`. If neither is referenced, choose the ID whose underlying
identifier ranks highest in the priority list above; ties are resolved by
lexicographically smaller `paper_id`. If both are already referenced, keep the
earlier `discovered_at` record (then lexicographically smaller `paper_id` on a
tie), migrate references from the retired ID once, and retain that retired ID
in `alternate_paper_ids`. All future records use the winner.

## 2. Unified Paper Schema

`papers/candidates.jsonl` and `papers/selected.jsonl` use the same schema.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | string | yes | Contract version, currently `1.0`. |
| `paper_id` | string | yes | Immutable canonical identity defined above. |
| `alternate_paper_ids` | string[] | yes | Retired IDs merged into this record; otherwise `[]`. |
| `title` | string | yes | Best available publication title. Must not be empty. |
| `authors` | string[] | yes | Ordered author names; `[]` if unavailable. |
| `year` | integer \| null | yes | Publication year. |
| `venue` | string \| null | yes | Published venue or repository label. |
| `abstract` | string \| null | yes | Best available abstract, without model completion. |
| `doi` | string \| null | yes | Normalized DOI without URL prefix. |
| `arxiv_id` | string \| null | yes | Normalized arXiv ID without version suffix. |
| `semantic_scholar_id` | string \| null | yes | Semantic Scholar paper ID. |
| `openalex_id` | string \| null | yes | OpenAlex work ID, e.g. `W123...`. |
| `url` | string \| null | yes | Preferred landing page URL. |
| `pdf_url` | string \| null | yes | Direct legal/open PDF URL when known. |
| `citation_count` | integer \| null | yes | Latest retained count; not treated as timeless fact. |
| `citation_count_source` | string \| null | yes | Source of the retained count. |
| `citation_count_updated_at` | string \| null | yes | ISO 8601 UTC retrieval time. |
| `sources` | string[] | yes | Metadata providers contributing to the merged record. Allowed initial values: `arxiv`, `semantic_scholar`, `openalex`. |
| `metadata_provenance` | object | yes | Map from canonical field name to the source(s) supporting its retained value. |
| `relation_to_seed` | object[] | yes | Discovery relationship(s) to seed papers. |
| `coverage_roles` | string[] | yes | Zero or more controlled roles defined below. |
| `selection_status` | string | yes | One of `candidate`, `selected`, `excluded`, `deferred`. |
| `selection_reason` | string[] | yes | Concise human/model screening reasons; `[]` before screening. |
| `discovered_at` | string | yes | ISO 8601 UTC time first entered into the project. |
| `updated_at` | string | yes | ISO 8601 UTC time canonical metadata last changed. |

`metadata_provenance` is intentionally lightweight. Example:

```json
{"title":["arxiv","semantic_scholar"],"abstract":["arxiv"],"year":["openalex"],"doi":["openalex","semantic_scholar"]}
```

Each `relation_to_seed` item has this shape:

```json
{"seed_paper_id":"arxiv-2301.00001","relation":"cites","source":"semantic_scholar"}
```

Allowed `relation` values are `seed`, `cites`, `cited_by`, `related`, and
`search_result`. `seed_paper_id` may be `null` only for `search_result`.

Allowed `coverage_roles` values:

- `foundational`: establishes an early definition, method, benchmark, or line
  of work needed to understand the topic.
- `representative`: clearly represents an important mainstream method family.
- `recent`: recent enough for the project search window; the concrete cutoff is
  defined per research run, not globally in this schema.
- `conflicting`: provides results, assumptions, or conclusions that materially
  conflict with another included work. The conflict must be explained in
  `selection_reason` or the paper note.
- `limited`: is useful specifically because it exposes a documented limitation,
  constrained setting, negative result, or known weak approach. This label does
  not mean “low quality.”

A single paper may have multiple roles. Roles are screening judgments rather
than claims made by the paper, so they require a reason and may be revised.

### 2.1 Example JSONL record

The line below is illustrative and does not assert that a real paper exists:

```json
{"schema_version":"1.0","paper_id":"arxiv-2401.01234","alternate_paper_ids":[],"title":"Illustrative Paper Title","authors":["A. Researcher","B. Researcher"],"year":2024,"venue":"arXiv","abstract":"Illustrative metadata only.","doi":null,"arxiv_id":"2401.01234","semantic_scholar_id":"0123456789abcdef","openalex_id":"W1234567890","url":"https://arxiv.org/abs/2401.01234","pdf_url":"https://arxiv.org/pdf/2401.01234","citation_count":12,"citation_count_source":"semantic_scholar","citation_count_updated_at":"2026-09-30T00:00:00Z","sources":["arxiv","semantic_scholar","openalex"],"metadata_provenance":{"title":["arxiv","semantic_scholar"],"authors":["arxiv"],"year":["openalex"],"citation_count":["semantic_scholar"]},"relation_to_seed":[{"seed_paper_id":null,"relation":"search_result","source":"arxiv"}],"coverage_roles":["recent"],"selection_status":"candidate","selection_reason":[],"discovered_at":"2026-09-30T00:00:00Z","updated_at":"2026-09-30T00:00:00Z"}
```

## 3. Deduplication and metadata merge

### 3.1 Match order

Compare records in this order and stop at the first reliable match:

1. Equal normalized non-null DOI.
2. Equal normalized non-null arXiv ID.
3. Equal non-null Semantic Scholar paper ID or equal non-null OpenAlex work ID.
4. Metadata fallback: equal normalized title and compatible year/authors.

For fallback matching, require:

- exact normalized title; and
- equal year or a difference of at most one year; and
- at least one equal normalized author name when both records have authors.

If author data is absent on either side, title/year can only create a
`possible_duplicate` for human review; it must not be auto-merged. Materially
different titles with shared authors/year are never sufficient for auto-merge.

A conflicting strong identifier prevents automatic merge. For example, equal
titles paired with two different non-null DOIs are flagged for review rather
than merged.

### 3.2 Field-level merge policy

Merging is additive first: fill missing fields, union identifiers, `sources`,
`alternate_paper_ids`, `relation_to_seed`, and `coverage_roles`, and remove exact
duplicates from arrays. Never replace a non-empty value solely because a later
source was queried.

When non-empty values conflict:

- Identifiers: keep all identifier namespaces. Two different values in the same
  strong namespace require review.
- Title: prefer the published/DOI-associated title; otherwise prefer the arXiv
  title, then Semantic Scholar, then OpenAlex. Ignore punctuation/case-only
  differences.
- Authors: prefer the most complete ordered list from the publication record;
  otherwise arXiv, Semantic Scholar, then OpenAlex. Do not synthesize an author
  order by unioning lists.
- Year: prefer the final publication year over preprint year. If publication
  state is unclear, retain the value supported by the most sources and record
  all supporting sources in `metadata_provenance`.
- Venue: prefer a final peer-reviewed venue over a repository/preprint label.
- Abstract: prefer a non-truncated abstract from the source closest to the
  paper (normally arXiv or the publisher); never concatenate abstracts.
- `url`: prefer DOI/publisher landing page, then arXiv abstract page, then
  Semantic Scholar, then OpenAlex.
- `pdf_url`: prefer a verified direct open-access PDF; never infer a URL that
  was not returned or verified.
- Citation count: retain the largest count among observations collected in the
  same run and store its source/time. Across later runs, use the newest
  observation rather than assuming counts from providers are directly
  comparable.
- Selection fields: `selected` is not downgraded by metadata merge. Exclusion or
  deferral conflicts require review. Union reasons without rewriting their
  meaning.

Any unresolved material conflict is recorded in `selection_reason` as a concise
`metadata conflict: ...` entry. An unselected record becomes `deferred` until
reviewed; an already selected record remains `selected` but is explicitly
flagged for review.

## 4. Candidates and selected records

`candidates.jsonl` is the canonical search/screening set. `selected.jsonl` is a
subset snapshot containing only records chosen for deep reading.

- Both files use the exact schema above and the same immutable `paper_id`.
- Promotion first updates the canonical record in `candidates.jsonl` to
  `selection_status: selected`, adds at least one `selection_reason`, and then
  copies that same full record into `selected.jsonl`.
- Selection does not create a new identity or renormalize metadata.
- Later metadata corrections are applied consistently to both copies when the
  paper exists in both files.
- Excluded/deferred records remain in `candidates.jsonl`; they are not written
  to `selected.jsonl`.

## 5. Paper Note Schema

Each selected paper is written to:

```text
papers/notes/{paper_id}.md
```

The note begins with YAML frontmatter:

```yaml
---
schema_version: "1.0"
paper_id: "arxiv-2401.01234"
title: "Illustrative Paper Title"
source_url: "https://arxiv.org/abs/2401.01234"
pdf_url: "https://arxiv.org/pdf/2401.01234"
input_coverage: "full_text" # full_text | partial_text | abstract_only | title_only
created_at: "2026-09-30T00:00:00Z"
updated_at: "2026-09-30T00:00:00Z"
---
```

The body may use domain-specific sections, but every important extracted fact or
judgment is represented by an evidence item:

```markdown
### E001

- type: experimental_evidence
- statement: Concise paraphrase of what the evidence supports.
- locator:
  - page: 7
  - section: "4.2 Main Results"
  - figure: null
  - table: "Table 2"
- supports: [E000]
- confidence: high
- notes: null
```

Evidence IDs are unique and stable within a note (`E001`, `E002`, ...). Do not
renumber existing items when editing a note. Allowed `type` values are:

- `paper_claim`: a claim explicitly made by the paper. It is not automatically
  treated as established fact.
- `experimental_evidence`: a reported experiment, observation, dataset result,
  analysis, or other empirical support.
- `author_limitation`: a limitation explicitly acknowledged by the authors.
- `model_inference`: an interpretation inferred from paper content. It must cite
  one or more other evidence items in `supports` and use calibrated language.
- `unverified`: information that could not be confirmed from the available
  input. It must not be used as positive support for a gap or hypothesis.

`locator` preserves every available position: page, section, subsection,
paragraph, figure, table, appendix, or supplied excerpt. Unknown locator fields
are `null`; page numbers must not be invented. `confidence` is one of `high`,
`medium`, or `low` and expresses extraction/inference confidence, not paper
quality. Short source excerpts are optional and must be clearly marked as
verbatim quotations.

Canonical evidence references are:

```text
[@{paper_id}]       # paper-level reference when no finer locator exists
[@{paper_id}#E001]  # preferred evidence-item reference
```

## 6. Downstream evidence-reference rules

`research/survey.md`, `research/gaps.md`, and `research/hypotheses.md` use stable
local statement IDs:

- survey finding: `SURV-001`
- gap: `GAP-001`
- hypothesis: `HYP-001`
- final candidate idea: `IDEA-001`

Each key statement contains:

- `evidence`: one or more canonical paper/evidence references;
- `derived_from`: upstream statement IDs, where applicable; and
- a label distinguishing `supported`, `inferred`, or `unverified` status.

Minimal example:

```markdown
### GAP-001

- status: inferred
- statement: A bounded, potentially underexplored research gap.
- evidence: [@arxiv-2401.01234#E003, @doi-<sha256>#E007]
- derived_from: [SURV-002]
- verification_needed: Search adjacent terminology and conflicting work.
```

Rules:

1. Every key statement about existing work cites at least one `paper_id`, and
   preferably a specific evidence item.
2. Survey synthesis may combine papers, but each component claim remains
   attributable to its supporting papers.
3. A gap cannot be supported only by `model_inference`; it must identify the
   underlying claims/evidence and state what further search is needed.
4. `unverified` items cannot serve as affirmative evidence. They are open checks.
5. Absence from the collected literature is written as “not found in the
   current search set,” never as proof of novelty.
6. Conflicting evidence is retained and cited; it is not silently resolved.
7. Hypotheses and candidate ideas remain `potentially novel` until broader
   prior-art checking and human review.

The intended trace is therefore explicit:

```text
IDEA-... -> HYP-.../GAP-... -> SURV-... -> [@paper_id#E...] ->
papers/notes/{paper_id}.md -> Paper Schema URL/identifier -> source paper
```

## 7. PDF cache

Downloaded PDFs are temporary inputs stored only under:

```text
papers/.cache/pdfs/
```

They are excluded from Git. Notes must reference the canonical `paper_id` and
source URLs, not depend on the cache path remaining available.
