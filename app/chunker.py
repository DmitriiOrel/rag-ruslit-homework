import re
from typing import Any

from app.config import CHUNK_OVERLAP_WORDS, CHUNK_SIZE_WORDS


WORD_RE = re.compile(r"\S+")


def chunk_text(
    text: str,
    chunk_size_words: int = CHUNK_SIZE_WORDS,
    overlap_words: int = CHUNK_OVERLAP_WORDS,
) -> list[str]:
    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be positive")
    if overlap_words < 0:
        raise ValueError("overlap_words cannot be negative")
    if overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be smaller than chunk_size_words")

    words = WORD_RE.findall(text)
    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size_words - overlap_words
    for start in range(0, len(words), step):
        part = words[start : start + chunk_size_words]
        if not part:
            break
        chunks.append(" ".join(part))
        if start + chunk_size_words >= len(words):
            break
    return chunks


def chunk_documents(
    documents: list[dict[str, Any]],
    chunk_size_words: int = CHUNK_SIZE_WORDS,
    overlap_words: int = CHUNK_OVERLAP_WORDS,
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for document in documents:
        for chunk_index, text in enumerate(
            chunk_text(document["text"], chunk_size_words, overlap_words)
        ):
            chunks.append(
                {
                    "chunk_id": f"{document['doc_id']}:{chunk_index}",
                    "doc_id": document["doc_id"],
                    "title": document["title"],
                    "source": document["source"],
                    "chunk_index": chunk_index,
                    "text": text,
                }
            )
    if not chunks:
        raise ValueError("No chunks created")
    return chunks
