from __future__ import annotations

import logging
import sys
import time

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QMessageBox

from src.clipboard import ClipboardError, GlobalMouseSelection, SelectionReader
from src.config import AppConfig, ConfigError, ConfigStore
from src.dictionary import (
    DictionaryError,
    DictionaryService,
    is_probably_english_selection,
)
from src.models import LookupResult
from src.notebook import NotebookError, WordNotebook
from src.ui.result_popup import ResultPopup
from src.ui.settings_window import SettingsWindow
from src.ui.translate_prompt import TranslatePrompt
from src.ui.tray import TrayIcon

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


class AppSignals(QObject):
    selection_detected = Signal(str)
    user_error = Signal(str)


class AppController(QObject):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.config_store = ConfigStore()
        self.config = self._load_config()
        self.selection_reader = SelectionReader()
        self.signals = AppSignals()
        self.mouse_selection: GlobalMouseSelection | None = None
        self._mouse_busy = False
        self._last_mouse_at = 0.0
        self._last_detected_text = ""

        self.result_popup = ResultPopup()
        self.result_popup.save_requested.connect(self.save_result)

        self.translate_prompt = TranslatePrompt()
        self.translate_prompt.translate_requested.connect(self.lookup_text)

        self.settings_window = SettingsWindow(self.config)
        self.settings_window.config_saved.connect(self.update_config)

        self.tray = TrayIcon()
        self.tray.settings_action.triggered.connect(self.show_settings)
        self.tray.quit_action.triggered.connect(self.quit)

        self.signals.selection_detected.connect(self.translate_prompt.show_for_text)
        self.signals.user_error.connect(self.show_error)

    def start(self) -> None:
        self.tray.show()
        self._register_mouse_selection()
        self.tray.showMessage("离线选词单词本", "已启动，鼠标选中英文后可点击翻译")
        self.show_settings()

    def _load_config(self) -> AppConfig:
        try:
            config = self.config_store.load()
            self.config_store.save(config)
            return config
        except ConfigError as exc:
            QMessageBox.warning(None, "配置错误", str(exc))
            return AppConfig.defaults()

    def _register_mouse_selection(self) -> None:
        try:
            if self.mouse_selection is not None:
                self.mouse_selection.stop()
            self.mouse_selection = GlobalMouseSelection(self._on_mouse_released)
            self.mouse_selection.start()
        except Exception as exc:
            LOGGER.exception("Failed to register mouse selection watcher")
            self.show_error(f"注册鼠标选词监听失败：{exc}")

    def _on_mouse_released(self) -> None:
        now = time.monotonic()
        if self._mouse_busy or now - self._last_mouse_at < 0.5:
            return
        self._mouse_busy = True
        self._last_mouse_at = now
        try:
            selected_text = self.selection_reader.read_selected_text()
        except ClipboardError:
            return
        except Exception:
            LOGGER.exception("Failed to read mouse selected text")
            return
        finally:
            self._mouse_busy = False

        if not is_probably_english_selection(selected_text):
            return
        if selected_text == self._last_detected_text:
            return
        self._last_detected_text = selected_text
        self.signals.selection_detected.emit(selected_text)

    def lookup_text(self, text: str) -> None:
        try:
            result = DictionaryService().lookup(text)
        except DictionaryError as exc:
            self.show_error(str(exc))
            return
        self.result_popup.show_result(result)

    def save_result(self, result: LookupResult) -> None:
        try:
            saved = WordNotebook(self.config.notebook_path).append(result)
        except NotebookError as exc:
            self.show_error(str(exc))
            return
        if not saved:
            self.tray.showMessage("已存在", f"单词本里已保存过：{result.query}")
            return
        self.tray.showMessage("保存成功", f"已保存：{result.query}")

    def update_config(self, config: AppConfig) -> None:
        try:
            self.config_store.save(config)
        except ConfigError as exc:
            self.show_error(str(exc))
            return
        self.config = config

    def show_settings(self) -> None:
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def show_error(self, message: str) -> None:
        QMessageBox.warning(None, "提示", message)

    def quit(self) -> None:
        if self.mouse_selection is not None:
            self.mouse_selection.stop()
        self.tray.hide()
        self.app.quit()


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    controller = AppController(app)
    controller.start()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
