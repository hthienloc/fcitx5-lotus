# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Main window assembling all configuration tabs with a modern layout.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
    QApplication,
    QFrame,
)
from PySide6.QtGui import QIcon
from i18n import _
from core.dbus_handler import LotusDBusHandler
from core.file_handler import Fcitx5ConfigHandler

from ui.pages.dynamic_settings import DynamicSettingsPage
from ui.pages.macro_editor import MacroEditorPage
from ui.pages.keymap_editor import KeymapEditorPage


class LotusSettingsWindow(QMainWindow):
    """Main entry window for Lotus Configuration GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("Fcitx5 Lotus Settings"))

        self.dbus_handler = LotusDBusHandler()
        self.file_handler = Fcitx5ConfigHandler()

        self._setup_ui()
        self._setup_window_size()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(
            """
            QListWidget {
                border: none;
                background: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 8px;
                margin: 2px 10px;
            }
            QListWidget::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QListWidget::item:hover:!selected {
                background: palette(alternate-base);
            }
        """
        )

        self.content_stack = QStackedWidget()

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: palette(alternate-base);")

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.content_stack, 1)

        self._add_page(
            _("General"), "preferences-system", DynamicSettingsPage(self.dbus_handler)
        )
        self._add_page(
            _("Macro"), "accessories-text-editor", MacroEditorPage(self.file_handler)
        )
        self._add_page(
            _("Keymap"),
            "preferences-desktop-keyboard",
            KeymapEditorPage(self.file_handler),
        )

        self.sidebar.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

    def _setup_window_size(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w = int(screen.width() * 0.55)
        h = int(screen.height() * 0.65)
        self.setMinimumSize(750, 500)
        self.resize(w, h)
        self.move((screen.width() - w) // 2, (screen.height() - h) // 2)

    def _add_page(self, title: str, icon_name: str, widget: QWidget):
        item = QListWidgetItem(QIcon.fromTheme(icon_name), title)
        self.sidebar.addItem(item)
        self.content_stack.addWidget(widget)
