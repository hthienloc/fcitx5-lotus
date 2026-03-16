/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "editor.h"
#include "lotus-config.h"
#include <fcitx-config/iniparser.h>
#include <fcitx-utils/i18n.h>
#include <QDesktopServices>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QMessageBox>
#include <QStringList>
#include <QUrl>
#include <QVBoxLayout>

namespace fcitx::lotus {

    namespace {

        constexpr auto* MacroSubConfigPath  = "lotus-macro";
        constexpr auto* KeymapSubConfigPath = "custom_keymap";

        QString keyListToText(const std::vector<fcitx::Key>& keyList) {
            QStringList keyLabels;
            keyLabels.reserve(static_cast<int>(keyList.size()));

            for (const auto& key : keyList) {
                keyLabels.push_back(QString::fromStdString(key.toString()));
            }

            return keyLabels.join(", ");
        }

        std::vector<fcitx::Key> textToKeyList(const QString& text) {
            std::vector<fcitx::Key> keyList;

            for (const auto& keyLabel : text.split(",", Qt::SkipEmptyParts)) {
                const auto trimmed = keyLabel.trimmed();
                if (!trimmed.isEmpty()) {
                    keyList.emplace_back(trimmed.toStdString());
                }
            }

            return keyList;
        }

        void syncComboItems(QComboBox* combo, const std::vector<std::string>& values) {
            combo->clear();
            for (const auto& value : values) {
                combo->addItem(QString::fromStdString(value));
            }
        }

        const std::vector<std::string>& modeSchemaOptions() {
            static const fcitx::ModeListAnnotation annotation;
            return annotation.list();
        }

        const std::vector<std::string> kFallbackInputMethods = {"Telex", "VNI", "VIQR", "Custom"};
        const std::vector<std::string> kFallbackCharsets     = {"Unicode", "Unicode Compound", "TCVN3", "VNI", "VIQR"};

    } // namespace

    LotusConfigEditor::LotusConfigEditor(QWidget* parent) :
        FcitxQtConfigUIWidget(parent),
        sidebar_(new QListWidget(this)),
        stacked_(new QStackedWidget(this)),
        mode_(new QComboBox(this)),
        inputMethod_(new QComboBox(this)),
        outputCharset_(new QComboBox(this)),
        spellCheck_(new QCheckBox(_("Enable Spell Check"), this)),
        enableMacro_(new QCheckBox(_("Enable Macro"), this)),
        capitalizeMacro_(new QCheckBox(_("Capitalize Macro"), this)),
        autoNonVnRestore_(new QCheckBox(_("Auto Restore Keys With Invalid Words"), this)),
        modernStyle_(new QCheckBox(_("Use oà, uý (Instead Of òa, úy)"), this)),
        freeMarking_(new QCheckBox(_("Allow Type With More Freedom"), this)),
        ddFreeStyle_(new QCheckBox(_("Allow dd To Produce đ When Auto Restore Keys With Invalid Words Is On"), this)),
        fixUinputWithAck_(new QCheckBox(_("Fix Uinput Mode With Ack"), this)),
        useLotusIcons_(new QCheckBox(_("Use Lotus Status Icons"), this)),
        macroEditor_(new QPushButton(_("Macro"), this)),
        customKeymap_(new QPushButton(_("Custom Keymap"), this)),
        profilePreset_(new QComboBox(this)),
        profileDescription_(new QLabel(this)),
        applyProfile_(new QPushButton(_("Apply Profile"), this)),
        modeMenuKey_(new QLineEdit(this)) {
        setMinimumSize(760, 520);

        auto* mainLayout = new QHBoxLayout(this);

        sidebar_->setFixedWidth(220);
        sidebar_->setIconSize(QSize(20, 20));
        sidebar_->setSpacing(4);
        sidebar_->setStyleSheet(
            "QListWidget { border: 1px solid palette(mid); border-radius: 6px; padding: 6px; }"
            "QListWidget::item { border-radius: 4px; padding: 8px; margin: 1px 0; }"
            "QListWidget::item:selected { background-color: #3daee9; color: white; }");

        sidebar_->addItem(new QListWidgetItem(QIcon::fromTheme("preferences-system"), _("General")));
        sidebar_->addItem(new QListWidgetItem(QIcon::fromTheme("input-keyboard"), _("Typing")));
        sidebar_->addItem(new QListWidgetItem(QIcon::fromTheme("preferences-plugin"), _("Features")));
        sidebar_->addItem(new QListWidgetItem(QIcon::fromTheme("emblem-favorite"), _("Profiles")));
        sidebar_->addItem(new QListWidgetItem(QIcon::fromTheme("settings-configure"), _("Integration")));

        setupChoiceSources();

        stacked_->addWidget(createGeneralPage());
        stacked_->addWidget(createTypingPage());
        stacked_->addWidget(createFeaturesPage());
        stacked_->addWidget(createProfilesPage());
        stacked_->addWidget(createIntegrationPage());

        mainLayout->addWidget(sidebar_);
        mainLayout->addWidget(stacked_, 1);

        setupConnections();
        sidebar_->setCurrentRow(0);
    }

