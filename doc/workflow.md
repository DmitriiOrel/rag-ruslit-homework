# Workflow

## 1. Ingest

`scripts/prepare_datasets.py` создает `data/raw/datasets.json`. `app/ingest.py` читает записи, проверяет обязательные поля, нормализует пробелы и сохраняет `documents.jsonl`.

## 2. Chunking

`app/chunker.py` режет каждый текст на чанки по 120 слов с overlap 30 слов. Overlap нужен, чтобы фразы на границе чанков не теряли контекст.

## 3. Index

`scripts/build_index.py` обучает `TfidfVectorizer` на текстах чанков и сохраняет vectorizer и sparse matrix в `data/index/`.

## 4. Retrieval

`app/retriever.py` преобразует вопрос тем же vectorizer и считает similarity через dot product между нормированными TF-IDF векторами.

## 5. Demo-answer

`app/generator.py` фильтрует найденные чанки по `MIN_SCORE`, выбирает предложения с пересечением слов вопроса и добавляет номера источников. Если релевантных чанков нет, возвращает отказ.

## 6. UI

`app/main.py` показывает вопрос, ответ и раскрываемые источники с `doc_id`, `chunk_id`, `score`, ссылкой и текстом.
