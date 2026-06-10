import pickle

import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from app.ingest import write_jsonl
from app.retriever import Retriever


def test_retriever_returns_best_matching_chunk(tmp_path) -> None:
    chunks = [
        {
            "chunk_id": "a:0",
            "doc_id": "a",
            "title": "Alice",
            "source": "memory",
            "chunk_index": 0,
            "text": "Alice found a golden key on a glass table.",
        },
        {
            "chunk_id": "b:0",
            "doc_id": "b",
            "title": "Frankenstein",
            "source": "memory",
            "chunk_index": 0,
            "text": "Victor studied natural philosophy and chemistry.",
        },
    ]
    texts = [chunk["text"] for chunk in chunks]
    vectorizer = TfidfVectorizer(norm="l2")
    matrix = vectorizer.fit_transform(texts)

    vectorizer_path = tmp_path / "vectorizer.pkl"
    matrix_path = tmp_path / "matrix.npz"
    chunks_path = tmp_path / "chunks.jsonl"

    with vectorizer_path.open("wb") as f:
        pickle.dump(vectorizer, f)
    scipy.sparse.save_npz(matrix_path, matrix)
    write_jsonl(chunks, chunks_path)

    retriever = Retriever(vectorizer_path, matrix_path, chunks_path)
    hits = retriever.search("golden key", k=2)

    assert hits[0]["doc_id"] == "a"
    assert hits[0]["score"] > hits[1]["score"]
