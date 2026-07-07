APP_STYLE = """
QWidget {
    background: #f7f8fb;
    color: #202124;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 14px;
}
QDialog, QFrame {
    background: #ffffff;
}
QLabel#TitleLabel {
    font-size: 18px;
    font-weight: 600;
    color: #111827;
}
QLabel#SubtitleLabel {
    color: #6b7280;
}
QLineEdit, QTextEdit {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px 10px;
}
QTextEdit {
    line-height: 1.4;
}
QPushButton {
    background: #2563eb;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #1d4ed8;
}
QPushButton:pressed {
    background: #1e40af;
}
QPushButton:disabled {
    background: #cbd5e1;
    color: #64748b;
}
QPushButton#SecondaryButton {
    background: #eef2ff;
    color: #1f2937;
}
QPushButton#SecondaryButton:hover {
    background: #e0e7ff;
}
"""

PROMPT_STYLE = """
QFrame {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 12px;
}
QLabel {
    color: #ffffff;
    font-size: 13px;
}
QPushButton {
    background: #f59e0b;
    border: none;
    border-radius: 8px;
    color: #111827;
    padding: 6px 12px;
    font-weight: 700;
}
QPushButton:hover {
    background: #fbbf24;
}
"""
