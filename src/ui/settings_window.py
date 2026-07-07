from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig, ConfigError
from src.ui.style import APP_STYLE


class SettingsWindow(QWidget):
    config_saved = Signal(AppConfig)

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.setWindowTitle("离线选词单词本设置")
        self.setMinimumSize(620, 220)
        self.setStyleSheet(APP_STYLE)

        self.notebook_input = QLineEdit(str(config.notebook_path))
        self.notebook_input.setPlaceholderText("选择或输入 .docx 单词本路径")

        title = QLabel("离线选词单词本")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("设置 Word 单词本位置。程序会把查询结果追加保存到该文件。")
        subtitle.setObjectName("SubtitleLabel")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(14)
        form.addRow("Word 单词本：", self._path_row(self.notebook_input, self._pick_notebook))

        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self._save)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(save_button)

    def _path_row(self, input_widget: QLineEdit, picker) -> QWidget:
        container = QWidget()
        browse_button = QPushButton("浏览")
        browse_button.setObjectName("SecondaryButton")
        browse_button.clicked.connect(picker)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(input_widget)
        layout.addWidget(browse_button)
        return container

    def _pick_notebook(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "选择 Word 单词本",
            "",
            "Word 文档 (*.docx)",
            options=QFileDialog.Option.DontConfirmOverwrite,
        )
        if path:
            notebook_path = Path(path)
            if not notebook_path.suffix:
                notebook_path = notebook_path.with_suffix(".docx")
            self.notebook_input.setText(str(notebook_path))

    def _save(self) -> None:
        config = AppConfig(
            notebook_path=Path(self.notebook_input.text().strip()),
        )
        try:
            config.validate()
        except ConfigError as exc:
            QMessageBox.warning(self, "设置无效", str(exc))
            return
        self.config_saved.emit(config)
        QMessageBox.information(self, "设置已保存", "设置保存成功")
