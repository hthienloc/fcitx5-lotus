/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#ifndef _LOTUS_CONFIG_EDITOR_EDITOR_H_
#define _LOTUS_CONFIG_EDITOR_EDITOR_H_

#include <fcitxqtconfiguiwidget.h>
#include <QCheckBox>
#include <QComboBox>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QPushButton>
#include <QStackedWidget>

namespace fcitx::lotus {

    class LotusConfigEditor : public FcitxQtConfigUIWidget {
        Q_OBJECT
      public:
        explicit LotusConfigEditor(QWidget* parent = nullptr);

        QString title() override;

        QString icon() override;

        void load() override;

        void save() override;

      private Q_SLOTS:
        void onSidebarRowChanged(int row);

      private:
        QWidget* createGeneralPage();
        QWidget* createTypingPage();
        QWidget* createFeaturesPage();
        QWidget* createIntegrationPage();
        QWidget* createProfilesPage();
        void     setupConnections();
        void     setupChoiceSources();
        void     syncProfilePreview();
        bool     openSubConfig(const QString& path) const;

        QListWidget*   sidebar_;
        QStackedWidget* stacked_;

        QComboBox* mode_;
        QComboBox* inputMethod_;
        QComboBox* outputCharset_;

        QCheckBox* spellCheck_;
        QCheckBox* enableMacro_;
        QCheckBox* capitalizeMacro_;
        QCheckBox* autoNonVnRestore_;
        QCheckBox* modernStyle_;
        QCheckBox* freeMarking_;
        QCheckBox* ddFreeStyle_;
        QCheckBox* fixUinputWithAck_;
        QCheckBox* useLotusIcons_;

        QPushButton* macroEditor_;
        QPushButton* customKeymap_;
        QComboBox*   profilePreset_;
        QLabel*      profileDescription_;
        QPushButton* applyProfile_;

        QLineEdit* modeMenuKey_;
    };

} // namespace fcitx::lotus

#endif
