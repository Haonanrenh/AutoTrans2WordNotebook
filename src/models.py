from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LookupResult:
    """Normalized dictionary lookup result passed between non-UI and UI layers."""

    query: str
    translation: str = ""
    phonetic_us: str = ""
    found: bool = False
    source: str = ""

    @property
    def display_translation(self) -> str:
        return self.translation if self.translation else "未找到释义"

    @property
    def display_phonetic(self) -> str:
        return self.phonetic_us if self.phonetic_us else "暂无美式音标"
