/*
 * SPDX-FileCopyrightText: 2026 Lotus Contributors
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef _LOTUS_CONFIG_EDITOR_MAIN_H_
#define _LOTUS_CONFIG_EDITOR_MAIN_H_

#include <fcitxqtconfiguiplugin.h>

namespace fcitx::lotus {

class LotusConfigEditorPlugin : public FcitxQtConfigUIPlugin {
    Q_OBJECT
  public:
    Q_PLUGIN_METADATA(IID FcitxQtConfigUIFactoryInterface_iid FILE "lotus-editor.json")

    explicit LotusConfigEditorPlugin(QObject* parent = nullptr);
    FcitxQtConfigUIWidget* create(const QString& key) override;
};

} // namespace fcitx::lotus

#endif
