#!/usr/bin/env python3
"""Search arXiv and emit canonical research-idea-lab JSONL records.

Adapted from aws-samples/sample-knowledge-acquisition-skill.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional

from paper_contract import canonical_record, utc_now, write_jsonl
from url_utils import USER_AGENT, safe_urlopen

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _text(entry: ET.Element, tag: str, namespace: str = "atom") -> str:
    element = entry.find(f"{namespace}:{tag}", NS)
    return element.text.strip() if element is not None and element.text else ""


def parse_entry(entry: ET.Element, timestamp: str) -> Optional[dict]:
    entry_url = _text(entry, "id")
    title = " ".join(_text(entry, "title").split())
    if not title:
        return None
    arxiv_id = entry_url.split("/abs/")[-1] if "/abs/" in entry_url else ""
    authors = [
        node.text.strip()
        for author in entry.findall("atom:author", NS)
        if (node := author.find("atom:name", NS)) is not None and node.text
    ]
    pdf_url = ""
    for link in entry.findall("atom:link", NS):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            pdf_url = link.get("href", "")
            break
    published = _text(entry, "published")
    raw = {
        "title": title,
        "authors": authors,
        "abstract": " ".join(_text(entry, "summary").split()),
        "year": int(published[:4]) if len(published) >= 4 else None,
        "venue": "arXiv",
        "doi": _text(entry, "doi", "arxiv"),
        "arxiv_id": arxiv_id,
        "url": entry_url or (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None),
        "pdf_url": pdf_url or (f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else None),
        "citation_count": None,
    }
    return canonical_record(
        raw,
        "arxiv",
        timestamp=timestamp,
        relation_to_seed=[
            {"seed_paper_id": None, "relation": "search_result", "source": "arxiv"}
        ],
    )


def search_arxiv(query: str, max_results: int = 20, *, timestamp: Optional[str] = None) -> list[dict]:
    timestamp = timestamp or utc_now()
    params = urllib.parse.urlencode(
        {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": min(max_results, 100),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
    )
    request = urllib.request.Request(
        f"{ARXIV_API}?{params}", headers={"User-Agent": USER_AGENT}
    )
    with safe_urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    records = []
    for entry in root.findall("atom:entry", NS):
        record = parse_entry(entry, timestamp)
        if record:
            records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    records = search_arxiv(args.query, args.max_results)
    if args.output:
        write_jsonl(args.output, records)
    else:
        for record in records:
            print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    print(f"Found {len(records)} arXiv papers", file=sys.stderr)


if __name__ == "__main__":
    main()
