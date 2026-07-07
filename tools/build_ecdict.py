from __future__ import annotations

import argparse
import tempfile
import urllib.request
from pathlib import Path

try:
    from tools.import_dictionary import import_csv_to_sqlite
except ModuleNotFoundError:
    from import_dictionary import import_csv_to_sqlite


ECDICT_BASE_URL = "https://raw.githubusercontent.com/skywind3000/ECDICT/master"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCE_DIR = PROJECT_ROOT / "src" / "resources"
DEFAULT_OUTPUT = RESOURCE_DIR / "builtin_dictionary.sqlite3"


def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        output_path.write_bytes(response.read())


def build_ecdict(*, use_mini: bool, output_path: Path) -> int:
    file_name = "ecdict.mini.csv" if use_mini else "ecdict.csv"
    with tempfile.TemporaryDirectory(prefix="ecdict-") as temp_dir:
        csv_path = Path(temp_dir) / file_name
        download_file(f"{ECDICT_BASE_URL}/{file_name}", csv_path)
        return import_csv_to_sqlite(csv_path, output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="下载 ECDICT 并构建内置 SQLite 词典")
    parser.add_argument(
        "--mini",
        action="store_true",
        help="下载较小的 ecdict.mini.csv，适合开发验证；默认下载完整 ecdict.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="输出 SQLite 文件路径，默认写入 src/resources/builtin_dictionary.sqlite3",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    imported = build_ecdict(use_mini=args.mini, output_path=args.output)
    print(f"ECDICT 构建完成：{imported} 条记录 -> {args.output}")


if __name__ == "__main__":
    main()
