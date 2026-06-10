import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.retriever import Retriever


QUESTIONS = [
    "What did Alice find on the table with a paper label?",
    "Which professor of natural philosophy did Victor visit first at Ingolstadt?",
    "What was Holmes's axiom about little things?",
    "How do I reset a Kubernetes cluster?",
]


if __name__ == "__main__":
    retriever = Retriever()
    for question in QUESTIONS:
        print(f"\nQUESTION: {question}")
        for hit in retriever.search(question, k=3):
            print(
                f"- doc_id={hit['doc_id']} score={hit['score']:.3f} "
                f"title={hit['title']} text={hit['text'][:180]}..."
            )
