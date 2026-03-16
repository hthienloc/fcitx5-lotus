# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Reusable UI components.
Uses system's libxkbcommon to natively resolve XKB keysym names,
convert keysyms to Unicode, and mathematically handle Shift modifiers.
"""

import ctypes
import ctypes.util
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal

# Tải thư viện libxkbcommon trực tiếp từ hệ thống Linux
libxkb = None
libxkb_path = ctypes.util.find_library("xkbcommon")
if libxkb_path:
    try:
        libxkb = ctypes.CDLL(libxkb_path)

        # Hàm lấy tên phím XKB (vd: exclam, Return, space)
        libxkb.xkb_keysym_get_name.argtypes = [
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        libxkb.xkb_keysym_get_name.restype = ctypes.c_int

        # Hàm check chữ hoa của XKB
        libxkb.xkb_keysym_to_lower.argtypes = [ctypes.c_uint32]
        libxkb.xkb_keysym_to_lower.restype = ctypes.c_uint32

        # Hàm chuyển keysym sang ký tự Unicode chuẩn
        libxkb.xkb_keysym_to_utf32.argtypes = [ctypes.c_uint32]
        libxkb.xkb_keysym_to_utf32.restype = ctypes.c_uint32

    except Exception as e:
        print(f"Failed to load libxkbcommon: {e}")


class HotkeyCaptureWidget(QPushButton):
    """A button that captures keystrokes to set an Fcitx5-compatible hotkey."""

    textChanged = Signal(str)

    def __init__(self, current_key="", parent=None):
        super().__init__(parent)
        self.setText(current_key if current_key else "None")
        self.setCheckable(True)
        self.current_key = current_key

    def keyPressEvent(self, event):
        """Captures the key press when button is checked."""
        if not self.isChecked():
            super().keyPressEvent(event)
            return

        key_code = event.key()

        # Bỏ qua nếu người dùng chỉ bấm các phím Modifier
        if key_code in (
            Qt.Key_Control,
            Qt.Key_Shift,
            Qt.Key_Alt,
            Qt.Key_Meta,
            Qt.Key_unknown,
        ):
            return

        # 1. Lấy Base Key trực tiếp bằng XKB Keysym
        keysym = event.nativeVirtualKey()
        base_key = ""
        is_upper = False
        is_symbol = False

        if libxkb and keysym > 0:
            buf = ctypes.create_string_buffer(64)
            if libxkb.xkb_keysym_get_name(keysym, buf, 64) > 0:
                base_key = buf.value.decode("utf-8")

            # Dùng XKB check chữ hoa
            lower_sym = libxkb.xkb_keysym_to_lower(keysym)
            if lower_sym != keysym:
                is_upper = True

            # Dùng XKB chuyển sang ký tự Unicode để biết có phải là số/dấu/symbol không
            utf32 = libxkb.xkb_keysym_to_utf32(keysym)
            if utf32 > 0:
                char = chr(utf32)
                # Nếu là ký tự có thể in ra nhưng KHÔNG PHẢI chữ cái và KHÔNG PHẢI dấu cách
                if not char.isalpha() and not char.isspace() and char.isprintable():
                    is_symbol = True

        # Fallback trong trường hợp cực hiếm Linux không load được libxkbcommon
        if not base_key:
            from PySide6.QtGui import QKeySequence

            base_key = QKeySequence(key_code).toString()
            if len(base_key) == 1:
                if base_key.isupper():
                    is_upper = True
                elif not base_key.isalpha() and not base_key.isspace():
                    is_symbol = True

        # 2. Xử lý Modifiers theo chuẩn cú pháp Fcitx5
        mods = []
        if event.modifiers() & Qt.ControlModifier:
            mods.append("Control")
        if event.modifiers() & Qt.AltModifier:
            mods.append("Alt")
        if event.modifiers() & Qt.MetaModifier:
            mods.append("Super")

        # 3. Thông minh triệt tiêu Shift nếu phím mang bản chất viết hoa HOẶC là dấu câu/số/symbol
        if event.modifiers() & Qt.ShiftModifier:
            if not (is_upper or is_symbol):
                mods.append("Shift")

        mods.append(base_key)
        self.current_key = "+".join(mods)

        self.setText(self.current_key)
        self.setChecked(False)
        self.textChanged.emit(self.current_key)
