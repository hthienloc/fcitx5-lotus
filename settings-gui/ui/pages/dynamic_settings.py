# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Dynamic Settings Page.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QLabel,
    QComboBox,
    QScrollArea,
    QFormLayout,
)
from i18n import _
from core.dbus_handler import LotusDBusHandler
from ui.components import HotkeyCaptureWidget


class DynamicSettingsPage(QWidget):
    def __init__(self, dbus_handler: LotusDBusHandler, parent=None):
        super().__init__(parent)
        self.dbus = dbus_handler
        self.current_values = {}
        self._setup_ui()
        self.load_config()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.form_layout = QFormLayout(self.container)
        self.form_layout.setContentsMargins(20, 20, 20, 20)
        self.form_layout.setSpacing(15)

        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def load_config(self):
        # Clear layout cũ
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        config_data = self.dbus.get_config()
        if not config_data:
            self.form_layout.addRow(QLabel(_("Failed to load configuration.")))
            return

        self.current_values = config_data.get("values", {})
        metadata_list = config_data.get("metadata", [])

        if not metadata_list:
            return

        for group in metadata_list:
            for item in group[1]:
                config_key = item[0]
                config_type = item[1]
                config_label = item[2]

                # Giá trị hiện tại (fallback về default của Fcitx5 nếu không có)
                current_val = self.current_values.get(config_key, item[3])

                # Bản thân nó giờ là 1 Python Dict sạch sẽ
                annotations = item[4]

                self._render_widget(
                    config_key, config_type, config_label, current_val, annotations
                )

    def _render_widget(self, key, type_str, label, value, annotations):
        # Bỏ qua External config (như Macro, Keymap đã có tab riêng)
        if type_str == "External":
            return

        # Checkbox (Booleans)
        if type_str == "Boolean":
            cb = QCheckBox()
            is_checked = str(value).lower() == "true"
            cb.setChecked(is_checked)
            cb.toggled.connect(
                lambda checked, k=key: self.update_config(
                    k, "True" if checked else "False"
                )
            )
            self.form_layout.addRow(_(label), cb)

        # Dropdown (Enums)
        elif "IsEnum" in annotations and str(annotations["IsEnum"]).lower() == "true":
            combo = QComboBox()
            enum_dict = annotations.get("Enum", {})

            # Sort enum_dict keys (0, 1, 2...) để giữ đúng thứ tự Fcitx5
            sorted_keys = sorted(
                enum_dict.keys(), key=lambda x: int(x) if str(x).isdigit() else x
            )
            for k in sorted_keys:
                combo.addItem(str(enum_dict[k]))

            combo.setCurrentText(str(value))
            combo.currentTextChanged.connect(
                lambda text, k=key: self.update_config(k, text)
            )
            self.form_layout.addRow(_(label), combo)

        # Hotkey Capture
        elif type_str == "List|Key":
            hotkey_str = ""
            if isinstance(value, dict) and "0" in value:
                hotkey_str = value["0"]

            hotkey_btn = HotkeyCaptureWidget(hotkey_str)
            # Fcitx5 yêu cầu List|Key phải gửi dạng dict {"0": "Tên_Phím"}
            hotkey_btn.textChanged.connect(
                lambda text, k=key: self.update_config(k, {"0": text})
            )
            self.form_layout.addRow(_(label), hotkey_btn)

        # String thuần
        elif type_str == "String":
            from PySide6.QtWidgets import QLineEdit

            le = QLineEdit(str(value))
            le.textChanged.connect(lambda text, k=key: self.update_config(k, text))
            self.form_layout.addRow(_(label), le)

    def update_config(self, key: str, new_value):
        self.current_values[key] = new_value
        self.dbus.set_config(self.current_values)
