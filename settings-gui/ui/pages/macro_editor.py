# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Macro Editor Page. Edits lotus-macro-table.conf.
Implements UI with row reordering and TSV import/export.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QLabel,
    QSizePolicy,
    QAbstractItemView,
    QFileDialog,
)
from PySide6.QtGui import QIcon
from i18n import _
from core.file_handler import Fcitx5ConfigHandler


class MacroEditorPage(QWidget):
    """UI for editing Lotus macros."""

    def __init__(self, config_handler: Fcitx5ConfigHandler, parent=None):
        super().__init__(parent)
        self.handler = config_handler
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Left Column
        left_column = QVBoxLayout()

        # Input row
        input_layout = QHBoxLayout()
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText(_("Abbreviation (e.g. kg)"))
        self.input_val = QLineEdit()
        self.input_val.setPlaceholderText(_("Full text (e.g. khô gà)"))
        self.input_val.returnPressed.connect(self.on_add)

        input_layout.addWidget(QLabel(_("Key:")))
        input_layout.addWidget(self.input_key, 1)
        input_layout.addWidget(QLabel(_("Value:")))
        input_layout.addWidget(self.input_val, 2)
        left_column.addLayout(input_layout)

        # Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([_("Abbr."), _("Text")])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self.on_row_selected)
        left_column.addWidget(self.table)

        main_layout.addLayout(left_column)

        # Sidebar Buttons
        sidebar_layout = QVBoxLayout()

        btn_style = "text-align: left; padding: 6px 12px;"

        self.btn_add = QPushButton(QIcon.fromTheme("list-add"), _("Add"))
        self.btn_remove = QPushButton(QIcon.fromTheme("list-remove"), _("Remove"))
        self.btn_up = QPushButton(QIcon.fromTheme("go-up"), _("Up"))
        self.btn_down = QPushButton(QIcon.fromTheme("go-down"), _("Down"))
        self.btn_import = QPushButton(QIcon.fromTheme("document-import"), _("Import"))
        self.btn_export = QPushButton(QIcon.fromTheme("document-export"), _("Export"))
        self.btn_save = QPushButton(_("Save to File"))

        for btn in [
            self.btn_add,
            self.btn_remove,
            self.btn_up,
            self.btn_down,
            self.btn_import,
            self.btn_export,
        ]:
            btn.setStyleSheet(btn_style)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.btn_add.clicked.connect(self.on_add)
        self.btn_remove.clicked.connect(self.on_remove)
        self.btn_up.clicked.connect(self.on_move_up)
        self.btn_down.clicked.connect(self.on_move_down)
        self.btn_import.clicked.connect(self.on_import)
        self.btn_export.clicked.connect(self.on_export)
        self.btn_save.clicked.connect(self.save_data)

        sidebar_layout.addWidget(self.btn_add)
        sidebar_layout.addWidget(self.btn_remove)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(self.btn_up)
        sidebar_layout.addWidget(self.btn_down)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_import)
        sidebar_layout.addWidget(self.btn_export)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(self.btn_save)

        main_layout.addLayout(sidebar_layout)
        self.update_button_states()

    def load_data(self):
        self.table.setRowCount(0)
        data = self.handler.read_array_config(self.handler.macro_file, "Macro")
        for item in data:
            self.upsert_row(item.get("Key", ""), item.get("Value", ""))

    def save_data(self):
        data = []
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            val_item = self.table.item(row, 1)
            if not key_item or not key_item.text():
                continue
            data.append(
                {"Key": key_item.text(), "Value": val_item.text() if val_item else ""}
            )

        self.handler.write_array_config(self.handler.macro_file, "Macro", data)
        QMessageBox.information(self, "Success", "Macros saved successfully.")

    def upsert_row(self, key: str, value: str):
        # Update existing
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0) and self.table.item(row, 0).text() == key:
                self.table.item(row, 1).setText(value)
                self.update_button_states()
                return

        # Insert new
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(key))
        self.table.setItem(row, 1, QTableWidgetItem(value))
        self.update_button_states()

    def update_button_states(self):
        row = self.table.currentRow()
        count = self.table.rowCount()
        self.btn_up.setEnabled(row > 0)
        self.btn_down.setEnabled(0 <= row < count - 1)

    def on_add(self):
        key = self.input_key.text().strip()
        val = self.input_val.text().strip()
        if not key or not val:
            return

        self.upsert_row(key, val)
        self.input_key.clear()
        self.input_val.clear()
        self.input_key.setFocus()

    def on_remove(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        rows_to_delete = set()
        for r in selected_ranges:
            for i in range(r.topRow(), r.bottomRow() + 1):
                rows_to_delete.add(i)

        # Delete from bottom to top to preserve indices
        for row in sorted(list(rows_to_delete), reverse=True):
            self.table.removeRow(row)

        self.update_button_states()

    def on_move_up(self):
        row = self.table.currentRow()
        if row <= 0:
            return

        self._swap_rows(row, row - 1)
        self.table.selectRow(row - 1)
        self.update_button_states()

    def on_move_down(self):
        row = self.table.currentRow()
        if row < 0 or row >= self.table.rowCount() - 1:
            return

        self._swap_rows(row, row + 1)
        self.table.selectRow(row + 1)
        self.update_button_states()

    def _swap_rows(self, row1, row2):
        key1 = self.table.takeItem(row1, 0)
        val1 = self.table.takeItem(row1, 1)
        key2 = self.table.takeItem(row2, 0)
        val2 = self.table.takeItem(row2, 1)

        self.table.setItem(row1, 0, key2)
        self.table.setItem(row1, 1, val2)
        self.table.setItem(row2, 0, key1)
        self.table.setItem(row2, 1, val1)

    def on_row_selected(self, row, column):
        key_item = self.table.item(row, 0)
        if key_item:
            self.input_key.setText(key_item.text())
        val_item = self.table.item(row, 1)
        if val_item:
            self.input_val.setText(val_item.text())
        self.update_button_states()

    def on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            _("Import Macros"),
            "",
            _("Tab-separated (*.tsv *.txt);;All files (*)"),
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open file for reading: {e}")
            return

        imported = 0
        skipped = 0
        confirmed = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                parts = line.split(",")

            if len(parts) < 2:
                skipped += 1
                continue

            key = parts[0].strip()
            val = parts[1].strip()
            if not key or not val:
                skipped += 1
                continue

            if not confirmed and self.table.rowCount() > 0:
                reply = QMessageBox.question(
                    self,
                    _("Confirm Import"),
                    _(
                        "The current macro list is not empty. Imported entries will be merged (existing keys will be updated). Continue?"
                    ),
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return
                confirmed = True
            else:
                confirmed = True

            self.upsert_row(key, val)
            imported += 1

        QMessageBox.information(
            self,
            _("Import Complete"),
            _(f"Imported {imported} entries, skipped {skipped} invalid lines."),
        )

    def on_export(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(
                self, _("Export"), _("The macro list is empty, nothing to export.")
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            _("Export Macros"),
            "lotus-macro.tsv",
            _("Tab-separated (*.tsv *.txt);;All files (*)"),
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("# Lotus Macro Table\n")
                f.write("# Format: shorthand<TAB>expanded text\n")

                for row in range(self.table.rowCount()):
                    key_item = self.table.item(row, 0)
                    val_item = self.table.item(row, 1)
                    if key_item and val_item and key_item.text():
                        f.write(f"{key_item.text()}\t{val_item.text()}\n")

            QMessageBox.information(
                self,
                _("Export Complete"),
                _(f"Exported {self.table.rowCount()} entries to:\n{path}"),
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open file for writing: {e}")
