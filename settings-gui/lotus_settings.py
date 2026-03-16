#!/usr/bin/env python3
"""
Fcitx5-Lotus Settings GUI
A modern settings interface for fcitx5-lotus input method using PySide6.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QGroupBox,
    QScrollArea,
    QLineEdit,
    QToolButton,
    QGridLayout,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal, QSize, QEvent
from PySide6.QtGui import QIcon, QFont, QKeyEvent, QPalette

# Import i18n module
from i18n import _, ngettext

# Import D-Bus handler
from dbus_handler import LotusDBusHandler


class HotkeyCaptureWidget(QFrame):
    """
    Custom widget for capturing keyboard shortcuts (hotkeys).
    Similar to fcitx5's hotkey capture behavior.
    """

    hotkeyChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.capturing = False
        self.current_keys = []
        self.modifiers = set()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        # Set frame style
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Hotkey display label
        self.hotkey_label = QLabel(_("Not Set"))
        self.hotkey_label.setAlignment(Qt.AlignCenter)
        self.hotkey_label.setStyleSheet(
            """
            QLabel {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 4px 12px;
                min-width: 120px;
            }
        """
        )

        # Clear button
        self.clear_btn = QToolButton()
        self.clear_btn.setText("✕")
        self.clear_btn.setFixedSize(24, 24)
        self.clear_btn.setToolTip(_("Clear hotkey"))
        self.clear_btn.setStyleSheet(
            """
            QToolButton {
                border: none;
                background: transparent;
                color: palette(text);
            }
            QToolButton:hover {
                background-color: palette(alternate-base);
                border-radius: 4px;
            }
        """
        )

        layout.addWidget(self.hotkey_label)
        layout.addWidget(self.clear_btn)
        layout.addStretch()

    def _connect_signals(self):
        self.clear_btn.clicked.connect(self.clear_hotkey)

    def setHotkey(self, keys: str):
        """Set the current hotkey display."""
        self.current_keys = keys.split("+") if keys else []
        self.hotkey_label.setText(keys if keys else _("Not Set"))

    def getHotkey(self) -> str:
        """Get the current hotkey as string."""
        return "+".join(self.current_keys)

    def clear_hotkey(self):
        """Clear the current hotkey."""
        self.current_keys = []
        self.hotkey_label.setText(_("Not Set"))
        self.hotkeyChanged.emit("")

    def event(self, event):
        """Handle key events for hotkey capture."""
        if event.type() == QEvent.KeyPress and self.capturing:
            key = event.key()

            # Handle modifiers
            if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
                self.modifiers.add(key)
                return True

            # Build key combination
            key_parts = []

            # Add modifiers
            if Qt.Key_Control in self.modifiers:
                key_parts.append("Ctrl")
            if Qt.Key_Shift in self.modifiers:
                key_parts.append("Shift")
            if Qt.Key_Alt in self.modifiers:
                key_parts.append("Alt")
            if Qt.Key_Meta in self.modifiers:
                key_parts.append("Super")

            # Add the main key
            key_text = event.text().upper() if event.text() else ""
            if not key_text:
                key_text = self._key_to_string(key)

            if key_text:
                key_parts.append(key_text)

            # Update display
            result = "+".join(key_parts)
            self.current_keys = key_parts
            self.hotkey_label.setText(result)
            self.capturing = False
            self.hotkeyChanged.emit(result)

            return True

        elif event.type() == QEvent.KeyRelease:
            if event.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
                self.modifiers.discard(event.key())

        return super().event(event)

    def _key_to_string(self, key: int) -> str:
        """Convert Qt key code to string."""
        key_map = {
            Qt.Key_Space: "Space",
            Qt.Key_Tab: "Tab",
            Qt.Key_Backspace: "Backspace",
            Qt.Key_Return: "Return",
            Qt.Key_Enter: "Enter",
            Qt.Key_Escape: "Escape",
            Qt.Key_Delete: "Delete",
            Qt.Key_Home: "Home",
            Qt.Key_End: "End",
            Qt.Key_PageUp: "PageUp",
            Qt.Key_PageDown: "PageDown",
            Qt.Key_Left: "Left",
            Qt.Key_Right: "Right",
            Qt.Key_Up: "Up",
            Qt.Key_Down: "Down",
            Qt.Key_F1: "F1",
            Qt.Key_F2: "F2",
            Qt.Key_F3: "F3",
            Qt.Key_F4: "F4",
            Qt.Key_F5: "F5",
            Qt.Key_F6: "F6",
            Qt.Key_F7: "F7",
            Qt.Key_F8: "F8",
            Qt.Key_F9: "F9",
            Qt.Key_F10: "F10",
            Qt.Key_F11: "F11",
            Qt.Key_F12: "F12",
        }
        return key_map.get(key, "")

    def focusInEvent(self, event):
        """Handle focus in to start capturing."""
        self.capturing = True
        self.hotkey_label.setText(_("Press keys..."))
        self.hotkey_label.setStyleSheet(
            """
            QLabel {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: 2px solid palette(highlight);
                border-radius: 4px;
                padding: 4px 12px;
                min-width: 120px;
            }
        """
        )
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Handle focus out to stop capturing."""
        self.capturing = False
        if not self.current_keys:
            self.hotkey_label.setText(_("Not Set"))
        self.hotkey_label.setStyleSheet(
            """
            QLabel {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 4px 12px;
                min-width: 120px;
            }
        """
        )
        super().focusOutEvent(event)


