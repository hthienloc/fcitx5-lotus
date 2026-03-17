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
    QComboBox,
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
        self.setStyleSheet("""
            QFrame#SettingCard {
                background-color: #212121;
                border: 1px solid #2d2d2d;
                border-radius: 8px;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 4px;
            """)
            self.main_layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        self.main_layout.addLayout(self.content_layout)


class DynamicSettingsPage(QWidget):
    def __init__(self, dbus_handler: LotusDBusHandler, category: str = "general", parent=None):
        super().__init__(parent)
        self.dbus = dbus_handler
        self.category = category
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
        self.scroll.setStyleSheet("background-color: transparent;")

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

        if self.category == "general":
            title = QLabel(_("General"))
            title.setObjectName("CategoryTitle")
            self.container_layout.addWidget(title)

            # Group: HOTKEYS
            header_hk = QLabel(_("HOTKEYS"))
            header_hk.setObjectName("GroupHeader")
            self.container_layout.addWidget(header_hk)
            card_hk = CardWidget("")
            if hotkey_items:
                for item in hotkey_items:
                    self._render_hotkey(item, card_hk.content_layout)
            self.container_layout.addWidget(card_hk)

            # Group: INPUT METHOD
            header_im = QLabel(_("INPUT METHOD"))
            header_im.setObjectName("GroupHeader")
            self.container_layout.addWidget(header_im)
            card_im = CardWidget("")
            if im_items:
                for item in im_items:
                    self._render_combobox(item, card_im.content_layout)
            if charset_items:
                for item in charset_items:
                    self._render_combobox(item, card_im.content_layout)
            self.container_layout.addWidget(card_im)

        elif self.category == "appearance":
            title = QLabel(_("Appearance"))
            title.setObjectName("CategoryTitle")
            self.container_layout.addWidget(title)

            # Group: THEME & ICONS
            header_app = QLabel(_("THEME & ICONS"))
            header_app.setObjectName("GroupHeader")
            self.container_layout.addWidget(header_app)
            card_app = CardWidget("")
            for item in option_items:
                if item[0] == "UseLotusIcons":
                    self._render_checkbox(item, card_app.content_layout)
            self.container_layout.addWidget(card_app)

        elif self.category == "typing":
            title = QLabel(_("Typing"))
            title.setObjectName("CategoryTitle")
            self.container_layout.addWidget(title)

            # Group: SPELLING & CORRECTIONS
            header1 = QLabel(_("SPELLING & CORRECTIONS"))
            header1.setObjectName("GroupHeader")
            self.container_layout.addWidget(header1)
            
            card1 = CardWidget("")
            for item in option_items:
                if item[0] in ["SpellCheck", "AutoNonVnRestore", "DdFreeStyle"]:
                    self._render_checkbox(item, card1.content_layout)
            self.container_layout.addWidget(card1)

            # Group: TYPING OPTIONS
            header2 = QLabel(_("TYPING OPTIONS"))
            header2.setObjectName("GroupHeader")
            self.container_layout.addWidget(header2)
            
            card2 = CardWidget("")
            for item in option_items:
                if item[0] in ["ModernStyle", "FreeMarking", "FixUinputWithAck"]:
                    self._render_checkbox(item, card2.content_layout)
            self.container_layout.addWidget(card2)

        elif self.category == "shortcuts":
            title = QLabel(_("Phím tắt"))
            title.setObjectName("CategoryTitle")
            self.container_layout.addWidget(title)

            card = CardWidget("")
            if hotkey_items:
                for item in hotkey_items:
                    self._render_hotkey(item, card.content_layout)
            self.container_layout.addWidget(card)

        elif self.category == "interface":
             title = QLabel(_("Giao diện"))
             title.setObjectName("CategoryTitle")
             self.container_layout.addWidget(title)
             # Future interface settings or empty for now
             self.container_layout.addWidget(QLabel(_("No interface settings available yet.")))

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

    def _render_combobox(self, item, layout):
        key, type_str, label, default, annotations = item
        val = str(self.current_values.get(key, default))

        if "Enum" not in annotations:
            return

        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel(_(label)))
        row_layout.addStretch()

        combo = QComboBox()
        enum_dict = annotations.get("Enum", {})
        sorted_keys = sorted(
            enum_dict.keys(), key=lambda x: int(x) if str(x).isdigit() else x
        )

        for k in sorted_keys:
            rb_text = str(enum_dict[k])
            combo.addItem(_(rb_text), rb_text)

        idx = combo.findData(val)
        if idx >= 0:
            combo.setCurrentIndex(idx)

        combo.currentTextChanged.connect(
            lambda text, k=key: self.update_config(k, combo.currentData())
        )
        row_layout.addWidget(combo)
        layout.addLayout(row_layout)

    def _render_radio_group(self, item, layout, columns=1):
        key, type_str, label, default, annotations = item
        val = str(self.current_values.get(key, default))

        if "Enum" not in annotations:
            return

        subtitle = QLabel(f"<b>{_(label)}</b>")
        if label != "Output Charset":
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

    def restore_defaults(self):
        """Resets current values to engine defaults."""
        config_data = self.dbus.get_config()
        if not config_data:
            return

        metadata_list = config_data.get("metadata", [])
        new_values = {}
        for group in metadata_list:
            for item in group[1]:
                key, type_str, label, default, annotations = item
                new_values[key] = default
        
        self.current_values = new_values
        self.load_config()

    def save_data(self, quiet=False):
        """Commits all staged changes to DBus."""
        if self.current_values:
            self.dbus.set_config(self.current_values)

    def update_config(self, key: str, new_value):
        """Updates internal state and notifies parent window of change."""
        self.current_values[key] = new_value
        # Notify the parent window (LotusSettingsWindow) if it exists
        main_win = self.window()
        if hasattr(main_win, "on_changed"):
            main_win.on_changed()
