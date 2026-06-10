import pytest

from app.ingest import ingest_records, normalize_text


def test_normalize_text_collapses_spaces() -> None:
    assert normalize_text(" Alice   found   a key . ") == "Alice found a key."


def test_ingest_records_rejects_duplicate_doc_id() -> None:
    records = [
        {"doc_id": "1", "title": "A", "source": "s", "text": "First text"},
        {"doc_id": "1", "title": "B", "source": "s", "text": "Second text"},
    ]

    with pytest.raises(ValueError, match="Duplicate doc_id"):
        ingest_records(records)


def test_ingest_records_skips_empty_text() -> None:
    records = [
        {"doc_id": "1", "title": "A", "source": "s", "text": "   "},
        {"doc_id": "2", "title": "B", "source": "s", "text": "Useful text"},
    ]

    documents = ingest_records(records)

    assert [document["doc_id"] for document in documents] == ["2"]
