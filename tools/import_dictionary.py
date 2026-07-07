from __future__ import annotations

import argparse
import csv
import sqlite3
from collections.abc import Iterable
from pathlib import Path


def pick_value(row: dict[str, str], keys: Iterable[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value:
            return value.strip()
    return ""


def import_csv_to_sqlite(csv_path: Path, sqlite_path: Path) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 文件不存在：{csv_path}")
    if csv_path.suffix.lower() != ".csv":
        raise ValueError("输入词典必须是 CSV 文件")
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    imported = 0
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                word TEXT PRIMARY KEY,
                translation TEXT NOT NULL DEFAULT '',
                phonetic_us TEXT NOT NULL DEFAULT ''
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_entries_word_lower ON entries (lower(word))"
        )

        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                word = pick_value(row, ["word", "name", "term"])
                if not word:
                    continue
                translation = pick_value(row, ["translation", "definition", "trans", "explanation"])
                phonetic_us = pick_value(row, ["phonetic_us", "usphone", "us_phonetic", "phonetic"])
                connection.execute(
                    """
                    INSERT INTO entries (word, translation, phonetic_us)
                    VALUES (?, ?, ?)
                    ON CONFLICT(word) DO UPDATE SET
                        translation = excluded.translation,
                        phonetic_us = excluded.phonetic_us
                    """,
                    (word, translation, phonetic_us),
                )
                imported += 1
        connection.commit()
    return imported


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入离线 CSV 词典到 SQLite")
    parser.add_argument("csv_path", type=Path, help="输入 CSV 词典文件")
    parser.add_argument("sqlite_path", type=Path, help="输出 SQLite 词典文件")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    imported = import_csv_to_sqlite(args.csv_path, args.sqlite_path)
    print(f"导入完成：{imported} 条记录 -> {args.sqlite_path}")


if __name__ == "__main__":
    main()
