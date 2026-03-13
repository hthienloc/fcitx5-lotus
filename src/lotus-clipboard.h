/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#ifndef _FCITX5_LOTUS_CLIPBOARD_H_
#define _FCITX5_LOTUS_CLIPBOARD_H_

#include <fcitx/addonmanager.h>
#include <fcitx/inputcontext.h>
#include <string>

namespace fcitx {

class ClipboardManager {
public:
    ClipboardManager(AddonManager* addonManager);
    
    std::string primary(InputContext* ic);
    std::string clipboard(InputContext* ic);
    
    void setPrimary(const std::string& str);
    void setClipboard(const std::string& str);

private:
    AddonInstance* clipboardAddon_ = nullptr;
};

} // namespace fcitx

#endif // _FCITX5_LOTUS_CLIPBOARD_H_
