from __future__ import annotations

from pathlib import Path

import pytest

from src.config import AppConfig, ConfigError, ConfigStore


def test_config_store_roundtrip(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    notebook_path = tmp_path / "words.docx"
    config = AppConfig(
        notebook_path=notebook_path,
    )

    store = ConfigStore(config_path)
    store.save(config)

    loaded = store.load()
    assert loaded == config


def test_config_rejects_non_docx_notebook(tmp_path: Path) -> None:
    config = AppConfig(
        notebook_path=tmp_path / "words.txt",
    )

    with pytest.raises(ConfigError):
        config.validate()


def test_config_ignores_legacy_dictionary_and_hotkey(tmp_path: Path) -> None:
    config = AppConfig.from_mapping(
        {
            "notebook_path": str(tmp_path / "words.docx"),
            "dictionary_path": str(tmp_path / "legacy.sqlite3"),
            "hotkey": "ctrl+shift+t",
        }
    )

    assert config.notebook_path == tmp_path / "words.docx"
