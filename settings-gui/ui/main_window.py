# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Main window assembling all configuration tabs.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
)
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
        self.resize(850, 600)

        # Initialize core handlers
        self.dbus_handler = LotusDBusHandler()
        self.file_handler = Fcitx5ConfigHandler()

        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Sidebar navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)

        # Content stack
        self.content_stack = QStackedWidget()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, 1)

        # Build pages
        self._add_page(_("General Settings"), DynamicSettingsPage(self.dbus_handler))
        self._add_page(_("Macro Editor"), MacroEditorPage(self.file_handler))
        self._add_page(_("Custom Keymap"), KeymapEditorPage(self.file_handler))

        # Connect sidebar to stack
        self.sidebar.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

    def _add_page(self, title: str, widget: QWidget):
        """Helper to add a page to the stack and sidebar."""
        self.sidebar.addItem(QListWidgetItem(title))
        self.content_stack.addWidget(widget)
