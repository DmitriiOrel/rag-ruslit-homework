import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.generator import ask


QUESTIONS = [
    "What did Alice find on the table with a paper label?",
    "Which professor of natural philosophy did Victor visit first at Ingolstadt?",
    "What was Holmes's axiom about little things?",
    "How do I reset a Kubernetes cluster?",
]


if __name__ == "__main__":
    for question in QUESTIONS:
        result = ask(question)
        print(f"\nQUESTION: {question}")
        print(result["answer"])
        print("SOURCES:")
        for source in result["sources"][:3]:
            print(
                f"- doc_id={source['doc_id']} score={source['score']:.3f} "
                f"title={source['title']}"
            )
