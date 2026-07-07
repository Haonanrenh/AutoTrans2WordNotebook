from __future__ import annotations

import sqlite3
from pathlib import Path

from src.dictionary import (
    DictionaryService,
    is_probably_english_selection,
    normalize_dictionary_text,
    normalize_query,
)
from tools.import_dictionary import import_csv_to_sqlite


def test_normalize_query_trims_whitespace() -> None:
    assert normalize_query("  good   morning  ") == "good morning"


def test_normalize_dictionary_text_converts_literal_newlines() -> None:
    assert normalize_dictionary_text("n. 世界\\nv. 体验/nadj. 全球的") == (
        "n. 世界\nv. 体验\nadj. 全球的"
    )


def test_is_probably_english_selection_filters_noise() -> None:
    assert is_probably_english_selection("good morning") is True
    assert is_probably_english_selection("你好") is False
    assert is_probably_english_selection("hello\nworld") is False


def test_sqlite_dictionary_lookup(tmp_path: Path) -> None:
    db_path = tmp_path / "dictionary.sqlite3"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE entries (word TEXT PRIMARY KEY, translation TEXT, phonetic_us TEXT)"
        )
        connection.execute(
            "INSERT INTO entries VALUES (?, ?, ?)",
            ("hello", "int. 你好\\nv. 打招呼", "həˈloʊ"),
        )

    result = DictionaryService(db_path).lookup("Hello")

    assert result.found is True
    assert result.query == "hello"
    assert result.translation == "int. 你好\nv. 打招呼"
    assert result.phonetic_us == "həˈloʊ"


def test_bundled_dictionary_lookup() -> None:
    result = DictionaryService().lookup("butylbenzene")

    assert result.found is True
    assert "丁苯" in result.translation


def test_import_csv_to_sqlite(tmp_path: Path) -> None:
    csv_path = tmp_path / "dict.csv"
    db_path = tmp_path / "dict.sqlite3"
    csv_path.write_text(
        "word,translation,phonetic_us\nworld,n. 世界,wɝːld\n",
        encoding="utf-8",
    )

    imported = import_csv_to_sqlite(csv_path, db_path)
    result = DictionaryService(db_path).lookup("world")

    assert imported == 1
    assert result.found is True
    assert result.translation == "n. 世界"
