from __future__ import annotations

import csv
import importlib.resources as resources
import re
import sqlite3
from pathlib import Path
from types import TracebackType

from src.models import LookupResult

MAX_QUERY_LENGTH = 200
SUPPORTED_SQLITE_SUFFIXES = {".db", ".sqlite", ".sqlite3"}
BUNDLED_SQLITE_NAME = "builtin_dictionary.sqlite3"
BUNDLED_CSV_NAME = "fallback_dictionary.csv"
ENGLISH_SELECTION_RE = re.compile(r"^[A-Za-z][A-Za-z0-9\s'\-.,;:()&/]*$")


class DictionaryError(RuntimeError):
    """Raised when the local dictionary cannot be queried safely."""


def normalize_query(text: str) -> str:
    normalized = " ".join(text.strip().split())
    if len(normalized) > MAX_QUERY_LENGTH:
        normalized = normalized[:MAX_QUERY_LENGTH]
    return normalized


def normalize_dictionary_text(text: str) -> str:
    text = text.replace("\\n", "\n").replace("/n", "\n")
    lines = [" ".join(line.strip().split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def is_probably_english_selection(text: str) -> bool:
    normalized = normalize_query(text)
    if not normalized or len(normalized) > 120:
        return False
    if "\n" in text or "\\n" in text:
        return False
    if not any(character.isalpha() for character in normalized):
        return False
    return bool(ENGLISH_SELECTION_RE.fullmatch(normalized))


class BundledDictionaryResource:
    def __init__(self) -> None:
        self._context = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        package_files = resources.files("src.resources")
        resource = (
            package_files / BUNDLED_SQLITE_NAME
            if (package_files / BUNDLED_SQLITE_NAME).is_file()
            else package_files / BUNDLED_CSV_NAME
        )
        self._context = resources.as_file(resource)
        self.path = self._context.__enter__()
        return self.path

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._context is not None:
            self._context.__exit__(exc_type, exc, traceback)


class DictionaryService:
    def __init__(self, dictionary_path: Path | None = None) -> None:
        self.dictionary_path = dictionary_path

    def lookup(self, raw_query: str) -> LookupResult:
        query = normalize_query(raw_query)
        if not query:
            return LookupResult(query="", found=False)
        if self.dictionary_path is None:
            with BundledDictionaryResource() as dictionary_path:
                return self._lookup_path(dictionary_path, query)
        return self._lookup_path(self.dictionary_path, query)

    def _lookup_path(self, dictionary_path: Path, query: str) -> LookupResult:
        self.dictionary_path = dictionary_path
        if not self.dictionary_path.exists():
            raise DictionaryError("内置词典文件不存在，请先构建 ECDICT 离线词典")

        suffix = self.dictionary_path.suffix.lower()
        if suffix in SUPPORTED_SQLITE_SUFFIXES:
            return SQLiteDictionary(self.dictionary_path).lookup(query)
        if suffix == ".csv":
            return CsvDictionary(self.dictionary_path).lookup(query)
        raise DictionaryError(f"不支持的词典格式：{suffix}")


class SQLiteDictionary:
    def __init__(self, path: Path) -> None:
        self.path = path

    def lookup(self, query: str) -> LookupResult:
        try:
            with sqlite3.connect(self.path) as connection:
                connection.row_factory = sqlite3.Row
                row = connection.execute(
                    """
                    SELECT word, translation, phonetic_us
                    FROM entries
                    WHERE lower(word) = lower(?)
                    LIMIT 1
                    """,
                    (query,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise DictionaryError(f"查询 SQLite 词典失败：{self.path}") from exc

        if row is None:
            return LookupResult(query=query, found=False, source=str(self.path))
        return LookupResult(
            query=row["word"] or query,
            translation=normalize_dictionary_text(row["translation"] or ""),
            phonetic_us=normalize_dictionary_text(row["phonetic_us"] or ""),
            found=True,
            source=str(self.path),
        )


class CsvDictionary:
    def __init__(self, path: Path) -> None:
        self.path = path

    def lookup(self, query: str) -> LookupResult:
        try:
            with self.path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    word = (row.get("word") or "").strip()
                    if word.lower() != query.lower():
                        continue
                    translation = row.get("translation") or row.get("definition") or ""
                    phonetic = row.get("phonetic_us") or row.get("phonetic") or ""
                    return LookupResult(
                        query=word,
                        translation=normalize_dictionary_text(translation),
                        phonetic_us=normalize_dictionary_text(phonetic),
                        found=True,
                        source=str(self.path),
                    )
        except OSError as exc:
            raise DictionaryError(f"读取 CSV 词典失败：{self.path}") from exc

        return LookupResult(query=query, found=False, source=str(self.path))
