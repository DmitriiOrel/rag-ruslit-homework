from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "index"

RAW_DATASET_JSON = RAW_DIR / "datasets.json"
DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"
CHUNKS_JSONL = PROCESSED_DIR / "chunks.jsonl"
VECTORIZER_PKL = INDEX_DIR / "vectorizer.pkl"
MATRIX_NPZ = INDEX_DIR / "matrix.npz"

CHUNK_SIZE_WORDS = 120
CHUNK_OVERLAP_WORDS = 30
TOP_K = 5
MIN_SCORE = 0.10
MAX_ANSWER_SENTENCES = 4
