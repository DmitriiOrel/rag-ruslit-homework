# Данные

## Источник

Корпус собран из Project Gutenberg - библиотеки public-domain текстов.

Скрипт подготовки: `scripts/prepare_datasets.py`.

| Gutenberg ID | URL | Что берется |
|---|---|---|
| 1342 | https://www.gutenberg.org/cache/epub/1342/pg1342.txt | Абзацы из `Pride and Prejudice` |
| 11 | https://www.gutenberg.org/cache/epub/11/pg11.txt | Абзацы из `Alice's Adventures in Wonderland` |
| 84 | https://www.gutenberg.org/cache/epub/84/pg84.txt | Абзацы из `Frankenstein` |
| 345 | https://www.gutenberg.org/cache/epub/345/pg345.txt | Абзацы из `Dracula` |
| 1661 | https://www.gutenberg.org/cache/epub/1661/pg1661.txt | Абзацы из `The Adventures of Sherlock Holmes` |

## Формат `datasets.json`

```json
{
  "doc_id": "pg1342-0001",
  "title": "Pride and Prejudice",
  "source": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
  "text": "..."
}
```

## Что индексируется

Индексируется только поле `text`. Поля `doc_id`, `title` и `source` остаются метаданными и выводятся в источниках.

## Очистка

- Удаляется служебная шапка и подвал Project Gutenberg.
- Текст разбивается по пустым строкам.
- Слишком короткие абзацы отбрасываются.
- Длинные абзацы ограничиваются, чтобы чанки были управляемого размера.

## Масштаб

MVP требует минимум 10 текстовых записей. В этом проекте:

- `datasets.json` содержит 1250 записей;
- после chunking получается 1667 чанков;
- TF-IDF индекс содержит 49692 признака.

Это покрывает уровень "отлично" по масштабу входного датасета и индекса.
