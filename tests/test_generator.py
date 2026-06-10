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
            "text": "Фамилия чиновника была Башмачкин.",
            "doc_id": "shinel",
            "chunk_id": "shinel:0",
            "title": "Шинель",
            "source": "memory",
        }
    ]

    answer = build_answer("Какая фамилия была у чиновника?", hits)

    assert "Башмачкин" in answer
    assert "[1]" in answer


def test_ask_accepts_injected_retriever() -> None:
    class FakeRetriever:
        def search(self, query: str, k: int):
            return [
                {
                    "score": 0.5,
                    "text": "Все смешалось в доме Облонских.",
                    "doc_id": "anna",
                    "chunk_id": "anna:0",
                    "title": "Анна Каренина",
                    "source": "memory",
                    "chunk_index": 0,
                }
            ]

    result = ask("Что смешалось в доме Облонских?", retriever=FakeRetriever())

    assert "Облонских" in result["answer"]
    assert result["sources"][0]["doc_id"] == "anna"
