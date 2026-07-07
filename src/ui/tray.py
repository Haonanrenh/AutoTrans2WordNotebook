from __future__ import annotations

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None) -> None:
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        super().__init__(QIcon(icon), parent)
        self.setToolTip("离线选词单词本")

        self.settings_action = QAction("设置")
        self.quit_action = QAction("退出")

        menu = QMenu()
        menu.addAction(self.settings_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)
        self.setContextMenu(menu)
