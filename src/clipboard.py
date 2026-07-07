from __future__ import annotations

import time

import keyboard
import mouse
import pyperclip

from src.dictionary import normalize_query


class ClipboardError(RuntimeError):
    """Raised when selected text cannot be copied from the active window."""


class SelectionReader:
    def __init__(self, copy_delay_seconds: float = 0.35, copy_timeout_seconds: float = 1.0) -> None:
        self.copy_delay_seconds = copy_delay_seconds
        self.copy_timeout_seconds = copy_timeout_seconds

    def read_selected_text(self) -> str:
        previous_clipboard = self._safe_paste()
        try:
            self._safe_copy("")
            self._release_modifier_keys()
            keyboard.press_and_release("ctrl+c")
            selected_text = self._wait_for_copied_text()
        finally:
            if previous_clipboard is not None:
                self._safe_copy(previous_clipboard)

        if not selected_text:
            raise ClipboardError("未读取到选中文本，请先选中英文单词或短语")
        return selected_text

    def _wait_for_copied_text(self) -> str:
        deadline = time.monotonic() + self.copy_timeout_seconds
        time.sleep(self.copy_delay_seconds)
        while time.monotonic() < deadline:
            copied_text = normalize_query(self._safe_paste() or "")
            if copied_text:
                return copied_text
            time.sleep(0.05)
        return ""

    def _release_modifier_keys(self) -> None:
        for key_name in ("ctrl", "alt", "shift"):
            try:
                keyboard.release(key_name)
            except ValueError:
                continue

    def _safe_paste(self) -> str | None:
        try:
            return pyperclip.paste()
        except pyperclip.PyperclipException:
            return None

    def _safe_copy(self, text: str) -> None:
        try:
            pyperclip.copy(text)
        except pyperclip.PyperclipException:
            return


class GlobalMouseSelection:
    def __init__(self, callback) -> None:
        self.callback = callback
        self._handle = None

    def start(self) -> None:
        self.stop()
        self._handle = mouse.on_button(
            self.callback,
            buttons=("left",),
            types=("up",),
        )

    def stop(self) -> None:
        if self._handle is None:
            return
        mouse.unhook(self._handle)
        self._handle = None