class CardWidget(QFrame):
    """
    A card-style container widget with modern styling.
    """

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setObjectName("cardWidget")

        # Apply modern card styling
        self.setStyleSheet(
            """
            #cardWidget {
                background-color: palette(window);
                border-radius: 8px;
                border: 1px solid palette(midlight);
            }
        """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        if self.title:
            title_label = QLabel(self.title)
            # Use system font
            font = QFont()
            font.setPointSize(14)
            font.setBold(True)
            title_label.setFont(font)
            main_layout.addWidget(title_label)


class BasicSettingsPage(QWidget):
    """
    Basic settings page with all configuration options from lotus-config.h:
    1. Mode (Chế độ)
    2. Input Method (Kiểu gõ)
    3. Output Charset (Bảng mã)
    4. Spell Check
    5. Enable Macro
    6. Capitalize Macro
    7. Auto Restore Keys With Invalid Words
    8. Modern Style (oà/uý)
    9. Free Marking
    10. Dd Free Style
    11. Fix Uinput With Ack
    12. Use Lotus Icons
    13. Mode Menu Hotkey
    """

    # Signal emitted when any setting changes
    settingChanged = Signal(str, object)

    def __init__(self, dbus_handler: LotusDBusHandler, parent=None):
        super().__init__(parent)
        self.dbus = dbus_handler
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        # Container widget
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Page title
        title = QLabel(_("Lotus Settings"))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        main_layout.addWidget(title)

        # Block 1: Mode (Chế độ hoạt động)
        block_mode = CardWidget(_("Mode"))
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(8)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)

        # Mode options from lotus-config.h
        modes = [
            ("Uinput (Smooth)", "Uinput (Smooth)"),
            ("Uinput (Slow)", "Uinput (Slow)"),
            ("Surrounding Text", "Surrounding Text"),
            ("Preedit", "Preedit"),
            ("Uinput (Hardcore)", "Uinput (Hardcore)"),
            ("OFF", "OFF"),
        ]

        for value, label in modes:
            radio = QRadioButton(_(label))
            radio.setProperty("config_key", "Mode")
            radio.setProperty("config_value", value)
            self.mode_group.addButton(radio)
            mode_layout.addWidget(radio)

        block_mode.layout().addLayout(mode_layout)
        main_layout.addWidget(block_mode)

        # Block 2: Input Method (Kiểu gõ)
        block_input_method = CardWidget(_("Input Method"))
        input_method_layout = QVBoxLayout()
        input_method_layout.setSpacing(8)

        self.input_method_group = QButtonGroup(self)
        self.input_method_group.setExclusive(True)

        # Input method options
        input_methods = [
            ("Telex", "Telex"),
            ("VNI", "VNI"),
        ]

        for value, label in input_methods:
            radio = QRadioButton(_(label))
            radio.setProperty("config_key", "InputMethod")
            radio.setProperty("config_value", value)
            self.input_method_group.addButton(radio)
            input_method_layout.addWidget(radio)

        block_input_method.layout().addLayout(input_method_layout)
        main_layout.addWidget(block_input_method)

        # Block 3: Output Charset (Bảng mã)
        block_charset = CardWidget(_("Output Charset"))
        charset_layout = QGridLayout()
        charset_layout.setSpacing(8)

        self.charset_group = QButtonGroup(self)
        self.charset_group.setExclusive(True)

        # Column 1
        charsets_left = [
            ("Unicode", "Unicode"),
            ("VNI Windows", "VNI Windows"),
            ("Vietnamese Locale CP1258", "Vietnamese Locale CP1258"),
        ]

        # Column 2
        charsets_right = [
            ("TCVN3 (ABC)", "TCVN3 (ABC)"),
            ("Unicode Compound", "Unicode Compound"),
        ]

        for i, (value, label) in enumerate(charsets_left):
            radio = QRadioButton(_(label))
            radio.setProperty("config_key", "OutputCharset")
            radio.setProperty("config_value", value)
            self.charset_group.addButton(radio)
            charset_layout.addWidget(radio, i, 0)

        for i, (value, label) in enumerate(charsets_right):
            radio = QRadioButton(_(label))
            radio.setProperty("config_key", "OutputCharset")
            radio.setProperty("config_value", value)
            self.charset_group.addButton(radio)
            charset_layout.addWidget(radio, i, 1)

        block_charset.layout().addLayout(charset_layout)
        main_layout.addWidget(block_charset)

        # Block 4: Macro Settings
        block_macro = CardWidget(_("Macro"))
        macro_layout = QVBoxLayout()
        macro_layout.setSpacing(8)

        self.enable_macro_check = QCheckBox(_("Enable Macro"))
        self.enable_macro_check.setProperty("config_key", "EnableMacro")
        self.enable_macro_check.setChecked(True)
        macro_layout.addWidget(self.enable_macro_check)

        self.capitalize_macro_check = QCheckBox(_("Capitalize Macro"))
        self.capitalize_macro_check.setProperty("config_key", "CapitalizeMacro")
        self.capitalize_macro_check.setChecked(True)
        macro_layout.addWidget(self.capitalize_macro_check)

        block_macro.layout().addLayout(macro_layout)
        main_layout.addWidget(block_macro)

        # Block 5: Spell Check
        block_spell = CardWidget(_("Spell Check"))
        spell_layout = QVBoxLayout()

        self.spell_check_check = QCheckBox(_("Enable Spell Check"))
        self.spell_check_check.setProperty("config_key", "SpellCheck")
        self.spell_check_check.setChecked(False)
        spell_layout.addWidget(self.spell_check_check)

        block_spell.layout().addLayout(spell_layout)
        main_layout.addWidget(block_spell)

        # Block 6: Behavior Options
        block_behavior = CardWidget(_("Behavior"))
        behavior_layout = QVBoxLayout()
        behavior_layout.setSpacing(8)

        self.modern_style_check = QCheckBox(_("Use oà, uý (Instead Of òa, úy)"))
        self.modern_style_check.setProperty("config_key", "ModernStyle")
        self.modern_style_check.setChecked(True)
        behavior_layout.addWidget(self.modern_style_check)

        self.auto_non_vn_restore_check = QCheckBox(
            _("Auto Restore Keys With Invalid Words")
        )
        self.auto_non_vn_restore_check.setProperty("config_key", "AutoNonVnRestore")
        self.auto_non_vn_restore_check.setChecked(True)
        behavior_layout.addWidget(self.auto_non_vn_restore_check)

        self.free_marking_check = QCheckBox(_("Allow Type With More Freedom"))
        self.free_marking_check.setProperty("config_key", "FreeMarking")
        self.free_marking_check.setChecked(True)
        behavior_layout.addWidget(self.free_marking_check)

        self.dd_free_style_check = QCheckBox(
            _("Allow dd To Produce đ When Auto Restore Keys With Invalid Words Is On")
        )
        self.dd_free_style_check.setProperty("config_key", "DdFreeStyle")
        self.dd_free_style_check.setChecked(True)
        behavior_layout.addWidget(self.dd_free_style_check)

        block_behavior.layout().addLayout(behavior_layout)
        main_layout.addWidget(block_behavior)

        # Block 7: UI Options
        block_ui = CardWidget(_("User Interface"))
        ui_layout = QVBoxLayout()
        ui_layout.setSpacing(8)

        self.fix_uinput_with_ack_check = QCheckBox(_("Fix Uinput Mode With Ack"))
        self.fix_uinput_with_ack_check.setProperty("config_key", "FixUinputWithAck")
        self.fix_uinput_with_ack_check.setChecked(False)
        ui_layout.addWidget(self.fix_uinput_with_ack_check)

        self.use_lotus_icons_check = QCheckBox(_("Use Lotus Status Icons"))
        self.use_lotus_icons_check.setProperty("config_key", "UseLotusIcons")
        self.use_lotus_icons_check.setChecked(False)
        ui_layout.addWidget(self.use_lotus_icons_check)

        block_ui.layout().addLayout(ui_layout)
        main_layout.addWidget(block_ui)

        # Block 8: Hotkeys
        block_hotkey = CardWidget(_("Hotkeys"))
        hotkey_layout = QHBoxLayout()

        hotkey_label = QLabel(_("Mode Menu Hotkey:"))
        hotkey_label.setStyleSheet("font-weight: 500;")

        self.hotkey_capture = HotkeyCaptureWidget()

        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_capture)
        hotkey_layout.addStretch()

        block_hotkey.layout().addLayout(hotkey_layout)
        main_layout.addWidget(block_hotkey)

        # Add stretch to push everything up
        main_layout.addStretch()

        scroll.setWidget(container)

        # Main layout for this page
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)

        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect all UI signals to handlers."""
        # Hotkey capture
        self.hotkey_capture.hotkeyChanged.connect(self._on_hotkey_changed)

        # Mode radio buttons
        self.mode_group.buttonClicked.connect(self._on_radio_changed)

        # Input method radio buttons
        self.input_method_group.buttonClicked.connect(self._on_radio_changed)

        # Charset radio buttons
        self.charset_group.buttonClicked.connect(self._on_radio_changed)

        # Checkboxes
        self.enable_macro_check.stateChanged.connect(self._on_checkbox_changed)
        self.capitalize_macro_check.stateChanged.connect(self._on_checkbox_changed)
        self.spell_check_check.stateChanged.connect(self._on_checkbox_changed)
        self.modern_style_check.stateChanged.connect(self._on_checkbox_changed)
        self.auto_non_vn_restore_check.stateChanged.connect(self._on_checkbox_changed)
        self.free_marking_check.stateChanged.connect(self._on_checkbox_changed)
        self.dd_free_style_check.stateChanged.connect(self._on_checkbox_changed)
        self.fix_uinput_with_ack_check.stateChanged.connect(self._on_checkbox_changed)
        self.use_lotus_icons_check.stateChanged.connect(self._on_checkbox_changed)

    def _on_hotkey_changed(self, keys: str):
        """Handle hotkey change."""
        self.settingChanged.emit("modeMenuKey", keys)

    def _on_radio_changed(self, button: QRadioButton):
        """Handle radio button change."""
        key = button.property("config_key")
        value = button.property("config_value")
        self.settingChanged.emit(key, value)

    def _on_checkbox_changed(self, state: int):
        """Handle checkbox change."""
        checkbox = self.sender()
        key = checkbox.property("config_key")
        value = state == Qt.Checked
        self.settingChanged.emit(key, value)

    def _load_settings(self):
        """Load settings from D-Bus or config file."""
        config = self.dbus.get_config()

        if config:
            # Mode
            mode = config.get("Mode", "Uinput (Smooth)")
            for btn in self.mode_group.buttons():
                if btn.property("config_value") == mode:
                    btn.setChecked(True)
                    break

            # Input Method
            input_method = config.get("InputMethod", "Telex")
            for btn in self.input_method_group.buttons():
                if btn.property("config_value") == input_method:
                    btn.setChecked(True)
                    break

            # Output Charset
            charset = config.get("OutputCharset", "Unicode")
            for btn in self.charset_group.buttons():
                if btn.property("config_value") == charset:
                    btn.setChecked(True)
                    break

            # Checkboxes
            self.enable_macro_check.setChecked(config.get("EnableMacro", True))
            self.capitalize_macro_check.setChecked(config.get("CapitalizeMacro", True))
            self.spell_check_check.setChecked(config.get("SpellCheck", False))
            self.modern_style_check.setChecked(config.get("ModernStyle", True))
            self.auto_non_vn_restore_check.setChecked(
                config.get("AutoNonVnRestore", True)
            )
            self.free_marking_check.setChecked(config.get("FreeMarking", True))
            self.dd_free_style_check.setChecked(config.get("DdFreeStyle", True))
            self.fix_uinput_with_ack_check.setChecked(
                config.get("FixUinputWithAck", False)
            )
            self.use_lotus_icons_check.setChecked(config.get("UseLotusIcons", False))

            # Hotkey
            mode_menu_key = config.get("modeMenuKey", "")
            if mode_menu_key:
                self.hotkey_capture.setHotkey(mode_menu_key)


class QuickTypingPage(QWidget):
    """Quick typing settings page (Gõ nhanh)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel(_("Quick Typing"))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        placeholder = QLabel(_("Quick typing settings will be displayed here."))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()


