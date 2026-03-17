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
    QVBoxLayout,
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
    QApplication,
    QFrame,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize
from i18n import _
from core.dbus_handler import LotusDBusHandler
from core.file_handler import Fcitx5ConfigHandler

from ui.pages.dynamic_settings import DynamicSettingsPage
from ui.pages.macro_editor import MacroEditorPage
from ui.pages.keymap_editor import KeymapEditorPage
from ui.pages.about import AboutPage


class LotusSettingsWindow(QMainWindow):
    """Main entry window for Lotus Configuration GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("Lotus Settings"))

        self.dbus_handler = LotusDBusHandler()
        self.file_handler = Fcitx5ConfigHandler()

        self._setup_ui()
        self._setup_window_size()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setSpacing(0)

        # Apply Global Styling
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
                font-size: 13px;
            }
            QLabel, QCheckBox, QRadioButton {
                background-color: transparent;
            }
            QLabel#CategoryTitle {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 5px;
            }
            QLabel#GroupHeader {
                font-size: 11px;
                font-weight: 800;
                color: #666666;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 15px;
                margin-bottom: 5px;
            }
            QListWidget#Sidebar {
                background-color: #212121;
                border: none;
                border-right: 1px solid #2d2d2d;
                outline: none;
                padding: 10px 0;
            }
            QListWidget#Sidebar::item {
                padding: 10px 20px;
                margin: 2px 10px;
                border-radius: 6px;
                color: #a0a0a0;
            }
            QListWidget#Sidebar::item:hover {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QListWidget#Sidebar::item:selected {
                background-color: #35a2e1;
                color: #ffffff;
            }
            QStackedWidget {
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
            QPushButton#Primary {
                background-color: #35a2e1;
            }
            QPushButton#Primary:hover {
                background-color: #4db1e4;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border-color: #35a2e1;
            }
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 5px 10px;
                color: #ffffff;
                min-width: 140px;
            }
            QComboBox:hover {
                border-color: #35a2e1;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #212121;
                border: 1px solid #2d2d2d;
                selection-background-color: #35a2e1;
                selection-color: #ffffff;
                color: #e0e0e0;
                outline: none;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding-left: 8px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #35a2e1;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: #252525;
                color: #555555;
            }
            QTableWidget {
                background-color: #212121;
                alternate-background-color: #282828;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
                gridline-color: transparent;
                outline: none;
            }
            QHeaderView::section {
                background-color: #212121;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #a0a0a0;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2d2d2d;
            }
            QTableWidget::item:selected {
                background-color: #35a2e1;
                color: #ffffff;
            }
            QCheckBox, QRadioButton {
                spacing: 8px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
            }
            QRadioButton::indicator {
                border-radius: 9px;
            }
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {
                border-color: #4db1e4;
            }
            QCheckBox::indicator:checked {
                background-color: #35a2e1;
                border-color: #35a2e1;
                image: none; /* Clear default checkmark if needed or use custom */
            }
            QRadioButton::indicator:checked {
                background-color: #35a2e1;
                border-color: #35a2e1;
            }
        """)

        main_h_layout = QHBoxLayout()
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFrameShape(QFrame.NoFrame)

        self.content_stack = QStackedWidget()

        main_h_layout.addWidget(self.sidebar)
        main_h_layout.addWidget(self.content_stack, 1)

        main_v_layout.addLayout(main_h_layout, 1)

        # Bottom Bar
        self._setup_bottom_bar(main_v_layout)

        # Pages Mapping
        self._setup_pages()

        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        self.sidebar.setCurrentRow(0)

    def _setup_bottom_bar(self, layout):
        container = QFrame()
        container.setObjectName("BottomBar")
        container.setStyleSheet("""
            QFrame#BottomBar {
                background-color: #212121;
                border-top: 1px solid #2d2d2d;
            }
        """)
        bar_layout = QHBoxLayout(container)
        bar_layout.setContentsMargins(20, 12, 20, 12)
        bar_layout.setSpacing(10)

        self.btn_reset = QPushButton(_("Restore Defaults"))
        self.btn_reset.clicked.connect(self.on_restore_defaults)
        bar_layout.addWidget(self.btn_reset)

        bar_layout.addStretch()

        self.btn_cancel = QPushButton(_("Cancel"))
        self.btn_cancel.clicked.connect(self.close)
        bar_layout.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton(_("Apply"))
        self.btn_apply.setEnabled(False)
        self.btn_apply.clicked.connect(lambda: self.on_save_all(quiet=True))
        bar_layout.addWidget(self.btn_apply)

        self.btn_ok = QPushButton(_("OK"))
        self.btn_ok.setObjectName("Primary")
        self.btn_ok.clicked.connect(self.on_ok)
        bar_layout.addWidget(self.btn_ok)

        layout.addWidget(container)

    def _setup_pages(self):
        # Top-level Settings Pages
        self._add_page(_("General"), "preferences-system", DynamicSettingsPage(self.dbus_handler, category="general"))
        self._add_page(_("Typing"), "input-keyboard", DynamicSettingsPage(self.dbus_handler, category="typing"))
        self._add_page(_("Macros"), "accessories-text-editor", MacroEditorPage(self.file_handler, self.dbus_handler))
        self._add_page(_("Keymap"), "preferences-desktop-keyboard", KeymapEditorPage(self.file_handler))
        self._add_page(_("Appearance"), "preferences-desktop-theme", DynamicSettingsPage(self.dbus_handler, category="appearance"))
        
        # Bottom section
        spacer = QListWidgetItem()
        spacer.setFlags(Qt.NoItemFlags)
        spacer.setSizeHint(QSize(0, 20))
        self.sidebar.addItem(spacer)
        self._add_page(_("About"), "help-about", AboutPage())

    def on_restore_defaults(self):
        """Resets all settings to their default values."""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            _("Confirm Reset"),
            _("Are you sure you want to restore all settings to their default values?"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for i in range(self.content_stack.count()):
                page = self.content_stack.widget(i)
                if hasattr(page, "restore_defaults"):
                    page.restore_defaults()
            self.on_changed()

    def on_changed(self):
        """Enables the apply button when changes are detected."""
        self.btn_apply.setEnabled(True)

    def on_save_all(self, quiet=False):
        """Triggers save on all pages that support it."""
        for i in range(self.content_stack.count()):
            page = self.content_stack.widget(i)
            if hasattr(page, "save_data"):
                page.save_data(quiet=True)
        
        self.btn_apply.setEnabled(False)
        if not quiet:
             from PySide6.QtWidgets import QMessageBox
             QMessageBox.information(self, _("Success"), _("All settings applied successfully."))

    def on_ok(self):
        self.on_save_all(quiet=True)
        self.close()

    def _on_sidebar_changed(self, index):
        item = self.sidebar.item(index)
        if item and item.data(Qt.UserRole) == "header":
            # Don't allow selecting headers, move to next item
            if index + 1 < self.sidebar.count():
                self.sidebar.setCurrentRow(index + 1)
        else:
            # Map index to stack (skipping headers is tricky, better use a mapping)
            # For simplicity, we can use item.data(Qt.UserRole + 1) to store widget index
            stack_idx = item.data(Qt.UserRole + 1)
            if stack_idx is not None:
                self.content_stack.setCurrentIndex(stack_idx)

    def _setup_window_size(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w = int(screen.width() * 0.45)
        h = int(screen.height() * 0.55)
        self.setMinimumSize(750, 500)
        self.resize(w, h)
        self.move((screen.width() - w) // 2, (screen.height() - h) // 2)

    def _add_header(self, title: str):
        item = QListWidgetItem(title)
        item.setData(Qt.UserRole, "header")
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        
        # Set styling directly since QListWidgetItem is not a QObject
        font = item.font()
        font.setBold(True)
        font.setPointSize(10)
        item.setFont(font)
        item.setForeground(Qt.gray)
        
        self.sidebar.addItem(item)

    def _add_page(self, title: str, icon_name: str, widget: QWidget):
        item = QListWidgetItem(QIcon.fromTheme(icon_name), title)
        item.setData(Qt.UserRole, "page")
        
        stack_idx = self.content_stack.addWidget(widget)
        item.setData(Qt.UserRole + 1, stack_idx)
        
        self.sidebar.addItem(item)