    QString LotusConfigEditor::title() {
        return _("Lotus");
    }

    QString LotusConfigEditor::icon() {
        return "fcitx-lotus";
    }

    void LotusConfigEditor::setupChoiceSources() {
        mode_->setEditable(false);
        syncComboItems(mode_, modeSchemaOptions());

        inputMethod_->setEditable(true);
        outputCharset_->setEditable(true);

        syncComboItems(inputMethod_, kFallbackInputMethods);
        syncComboItems(outputCharset_, kFallbackCharsets);
    }

    QWidget* LotusConfigEditor::createGeneralPage() {
        auto* page   = new QWidget(this);
        auto* layout = new QVBoxLayout(page);
        auto* form   = new QFormLayout();

        form->addRow(_("Mode"), mode_);
        form->addRow(_("Input Method"), inputMethod_);

        layout->addLayout(form);
        layout->addStretch();
        return page;
    }

    QWidget* LotusConfigEditor::createTypingPage() {
        auto* page   = new QWidget(this);
        auto* layout = new QVBoxLayout(page);

        layout->addWidget(modernStyle_);
        layout->addWidget(freeMarking_);
        layout->addWidget(ddFreeStyle_);
        layout->addWidget(autoNonVnRestore_);
        layout->addWidget(fixUinputWithAck_);
        layout->addStretch();

        return page;
    }

    QWidget* LotusConfigEditor::createFeaturesPage() {
        auto* page   = new QWidget(this);
        auto* layout = new QVBoxLayout(page);
        auto* form   = new QFormLayout();

        form->addRow(_("Output Charset"), outputCharset_);
        layout->addLayout(form);

        layout->addWidget(spellCheck_);
        layout->addWidget(enableMacro_);
        layout->addWidget(capitalizeMacro_);
        layout->addStretch();
        return page;
    }

    QWidget* LotusConfigEditor::createProfilesPage() {
        auto* page   = new QWidget(this);
        auto* layout = new QVBoxLayout(page);

        profilePreset_->addItem(_("Balanced (Default)"), "balanced");
        profilePreset_->addItem(_("Compatibility (Stable apps)"), "compatibility");
        profilePreset_->addItem(_("Performance (Fast input)"), "performance");

        profileDescription_->setWordWrap(true);
        profileDescription_->setStyleSheet("QLabel { color: palette(mid); }");

        auto* form = new QFormLayout();
        form->addRow(_("Profile"), profilePreset_);

        layout->addLayout(form);
        layout->addWidget(profileDescription_);
        layout->addWidget(applyProfile_);
        layout->addStretch();

        syncProfilePreview();
        return page;
    }

    QWidget* LotusConfigEditor::createIntegrationPage() {
        auto* page   = new QWidget(this);
        auto* layout = new QVBoxLayout(page);
        auto* form   = new QFormLayout();

        modeMenuKey_->setPlaceholderText(_("Example: grave, Control+grave"));

        form->addRow(_("Mode Menu Hotkey"), modeMenuKey_);

        layout->addWidget(useLotusIcons_);
        layout->addLayout(form);

        macroEditor_->setIcon(QIcon::fromTheme("document-edit"));
        customKeymap_->setIcon(QIcon::fromTheme("input-keyboard-virtual"));
        macroEditor_->setStyleSheet("QPushButton { text-align: left; padding: 6px 10px; }");
        customKeymap_->setStyleSheet("QPushButton { text-align: left; padding: 6px 10px; }");

        layout->addWidget(new QLabel(_("Open sub-configuration:"), this));
        layout->addWidget(macroEditor_);
        layout->addWidget(customKeymap_);
        layout->addStretch();

        return page;
    }

    void LotusConfigEditor::syncProfilePreview() {
        const auto preset = profilePreset_->currentData().toString();
        if (preset == "compatibility") {
            profileDescription_->setText(_("Recommended for apps with strict input behavior. Uses Uinput (Slow), enables restore/fix options, and keeps macro disabled."));
            return;
        }
        if (preset == "performance") {
            profileDescription_->setText(_("Optimized for speed. Uses Uinput (Smooth), enables macro workflow, and keeps correction options lightweight."));
            return;
        }
        profileDescription_->setText(_("Balanced defaults for common Linux workflows."));
    }

    bool LotusConfigEditor::openSubConfig(const QString& path) const {
        const QUrl url(QStringLiteral("fcitx://config/addon/lotus/") + path);
        if (QDesktopServices::openUrl(url)) {
            return true;
        }

        QMessageBox::warning(
            const_cast<LotusConfigEditor*>(this), _("Unable to open sub-configuration"),
            _("Could not open Lotus sub-configuration. Ensure fcitx5-configtool is available."));
        return false;
    }

