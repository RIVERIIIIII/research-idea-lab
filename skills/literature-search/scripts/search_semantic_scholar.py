#!/usr/bin/env python3
"""Search and expand Semantic Scholar papers into canonical JSONL records.

Adapted from aws-samples/sample-knowledge-acquisition-skill.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from paper_contract import canonical_record, utc_now, write_jsonl
from url_utils import USER_AGENT, safe_urlopen

S2_API = "https://api.semanticscholar.org/graph/v1"
S2_RECOMMENDATIONS_API = "https://api.semanticscholar.org/recommendations/v1"
FIELDS = (
    "paperId,title,authors,abstract,year,venue,citationCount,referenceCount,"
    "externalIds,url,publicationDate,openAccessPdf"
)


def s2_request(url: str, api_key: Optional[str] = None) -> dict:
    headers = {"User-Agent": USER_AGENT}
    if api_key:
        headers["x-api-key"] = api_key
    for attempt in range(3):
        request = urllib.request.Request(url, headers=headers)
        try:
            with safe_urlopen(request, timeout=30) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                raise
            wait = 2 ** (attempt + 1)
            print(f"Semantic Scholar rate limited; retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)
    return {}


def parse_paper(
    data: dict,
    *,
    timestamp: str,
    relation: str = "search_result",
    seed_paper_id: Optional[str] = None,
) -> Optional[dict]:
    if not data or not data.get("title"):
        return None
    external = data.get("externalIds") or {}
    arxiv_id = external.get("ArXiv")
    open_pdf = (data.get("openAccessPdf") or {}).get("url")
    pdf_url = open_pdf or (f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else None)
    raw = {
        "title": data["title"],
        "authors": [
            author.get("name", "")
            for author in (data.get("authors") or [])
            if author.get("name")
        ],
        "abstract": data.get("abstract"),
        "year": data.get("year"),
        "venue": data.get("venue"),
        "doi": external.get("DOI"),
        "arxiv_id": arxiv_id,
        "semantic_scholar_id": data.get("paperId"),
        "openalex_id": external.get("OpenAlex"),
        "url": data.get("url"),
        "pdf_url": pdf_url,
        "citation_count": data.get("citationCount"),
    }
    return canonical_record(
        raw,
        "semantic_scholar",
        timestamp=timestamp,
        relation_to_seed=[
            {
                "seed_paper_id": seed_paper_id,
                "relation": relation,
                "source": "semantic_scholar",
            }
        ],
    )


def search_semantic_scholar(
    query: str,
    max_results: int = 20,
    *,
    api_key: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> list[dict]:
    timestamp = timestamp or utc_now()
    params = urllib.parse.urlencode(
        {"query": query, "limit": min(max_results, 100), "fields": FIELDS}
    )
    response = s2_request(f"{S2_API}/paper/search?{params}", api_key)
    records = []
    for item in response.get("data", []):
        record = parse_paper(item, timestamp=timestamp)
        if record:
            records.append(record)
    return records


def get_paper(
    paper_id: str, *, api_key: Optional[str] = None, timestamp: Optional[str] = None
) -> Optional[dict]:
    timestamp = timestamp or utc_now()
    encoded = urllib.parse.quote(paper_id, safe="")
    params = urllib.parse.urlencode({"fields": FIELDS})
    data = s2_request(f"{S2_API}/paper/{encoded}?{params}", api_key)
    record = parse_paper(data, timestamp=timestamp, relation="seed")
    if record:
        record["relation_to_seed"][0]["seed_paper_id"] = record["paper_id"]
    return record


def expand_paper(
    paper_id: str,
    seed_paper_id: str,
    relation: str,
    max_results: int,
    *,
    api_key: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> list[dict]:
    timestamp = timestamp or utc_now()
    encoded = urllib.parse.quote(paper_id, safe="")
    if relation == "cites":
        # Papers returned by /citations cite the seed.
        url = f"{S2_API}/paper/{encoded}/citations?" + urllib.parse.urlencode(
            {"fields": FIELDS, "limit": min(max_results, 1000)}
        )
        payload_key, item_key = "data", "citingPaper"
    elif relation == "cited_by":
        # Papers returned by /references are cited by the seed.
        url = f"{S2_API}/paper/{encoded}/references?" + urllib.parse.urlencode(
            {"fields": FIELDS, "limit": min(max_results, 1000)}
        )
        payload_key, item_key = "data", "citedPaper"
    elif relation == "related":
        url = f"{S2_RECOMMENDATIONS_API}/papers/forpaper/{encoded}?" + urllib.parse.urlencode(
            {"fields": FIELDS, "limit": min(max_results, 500)}
        )
        payload_key, item_key = "recommendedPapers", None
    else:
        raise ValueError(f"Unsupported expansion relation: {relation}")

    response = s2_request(url, api_key)
    records = []
    for item in response.get(payload_key, []):
        data = item.get(item_key, {}) if item_key else item
        record = parse_paper(
            data,
            timestamp=timestamp,
            relation=relation,
            seed_paper_id=seed_paper_id,
        )
        if record:
            records.append(record)
    return records[:max_results]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--query")
    mode.add_argument("--citations-of")
    mode.add_argument("--references-of")
    mode.add_argument("--related-to")
    parser.add_argument("--seed-paper-id", help="Canonical seed paper_id for expansion provenance")
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--api-key", default=os.environ.get("S2_API_KEY"))
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    timestamp = utc_now()
    if args.query:
        records = search_semantic_scholar(
            args.query, args.max_results, api_key=args.api_key, timestamp=timestamp
        )
    else:
        provider_id = args.citations_of or args.references_of or args.related_to
        relation = "cites" if args.citations_of else "cited_by" if args.references_of else "related"
        records = expand_paper(
            provider_id,
            args.seed_paper_id or provider_id,
            relation,
            args.max_results,
            api_key=args.api_key,
            timestamp=timestamp,
        )
    if args.output:
        write_jsonl(args.output, records)
    else:
        for record in records:
            print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    print(f"Found {len(records)} Semantic Scholar papers", file=sys.stderr)


if __name__ == "__main__":
    main()
