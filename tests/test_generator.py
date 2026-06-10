from app.generator import REFUSAL_NO_CONTEXT, ask, build_answer


def test_build_answer_refuses_when_scores_are_low() -> None:
    hits = [
        {
            "score": 0.01,
            "text": "Irrelevant text.",
            "doc_id": "x",
            "chunk_id": "x:0",
            "title": "X",
            "source": "memory",
        }
    ]

    assert build_answer("question", hits) == REFUSAL_NO_CONTEXT


def test_build_answer_cites_source_numbers() -> None:
    hits = [
        {
            "score": 0.5,
            "text": "Alice found a little golden key on a glass table.",
            "doc_id": "alice",
            "chunk_id": "alice:0",
            "title": "Alice",
            "source": "memory",
        }
    ]

    answer = build_answer("What did Alice find?", hits)

    assert "golden key" in answer
    assert "[1]" in answer


def test_ask_accepts_injected_retriever() -> None:
    class FakeRetriever:
        def search(self, query: str, k: int):
            return [
                {
                    "score": 0.5,
                    "text": "Elizabeth often spoke with Charlotte Lucas.",
                    "doc_id": "pp",
                    "chunk_id": "pp:0",
                    "title": "Pride and Prejudice",
                    "source": "memory",
                    "chunk_index": 0,
                }
            ]

    result = ask("Who spoke with Charlotte?", retriever=FakeRetriever())

    assert "Charlotte Lucas" in result["answer"]
    assert result["sources"][0]["doc_id"] == "pp"
