import json
import os
import re
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import RAW_DATASET_JSON
from app.ingest import normalize_text


RUSLIT_ARCHIVE_URL = "https://github.com/d0rj/RusLit/archive/refs/heads/main.zip"
RUSLIT_BLOB_URL = "https://github.com/d0rj/RusLit/blob/main"
MAX_RECORDS = 1250
MIN_PARAGRAPH_CHARS = 140
MAX_PARAGRAPH_CHARS = 1800

SOURCES = [
    {"author": "Лев Толстой", "title": "Анна Каренина", "path": "prose/Tolstoy/Анна Каренина.txt"},
    {"author": "Лев Толстой", "title": "Война и мир. Том 1", "path": "prose/Tolstoy/Война и мир. Том 1.txt"},
    {"author": "Федор Достоевский", "title": "Братья Карамазовы", "path": "prose/Dostoevsky/Братья Карамазовы.txt"},
    {"author": "Федор Достоевский", "title": "Идиот", "path": "prose/Dostoevsky/Идиот.txt"},
    {"author": "Николай Гоголь", "title": "Мертвые души", "path": "prose/Gogol/Мёртвые души.txt"},
    {"author": "Николай Гоголь", "title": "Шинель", "path": "prose/Gogol/Шинель.txt"},
    {"author": "Николай Гоголь", "title": "Ревизор", "path": "prose/Gogol/Ревизор.txt"},
    {"author": "Антон Чехов", "title": "Палата N 6", "path": "prose/Chekhov/Палата №6.txt"},
    {"author": "Антон Чехов", "title": "Каштанка", "path": "prose/Chekhov/Каштанка.txt"},
    {"author": "Иван Тургенев", "title": "Отцы и дети", "path": "prose/Turgenev/Отцы и дети.txt"},
]

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")


def download_archive(target: Path) -> None:
    request = urllib.request.Request(
        RUSLIT_ARCHIVE_URL,
        headers={"User-Agent": "educational-rag-homework/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        target.write_bytes(response.read())


def extract_archive(archive_path: Path, target_dir: Path) -> Path:
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(target_dir)
    roots = [path for path in target_dir.iterdir() if path.is_dir()]
    if not roots:
        raise RuntimeError("RusLit archive did not contain a root directory")
    return roots[0]


def get_corpus_root(tmp_dir: Path) -> Path:
    local_root = os.getenv("RUSLIT_DIR")
    if local_root:
        root = Path(local_root)
        if root.exists():
            return root
        raise FileNotFoundError(f"RUSLIT_DIR does not exist: {root}")

    archive_path = tmp_dir / "ruslit.zip"
    download_archive(archive_path)
    return extract_archive(archive_path, tmp_dir / "ruslit")


def source_url(relative_path: str) -> str:
    return f"{RUSLIT_BLOB_URL}/{quote(relative_path)}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def split_long_paragraph(paragraph: str) -> list[str]:
    if len(paragraph) <= MAX_PARAGRAPH_CHARS:
        return [paragraph]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in SENTENCE_SPLIT_RE.split(paragraph):
        sentence = sentence.strip()
        if not sentence:
            continue
        if current and current_len + len(sentence) + 1 > MAX_PARAGRAPH_CHARS:
            chunks.append(" ".join(current))
            current = []
            current_len = 0
        if len(sentence) > MAX_PARAGRAPH_CHARS:
            words = sentence.split()
            for start in range(0, len(words), 120):
                chunks.append(" ".join(words[start : start + 120]))
            continue
        current.append(sentence)
        current_len += len(sentence) + 1

    if current:
        chunks.append(" ".join(current))
    return chunks


def iter_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    for raw_paragraph in re.split(r"\n\s*\n", text):
        paragraph = normalize_text(raw_paragraph)
        for chunk in split_long_paragraph(paragraph):
            if len(chunk) < MIN_PARAGRAPH_CHARS:
                continue
            if len(CYRILLIC_RE.findall(chunk)) < 60:
                continue
            if chunk.isupper():
                continue
            paragraphs.append(chunk)
    return paragraphs


def collect_records(corpus_root: Path, max_records: int = MAX_RECORDS) -> list[dict[str, str]]:
    per_source_limit = max_records // len(SOURCES)
    records: list[dict[str, str]] = []
    source_records: list[list[dict[str, str]]] = []

    for source_number, source in enumerate(SOURCES, start=1):
        text_path = corpus_root / source["path"]
        if not text_path.exists():
            raise FileNotFoundError(f"RusLit source not found: {text_path}")

        paragraphs = iter_paragraphs(read_text(text_path))
        current_source_records = [
            {
                "doc_id": f"ruslit-{source_number:02d}-{index:04d}",
                "title": source["title"],
                "author": source["author"],
                "source": source_url(source["path"]),
                "text": paragraph,
            }
            for index, paragraph in enumerate(paragraphs, start=1)
        ]
        source_records.append(current_source_records)
        records.extend(current_source_records[:per_source_limit])

    if len(records) < max_records:
        positions = [per_source_limit for _ in source_records]
        while len(records) < max_records:
            added = False
            for source_index, current_source_records in enumerate(source_records):
                position = positions[source_index]
                if position < len(current_source_records):
                    records.append(current_source_records[position])
                    positions[source_index] += 1
                    added = True
                    if len(records) >= max_records:
                        break
            if not added:
                break

    records = records[:max_records]
    if len(records) < 1000:
        raise RuntimeError(f"Expected at least 1000 records, got {len(records)}")
    return records


def build_records(max_records: int = MAX_RECORDS) -> list[dict[str, str]]:
    with tempfile.TemporaryDirectory() as tmp:
        corpus_root = get_corpus_root(Path(tmp))
        return collect_records(corpus_root, max_records=max_records)


if __name__ == "__main__":
    records = build_records()
    RAW_DATASET_JSON.parent.mkdir(parents=True, exist_ok=True)
    with RAW_DATASET_JSON.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(records)} records to {RAW_DATASET_JSON}")
