import pytest

from app.chunker import chunk_documents, chunk_text


def test_chunk_text_keeps_overlap() -> None:
    text = " ".join(f"word{i}" for i in range(10))

    chunks = chunk_text(text, chunk_size_words=5, overlap_words=2)

    assert chunks == [
        "word0 word1 word2 word3 word4",
        "word3 word4 word5 word6 word7",
        "word6 word7 word8 word9",
    ]


def test_chunk_text_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text("one two three", chunk_size_words=3, overlap_words=3)


def test_chunk_documents_preserves_metadata() -> None:
    documents = [
        {
            "doc_id": "doc-1",
            "title": "Demo",
            "source": "memory",
            "text": "alpha beta gamma delta epsilon zeta",
        }
    ]

    chunks = chunk_documents(documents, chunk_size_words=4, overlap_words=1)

    assert chunks[0]["chunk_id"] == "doc-1:0"
    assert chunks[0]["title"] == "Demo"
    assert chunks[1]["text"] == "delta epsilon zeta"
