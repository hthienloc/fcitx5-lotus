/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "lotus-clipboard.h"
#include <clipboard_public.h>

namespace fcitx {

ClipboardManager::ClipboardManager(AddonManager* addonManager) {
    if (addonManager != nullptr) {
        clipboardAddon_ = addonManager->addon("clipboard", true);
    }
}

std::string ClipboardManager::primary(InputContext* ic) {
    if (clipboardAddon_ && ic) {
        return clipboardAddon_->call<IClipboard::primary>(ic);
    }
    return "";
}

std::string ClipboardManager::clipboard(InputContext* ic) {
    if (clipboardAddon_ && ic) {
        return clipboardAddon_->call<IClipboard::clipboard>(ic);
    }
    return "";
}

void ClipboardManager::setPrimary(const std::string& str) {
    if (clipboardAddon_) {
        clipboardAddon_->call<IClipboard::setPrimary>("fcitx5-lotus", str);
    }
}

void ClipboardManager::setClipboard(const std::string& str) {
    if (clipboardAddon_) {
        clipboardAddon_->call<IClipboard::setClipboard>("fcitx5-lotus", str);
    }
}

} // namespace fcitx
