from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

APP_DIR_NAME = "AutoTrans2WordNotebook"
CONFIG_FILE_NAME = "config.json"


class ConfigError(ValueError):
    """Raised when a user-facing configuration value is invalid."""


def default_app_dir() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / APP_DIR_NAME
    return Path.home() / f".{APP_DIR_NAME}"


@dataclass(frozen=True)
class AppConfig:
    notebook_path: Path

    @classmethod
    def defaults(cls) -> AppConfig:
        app_dir = default_app_dir()
        return cls(
            notebook_path=app_dir / "vocabulary.docx",
        )

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> AppConfig:
        defaults = cls.defaults()
        return cls(
            notebook_path=Path(data.get("notebook_path") or defaults.notebook_path),
        )

    def to_json_dict(self) -> dict[str, str]:
        return {
            "notebook_path": str(self.notebook_path),
        }

    def validate(self) -> None:
        if self.notebook_path.suffix.lower() != ".docx":
            raise ConfigError("单词本文件必须是 .docx 格式")
        if not self.notebook_path.parent.exists():
            raise ConfigError(f"单词本目录不存在：{self.notebook_path.parent}")


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_app_dir() / CONFIG_FILE_NAME

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig.defaults()

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"配置文件格式错误：{self.path}") from exc

        if not isinstance(raw, dict):
            raise ConfigError("配置文件内容必须是 JSON 对象")
        return AppConfig.from_mapping(raw)

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        config.notebook_path.parent.mkdir(parents=True, exist_ok=True)
        config.validate()
        self.path.write_text(
            json.dumps(config.to_json_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
