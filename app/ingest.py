import json
import re
from pathlib import Path
from typing import Any

from app.config import DOCUMENTS_JSONL, RAW_DATASET_JSON


REQUIRED_FIELDS = ("doc_id", "title", "source", "text")


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text


def load_raw_records(path: Path = RAW_DATASET_JSON) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}. Run: uv run python scripts/prepare_datasets.py"
        )
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("datasets.json must contain a list of records")
    return data


def ingest_records(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for row_number, record in enumerate(records, start=1):
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            raise ValueError(f"Record #{row_number} is missing fields: {missing}")

        doc_id = str(record["doc_id"]).strip()
        if not doc_id:
            raise ValueError(f"Record #{row_number} has an empty doc_id")
        if doc_id in seen_ids:
            raise ValueError(f"Duplicate doc_id: {doc_id}")
        seen_ids.add(doc_id)

        text = normalize_text(str(record["text"]))
        if not text:
            continue

        documents.append(
            {
                "doc_id": doc_id,
                "title": normalize_text(str(record["title"])),
                "source": normalize_text(str(record["source"])),
                "text": text,
            }
        )

    if not documents:
        raise ValueError("No non-empty documents after ingestion")
    return documents


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def ingest_dataset(
    raw_path: Path = RAW_DATASET_JSON,
    output_path: Path = DOCUMENTS_JSONL,
) -> list[dict[str, str]]:
    documents = ingest_records(load_raw_records(raw_path))
    write_jsonl(documents, output_path)
    return documents
