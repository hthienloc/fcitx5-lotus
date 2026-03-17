# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import subprocess
import getpass
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, 
                             QPushButton, QFileDialog, QMessageBox, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from i18n import _

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Root layout for this widget
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area to handle overcrowding
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")
        
        content_widget = QWidget()
        content_widget.setObjectName("AboutContent")
        # Use ID selector and explicitly include button styles to ensure they are applied
        content_widget.setStyleSheet("""
            #AboutContent { background-color: #1a1a1a; }
            QPushButton#Primary {
                background-color: #35a2e1;
                color: #ffffff;
                font-weight: 600;
                border-radius: 6px;
            }
            QPushButton#Primary:hover {
                background-color: #4db1e4;
            }
            QPushButton#Primary:pressed {
                background-color: #252525;
            }
        """)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Logo/Icon 
        try:
            pixmap = QIcon.fromTheme("fcitx-lotus").pixmap(80, 80)
            if pixmap.isNull():
                logo = QLabel("🪷")
                logo.setStyleSheet("font-size: 64px; margin-bottom: 5px;")
            else:
                logo = QLabel()
                logo.setPixmap(pixmap)
                logo.setStyleSheet("margin-bottom: 5px;")
        except Exception:
            logo = QLabel("🪷")
            logo.setStyleSheet("font-size: 64px; margin-bottom: 5px;")
            
        layout.addWidget(logo, alignment=Qt.AlignCenter)

        title = QLabel("Fcitx5 Lotus")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #ffffff; margin-top: -5px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        version = QLabel(_("Version 1.4.2 (Stable)"))
        version.setStyleSheet("color: #35a2e1; font-size: 13px; font-weight: 600; background-color: #1e3a4f; padding: 4px 12px; border-radius: 12px;")
        layout.addWidget(version, alignment=Qt.AlignCenter)

        desc = QLabel(_("A state-of-the-art Vietnamese input method engine for Linux, designed for speed, stability, and a premium user experience."))
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("max-width: 900px; color: #b0b0b0; font-size: 15px; line-height: 1.6;")
        layout.addWidget(desc, alignment=Qt.AlignCenter)

        # GitHub Project Link
        github_link = QLabel('<a href="https://github.com/LotusInputMethod/fcitx5-lotus" style="color: #35a2e1; text-decoration: none;">github.com/LotusInputMethod/fcitx5-lotus</a>')
        github_link.setOpenExternalLinks(True)
        github_link.setStyleSheet("font-size: 13px;")
        layout.addWidget(github_link, alignment=Qt.AlignCenter)

        # Support Buttons Row
        support_layout = QHBoxLayout()
        support_layout.setSpacing(15)
        support_layout.setAlignment(Qt.AlignCenter)
        
        btn_bug = QPushButton(_("Report Bug"))
        btn_bug.setObjectName("Primary")
        btn_bug.setFixedWidth(200)
        btn_bug.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/LotusInputMethod/fcitx5-lotus/issues/new?template=bug_report.yml")))
        
        btn_feature = QPushButton(_("Request Feature"))
        btn_feature.setObjectName("Primary")
        btn_feature.setFixedWidth(200)
        btn_feature.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/LotusInputMethod/fcitx5-lotus/issues/new?template=feature_request.yml")))

        support_layout.addWidget(btn_bug)
        support_layout.addWidget(btn_feature)
        layout.addLayout(support_layout)

        # Export Log Button
        self.btn_export_log = QPushButton(_("Export Debug Logs"))
        self.btn_export_log.setObjectName("Primary")
        self.btn_export_log.setFixedWidth(415) # 200 + 200 + 15 spacing
        self.btn_export_log.clicked.connect(self._on_export_logs)
        layout.addWidget(self.btn_export_log, alignment=Qt.AlignCenter)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #2d2d2d; margin: 10px 0;")
        layout.addWidget(line)

        # Credits Section
        credits_title = QLabel(_("DEVELOPED BY"))
        credits_title.setStyleSheet("color: #666666; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-bottom: 5px;")
        layout.addWidget(credits_title, alignment=Qt.AlignCenter)

        # Authors List - Single Column
        authors_layout = QVBoxLayout()
        authors_layout.setSpacing(12)
        
        authors_data = [
            ("Nguyễn Hoàng Kỳ", "https://github.com/nhktmdzhg"),
            ("Nguyễn Hồng Hiệp", "https://github.com/justanoobcoder"),
            ("Đặng Quang Hiển", "https://github.com/Miho1254"),
            ("Zebra2711", "https://github.com/Zebra2711"),
            ("Huỳnh Thiện Lộc", "https://github.com/hthienloc"),
        ]
        
        for name, profile_url in authors_data:
            author_link = QLabel(f'<a href="{profile_url}" style="color: #ffffff; text-decoration: none;">{name}</a>')
            author_link.setOpenExternalLinks(True)
            author_link.setCursor(Qt.PointingHandCursor)
            author_link.setStyleSheet("""
                QLabel { 
                    font-size: 14px; 
                    font-weight: 600; 
                    padding: 4px 0;
                }
                QLabel:hover {
                    color: #35a2e1;
                }
            """)
            authors_layout.addWidget(author_link, alignment=Qt.AlignCenter)

        layout.addLayout(authors_layout)
        layout.addStretch()

        # Footer
        footer_line = QFrame()
        footer_line.setFrameShape(QFrame.HLine)
        footer_line.setStyleSheet("background-color: #2d2d2d;")
        layout.addWidget(footer_line)

        license_info = QLabel(_("Licensed under the GNU General Public License v3.0"))
        license_info.setStyleSheet("color: #555555; font-size: 11px;")
        layout.addWidget(license_info, alignment=Qt.AlignCenter)

        scroll.setWidget(content_widget)
        root_layout.addWidget(scroll)

    def _on_export_logs(self):
        # Using names that don't conflict with _
        save_dialog_result = QFileDialog.getSaveFileName(
            self, _("Save Debug Log"), 
            os.path.expanduser("~/fcitx5-lotus-debug.log"),
            "Log Files (*.log);;All Files (*)"
        )
        
        if not save_dialog_result or not save_dialog_result[0]:
            return
            
        export_filename = save_dialog_result[0]

        try:
            with open(export_filename, 'w') as log_output_file:
                log_output_file.write("=== Fcitx5 Lotus Debug Log Export ===\n")
                log_output_file.write(f"Version: 1.4.2\n")
                log_output_file.write(f"User: {getpass.getuser()}\n")
                log_output_file.write("--------------------------------------\n\n")

                system_log_path = "/tmp/fcitx5-lotus-server.log"
                log_output_file.write(f"--- Server Log ({system_log_path}) ---\n")
                if os.path.exists(system_log_path):
                    with open(system_log_path, 'r') as src_log:
                        log_output_file.write(src_log.read())
                else:
                    log_output_file.write("Log file not found.\n")
                log_output_file.write("\n\n")

                log_output_file.write("--- Systemd Journal (fcitx5-lotus-server) ---\n")
                try:
                    current_sys_user = getpass.getuser()
                    process_capture = subprocess.run(
                        ['journalctl', f'-u', f'fcitx5-lotus-server@{current_sys_user}.service', '--no-pager', '-n', '200'],
                        capture_output=True, text=True
                    )
                    log_output_file.write(process_capture.stdout if process_capture.stdout else "No journal entries found.\n")
                except Exception as journal_ex:
                    log_output_file.write(f"Error collecting journal: {str(journal_ex)}\n")
                
                log_output_file.write("\n\n--- End of Log ---\n")

            QMessageBox.information(self, _("Success"), _("Debug logs exported successfully to:\n") + export_filename)
        except Exception as export_ex:
            QMessageBox.critical(self, _("Error"), _("Failed to export logs:\n") + str(export_ex))
