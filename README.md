# RusLit RAG Homework

Учебный русскоязычный RAG над открытым корпусом русской литературы RusLit. Pipeline полностью локальный:

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

Если нужно пересобрать исходный корпус из RusLit:

```bash
uv run python scripts/prepare_datasets.py
uv run python scripts/build_index.py
```

## Данные

Источник: [d0rj/RusLit](https://github.com/d0rj/RusLit), открытый корпус русской литературы в UTF-8. В README источника указано, что тексты находятся в public domain; также есть Kaggle-зеркало.

Индексируется поле `text` из `data/raw/datasets.json`. Метаданные `doc_id`, `title`, `author` и `source` не участвуют в TF-IDF, но используются для ссылок на источники.

Использованные произведения:

| Автор | Произведение |
|---|---|
| Лев Толстой | Анна Каренина |
| Лев Толстой | Война и мир. Том 1 |
| Федор Достоевский | Братья Карамазовы |
| Федор Достоевский | Идиот |
| Николай Гоголь | Мертвые души |
| Николай Гоголь | Шинель |
| Николай Гоголь | Ревизор |
| Антон Чехов | Палата N 6 |
| Антон Чехов | Каштанка |
| Иван Тургенев | Отцы и дети |

Подробно: [doc/DATA.md](doc/DATA.md).

Фактический масштаб после подготовки данных:

- `data/raw/datasets.json`: 1250 записей.
- `data/processed/chunks.jsonl`: 3378 чанков после нарезки.
- TF-IDF index: 205449 признаков.

## Demo-вопросы

После `uv run python scripts/build_index.py` можно проверить:

| Вопрос | Ожидаемое поведение |
|---|---|
| Что смешалось в доме Облонских? | Ответ по `Анна Каренина`: "Все смешалось в доме Облонских". |
| Какая фамилия была у чиновника? | Ответ по `Шинель`: фамилия чиновника была Башмачкин. |
| Что сказал незнакомец после слов Без имени нельзя? | Ответ по `Каштанка`: "Ты будешь - Тетка". |
| Как перезапустить кластер Kubernetes? | Negative-case: система отказывается, потому что в корпусе нет релевантного контекста. |

## Логи проверки

```text
uv run python scripts/build_index.py
Index built: 1250 documents, 3378 chunks, 205449 TF-IDF features

uv run pytest tests/ -v
11 passed
```

Короткий demo-output:

```text
QUESTION: Что смешалось в доме Облонских?
ANSWER: Все смешалось в доме Облонских.
TOP SOURCE: doc_id=ruslit-01-0001 score=0.235 title=Анна Каренина

QUESTION: Какая фамилия была у чиновника?
ANSWER: Фамилия чиновника была Башмачкин.
TOP SOURCE: doc_id=ruslit-06-0001 score=0.178 title=Шинель

QUESTION: Что сказал незнакомец после слов Без имени нельзя?
ANSWER: Незнакомец подумал и сказал: "Ты будешь - Тетка..."
TOP SOURCE: doc_id=ruslit-09-0009 score=0.150 title=Каштанка

QUESTION: Как перезапустить кластер Kubernetes?
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
- Морфология русского языка в MVP не нормализуется, поэтому лучше задавать вопросы словами, близкими к тексту источника.
- Ответ extractive: система выбирает предложения из источников, без внешней LLM.
- Если score ниже порога, система отказывается и не придумывает факты.