    void LotusConfigEditor::setupConnections() {
        connect(sidebar_, &QListWidget::currentRowChanged, this, &LotusConfigEditor::onSidebarRowChanged);

        connect(mode_, &QComboBox::currentTextChanged, this, [this]() { emit changed(true); });
        connect(inputMethod_, &QComboBox::currentTextChanged, this, [this]() { emit changed(true); });
        connect(outputCharset_, &QComboBox::currentTextChanged, this, [this]() { emit changed(true); });
        connect(modeMenuKey_, &QLineEdit::textChanged, this, [this]() { emit changed(true); });

        connect(spellCheck_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(enableMacro_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(capitalizeMacro_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(autoNonVnRestore_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(modernStyle_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(freeMarking_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(ddFreeStyle_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(fixUinputWithAck_, &QCheckBox::toggled, this, [this]() { emit changed(true); });
        connect(useLotusIcons_, &QCheckBox::toggled, this, [this]() { emit changed(true); });

        connect(profilePreset_, &QComboBox::currentIndexChanged, this, [this]() { syncProfilePreview(); });
        connect(applyProfile_, &QPushButton::clicked, this, [this]() {
            const auto preset = profilePreset_->currentData().toString();
            if (preset == "compatibility") {
                mode_->setCurrentText("Uinput (Slow)");
                enableMacro_->setChecked(false);
                autoNonVnRestore_->setChecked(true);
                fixUinputWithAck_->setChecked(true);
            } else if (preset == "performance") {
                mode_->setCurrentText("Uinput (Smooth)");
                enableMacro_->setChecked(true);
                autoNonVnRestore_->setChecked(false);
                fixUinputWithAck_->setChecked(false);
            } else {
                mode_->setCurrentText("Uinput (Smooth)");
                enableMacro_->setChecked(true);
                autoNonVnRestore_->setChecked(true);
                fixUinputWithAck_->setChecked(false);
            }
            emit changed(true);
        });

        connect(macroEditor_, &QPushButton::clicked, this, [this]() { openSubConfig(MacroSubConfigPath); });
        connect(customKeymap_, &QPushButton::clicked, this, [this]() { openSubConfig(KeymapSubConfigPath); });
    }

    void LotusConfigEditor::onSidebarRowChanged(int row) {
        if (row >= 0 && row < stacked_->count()) {
            stacked_->setCurrentIndex(row);
        }
    }

    void LotusConfigEditor::load() {
        fcitx::lotusConfig config;
        fcitx::readAsIni(config, "conf/lotus.conf");

        auto inputMethods = config.inputMethod.annotation().list();
        if (inputMethods.empty()) {
            inputMethods = kFallbackInputMethods;
        }
        syncComboItems(inputMethod_, inputMethods);

        auto charsets = config.outputCharset.annotation().list();
        if (charsets.empty()) {
            charsets = kFallbackCharsets;
        }
        syncComboItems(outputCharset_, charsets);

        mode_->setCurrentText(QString::fromStdString(config.mode.value()));
        inputMethod_->setCurrentText(QString::fromStdString(config.inputMethod.value()));
        outputCharset_->setCurrentText(QString::fromStdString(config.outputCharset.value()));

        spellCheck_->setChecked(config.spellCheck.value());
        enableMacro_->setChecked(config.enableMacro.value());
        capitalizeMacro_->setChecked(config.capitalizeMacro.value());
        autoNonVnRestore_->setChecked(config.autoNonVnRestore.value());
        modernStyle_->setChecked(config.modernStyle.value());
        freeMarking_->setChecked(config.freeMarking.value());
        ddFreeStyle_->setChecked(config.ddFreeStyle.value());
        fixUinputWithAck_->setChecked(config.fixUinputWithAck.value());
        useLotusIcons_->setChecked(config.useLotusIcons.value());

        modeMenuKey_->setText(keyListToText(config.modeMenuKey.value()));

        emit changed(false);
    }

    void LotusConfigEditor::save() {
        fcitx::lotusConfig config;
        fcitx::readAsIni(config, "conf/lotus.conf");

        config.mode.setValue(mode_->currentText().toStdString());
        config.inputMethod.setValue(inputMethod_->currentText().toStdString());
        config.outputCharset.setValue(outputCharset_->currentText().toStdString());

        config.spellCheck.setValue(spellCheck_->isChecked());
        config.enableMacro.setValue(enableMacro_->isChecked());
        config.capitalizeMacro.setValue(capitalizeMacro_->isChecked());
        config.autoNonVnRestore.setValue(autoNonVnRestore_->isChecked());
        config.modernStyle.setValue(modernStyle_->isChecked());
        config.freeMarking.setValue(freeMarking_->isChecked());
        config.ddFreeStyle.setValue(ddFreeStyle_->isChecked());
        config.fixUinputWithAck.setValue(fixUinputWithAck_->isChecked());
        config.useLotusIcons.setValue(useLotusIcons_->isChecked());

        config.modeMenuKey.setValue(textToKeyList(modeMenuKey_->text()));

        fcitx::safeSaveAsIni(config, "conf/lotus.conf");
        emit changed(false);
    }

} // namespace fcitx::lotus
