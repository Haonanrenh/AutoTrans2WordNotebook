from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from src.ui.style import PROMPT_STYLE


class TranslatePrompt(QFrame):
    translate_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
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
        self.adjustSize()
        self.move(self._bounded_position(QCursor.pos()))
        self.show()
        self.raise_()
        self.activateWindow()
        self.hide_timer.start(6000)

    def _emit_translate(self) -> None:
        if self._text:
            self.translate_requested.emit(self._text)
        self.hide()

    def _bounded_position(self, cursor_position: QPoint) -> QPoint:
        margin = 12
        target_x = cursor_position.x() + margin
        target_y = cursor_position.y() + margin

        screen = QGuiApplication.screenAt(cursor_position) or QGuiApplication.primaryScreen()
        if screen is None:
            return QPoint(target_x, target_y)

        area = screen.availableGeometry()
        width = max(self.sizeHint().width(), self.minimumWidth())
        height = self.sizeHint().height()

        if target_x + width > area.right():
            target_x = cursor_position.x() - width - margin
        if target_y + height > area.bottom():
            target_y = cursor_position.y() - height - margin

        target_x = min(max(target_x, area.left() + margin), area.right() - width - margin)
        target_y = min(max(target_y, area.top() + margin), area.bottom() - height - margin)
        return QPoint(target_x, target_y)
