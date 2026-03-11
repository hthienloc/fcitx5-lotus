/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#ifndef _LOTUS_MACRO_EDITOR_MAIN_H_
#define _LOTUS_MACRO_EDITOR_MAIN_H_

#include <fcitxqtconfiguiplugin.h>

namespace fcitx::lotus {

    /**
     * @brief Fcitx5 plugin for the Lotus macro editor.
     *
     * Registers and creates the MacroEditor config UI widget.
     */
    class MacroEditorPlugin : public FcitxQtConfigUIPlugin {
        Q_OBJECT
      public:
        /**
         * @brief Fcitx5 plugin metadata.
         */
        Q_PLUGIN_METADATA(IID FcitxQtConfigUIFactoryInterface_iid FILE "macro-editor.json")

        /**
         * @brief Constructs a macro editor plugin.
         * @param parent Parent object.
         */
        explicit MacroEditorPlugin(QObject* parent = nullptr);

        /**
         * @brief Creates a macro editor widget.
         * @param key Configuration key (expects "macro").
         * @return MacroEditor widget or nullptr.
         */
        FcitxQtConfigUIWidget* create(const QString& key) override;
    };
} // namespace fcitx::lotus

#endif
