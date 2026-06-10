# Iter 02: Ingestion

Добавлен `app/ingest.py`: чтение JSON, валидация обязательных полей, проверка уникальности `doc_id`, нормализация текста и запись JSONL.

Проверка: тесты `tests/test_ingest.py`.
