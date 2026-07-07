from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from src.models import LookupResult
from src.ui.style import APP_STYLE


class ResultPopup(QDialog):
    save_requested = Signal(LookupResult)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("离线翻译结果")
        self.setMinimumSize(520, 360)
        self.setStyleSheet(APP_STYLE)
        self._result: LookupResult | None = None

        self.title_label = QLabel("翻译结果")
        self.title_label.setObjectName("TitleLabel")
        self.query_label = QLabel()
        self.query_label.setWordWrap(True)
        self.phonetic_label = QLabel()
        self.phonetic_label.setObjectName("SubtitleLabel")
        self.translation_text = QTextEdit()
        self.translation_text.setReadOnly(True)

        self.save_button = QPushButton("保存到单词本")
        self.close_button = QPushButton("关闭")
        self.close_button.setObjectName("SecondaryButton")
        buttons = QDialogButtonBox()
        buttons.addButton(self.save_button, QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(self.close_button, QDialogButtonBox.ButtonRole.RejectRole)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addWidget(self.query_label)
        layout.addWidget(self.phonetic_label)
        layout.addWidget(self.translation_text)
        layout.addWidget(buttons)

        self.save_button.clicked.connect(self._emit_save)
        self.close_button.clicked.connect(self.reject)

    def show_result(self, result: LookupResult) -> None:
        self._result = result
        self.query_label.setText(f"原文：{result.query}")
        self.phonetic_label.setText(f"美式音标：{result.display_phonetic}")
        self.translation_text.setPlainText(result.display_translation)
        self.save_button.setEnabled(result.found)
        self.show()
        self.raise_()
        self.activateWindow()

    def _emit_save(self) -> None:
        if self._result is not None:
            self.save_requested.emit(self._result)
