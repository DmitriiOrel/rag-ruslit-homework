import json

from app.config import RAW_DATASET_JSON


def test_raw_dataset_has_required_mvp_scale() -> None:
    with RAW_DATASET_JSON.open("r", encoding="utf-8") as f:
        records = json.load(f)

    assert len(records) >= 1000
    assert {"doc_id", "title", "source", "text"} <= set(records[0])
