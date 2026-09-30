#!/usr/bin/env python3
"""Unified literature search, deduplication, and lightweight screening.

The API fan-out is adapted from aws-samples/sample-knowledge-acquisition-skill;
the schema, identity, merge, and screening behavior follows docs/data-contract.md.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from paper_contract import (
    VALID_ROLES,
    deduplicate,
    read_jsonl,
    utc_now,
    validate_record,
    write_jsonl,
)
from search_arxiv import search_arxiv
from search_openalex import search_openalex
from search_semantic_scholar import expand_paper, get_paper, search_semantic_scholar

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "in", "is", "of", "on", "or", "over", "the", "to", "using", "what", "with",
}


def build_queries(args: argparse.Namespace) -> list[str]:
    queries = [value.strip() for value in (args.query or []) if value.strip()]
    if not queries:
        parts = [args.topic, args.question] + (args.keywords or [])
        combined = " ".join(value.strip() for value in parts if value and value.strip())
        if combined:
            queries.append(combined)
    # Preserve order and avoid repeated API requests.
    return list(dict.fromkeys(queries))


def query_terms(queries: list[str]) -> set[str]:
    terms = set()
    for query in queries:
        for term in re.findall(r"[\w-]+", query.lower()):
            if len(term) > 2 and term not in STOPWORDS:
                terms.add(term)
    return terms


def relevance_score(record: dict, terms: set[str], recent_since: int) -> tuple[float, int]:
    title = (record.get("title") or "").lower()
    abstract = (record.get("abstract") or "").lower()
    title_hits = sum(term in title for term in terms)
    abstract_hits = sum(term in abstract for term in terms)
    citations = record.get("citation_count") or 0
    completeness = sum(
        bool(record.get(field))
        for field in ("abstract", "doi", "arxiv_id", "venue", "pdf_url")
    )
    recent_bonus = 1.5 if record.get("year") and record["year"] >= recent_since else 0.0
    # Citations provide bounded context but cannot dominate relevance/coverage.
    citation_context = min(math.log1p(max(citations, 0)), 4.0) * 0.2
    score = title_hits * 3 + abstract_hits + completeness * 0.25 + recent_bonus + citation_context
    return score, title_hits + abstract_hits


def parse_role_overrides(values: Optional[list[str]]) -> dict[str, set[str]]:
    overrides: dict[str, set[str]] = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError(f"Invalid --coverage-role {value!r}; expected PAPER_ID=role[,role]")
        paper_id, role_text = value.split("=", 1)
        roles = {role.strip() for role in role_text.split(",") if role.strip()}
        invalid = roles - VALID_ROLES
        if invalid:
            raise ValueError(f"Invalid coverage role(s): {sorted(invalid)}")
        overrides.setdefault(paper_id.strip(), set()).update(roles)
    return overrides


def screen_records(
    records: list[dict],
    queries: list[str],
    *,
    select_count: int,
    recent_since: int,
    role_overrides: dict[str, set[str]],
) -> list[dict]:
    terms = query_terms(queries)
    ranked = []
    for record in records:
        record["selection_reason"] = [
            reason
            for reason in record.get("selection_reason", [])
            if not reason.startswith("lightweight screening:")
            and not reason.startswith("not selected in current bounded screening")
        ]
        if record.get("year") and record["year"] >= recent_since:
            if "recent" not in record["coverage_roles"]:
                record["coverage_roles"].append("recent")
        for role in sorted(role_overrides.get(record["paper_id"], set())):
            if role not in record["coverage_roles"]:
                record["coverage_roles"].append(role)
        if any(reason.startswith("metadata conflict:") for reason in record["selection_reason"]):
            record["selection_status"] = "deferred"
            continue
        score, overlap = relevance_score(record, terms, recent_since)
        ranked.append((score, overlap, record.get("pdf_url") is not None, record))

    ranked.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
            item[3].get("year") or 0,
            item[3]["paper_id"],
        ),
        reverse=True,
    )
    selected = [item[3] for item in ranked[: max(0, select_count)]]

    # Reserve representation for a recent paper when possible.
    if selected and not any("recent" in record["coverage_roles"] for record in selected):
        recent_candidate = next(
            (item[3] for item in ranked if "recent" in item[3]["coverage_roles"]), None
        )
        if recent_candidate:
            selected[-1] = recent_candidate
    selected_ids = {record["paper_id"] for record in selected}

    for score, overlap, _, record in ranked:
        if record["paper_id"] in selected_ids:
            record["selection_status"] = "selected"
            record["selection_reason"].append(
                "lightweight screening: selected from bounded search set; "
                f"query_overlap={overlap}; score={score:.2f}"
            )
        else:
            record["selection_status"] = "deferred"
            record["selection_reason"].append(
                "not selected in current bounded screening; this is not evidence of irrelevance"
            )
        record["updated_at"] = utc_now()
    return [record for record in records if record.get("selection_status") == "selected"]


def validate_all(records: list[dict], label: str) -> None:
    ids = set()
    for index, record in enumerate(records, 1):
        errors = validate_record(record)
        if record.get("paper_id") in ids:
            errors.append("duplicate paper_id")
        ids.add(record.get("paper_id"))
        if errors:
            raise ValueError(f"{label} record {index}: {'; '.join(errors)}")


def run(args: argparse.Namespace) -> dict:
    queries = build_queries(args)
    if not queries and not args.seed:
        raise ValueError("Provide --topic, --question, --keywords, --query, or --seed")
    timestamp = utc_now()
    sources = [source.strip() for source in args.sources.split(",") if source.strip()]
    unknown = set(sources) - {"arxiv", "s2", "openalex"}
    if unknown:
        raise ValueError(f"Unknown sources: {sorted(unknown)}")

    raw_records = []
    source_counts = Counter({"arxiv": 0, "semantic_scholar": 0, "openalex": 0})
    expansion_counts = Counter({"citations": 0, "references": 0, "related": 0, "seeds": 0})
    errors = []
    for query_index, query in enumerate(queries):
        for source in sources:
            try:
                if source == "arxiv":
                    records = search_arxiv(query, args.max_results_per_source, timestamp=timestamp)
                    source_name = "arxiv"
                elif source == "s2":
                    records = search_semantic_scholar(
                        query,
                        args.max_results_per_source,
                        api_key=args.api_key,
                        timestamp=timestamp,
                    )
                    source_name = "semantic_scholar"
                else:
                    records = search_openalex(query, args.max_results_per_source, timestamp=timestamp)
                    source_name = "openalex"
                raw_records.extend(records)
                source_counts[source_name] += len(records)
            except Exception as exc:  # Preserve partial results from other providers.
                message = f"{source} query failed for {query!r}: {type(exc).__name__}: {exc}"
                print(f"Warning: {message}", file=sys.stderr)
                errors.append(message)
        if query_index + 1 < len(queries) and "arxiv" in sources:
            time.sleep(3)

    for seed in args.seed or []:
        try:
            seed_record = get_paper(seed, api_key=args.api_key, timestamp=timestamp)
            if not seed_record:
                raise ValueError("seed could not be resolved")
            raw_records.append(seed_record)
            source_counts["semantic_scholar"] += 1
            expansion_counts["seeds"] += 1
            for relation, report_key in (
                ("cites", "citations"),
                ("cited_by", "references"),
                ("related", "related"),
            ):
                expanded = expand_paper(
                    seed,
                    seed_record["paper_id"],
                    relation,
                    args.expansion_limit,
                    api_key=args.api_key,
                    timestamp=timestamp,
                )
                raw_records.extend(expanded)
                source_counts["semantic_scholar"] += len(expanded)
                expansion_counts[report_key] += len(expanded)
        except Exception as exc:
            message = f"seed expansion failed for {seed!r}: {type(exc).__name__}: {exc}"
            print(f"Warning: {message}", file=sys.stderr)
            errors.append(message)

    # First merge the current run before assigning persistent identity. This
    # allows a DOI discovered by a later provider in the same run to determine
    # the initial paper_id.
    batch_records, batch_stats = deduplicate(
        raw_records, existing=None, preserve_existing_ids=False
    )
    existing = read_jsonl(args.candidates)
    candidates, existing_stats = deduplicate(
        batch_records, existing=existing, preserve_existing_ids=True
    )
    roles = parse_role_overrides(args.coverage_role)
    selected = screen_records(
        candidates,
        queries,
        select_count=args.select_count,
        recent_since=args.recent_since,
        role_overrides=roles,
    )
    validate_all(candidates, "candidate")
    validate_all(selected, "selected")
    write_jsonl(args.candidates, candidates)
    write_jsonl(args.selected, selected)

    report = {
        "queries": queries,
        "seeds": args.seed or [],
        "source_counts": dict(source_counts),
        "expansion_counts": dict(expansion_counts),
        "raw_before_dedup": len(raw_records),
        "batch_after_dedup": len(batch_records),
        "batch_dedup": batch_stats,
        "existing_merge": existing_stats,
        "candidates": len(candidates),
        "selected": len(selected),
        "errors": errors,
        "candidates_path": str(Path(args.candidates)),
        "selected_path": str(Path(args.selected)),
    }
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic")
    parser.add_argument("--question")
    parser.add_argument("--keywords", action="append")
    parser.add_argument("--query", action="append", help="Repeat for multiple explicit queries")
    parser.add_argument("--seed", action="append", help="S2-supported paper identifier")
    parser.add_argument("--sources", default="arxiv,s2,openalex")
    parser.add_argument("--max-results-per-source", type=int, default=20)
    parser.add_argument("--expansion-limit", type=int, default=10)
    parser.add_argument("--select-count", type=int, default=10)
    parser.add_argument(
        "--recent-since",
        type=int,
        default=datetime.now(timezone.utc).year - 2,
        help="Year threshold for automatic recent role",
    )
    parser.add_argument(
        "--coverage-role",
        action="append",
        help="Explicit annotation PAPER_ID=role[,role]",
    )
    parser.add_argument("--api-key", default=os.environ.get("S2_API_KEY"))
    parser.add_argument("--candidates", default="papers/candidates.jsonl")
    parser.add_argument("--selected", default="papers/selected.jsonl")
    parser.add_argument("--report", help="Optional JSON run report")
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
