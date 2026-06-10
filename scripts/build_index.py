import pickle
import sys
from pathlib import Path

import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.chunker import chunk_documents
from app.config import CHUNKS_JSONL, DOCUMENTS_JSONL, INDEX_DIR, MATRIX_NPZ, VECTORIZER_PKL
from app.ingest import ingest_dataset, write_jsonl


def build_index() -> dict[str, int]:
    documents = ingest_dataset(output_path=DOCUMENTS_JSONL)
    chunks = chunk_documents(documents)
    write_jsonl(chunks, CHUNKS_JSONL)

    texts = [chunk["text"] for chunk in chunks]
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        norm="l2",
    )
    matrix = vectorizer.fit_transform(texts)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with VECTORIZER_PKL.open("wb") as f:
        pickle.dump(vectorizer, f)
    scipy.sparse.save_npz(MATRIX_NPZ, matrix)

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "features": len(vectorizer.get_feature_names_out()),
    }


if __name__ == "__main__":
    stats = build_index()
    print(
        "Index built: "
        f"{stats['documents']} documents, {stats['chunks']} chunks, "
        f"{stats['features']} TF-IDF features"
    )
