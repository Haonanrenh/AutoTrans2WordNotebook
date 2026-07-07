from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from src.ui.style import PROMPT_STYLE


class TranslatePrompt(QFrame):
    translate_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("翻译提示")
        self.setMinimumWidth(280)
        self.setStyleSheet(PROMPT_STYLE)
        self._text = ""

        self.label = QLabel()
        self.label.setWordWrap(False)
        self.button = QPushButton("翻译")
        self.button.clicked.connect(self._emit_translate)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        layout.addWidget(self.label, stretch=1)
        layout.addWidget(self.button)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def show_for_text(self, text: str) -> None:
        self._text = text
        preview = text if len(text) <= 28 else f"{text[:28]}..."
        self.label.setText(f"检测到：{preview}")
        position = QCursor.pos()
        self.move(position.x() + 12, position.y() + 12)
        self.show()
        self.raise_()
        self.hide_timer.start(6000)

    def _emit_translate(self) -> None:
        if self._text:
            self.translate_requested.emit(self._text)
        self.hide()
