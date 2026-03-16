# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Dynamic Settings Page with Card-based Layout matching modern guidelines.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QScrollArea,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from i18n import _
from core.dbus_handler import LotusDBusHandler
from ui.components import HotkeyCaptureWidget


class CardWidget(QFrame):
    """A visual container (Card) for grouping related settings."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        self.setStyleSheet(
            """
            QFrame#SettingCard {
                background-color: palette(base);
                border: 1px solid palette(alternate-base);
                border-radius: 10px;
            }
        """
        )

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 15, 20, 15)
        self.main_layout.setSpacing(10)

        title_label = QLabel(title)
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)

        self.main_layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        self.main_layout.addLayout(self.content_layout)


class DynamicSettingsPage(QWidget):
    def __init__(self, dbus_handler: LotusDBusHandler, parent=None):
        super().__init__(parent)
        self.dbus = dbus_handler
        self.current_values = {}
        self.button_groups = []

        self._setup_ui()
        self.load_config()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 20, 30, 20)
        self.container_layout.setSpacing(20)

        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def load_config(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.button_groups.clear()

        config_data = self.dbus.get_config()
        if not config_data:
            self.container_layout.addWidget(QLabel(_("Failed to load configuration.")))
            return

        self.current_values = config_data.get("values", {})
        metadata_list = config_data.get("metadata", [])
        if not metadata_list:
            return

        hotkey_items = []
        im_items = []
        charset_items = []
        option_items = []

        for group in metadata_list:
            for item in group[1]:
                k = item[0]
                if k == "ModeMenuKey":
                    hotkey_items.append(item)
                elif k == "InputMethod" or k == "Mode":
                    im_items.append(item)
                elif k == "OutputCharset":
                    charset_items.append(item)
                elif item[1] == "Boolean":
                    option_items.append(item)

        if hotkey_items:
            card_hk = CardWidget(_("Phím tắt"))
            for item in hotkey_items:
                self._render_hotkey(item, card_hk.content_layout)
            self.container_layout.addWidget(card_hk)

        if im_items:
            card_im = CardWidget(_("Kiểu gõ / Chế độ"))
            for item in im_items:
                self._render_radio_group(item, card_im.content_layout, columns=1)
            self.container_layout.addWidget(card_im)

        if charset_items:
            card_cs = CardWidget(_("Bảng mã"))
            for item in charset_items:
                self._render_radio_group(item, card_cs.content_layout, columns=2)
            self.container_layout.addWidget(card_cs)

        if option_items:
            card_opt = CardWidget(_("Tùy chọn"))
            for item in option_items:
                self._render_checkbox(item, card_opt.content_layout)
            self.container_layout.addWidget(card_opt)

        self.container_layout.addStretch()

    def _render_hotkey(self, item, layout):
        key, type_str, label, default, annotations = item
        val = self.current_values.get(key, default)

        hotkey_str = val.get("0", "") if isinstance(val, dict) else ""

        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel(_(label)))

        hk_btn = HotkeyCaptureWidget(hotkey_str)
        hk_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hk_btn.setMinimumWidth(150)
        hk_btn.textChanged.connect(
            lambda text, k=key: self.update_config(k, {"0": text})
        )

        row_layout.addWidget(hk_btn)
        layout.addLayout(row_layout)

    def _render_radio_group(self, item, layout, columns=1):
        key, type_str, label, default, annotations = item
        val = str(self.current_values.get(key, default))

        if "Enum" not in annotations:
            return

        subtitle = QLabel(f"<b>{_(label)}</b>")
        subtitle.setStyleSheet("color: palette(text); padding-top: 5px;")
        layout.addWidget(subtitle)

        enum_dict = annotations.get("Enum", {})
        sorted_keys = sorted(
            enum_dict.keys(), key=lambda x: int(x) if str(x).isdigit() else x
        )

        btn_group = QButtonGroup(self)
        self.button_groups.append(btn_group)

        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        row, col = 0, 0
        for k in sorted_keys:
            rb_text = str(enum_dict[k])
            rb = QRadioButton(_(rb_text))

            rb.setProperty("val_str", rb_text)

            if rb_text == val:
                rb.setChecked(True)

            btn_group.addButton(rb)
            grid.addWidget(rb, row, col)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        btn_group.buttonClicked.connect(
            lambda btn, k=key: self.update_config(k, btn.property("val_str"))
        )
        layout.addLayout(grid)

    def _render_checkbox(self, item, layout):
        key, type_str, label, default, annotations = item
        val = self.current_values.get(key, default)

        cb = QCheckBox(_(label))
        is_checked = str(val).lower() == "true"
        cb.setChecked(is_checked)

        cb.toggled.connect(
            lambda checked, k=key: self.update_config(k, "True" if checked else "False")
        )
        layout.addWidget(cb)

    def update_config(self, key: str, new_value):
        self.current_values[key] = new_value
        self.dbus.set_config(self.current_values)
