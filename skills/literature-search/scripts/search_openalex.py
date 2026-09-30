#!/usr/bin/env python3
"""Search OpenAlex and emit canonical research-idea-lab JSONL records.

Adapted from aws-samples/sample-knowledge-acquisition-skill.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from paper_contract import canonical_record, utc_now, write_jsonl
from url_utils import USER_AGENT, safe_urlopen

OPENALEX_API = "https://api.openalex.org"


def openalex_request(url: str) -> dict:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    for attempt in range(3):
        request = urllib.request.Request(url, headers=headers)
        try:
            with safe_urlopen(request, timeout=30) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                raise
            wait = 2 ** (attempt + 1)
            print(f"OpenAlex rate limited; retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    return {}


def _abstract(work: dict) -> Optional[str]:
    inverted = work.get("abstract_inverted_index") or {}
    positioned = [(position, word) for word, positions in inverted.items() for position in positions]
    if not positioned:
        return None
    return " ".join(word for _, word in sorted(positioned))


def parse_work(work: dict, timestamp: str) -> Optional[dict]:
    if not work or not work.get("title"):
        return None
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    ids = work.get("ids") or {}
    arxiv_id = ids.get("arxiv")
    if not arxiv_id:
        for location in work.get("locations") or []:
            landing = location.get("landing_page_url") or ""
            if "arxiv.org/" in landing:
                arxiv_id = landing.rstrip("/").split("/")[-1]
                break
    best_oa = work.get("best_oa_location") or {}
    pdf_url = best_oa.get("pdf_url") or primary.get("pdf_url")
    if not pdf_url and arxiv_id:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    raw = {
        "title": work["title"],
        "authors": [
            authorship.get("author", {}).get("display_name", "")
            for authorship in work.get("authorships") or []
            if authorship.get("author", {}).get("display_name")
        ],
        "abstract": _abstract(work),
        "year": work.get("publication_year"),
        "venue": source.get("display_name"),
        "doi": work.get("doi") or ids.get("doi"),
        "arxiv_id": arxiv_id,
        "openalex_id": work.get("id"),
        "url": primary.get("landing_page_url") or work.get("doi") or work.get("id"),
        "pdf_url": pdf_url,
        "citation_count": work.get("cited_by_count"),
    }
    return canonical_record(
        raw,
        "openalex",
        timestamp=timestamp,
        relation_to_seed=[
            {"seed_paper_id": None, "relation": "search_result", "source": "openalex"}
        ],
    )


def search_openalex(
    query: str, max_results: int = 20, *, timestamp: Optional[str] = None
) -> list[dict]:
    timestamp = timestamp or utc_now()
    params = urllib.parse.urlencode(
        {
            "search": query,
            "per_page": min(max_results, 50),
            "page": 1,
            "sort": "relevance_score:desc",
        }
    )
    response = openalex_request(f"{OPENALEX_API}/works?{params}")
    records = []
    for work in response.get("results", []):
        record = parse_work(work, timestamp)
        if record:
            records.append(record)
    return records[:max_results]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    records = search_openalex(args.query, args.max_results)
    if args.output:
        write_jsonl(args.output, records)
    else:
        for record in records:
            print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    print(f"Found {len(records)} OpenAlex papers", file=sys.stderr)


if __name__ == "__main__":
    main()
