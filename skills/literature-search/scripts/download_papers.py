#!/usr/bin/env python3
"""Download selected-paper PDFs to papers/.cache/pdfs/.

Adapted from aws-samples/sample-knowledge-acquisition-skill.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

from paper_contract import read_jsonl
from url_utils import USER_AGENT, safe_urlopen


def validate_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                return False
            handle.seek(0, os.SEEK_END)
            handle.seek(max(0, handle.tell() - 2048))
            return b"%%EOF" in handle.read()
    except OSError:
        return False


def destination(output_dir: Path, paper_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", paper_id):
        raise ValueError(f"Unsafe paper_id for filename: {paper_id!r}")
    return output_dir / f"{paper_id}.pdf"


def download_pdf(url: str, target: Path, timeout: int = 60) -> bool:
    if not url.startswith("https://"):
        print(f"Error: PDF URL must use HTTPS: {url}", file=sys.stderr)
        return False
    partial = target.with_suffix(target.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with safe_urlopen(request, timeout=timeout) as response, partial.open("wb") as handle:
            while chunk := response.read(64 * 1024):
                handle.write(chunk)
        if not validate_pdf(partial):
            partial.unlink(missing_ok=True)
            print(f"Error: response is not a complete PDF: {url}", file=sys.stderr)
            return False
        partial.replace(target)
        return True
    except Exception as exc:
        partial.unlink(missing_ok=True)
        print(f"Error downloading {url}: {exc}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", default="papers/selected.jsonl")
    parser.add_argument("--output-dir", default="papers/.cache/pdfs")
    parser.add_argument("--max-downloads", type=int, default=10)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [
        record
        for record in read_jsonl(args.jsonl)
        if record.get("selection_status") == "selected" and record.get("pdf_url")
    ]
    downloaded = skipped = failed = planned = 0
    for record in records:
        if downloaded + planned >= args.max_downloads:
            break
        target = destination(output_dir, record["paper_id"])
        if target.exists() and validate_pdf(target):
            skipped += 1
            continue
        if args.dry_run:
            print(f"{record['paper_id']}\t{record['pdf_url']}\t{target}")
            planned += 1
            continue
        print(f"Downloading {record['paper_id']}: {record['title'][:70]}", file=sys.stderr)
        if download_pdf(record["pdf_url"], target):
            downloaded += 1
        else:
            failed += 1
        time.sleep(max(0.0, args.delay))
    print(
        f"Done: downloaded={downloaded} skipped={skipped} failed={failed} planned={planned}",
        file=sys.stderr,
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