class AdvancedPage(QWidget):
    """Advanced settings page (Nâng cao)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel(_("Advanced"))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        placeholder = QLabel(_("Advanced settings will be displayed here."))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()


class MacroPage(QWidget):
    """Macro settings page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel(_("Macro"))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        placeholder = QLabel(_("Macro settings will be displayed here."))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()


class ConversionPage(QWidget):
    """Conversion settings page (Chuyển đổi)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel(_("Conversion"))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        placeholder = QLabel(_("Conversion settings will be displayed here."))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()


class UIPage(QWidget):
    """UI settings page (Giao diện)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel(_("User Interface"))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        placeholder = QLabel(_("UI settings will be displayed here."))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()


class AboutPage(QWidget):
    """About page (Giới thiệu)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel(_("About"))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        info = QLabel(
            "<h2>Fcitx5-Lotus</h2>"
            "<p>Vietnamese input method for Fcitx5</p>"
            "<p>Version: 1.0.0</p>"
            "<p>Source: <a href='https://github.com/fcitx5-contrib/fcitx5-lotus'>GitHub</a></p>"
        )
        info.setTextFormat(Qt.RichText)
        info.setOpenExternalLinks(True)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        layout.addStretch()


class LotusSettingsWindow(QMainWindow):
    """
    Main settings window with sidebar navigation.
    """

    def __init__(self):
        super().__init__()

        # Initialize D-Bus handler
        self.dbus = LotusDBusHandler()

        self._setup_ui()
        self._setup_sidebar()
        self._setup_pages()

    def _setup_ui(self):
        """Setup main window UI."""
        self.setWindowTitle(_("Fcitx5-Lotus Settings"))
        self.setMinimumSize(800, 600)

        # Use system theme with proper font
        font = self.font()
        font.setPointSize(11)
        self.setFont(font)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: palette(window);
            }
            QListWidget {
                background-color: palette(window);
                border: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px 8px;
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QListWidget::item:hover {
                background-color: palette(alternate-base);
            }
            QLabel {
                color: palette(window-text);
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton {
                spacing: 8px;
            }
        """
        )

    def _setup_sidebar(self):
        """Setup sidebar with navigation items."""
        # Central widget with horizontal layout
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("background-color: palette(window);")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.setSpacing(4)

        # App title
        app_title = QLabel("Fcitx5-Lotus")
        app_font = QFont()
        app_font.setPointSize(18)
        app_font.setBold(True)
        app_title.setFont(app_font)
        app_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_title)

        sidebar_layout.addSpacing(16)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setFrameShape(QFrame.NoFrame)
        self.nav_list.setSpacing(4)

        # Navigation items with icons
        nav_items = [
            ("settings", _("Basic")),
            ("keyboard", _("Quick Typing")),
            ("tune", _("Advanced")),
            ("code", _("Macro")),
            ("swap_horiz", _("Conversion")),
            ("palette", _("User Interface")),
            ("info", _("About")),
        ]

        for icon_name, text in nav_items:
            item = QListWidgetItem(text)
            item.setIcon(QIcon.fromTheme(icon_name))
            item.setSizeHint(QSize(0, 48))
            self.nav_list.addItem(item)

        sidebar_layout.addWidget(self.nav_list)

        # Add stretch to push items to top
        sidebar_layout.addStretch()

        # Main content area
        self.content_stack = QStackedWidget()

        # Add widgets to main layout
        main_layout.addWidget(sidebar)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: palette(midlight);")
        main_layout.addWidget(separator)

        main_layout.addWidget(self.content_stack, 1)

        # Connect sidebar selection to content
        self.nav_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)

        # Select first item by default
        self.nav_list.setCurrentRow(0)

    def _setup_pages(self):
        """Setup all content pages."""
        # Page 0: Basic Settings
        self.basic_page = BasicSettingsPage(self.dbus)
        self.content_stack.addWidget(self.basic_page)

        # Page 1: Quick Typing
        self.quick_typing_page = QuickTypingPage()
        self.content_stack.addWidget(self.quick_typing_page)

        # Page 2: Advanced
        self.advanced_page = AdvancedPage()
        self.content_stack.addWidget(self.advanced_page)

        # Page 3: Macro
        self.macro_page = MacroPage()
        self.content_stack.addWidget(self.macro_page)

        # Page 4: Conversion
        self.conversion_page = ConversionPage()
        self.content_stack.addWidget(self.conversion_page)

        # Page 5: UI
        self.ui_page = UIPage()
        self.content_stack.addWidget(self.ui_page)

        # Page 6: About
        self.about_page = AboutPage()
        self.content_stack.addWidget(self.about_page)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Use system theme
    app.setStyle("fusion")

    window = LotusSettingsWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
