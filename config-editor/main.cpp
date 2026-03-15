/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "main.h"
#include "editor.h"

namespace fcitx::lotus {

    LotusConfigEditorPlugin::LotusConfigEditorPlugin(QObject* parent) : FcitxQtConfigUIPlugin(parent) {}

    FcitxQtConfigUIWidget* LotusConfigEditorPlugin::create(const QString& key) {
        if (key == "lotus") {
            auto* editor = new LotusConfigEditor; //NOLINT
            editor->load();
            return editor;
        }
        return nullptr;
    }

} // namespace fcitx::lotus
