/*
 * SPDX-FileCopyrightText: 2026 Lotus Contributors
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef _LOTUS_CONFIG_EDITOR_EDITOR_H_
#define _LOTUS_CONFIG_EDITOR_EDITOR_H_

#include <fcitxqtconfiguiwidget.h>
#include <QCheckBox>
#include <QComboBox>
#include <QKeySequenceEdit>
#include <QListWidget>
#include <QMap>
#include <QStackedWidget>

namespace fcitx::lotus {

class LotusConfigEditor : public FcitxQtConfigUIWidget {
    Q_OBJECT
  public:
    explicit LotusConfigEditor(QWidget* parent = nullptr);

    QString title() override;
    QString icon() override;
    void    load() override;
    void    save() override;

  private:
    std::string configPath() const;
    void     buildUI();
    QWidget* buildSidebar();
    QWidget* buildGeneralPage();
    QWidget* buildTypingPage();
    QWidget* buildMacroPage();
    QWidget* buildShortcutsPage();
    QWidget* buildAppearancePage();

    void setupConnections();

    QListWidget*   sidebar_;
    QStackedWidget* pageStack_;
    QMap<int, int> sidebarRowToPageIndex_;

    QComboBox*       mode_;
    QComboBox*       inputMethod_;
    QComboBox*       outputCharset_;
    QCheckBox*       useLotusIcons_;
    QKeySequenceEdit* modeMenuKey_;

    QCheckBox* spellCheck_;
    QCheckBox* autoNonVnRestore_;
    QCheckBox* ddFreeStyle_;
    QCheckBox* modernStyle_;
    QCheckBox* freeMarking_;
    QCheckBox* fixUinputWithAck_;

    QCheckBox* enableMacro_;
    QCheckBox* capitalizeMacro_;
};

} // namespace fcitx::lotus

#endif
