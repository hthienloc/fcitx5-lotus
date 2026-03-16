/*
 * SPDX-FileCopyrightText: 2026 Lotus Contributors
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "main.h"
#include "editor.h"

namespace fcitx::lotus {

LotusConfigEditorPlugin::LotusConfigEditorPlugin(QObject* parent) : FcitxQtConfigUIPlugin(parent) {}

FcitxQtConfigUIWidget* LotusConfigEditorPlugin::create(const QString& key) {
    // Different Fcitx frontends/entry points may pass slightly different keys
    // for addon-level config UI. Accept common aliases to avoid fallback to
    // the generic auto-generated page.
    if (key.isEmpty() || key == "lotus" || key == "main" || key == "config") {
        auto* editor = new LotusConfigEditor; //NOLINT
        editor->load();
        return editor;
    }
    return nullptr;
}

} // namespace fcitx::lotus
