import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import RAW_DATASET_JSON
from app.ingest import normalize_text


SOURCES = [
    {
        "gutenberg_id": "1342",
        "title": "Pride and Prejudice",
        "url": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
    },
    {
        "gutenberg_id": "11",
        "title": "Alice's Adventures in Wonderland",
        "url": "https://www.gutenberg.org/cache/epub/11/pg11.txt",
    },
    {
        "gutenberg_id": "84",
        "title": "Frankenstein",
        "url": "https://www.gutenberg.org/cache/epub/84/pg84.txt",
    },
    {
        "gutenberg_id": "345",
        "title": "Dracula",
        "url": "https://www.gutenberg.org/cache/epub/345/pg345.txt",
    },
    {
        "gutenberg_id": "1661",
        "title": "The Adventures of Sherlock Holmes",
        "url": "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    },
]

START_RE = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
END_RE = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*", re.I | re.S)
MAX_RECORDS = 1250
MIN_PARAGRAPH_CHARS = 120
MAX_PARAGRAPH_CHARS = 1800


def download_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "educational-rag-homework/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def strip_gutenberg_boilerplate(text: str) -> str:
    start = START_RE.search(text)
    if start:
        text = text[start.end() :]
    end = END_RE.search(text)
    if end:
        text = text[: end.start()]
    return text.strip()


def iter_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    for raw_paragraph in re.split(r"\n\s*\n", text):
        paragraph = normalize_text(raw_paragraph)
        if len(paragraph) < MIN_PARAGRAPH_CHARS:
            continue
        if paragraph.isupper():
            continue
        paragraphs.append(paragraph[:MAX_PARAGRAPH_CHARS])
    return paragraphs


def build_records(max_records: int = MAX_RECORDS) -> list[dict[str, str]]:
    per_book_limit = max_records // len(SOURCES)
    records: list[dict[str, str]] = []

    for source in SOURCES:
        text = strip_gutenberg_boilerplate(download_text(source["url"]))
        paragraphs = iter_paragraphs(text)[:per_book_limit]
        for index, paragraph in enumerate(paragraphs, start=1):
            records.append(
                {
                    "doc_id": f"pg{source['gutenberg_id']}-{index:04d}",
                    "title": source["title"],
                    "source": source["url"],
                    "text": paragraph,
                }
            )

    if len(records) < 1000:
        raise RuntimeError(f"Expected at least 1000 records, got {len(records)}")
    return records


if __name__ == "__main__":
    records = build_records()
    RAW_DATASET_JSON.parent.mkdir(parents=True, exist_ok=True)
    with RAW_DATASET_JSON.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(records)} records to {RAW_DATASET_JSON}")
