import pickle
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse

from app.config import CHUNKS_JSONL, MATRIX_NPZ, TOP_K, VECTORIZER_PKL
from app.ingest import load_jsonl


class Retriever:
    def __init__(
        self,
        vectorizer_path: Path = VECTORIZER_PKL,
        matrix_path: Path = MATRIX_NPZ,
        chunks_path: Path = CHUNKS_JSONL,
    ) -> None:
        self.vectorizer = self._load_vectorizer(vectorizer_path)
        self.matrix = self._load_matrix(matrix_path)
        self.chunks = load_jsonl(chunks_path)
        if self.matrix.shape[0] != len(self.chunks):
            raise ValueError("Index matrix rows do not match chunk count")

    @staticmethod
    def _load_vectorizer(path: Path) -> Any:
        if not path.exists():
            raise FileNotFoundError(
                f"Index not found: {path}. Run: uv run python scripts/build_index.py"
            )
        with path.open("rb") as f:
            return pickle.load(f)

    @staticmethod
    def _load_matrix(path: Path) -> scipy.sparse.csr_matrix:
        if not path.exists():
            raise FileNotFoundError(
                f"Index not found: {path}. Run: uv run python scripts/build_index.py"
            )
        return scipy.sparse.load_npz(path)

    def search(self, query: str, k: int = TOP_K) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            return []

        k = max(0, min(k, len(self.chunks)))
        if k == 0:
            return []

        query_vector = self.vectorizer.transform([query])
        scores = (self.matrix @ query_vector.T).toarray().ravel()
        top_indices = np.argsort(scores)[::-1][:k]

        results: list[dict[str, Any]] = []
        for index in top_indices:
            chunk = self.chunks[int(index)]
            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "title": chunk["title"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "score": float(scores[index]),
                }
            )
        return results
