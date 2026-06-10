import re
from typing import Any

from app.config import MAX_ANSWER_SENTENCES, MIN_SCORE, TOP_K
from app.retriever import Retriever

REFUSAL_EMPTY_QUESTION = "Введите вопрос."
REFUSAL_NO_CONTEXT = (
    "Я не нашел достаточно релевантных фрагментов в корпусе RusLit, "
    "поэтому не буду придумывать ответ без источников."
)

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё'-]{2,}")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


def split_sentences(text: str) -> list[str]:
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]
    return sentences or [text.strip()]


def _sentence_score(sentence: str, query_tokens: set[str], hit_score: float) -> float:
    sentence_tokens = tokenize(sentence)
    overlap = len(sentence_tokens & query_tokens)
    if overlap == 0:
        return 0.0
    return overlap + hit_score


def build_answer(question: str, hits: list[dict[str, Any]]) -> str:
    relevant_hits = [hit for hit in hits if hit["score"] >= MIN_SCORE]
    if not relevant_hits:
        return REFUSAL_NO_CONTEXT

    query_tokens = tokenize(question)
    candidates: list[tuple[float, int, str, dict[str, Any]]] = []
    for hit_number, hit in enumerate(relevant_hits, start=1):
        for sentence in split_sentences(hit["text"]):
            score = _sentence_score(sentence, query_tokens, hit["score"])
            if score > 0:
                candidates.append((score, hit_number, sentence, hit))

    if not candidates:
        candidates = [
            (hit["score"], index, hit["text"], hit)
            for index, hit in enumerate(relevant_hits, start=1)
        ]

    candidates.sort(key=lambda row: row[0], reverse=True)
    used_sentences: set[str] = set()
    answer_lines = ["По найденным источникам:"]

    for _, source_number, sentence, _hit in candidates:
        normalized = sentence.lower()
        if normalized in used_sentences:
            continue
        used_sentences.add(normalized)
        answer_lines.append(f"- {sentence} [{source_number}]")
        if len(used_sentences) >= MAX_ANSWER_SENTENCES:
            break

    return "\n".join(answer_lines)


def format_sources(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "doc_id": hit["doc_id"],
            "chunk_id": hit["chunk_id"],
            "title": hit["title"],
            "source": hit["source"],
            "score": hit["score"],
            "text": hit["text"],
        }
        for hit in hits
    ]


def ask(
    question: str,
    k: int = TOP_K,
    retriever: Retriever | None = None,
) -> dict[str, Any]:
    if not question.strip():
        return {"answer": REFUSAL_EMPTY_QUESTION, "sources": []}

    active_retriever = retriever or Retriever()
    hits = active_retriever.search(question, k=k)
    return {
        "answer": build_answer(question, hits),
        "sources": format_sources(hits),
    }
