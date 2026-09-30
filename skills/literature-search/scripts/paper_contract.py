"""Paper schema, identity, merge, and deduplication for research-idea-lab."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional, Union

SCHEMA_VERSION = "1.0"
IDENTIFIER_FIELDS = ("doi", "arxiv_id", "semantic_scholar_id", "openalex_id")
VALID_ROLES = {"foundational", "representative", "recent", "conflicting", "limited"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean_text(value: object) -> Optional[str]:
    if value is None:
        return None
    cleaned = " ".join(str(value).split())
    return cleaned or None


def normalize_doi(value: object) -> Optional[str]:
    text = clean_text(value)
    if not text:
        return None
    text = text.lower()
    text = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text or None


def normalize_arxiv_id(value: object) -> Optional[str]:
    text = clean_text(value)
    if not text:
        return None
    text = text.lower()
    text = re.sub(r"^arxiv:\s*", "", text)
    text = re.sub(r"^https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/", "", text)
    text = re.sub(r"\.pdf$", "", text)
    text = re.sub(r"v\d+$", "", text)
    return text or None


def normalize_s2_id(value: object) -> Optional[str]:
    text = clean_text(value)
    return text.lower() if text else None


def normalize_openalex_id(value: object) -> Optional[str]:
    text = clean_text(value)
    if not text:
        return None
    text = re.sub(r"^https?://openalex\.org/", "", text, flags=re.I)
    return text.upper() or None


def normalize_title(value: object) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value) or "").lower()
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def normalize_author(value: object) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value) or "").lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_paper_id(record: dict) -> str:
    doi = normalize_doi(record.get("doi"))
    if doi:
        return f"doi-{_sha(doi)}"
    arxiv_id = normalize_arxiv_id(record.get("arxiv_id"))
    if arxiv_id:
        return f"arxiv-{arxiv_id.replace('/', '-')}"
    s2_id = normalize_s2_id(record.get("semantic_scholar_id"))
    if s2_id:
        return f"s2-{s2_id}"
    openalex_id = normalize_openalex_id(record.get("openalex_id"))
    if openalex_id:
        return f"openalex-{openalex_id.lower()}"
    title = normalize_title(record.get("title"))
    if not title:
        raise ValueError("Cannot create paper_id without a title or strong identifier")
    year = record.get("year")
    authors = record.get("authors") or []
    first_author = normalize_author(authors[0]) if authors else ""
    fingerprint = f"{title}|{year or ''}|{first_author}"
    return f"meta-{_sha(fingerprint)}"


def canonical_record(
    raw: dict,
    source: str,
    *,
    timestamp: Optional[str] = None,
    relation_to_seed: Optional[list[dict]] = None,
) -> dict:
    """Convert one provider record to the exact project Paper Schema."""
    timestamp = timestamp or utc_now()
    title = clean_text(raw.get("title"))
    if not title:
        raise ValueError("Paper record has no title")
    authors = [clean_text(a) for a in raw.get("authors", [])]
    authors = [a for a in authors if a]
    year = raw.get("year")
    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None
    citation = raw.get("citation_count", raw.get("citationCount"))
    try:
        citation = int(citation) if citation is not None else None
    except (TypeError, ValueError):
        citation = None

    record = {
        "schema_version": SCHEMA_VERSION,
        "paper_id": "",
        "alternate_paper_ids": [],
        "title": title,
        "authors": authors,
        "year": year,
        "venue": clean_text(raw.get("venue")),
        "abstract": clean_text(raw.get("abstract")),
        "doi": normalize_doi(raw.get("doi")),
        "arxiv_id": normalize_arxiv_id(raw.get("arxiv_id")),
        "semantic_scholar_id": normalize_s2_id(
            raw.get("semantic_scholar_id", raw.get("paperId"))
        ),
        "openalex_id": normalize_openalex_id(raw.get("openalex_id")),
        "url": clean_text(raw.get("url")),
        "pdf_url": clean_text(raw.get("pdf_url")),
        "citation_count": citation,
        "citation_count_source": source if citation is not None else None,
        "citation_count_updated_at": timestamp if citation is not None else None,
        "sources": [source],
        "metadata_provenance": {},
        "relation_to_seed": relation_to_seed or [],
        "coverage_roles": [],
        "selection_status": "candidate",
        "selection_reason": [],
        "discovered_at": timestamp,
        "updated_at": timestamp,
    }
    for field in (
        "title",
        "authors",
        "year",
        "venue",
        "abstract",
        "doi",
        "arxiv_id",
        "semantic_scholar_id",
        "openalex_id",
        "url",
        "pdf_url",
        "citation_count",
    ):
        value = record[field]
        if value not in (None, "", []):
            record["metadata_provenance"][field] = [source]
    record["paper_id"] = generate_paper_id(record)
    return record


def _year_compatible(left: Optional[int], right: Optional[int]) -> bool:
    return left is not None and right is not None and abs(left - right) <= 1


def _author_overlap(left: list[str], right: list[str]) -> bool:
    if not left or not right:
        return False
    return bool({normalize_author(x) for x in left} & {normalize_author(x) for x in right})


def _stronger_conflict(left: dict, right: dict, matched_by: str) -> list[str]:
    """Return conflicts in namespaces stronger than the proposed match."""
    order = list(IDENTIFIER_FIELDS)
    cutoff = order.index(matched_by) if matched_by in order else len(order)
    conflicts = []
    for field in order[:cutoff]:
        a, b = left.get(field), right.get(field)
        if a and b and a != b:
            conflicts.append(field)
    return conflicts


def find_match(candidate: dict, records: list[dict]) -> tuple[Optional[int], Optional[str], list[str]]:
    for field in IDENTIFIER_FIELDS:
        value = candidate.get(field)
        if not value:
            continue
        for index, existing in enumerate(records):
            if existing.get(field) == value:
                return index, field, _stronger_conflict(candidate, existing, field)

    title = normalize_title(candidate.get("title"))
    if not title:
        return None, None, []
    for index, existing in enumerate(records):
        if normalize_title(existing.get("title")) != title:
            continue
        if not _year_compatible(candidate.get("year"), existing.get("year")):
            continue
        if candidate.get("authors") and existing.get("authors"):
            if not _author_overlap(candidate["authors"], existing["authors"]):
                continue
        else:
            # Missing authors only creates a possible duplicate; no auto-merge.
            continue
        conflicts = [
            field
            for field in IDENTIFIER_FIELDS
            if candidate.get(field)
            and existing.get(field)
            and candidate[field] != existing[field]
        ]
        return index, "metadata", conflicts
    return None, None, []


def _source_rank(source: str, field: str) -> int:
    if field in {"year", "venue", "url"}:
        order = ["openalex", "semantic_scholar", "arxiv"]
    else:
        order = ["arxiv", "semantic_scholar", "openalex"]
    try:
        return order.index(source)
    except ValueError:
        return len(order)


def _field_source(record: dict, field: str) -> str:
    values = record.get("metadata_provenance", {}).get(field, [])
    return values[0] if values else (record.get("sources") or [""])[0]


def _union(items: Iterable[object]) -> list:
    result = []
    seen = set()
    for item in items:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def mark_conflict(record: dict, fields: list[str]) -> None:
    reason = "metadata conflict: differing strong identifier(s): " + ", ".join(fields)
    if reason not in record["selection_reason"]:
        record["selection_reason"].append(reason)
    if record["selection_status"] != "selected":
        record["selection_status"] = "deferred"


def merge_records(target: dict, incoming: dict, *, preserve_paper_id: bool) -> dict:
    """Merge incoming metadata into target while retaining provenance."""
    original_id = target["paper_id"]
    changed = False

    for field in IDENTIFIER_FIELDS:
        if not target.get(field) and incoming.get(field):
            target[field] = incoming[field]
            target.setdefault("metadata_provenance", {})[field] = incoming.get(
                "metadata_provenance", {}
            ).get(field, incoming.get("sources", []))
            changed = True
        elif target.get(field) and target.get(field) == incoming.get(field):
            target["metadata_provenance"][field] = _union(
                target["metadata_provenance"].get(field, [])
                + incoming.get("metadata_provenance", {}).get(field, [])
            )

    for field in ("title", "authors", "year", "venue", "abstract", "url", "pdf_url"):
        current, new = target.get(field), incoming.get(field)
        if new in (None, "", []):
            continue
        if current in (None, "", []):
            target[field] = new
            target["metadata_provenance"][field] = incoming["metadata_provenance"].get(
                field, incoming.get("sources", [])
            )
            changed = True
        elif current == new or (
            field == "title" and normalize_title(current) == normalize_title(new)
        ):
            target["metadata_provenance"][field] = _union(
                target["metadata_provenance"].get(field, [])
                + incoming["metadata_provenance"].get(field, [])
            )
        elif _source_rank(_field_source(incoming, field), field) < _source_rank(
            _field_source(target, field), field
        ):
            target[field] = new
            target["metadata_provenance"][field] = incoming["metadata_provenance"].get(
                field, incoming.get("sources", [])
            )
            changed = True

    new_time = incoming.get("citation_count_updated_at")
    old_time = target.get("citation_count_updated_at")
    if incoming.get("citation_count") is not None:
        use_new = target.get("citation_count") is None or (new_time or "") > (old_time or "")
        if new_time == old_time:
            use_new = incoming["citation_count"] > (target.get("citation_count") or 0)
        if use_new:
            for field in (
                "citation_count",
                "citation_count_source",
                "citation_count_updated_at",
            ):
                target[field] = incoming[field]
            target["metadata_provenance"]["citation_count"] = incoming[
                "metadata_provenance"
            ].get("citation_count", incoming.get("sources", []))
            changed = True

    for field in ("sources", "relation_to_seed", "coverage_roles", "selection_reason"):
        merged = _union(target.get(field, []) + incoming.get(field, []))
        if merged != target.get(field, []):
            target[field] = merged
            changed = True

    target["alternate_paper_ids"] = _union(
        target.get("alternate_paper_ids", []) + incoming.get("alternate_paper_ids", [])
    )
    if preserve_paper_id:
        if incoming["paper_id"] != original_id:
            target["alternate_paper_ids"] = _union(
                target["alternate_paper_ids"] + [incoming["paper_id"]]
            )
        target["paper_id"] = original_id
    else:
        target["paper_id"] = generate_paper_id(target)
        retired = [x for x in (original_id, incoming["paper_id"]) if x != target["paper_id"]]
        target["alternate_paper_ids"] = _union(target["alternate_paper_ids"] + retired)

    if changed:
        target["updated_at"] = incoming.get("updated_at") or utc_now()
    return target


def deduplicate(
    incoming: list[dict],
    *,
    existing: Optional[list[dict]] = None,
    preserve_existing_ids: bool = True,
) -> tuple[list[dict], dict]:
    """Deduplicate records and return records plus merge/conflict statistics."""
    records = [dict(r) for r in (existing or [])]
    existing_count = len(records)
    stats = {"input": len(incoming), "merged": 0, "conflicts": 0, "added": 0}
    for candidate in incoming:
        index, matched_by, conflicts = find_match(candidate, records)
        if index is None:
            records.append(candidate)
            stats["added"] += 1
            continue
        if conflicts:
            mark_conflict(records[index], conflicts)
            mark_conflict(candidate, conflicts)
            records.append(candidate)
            stats["conflicts"] += 1
            stats["added"] += 1
            continue
        merge_records(
            records[index],
            candidate,
            preserve_paper_id=preserve_existing_ids and index < existing_count,
        )
        stats["merged"] += 1
    return records, stats


def read_jsonl(path: Union[str, Path]) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {path}:{number}: {exc}") from exc
    return records


def write_jsonl(path: Union[str, Path], records: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    temp.replace(path)


def validate_record(record: dict) -> list[str]:
    required = {
        "schema_version", "paper_id", "alternate_paper_ids", "title", "authors",
        "year", "venue", "abstract", "doi", "arxiv_id", "semantic_scholar_id",
        "openalex_id", "url", "pdf_url", "citation_count",
        "citation_count_source", "citation_count_updated_at", "sources",
        "metadata_provenance", "relation_to_seed", "coverage_roles",
        "selection_status", "selection_reason", "discovered_at", "updated_at",
    }
    errors = [f"missing field: {field}" for field in sorted(required - record.keys())]
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported schema_version")
    if not record.get("paper_id") or not record.get("title"):
        errors.append("paper_id and title must be non-empty")
    invalid_roles = set(record.get("coverage_roles", [])) - VALID_ROLES
    if invalid_roles:
        errors.append(f"invalid coverage_roles: {sorted(invalid_roles)}")
    if record.get("selection_status") not in {"candidate", "selected", "excluded", "deferred"}:
        errors.append("invalid selection_status")
    return errors
