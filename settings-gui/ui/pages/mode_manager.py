# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Mode Manager Page for per-application input mode configuration.
"""

import os
import re
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QFrame,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QDialog,
    QTabWidget,
    QFileDialog,
    QComboBox,
    QGridLayout,
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
from i18n import _
from ui.pages.dynamic_settings import CardWidget
from core.dbus_handler import LotusDBusHandler

# Mode constants as defined in C++ LotusEngine
MODE_OFF = 0
MODE_SMOOTH = 1
MODE_SLOW = 2
MODE_HARDCORE = 3
MODE_SURROUNDING = 4
MODE_PREEDIT = 5
MODE_EMOJI = 6
MODE_DEFAULT = -1  # UI special value for "Use Global Default"

MODE_INFO = {
    MODE_DEFAULT: {"title": _("System Default"), "icon": "preferences-system"},
    MODE_OFF: {"title": _("Off"), "icon": "input-keyboard"},
    MODE_SMOOTH: {"title": _("Uinput (Smooth)"), "icon": "input-keyboard"},
    MODE_SLOW: {"title": _("Uinput (Slow)"), "icon": "input-keyboard"},
    MODE_HARDCORE: {"title": _("Uinput (Hardcore)"), "icon": "input-keyboard"},
    MODE_SURROUNDING: {"title": _("Surrounding Text"), "icon": "text-field"},
    MODE_PREEDIT: {"title": _("Preedit"), "icon": "text-field"},
    MODE_EMOJI: {"title": _("Emoji Picker"), "icon": "face-smile"},
}

APP_RULES_PATH = os.path.expanduser("~/.config/fcitx5/conf/lotus-app-rules.conf")


class ModeCard(QFrame):
    """A card for selecting an input mode."""

    clicked = Signal(int)

    def __init__(self, mode: int, selected: bool = False, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.selected = selected
        self.setObjectName("ModeCard")
        self.setCursor(Qt.PointingHandCursor)
        self._setup_ui()
        self.update_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(5)

        info = MODE_INFO[self.mode]
        title_label = QLabel(info["title"])
        title_label.setObjectName("ModeCardTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: bold; font-size: 13px;")

        layout.addWidget(title_label)

    def update_style(self):
        if self.selected:
            self.setStyleSheet(
                """
                QFrame#ModeCard {
                    border: 2px solid palette(highlight);
                    background: palette(highlight);
                    border-radius: 8px;
                }
                QLabel { color: palette(highlighted-text); }
            """
            )
        else:
            self.setStyleSheet(
                """
                QFrame#ModeCard {
                    border: 1px solid palette(mid);
                    background: palette(alternate-base);
                    border-radius: 8px;
                }
            """
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.mode)


class AddAppDialog(QDialog):
    """Dialog to add a new application to the rules list."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Add Application"))
        self.setMinimumSize(500, 450)
        self.selected_app = None
        self._setup_ui()
        self._load_running_apps()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_title = QLabel(_("Add Application"))
        header_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_subtitle = QLabel(_("Assign a specific input mode to an application"))
        header_subtitle.setStyleSheet("opacity: 0.7;")

        layout.addWidget(header_title)
        layout.addWidget(header_subtitle)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Running Apps
        self.running_tab = QWidget()
        running_layout = QVBoxLayout(self.running_tab)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search process name..."))
        self.search_input.textChanged.connect(self._filter_running_apps)
        running_layout.addWidget(self.search_input)

        self.running_list = QListWidget()
        self.running_list.setIconSize(QSize(32, 32))
        self.running_list.itemClicked.connect(self._on_app_selected)
        running_layout.addWidget(self.running_list)
        
        self.tabs.addTab(self.running_tab, _("Running"))

        # Tab 2: Browse File
        self.browse_tab = QWidget()
        browse_layout = QVBoxLayout(self.browse_tab)
        browse_layout.setAlignment(Qt.AlignCenter)
        btn_browse = QPushButton(_("Browse Executable..."))
        btn_browse.clicked.connect(self._on_browse_file)
        browse_layout.addWidget(btn_browse)
        self.tabs.addTab(self.browse_tab, _("Browse file"))

        # Tab 3: Manual Input
        self.manual_tab = QWidget()
        manual_layout = QVBoxLayout(self.manual_tab)
        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText(_("Enter application name or path..."))
        manual_layout.addWidget(self.manual_input)
        manual_layout.addStretch()
        self.tabs.addTab(self.manual_tab, _("Manual input"))

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        self.selection_label = QLabel(_("No application selected"))
        self.selection_label.setStyleSheet("opacity: 0.7;")
        
        self.btn_cancel = QPushButton(_("Cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_add = QPushButton(_("Add"))
        self.btn_add.setObjectName("Primary")
        self.btn_add.setEnabled(False)
        self.btn_add.clicked.connect(self._on_add_clicked)

        bottom_layout.addWidget(self.selection_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_cancel)
        bottom_layout.addWidget(self.btn_add)
        layout.addLayout(bottom_layout)

    def _load_running_apps(self):
        """Loads running processes from /proc."""
        apps = []
        try:
            for pid_dir in os.listdir("/proc"):
                if not pid_dir.isdigit():
                    continue
                pid = int(pid_dir)
                try:
                    with open(f"/proc/{pid}/comm", "r") as f:
                        name = f.read().strip()
                    with open(f"/proc/{pid}/cmdline", "r") as f:
                        cmdline = f.read().replace("\x00", " ").strip()
                    
                    if not cmdline:
                        continue
                        
                    exe = ""
                    try:
                        exe = os.readlink(f"/proc/{pid}/exe")
                    except Exception:
                        pass
                    
                    if name and exe:
                        apps.append({"name": name, "exe": exe, "pid": pid})
                except Exception:
                    continue
        except Exception:
            pass

        unique_apps = {}
        for app in apps:
            key = app["exe"]
            if key not in unique_apps:
                unique_apps[key] = app
        
        sorted_apps = sorted(unique_apps.values(), key=lambda x: x["name"].lower())
        self.full_app_list = sorted_apps
        self._populate_list(sorted_apps)

    def _populate_list(self, apps):
        self.running_list.clear()
        for app in apps:
            item = QListWidgetItem()
            item.setText(f"{app['name']}\n{app['exe']}")
            item.setData(Qt.UserRole, app)
            item.setIcon(QIcon.fromTheme(app["name"].lower(), QIcon.fromTheme("application-x-executable")))
            self.running_list.addItem(item)

    def _filter_running_apps(self, text):
        filtered = [a for a in self.full_app_list if text.lower() in a["name"].lower() or text.lower() in a["exe"].lower()]
        self._populate_list(filtered)

    def _on_app_selected(self, item):
        app = item.data(Qt.UserRole)
        self.selected_app = app["name"]
        self.selection_label.setText(f"{_('Selected:')} {self.selected_app}")
        self.btn_add.setEnabled(True)

    def _on_browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, _("Select executable"), "/usr/bin")
        if path:
            self.selected_app = os.path.basename(path)
            self.btn_add.setEnabled(True)
            self.accept()

    def _on_add_clicked(self):
        if self.tabs.currentIndex() == 2: # Manual
            self.selected_app = self.manual_input.text().strip()
            if not self.selected_app:
                return
        self.accept()


class ModeManagerPage(QWidget):
    """Main Mode Manager page."""

    def __init__(self, dbus_handler: LotusDBusHandler, parent=None):
        super().__init__(parent)
        self.dbus = dbus_handler
        self.app_rules = {}
        self.selected_app = None
        self._icon_cache = {}
        self._path_cache = {}
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Left Sidebar (Expanded)
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(240)
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(15, 20, 15, 20)
        self.sidebar_layout.setSpacing(10)

        self.app_search = QLineEdit()
        self.app_search.setPlaceholderText(_("Search applications..."))
        self.app_search.textChanged.connect(self._filter_apps)
        self.sidebar_layout.addWidget(self.app_search)

        self.app_list = QListWidget()
        self.app_list.setIconSize(QSize(24, 24))
        self.app_list.itemClicked.connect(self._on_app_selected)
        self.sidebar_layout.addWidget(self.app_list)

        self.btn_add_app = QPushButton(_("+ Add Application"))
        self.btn_add_app.clicked.connect(self._on_add_app)
        self.sidebar_layout.addWidget(self.btn_add_app)

        self.layout.addWidget(self.sidebar_widget)

        # Right Content Area
        self.content_widget = QScrollArea()
        self.content_widget.setWidgetResizable(True)
        self.content_widget.setFrameShape(QFrame.NoFrame)
        
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(30, 20, 30, 30)
        self.main_layout.setSpacing(20)

        # 1. Global Mode Section (Dropdown)
        self.global_card = CardWidget(_("Global Mode Settings"))
        global_layout = QHBoxLayout()
        global_layout.addWidget(QLabel(_("Global Default Mode:")))
        self.combo_global_mode = QComboBox()
        global_modes = [
            MODE_OFF, MODE_SMOOTH, MODE_SLOW, MODE_HARDCORE,
            MODE_SURROUNDING, MODE_PREEDIT, MODE_EMOJI
        ]
        for m in global_modes:
            self.combo_global_mode.addItem(MODE_INFO[m]["title"], MODE_INFO[m]["title"])
            
        self.combo_global_mode.currentIndexChanged.connect(self._on_global_mode_changed)
        global_layout.addWidget(self.combo_global_mode)
        self.global_card.content_layout.addLayout(global_layout)
        self.main_layout.addWidget(self.global_card)

        # 2. Selected App Settings (Grid)
        self.app_settings_card = CardWidget(_("Application Specific Mode"))
        self.app_settings_layout = QVBoxLayout()
        
        # App Info Header
        self.app_header_layout = QHBoxLayout()
        self.app_icon_label = QLabel()
        self.app_icon_label.setFixedSize(48, 48)
        self.app_name_label = QLabel(_("Select an application"))
        self.app_name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.app_header_layout.addWidget(self.app_icon_label)
        self.app_header_layout.addWidget(self.app_name_label)
        self.app_header_layout.addStretch()
        self.app_settings_layout.addLayout(self.app_header_layout)
        self.app_settings_layout.addSpacing(10)

        # Grid for App Modes
        self.mode_grid = QGridLayout()
        self.mode_grid.setSpacing(10)
        self.mode_cards = {}
        
        grid_modes = [
            MODE_DEFAULT, MODE_OFF,
            MODE_SMOOTH, MODE_SLOW,
            MODE_HARDCORE, MODE_SURROUNDING,
            MODE_PREEDIT, MODE_EMOJI
        ]
        for i, m in enumerate(grid_modes):
            card = ModeCard(m)
            card.clicked.connect(self._on_app_mode_changed)
            self.mode_cards[m] = card
            self.mode_grid.addWidget(card, i // 2, i % 2)
            
        self.app_settings_layout.addLayout(self.mode_grid)
        self.app_settings_card.content_layout.addLayout(self.app_settings_layout)
        self.main_layout.addWidget(self.app_settings_card)
        self.main_layout.addStretch()

        # Initial visibility
        self.app_settings_card.setVisible(False)

        self.content_widget.setWidget(self.main_container)
        self.layout.addWidget(self.content_widget)

    def load_data(self):
        """Loads rules from config and global mode from DBus."""
        self.app_rules = {}
        if os.path.exists(APP_RULES_PATH):
            try:
                with open(APP_RULES_PATH, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        app, mode = line.split("=", 1)
                        self.app_rules[app] = int(mode)
            except Exception: pass

        # Sync Global Mode
        config = self.dbus.get_config()
        mode_str = config.get("values", {}).get("Mode", "Uinput (Smooth)")
        self.combo_global_mode.blockSignals(True)
        idx = self.combo_global_mode.findText(mode_str)
        if idx >= 0:
            self.combo_global_mode.setCurrentIndex(idx)
        self.combo_global_mode.blockSignals(False)
        
        self._populate_app_list()

    def _populate_app_list(self):
        self.app_list.clear()
        self._scan_desktop_files()
        apps_to_show = set(self.app_rules.keys())
        if self.selected_app:
            apps_to_show.add(self.selected_app)

        for app in sorted(apps_to_show):
            mode = self.app_rules.get(app, MODE_DEFAULT)
            mode_text = MODE_INFO.get(mode, MODE_INFO[MODE_SMOOTH])["title"]
            
            item = QListWidgetItem()
            item.setText(f"{app}\n{mode_text}")
            item.setData(Qt.UserRole, (app, mode))
            item.setIcon(self._resolve_icon(app))
            self.app_list.addItem(item)
            
            if app == self.selected_app:
                self.app_list.setCurrentItem(item)

    def _scan_desktop_files(self):
        paths = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        for p in paths:
            if not os.path.isdir(p): continue
            for f in os.listdir(p):
                if not f.endswith(".desktop"): continue
                try:
                    with open(os.path.join(p, f), "r") as df:
                        content = df.read()
                        exec_match = re.search(r"^Exec=([^ \n]+)", content, re.MULTILINE)
                        icon_match = re.search(r"^Icon=([^\n]+)", content, re.MULTILINE)
                        if exec_match:
                            binary_name = os.path.basename(exec_match.group(1))
                            if icon_match:
                                self._icon_cache[binary_name] = icon_match.group(1).strip()
                except Exception: continue

    def _resolve_icon(self, app_name):
        icon_name = self._icon_cache.get(app_name, app_name.lower())
        return QIcon.fromTheme(icon_name, QIcon.fromTheme("application-x-executable"))

    def _filter_apps(self, text):
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            item.setHidden(text.lower() not in item.text().split("\n")[0].lower())

    def _on_app_selected(self, item):
        app_name, mode = item.data(Qt.UserRole)
        self.selected_app = app_name
        self.current_app_mode = mode
        
        self.app_name_label.setText(app_name)
        self.app_icon_label.setPixmap(self._resolve_icon(app_name).pixmap(48, 48))
        self.app_settings_card.setVisible(True)
        self._update_mode_cards()

    def _on_global_mode_changed(self, index):
        mode_text = self.combo_global_mode.currentText()
        config = self.dbus.get_config()
        config["values"]["Mode"] = mode_text
        self.dbus.set_config(config)
        self._notify_changed()

    def _on_app_mode_changed(self, mode):
        self.current_app_mode = mode
        if mode == MODE_DEFAULT:
            if self.selected_app in self.app_rules:
                del self.app_rules[self.selected_app]
        else:
            self.app_rules[self.selected_app] = mode
        
        self.save_data(quiet=True)
        self._update_mode_cards()
        self._populate_app_list()
        self._notify_changed()

    def _update_mode_cards(self):
        for m, card in self.mode_cards.items():
            card.selected = (m == self.current_app_mode)
            card.update_style()

    def _on_add_app(self):
        dialog = AddAppDialog(self)
        if dialog.exec():
            new_app = dialog.selected_app
            if new_app not in self.app_rules:
                self.app_rules[new_app] = MODE_SMOOTH
            self.selected_app = new_app
            self.save_data(quiet=True)
            self._populate_app_list()
            self._notify_changed()

    def _notify_changed(self):
        main_win = self.window()
        if hasattr(main_win, "on_changed"):
            main_win.on_changed()

    def is_modified_from_default(self):
        original_rules = {}
        if os.path.exists(APP_RULES_PATH):
            try:
                with open(APP_RULES_PATH, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or "=" not in line: continue
                        app, mode = line.split("=", 1)
                        original_rules[app] = int(mode)
            except Exception: pass
        return self.app_rules != original_rules

    def save_data(self, quiet=False):
        try:
            os.makedirs(os.path.dirname(APP_RULES_PATH), exist_ok=True)
            with open(APP_RULES_PATH, "w") as f:
                f.write("# Lotus Per-App Configuration\n")
                for app, mode in sorted(self.app_rules.items()):
                    f.write(f"{app}={mode}\n")
        except Exception as e:
            print(f"Error saving app rules: {e}")

    def restore_defaults(self):
        self.load_data()
