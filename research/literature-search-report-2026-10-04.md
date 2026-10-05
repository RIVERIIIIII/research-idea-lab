# Literature Search Run — 2026-10-04

## Scope

Bounded formal corpus construction for two candidate directions defined in
`research/candidate-directions.md`:

1. application-aware optical soft-failure mitigation for geo-distributed large-model training;
2. SRLG/regional-failure-aware joint training-topology and optical-path survivability.

This run performs search, deduplication, metadata normalization, and lightweight
screening only. Selection is not a novelty conclusion.

## Queries

### Candidate 1

- `optical soft failure recovery modulation spectrum elastic optical network`
- `soft failure evolution QoT proactive reconfiguration optical transport network`
- `geo-distributed large language model training optical network resource allocation`
- `elastic distributed training worker removal bandwidth adaptation`

### Candidate 2

- `shared risk link group regional failure optical datacenter network protection`
- `disaster resilient optical datacenter service placement protection`
- `geo-distributed AI training optical network resource allocation topology`
- `training parallelism topology SRLG optical network`

### Exact-title/direct-neighbor supplement

- CD-CBA for pipeline-parallel distributed LLM training over optical networks
- memory-aware and spectrum-efficient large-model training over optical WANs
- flexible-bandwidth optical transport for geo-distributed machine learning
- resource elasticity in distributed deep learning
- regional-failure-resilient virtual infrastructure mapping
- QoT-assured shared-backup protection under SRLG failures
- software-defined cloud–optical networks for geo-distributed machine learning
- task placement and traffic interleaving for cross-datacenter LLM training

## Retrieval summary

| Run | arXiv | Semantic Scholar | OpenAlex | Raw | After within-run dedup |
|---|---:|---:|---:|---:|---:|
| Candidate 1 | 28 | 7 | 28 | 63 | 59 |
| Candidate 2 | 28 | 7 | 23 | 58 | 54 |
| Supplement | 24 | 0 | 22 | 46 | 40 |

Semantic Scholar returned HTTP 429 for most queries. Partial Semantic Scholar
results were retained; the failure is a coverage limitation and is not evidence
that related work does not exist.

## Formal outputs

- `papers/candidates.jsonl`: 149 deduplicated records.
- `papers/selected.jsonl`: 12 selected records.
- Ten earlier pipeline-validation candidate records remain in `candidates.jsonl`
  as `deferred` for identity continuity; none remain in the formal selected set.
- Two records for *Robust QoT Assured Resource Allocation in Shared Backup Path
  Protection Based EONs* contain a strong-identifier metadata conflict. They are
  retained separately and deferred for manual review.

## Screening rationale

The selected set intentionally covers:

- foundational and representative optical soft-failure response;
- soft-failure evolution/prediction;
- optical-only approaches that test whether compute coupling is necessary;
- distributed-training elasticity as a conflicting/simple alternative;
- recent large-model training and optical-spectrum co-scheduling;
- foundational regional/SRLG protection and compute-network mapping;
- recent direct work on geo-distributed ML/LLM training over optical transport.

Low citation count was not used as an exclusion criterion. Unselected search
results are `deferred`; absence from the selected set is not evidence of
irrelevance or novelty.
