# Gutenberg RAG Homework

Учебный RAG над открытыми текстами Project Gutenberg. Pipeline полностью локальный:

```
datasets.json -> ingest -> chunking -> TF-IDF index -> retrieval -> demo-answer -> Streamlit UI
```

Внешние LLM и API-ключи не нужны. Ответ строится только из найденных фрагментов, а UI показывает источники: `doc_id`, `chunk_id`, `score`, название, ссылку и текст.

## Быстрый запуск

```bash
uv sync
uv run python scripts/build_index.py
uv run streamlit run app/main.py
```

Откройте адрес, который покажет Streamlit, обычно http://localhost:8501.

## Проверка из консоли

```bash
uv run pytest tests/ -v
uv run python scripts/check_retrieval.py
uv run python scripts/check_generator.py
```

Если нужно пересобрать исходный корпус из Project Gutenberg:

```bash
uv run python scripts/prepare_datasets.py
uv run python scripts/build_index.py
```

## Данные

Источник: открытые public-domain тексты Project Gutenberg.

Индексируется поле `text` из `data/raw/datasets.json`. Метаданные `doc_id`, `title` и `source` не участвуют в TF-IDF, но используются для ссылок на источники.

Использованные книги:

| Gutenberg ID | Книга |
|---|---|
| 1342 | Pride and Prejudice |
| 11 | Alice's Adventures in Wonderland |
| 84 | Frankenstein |
| 345 | Dracula |
| 1661 | The Adventures of Sherlock Holmes |

Подробно: [doc/DATA.md](doc/DATA.md).

Фактический масштаб после подготовки данных:

- `data/raw/datasets.json`: 1250 записей.
- `data/processed/chunks.jsonl`: 1667 чанков после нарезки.
- TF-IDF index: 49692 признака.

## Demo-вопросы

После `uv run python scripts/build_index.py` можно проверить:

| Вопрос | Ожидаемое поведение |
|---|---|
| What did Alice find on the table with a paper label? | Ответ по `Alice's Adventures in Wonderland`: little bottle и label `DRINK ME`. |
| Which professor of natural philosophy did Victor visit first at Ingolstadt? | Ответ по `Frankenstein`: M. Krempe, professor of natural philosophy. |
| What was Holmes's axiom about little things? | Ответ по `The Adventures of Sherlock Holmes`: little things are infinitely the most important. |
| How do I reset a Kubernetes cluster? | Negative-case: система должна отказаться, потому что в корпусе нет релевантного контекста. |

## Логи проверки

```text
uv run python scripts/build_index.py
Index built: 1250 documents, 1667 chunks, 49692 TF-IDF features

uv run pytest tests/ -v
11 passed
```

Короткий demo-output:

```text
QUESTION: What did Alice find on the table with a paper label?
ANSWER: ... little bottle ... paper label ... "DRINK ME" ...
TOP SOURCE: doc_id=pg11-0015 score=0.214 title=Alice's Adventures in Wonderland

QUESTION: Which professor of natural philosophy did Victor visit first at Ingolstadt?
ANSWER: Krempe, professor of natural philosophy.
TOP SOURCE: doc_id=pg84-0087 score=0.267 title=Frankenstein

QUESTION: What was Holmes's axiom about little things?
ANSWER: little things are infinitely the most important.
TOP SOURCE: doc_id=pg1661-0250 score=0.543 title=The Adventures of Sherlock Holmes

QUESTION: How do I reset a Kubernetes cluster?
ANSWER: отказ без выдумок, релевантный контекст не найден.
TOP SOURCE SCORE: 0.000
```

## Структура

```
app/
  chunker.py      # нарезка текста на чанки
  generator.py    # extractive demo-answer и отказ без контекста
  ingest.py       # чтение и валидация datasets.json
  main.py         # Streamlit UI
  retriever.py    # TF-IDF retrieval
scripts/
  prepare_datasets.py
  build_index.py
  check_retrieval.py
  check_generator.py
tests/
doc/
data/raw/datasets.json
```

## Ограничения MVP

- TF-IDF ищет по словам, а не по глубокому смыслу.
- Ответ extractive: система выбирает предложения из источников, без внешней LLM.
- Если score ниже порога, система отказывается и не придумывает факты.
