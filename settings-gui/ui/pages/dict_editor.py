# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Dictionary Editor Page. Edits lotus-dict-table.conf.
Implements UI with row reordering and TSV import/export.
"""

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QLabel,
    QAbstractItemView,
    QFileDialog,
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt
from i18n import _
from core.dbus_handler import LotusDBusHandler
from ui.pages.base_editor import BaseEditorPage
from ui.pages.dynamic_settings import CardWidget


class DictEditorPage(BaseEditorPage):
    """UI for editing Lotus dictionary."""

    def __init__(
        self,
        dbus_handler: LotusDBusHandler,
        parent=None,
    ):
        super().__init__(parent)
        self.dbus = dbus_handler
        self.word_map = {}  # word -> QTableWidgetItem
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        title = QLabel(_("Dictionary"))
        title.setObjectName("CategoryTitle")
        main_layout.addWidget(title)

        # Main content area
        editor_card = CardWidget("")
        content_layout = QVBoxLayout()
        editor_card.content_layout.addLayout(content_layout)
        main_layout.addWidget(editor_card)

        # 1. Input Row (Top)
        input_layout = QHBoxLayout()
        self.input_word = QLineEdit()
        self.input_word.setPlaceholderText(_("Word (e.g. khongdau)"))
        self.input_word.setClearButtonEnabled(True)
        self.input_word.returnPressed.connect(self.on_add)

        self.btn_add = QPushButton(QIcon.fromTheme("list-add"), _("Add"))
        self.btn_add.clicked.connect(self.on_add)
        self.input_word.textChanged.connect(self._update_add_button_icon)

        input_layout.addWidget(QLabel(_("Word:")))
        input_layout.addWidget(self.input_word, 1)
        input_layout.addWidget(self.btn_add)
        content_layout.addLayout(input_layout)

        # 1b. Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search words..."))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(QLabel(_("Search:")))
        search_layout.addWidget(self.search_input)
        content_layout.addLayout(search_layout)

        # 2. Table Area
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels([_("Word")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.apply_table_style()  # Apply custom table styling
        self.table.cellClicked.connect(self.on_row_selected)
        content_layout.addWidget(self.table)

        # 3. Bottom Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 5, 0, 0)

        self.btn_remove = QPushButton(QIcon.fromTheme("list-remove"), _("Remove"))
        self.btn_remove.clicked.connect(self.on_remove)

        self.btn_import = QPushButton(QIcon.fromTheme("document-import"), _("Import"))
        self.btn_export = QPushButton(QIcon.fromTheme("document-export"), _("Export"))
        self.btn_import.clicked.connect(self.on_import)
        self.btn_export.clicked.connect(self.on_export)

        toolbar_layout.addWidget(self.btn_remove)
        toolbar_layout.addStretch()

        content_layout.addLayout(toolbar_layout)
        self.update_button_states()

    def load_data(self):
        self.blockSignals(True)
        try:
            self.table.setRowCount(0)
            self.word_map.clear()
            data = self.dbus.get_sub_config_list("lotus-dict", "Dictionary")
            for item in data:
                self.upsert_row(item.get("Word", ""), sort=False)
            self.sort_invalid_to_top()
        finally:
            self.blockSignals(False)

    def restore_defaults(self):
        """Resets dictionary to empty."""
        self.blockSignals(True)
        try:
            self.table.setRowCount(0)
            self.word_map.clear()
            self._on_item_changed()
        finally:
            self.blockSignals(False)

    def is_modified_from_default(self):
        """Returns True if the dictionary has entries."""
        return self.table.rowCount() > 0

    def save_data(self, quiet=False):
        data = []
        for row in range(self.table.rowCount()):
            word_item = self.table.item(row, 0)
            if not word_item or not word_item.text():
                continue
            data.append({"Word": word_item.text()})

        self.dbus.set_sub_config_list("lotus-dict", "Dictionary", data)
        if not quiet:
            QMessageBox.information(self, _("Success"), _("Dictionary saved successfully."))

    def upsert_row(self, word: str, sort: bool = True):
        # Check if exists (O(1))
        existing_item = self.word_map.get(word)
        if existing_item:
            row = self.table.row(existing_item)
            self._apply_row_highlight(row, word)
            if sort:
                self.sort_invalid_to_top()
                self.on_search_changed()
                self.update_button_states()
            return

        # Insert new
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QTableWidgetItem(word)
        self.table.setItem(row, 0, item)
        self.word_map[word] = item
        self._apply_row_highlight(row, word)
        if sort:
            self.sort_invalid_to_top()
            self.on_search_changed()
            self.update_button_states()
            self._on_item_changed()

    def _is_invalid_word(self, word: str) -> bool:
        """Checks if word contains spaces."""
        if not word:
            return False
        return " " in word

    def _apply_row_highlight(self, row: int, word: str):
        """Applies red background and warning icon to rows with invalid words."""
        is_invalid = self._is_invalid_word(word)
        bg_color = Qt.transparent
        tooltip = ""
        icon = QIcon()
        if is_invalid:
            bg_color = QColor(Qt.red)
            bg_color.setAlpha(60)
            icon = QIcon.fromTheme("dialog-warning")
            tooltip = _("Warning: Dictionary words should not contain spaces.")

        item = self.table.item(row, 0)
        if item:
            item.setBackground(bg_color)
            item.setToolTip(tooltip)
            item.setIcon(icon)

    def sort_invalid_to_top(self):
        """Moves all invalid entries to the top, then sorts by word."""
        rows = list(self.word_map.keys())
        rows.sort(key=lambda x: (not self._is_invalid_word(x), x.lower()))

        self.blockSignals(True)
        self.table.setRowCount(0)
        self.word_map.clear()
        for word in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            item = QTableWidgetItem(word)
            self.table.setItem(row_idx, 0, item)
            self.word_map[word] = item
            self._apply_row_highlight(row_idx, word)
        self.on_search_changed()
        self.blockSignals(False)

    def on_search_changed(self):
        """Filters the table rows based on the search input."""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            word_item = self.table.item(row, 0)
            word = word_item.text().lower() if word_item else ""
            self.table.setRowHidden(row, search_text not in word)

    def on_add(self):
        word = self.input_word.text().strip()
        if not word:
            return

        self.upsert_row(word)
        self.input_word.clear()
        self._update_add_button_icon()
        self.input_word.setFocus()

    def _update_add_button_icon(self):
        """Handles validation and Add button state."""
        word = self.input_word.text().strip()
        is_invalid = self._is_invalid_word(word)
        
        if is_invalid:
            self.input_word.setStyleSheet("color: red;")
            self.input_word.setToolTip(_("Warning: Dictionary words should not contain spaces."))
        else:
            self.input_word.setStyleSheet("")
            self.input_word.setToolTip("")

        self.btn_add.setEnabled(not is_invalid and bool(word))

        if word in self.word_map:
            self.btn_add.setIcon(QIcon.fromTheme("document-save"))
            self.btn_add.setText(_("Exists"))
            self.btn_add.setEnabled(False)
        else:
            self.btn_add.setIcon(QIcon.fromTheme("list-add"))
            self.btn_add.setText(_("Add"))

    def on_row_selected(self, row, column):
        word_item = self.table.item(row, 0)
        if word_item:
            self.input_word.setText(word_item.text())
        self.update_button_states()

    def on_remove(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        rows_to_delete = set()
        for r in selected_ranges:
            for i in range(r.topRow(), r.bottomRow() + 1):
                rows_to_delete.add(i)

        for row in sorted(list(rows_to_delete), reverse=True):
            item = self.table.item(row, 0)
            if item:
                word = item.text()
                if word in self.word_map:
                    del self.word_map[word]
            self.table.removeRow(row)

        self.update_button_states()
        self._on_item_changed()
        self._update_add_button_icon()

    def on_import(self):
        path, _filter = QFileDialog.getOpenFileName(
            self,
            _("Import Dictionary"),
            "",
            _("Text files (*.txt *.tsv);;All files (*)"),
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (IOError, OSError, UnicodeDecodeError) as e:
            QMessageBox.warning(self, "Error", f"Cannot open file for reading: {e}")
            return

        imported = 0
        confirmed = False
        for line in lines:
            word = line.strip()
            if not word or word.startswith("#"):
                continue

            if not confirmed and self.table.rowCount() > 0:
                reply = QMessageBox.question(
                    self,
                    _("Confirm Import"),
                    _(
                        "The current dictionary is not empty. Imported entries will be merged. Continue?"
                    ),
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return
                confirmed = True
            else:
                confirmed = True

            self.upsert_row(word, sort=False)
            imported += 1

        self.sort_invalid_to_top()

        QMessageBox.information(
            self,
            _("Import Complete"),
            _(f"Imported {imported} words."),
        )

    def on_export(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(
                self, _("Export"), _("The dictionary is empty, nothing to export.")
            )
            return
        path, _filter = QFileDialog.getSaveFileName(
            self,
            _("Export Dictionary"),
            "lotus-dict.txt",
            _("Text files (*.txt);;All files (*)"),
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("# Lotus Dictionary\n")
                for row in range(self.table.rowCount()):
                    word_item = self.table.item(row, 0)
                    if word_item and word_item.text():
                        f.write(f"{word_item.text()}\n")
            QMessageBox.information(
                self,
                _("Export Complete"),
                _(f"Exported {self.table.rowCount()} words to:\n{path}"),
            )
        except (IOError, OSError) as e:
            QMessageBox.warning(self, "Error", f"Cannot open file for writing: {e}")
