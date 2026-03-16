/*
 * SPDX-FileCopyrightText: 2026 Lotus Contributors
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

// NOLINTBEGIN(cppcoreguidelines-owning-memory)
#include "editor.h"

#include "lotus-config.h"
#include <fcitx-config/iniparser.h>
#include <fcitx-utils/i18n.h>
#include <QFormLayout>
#include <QFrame>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QScrollArea>
#include <QVBoxLayout>

#if LOTUS_USE_MODERN_FCITX_API
#include <fcitx-utils/standardpaths.h>
#else
#include <fcitx-utils/standardpath.h>
#endif

namespace fcitx::lotus {

LotusConfigEditor::LotusConfigEditor(QWidget* parent) :
    FcitxQtConfigUIWidget(parent), mode_(new QComboBox(this)), inputMethod_(new QComboBox(this)), outputCharset_(new QComboBox(this)),
    useLotusIcons_(new QCheckBox(_("Use Lotus status icons"), this)), modeMenuKey_(new QKeySequenceEdit(this)),
    spellCheck_(new QCheckBox(_("Enable spell check"), this)), autoNonVnRestore_(new QCheckBox(_("Auto restore invalid words"), this)),
    ddFreeStyle_(new QCheckBox(_("Allow dd -> đ when auto-restore is enabled"), this)), modernStyle_(new QCheckBox(_("Use oà, uý instead of òa, úy"), this)),
    freeMarking_(new QCheckBox(_("Allow freer typing"), this)), fixUinputWithAck_(new QCheckBox(_("Fix Uinput mode with Ack"), this)),
    enableMacro_(new QCheckBox(_("Enable macro"), this)), capitalizeMacro_(new QCheckBox(_("Capitalize macro"), this)) {
    setMinimumSize(760, 520);

    mode_->addItems({"Uinput (Smooth)", "Uinput (Slow)", "Surrounding Text", "Preedit", "Uinput (Hardcore)", "OFF"});
    inputMethod_->setEditable(true);
    inputMethod_->addItems({"Telex", "VNI", "VIQR", "Telex 2", "Custom"});
    outputCharset_->setEditable(true);
    outputCharset_->addItem("Unicode");

    auto* rootLayout  = new QVBoxLayout(this);
    auto* scrollArea  = new QScrollArea(this);
    auto* content     = new QWidget(this);
    auto* contentVBox = new QVBoxLayout(content);

    auto* header = new QLabel(_("Lotus Configuration"), content);
    header->setStyleSheet("font-size: 22px; font-weight: 600;");
    contentVBox->addWidget(header);

    auto* subtitle = new QLabel(_("Grouped layout for easier navigation and future options."), content);
    subtitle->setStyleSheet("color: palette(mid);");
    contentVBox->addWidget(subtitle);

    auto* coreGroup  = new QGroupBox(_("Core typing setup"), content);
    auto* coreLayout = new QFormLayout(coreGroup);
    coreLayout->addRow(_("Mode"), mode_);
    coreLayout->addRow(_("Input Method"), inputMethod_);
    coreLayout->addRow(_("Output Charset"), outputCharset_);
    coreLayout->addRow(_("Mode Menu Hotkey"), modeMenuKey_);
    coreLayout->addRow(QString(), useLotusIcons_);
    contentVBox->addWidget(coreGroup);

    auto* typingGroup  = new QGroupBox(_("Typing behavior"), content);
    auto* typingLayout = new QVBoxLayout(typingGroup);
    typingLayout->addWidget(spellCheck_);
    typingLayout->addWidget(autoNonVnRestore_);
    typingLayout->addWidget(ddFreeStyle_);
    typingLayout->addWidget(modernStyle_);
    typingLayout->addWidget(freeMarking_);
    typingLayout->addWidget(fixUinputWithAck_);
    contentVBox->addWidget(typingGroup);

    auto* macroGroup  = new QGroupBox(_("Macro"), content);
    auto* macroLayout = new QVBoxLayout(macroGroup);
    macroLayout->addWidget(enableMacro_);
    macroLayout->addWidget(capitalizeMacro_);

    auto* macroRow = new QHBoxLayout();
    macroRow->addWidget(new QLabel(_("Edit macro table from Lotus > Macro option in Fcitx settings."), macroGroup));
    macroRow->addStretch();
    macroLayout->addLayout(macroRow);

    contentVBox->addWidget(macroGroup);

    auto* advancedGroup = new QGroupBox(_("Advanced"), content);
    auto* advLayout     = new QVBoxLayout(advancedGroup);
    advLayout->addWidget(new QLabel(_("Custom Keymap can be edited from Lotus > Custom Keymap."), advancedGroup));
    contentVBox->addWidget(advancedGroup);

    contentVBox->addStretch();

    scrollArea->setWidget(content);
    scrollArea->setWidgetResizable(true);
    scrollArea->setFrameShape(QFrame::NoFrame);
    rootLayout->addWidget(scrollArea);

    setupConnections();
}

QString LotusConfigEditor::title() {
    return _("Lotus");
}

QString LotusConfigEditor::icon() {
    return "fcitx-lotus";
}

std::string LotusConfigEditor::configPath() const {
#if LOTUS_USE_MODERN_FCITX_API
    std::string configDir = (StandardPaths::global().userDirectory(StandardPathsType::Config) / "fcitx5" / "conf").string();
#else
    std::string configDir = StandardPath::global().userDirectory(StandardPath::Type::Config) + "/fcitx5/conf";
#endif
    return configDir + "/lotus.conf";
}

void LotusConfigEditor::setupConnections() {
    auto markChanged = [this]() { emit changed(true); };

    connect(mode_, &QComboBox::currentTextChanged, this, [markChanged](const QString&) { markChanged(); });
    connect(inputMethod_, &QComboBox::currentTextChanged, this, [markChanged](const QString&) { markChanged(); });
    connect(outputCharset_, &QComboBox::currentTextChanged, this, [markChanged](const QString&) { markChanged(); });
    connect(modeMenuKey_, &QKeySequenceEdit::keySequenceChanged, this, [markChanged](const QKeySequence&) { markChanged(); });

    connect(useLotusIcons_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(spellCheck_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(autoNonVnRestore_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(ddFreeStyle_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(modernStyle_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(freeMarking_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(fixUinputWithAck_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(enableMacro_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
    connect(capitalizeMacro_, &QCheckBox::toggled, this, [markChanged](bool) { markChanged(); });
}

void LotusConfigEditor::load() {
    lotusConfig config;
    readAsIni(config, configPath());

    mode_->setCurrentText(QString::fromStdString(config.mode.value()));

    const auto inputMethod = QString::fromStdString(config.inputMethod.value());
    if (inputMethod_->findText(inputMethod) < 0) {
        inputMethod_->addItem(inputMethod);
    }
    inputMethod_->setCurrentText(inputMethod);

    const auto outputCharset = QString::fromStdString(config.outputCharset.value());
    if (outputCharset_->findText(outputCharset) < 0) {
        outputCharset_->addItem(outputCharset);
    }
    outputCharset_->setCurrentText(outputCharset);

    useLotusIcons_->setChecked(config.useLotusIcons.value());

    if (!config.modeMenuKey.value().empty()) {
        const auto seq = QString::fromStdString(config.modeMenuKey.value().front().toString());
        modeMenuKey_->setKeySequence(QKeySequence::fromString(seq));
    } else {
        modeMenuKey_->clear();
    }

    spellCheck_->setChecked(config.spellCheck.value());
    autoNonVnRestore_->setChecked(config.autoNonVnRestore.value());
    ddFreeStyle_->setChecked(config.ddFreeStyle.value());
    modernStyle_->setChecked(config.modernStyle.value());
    freeMarking_->setChecked(config.freeMarking.value());
    fixUinputWithAck_->setChecked(config.fixUinputWithAck.value());
    enableMacro_->setChecked(config.enableMacro.value());
    capitalizeMacro_->setChecked(config.capitalizeMacro.value());

    emit changed(false);
}

void LotusConfigEditor::save() {
    lotusConfig config;
    readAsIni(config, configPath());

    config.mode.setValue(mode_->currentText().toStdString());
    config.inputMethod.setValue(inputMethod_->currentText().trimmed().toStdString());
    config.outputCharset.setValue(outputCharset_->currentText().trimmed().toStdString());
    config.useLotusIcons.setValue(useLotusIcons_->isChecked());

    std::vector<Key> keys;
    const auto       keyText = modeMenuKey_->keySequence().toString(QKeySequence::PortableText);
    if (!keyText.isEmpty()) {
        keys.emplace_back(keyText.toStdString());
    }
    config.modeMenuKey.setValue(keys);

    config.spellCheck.setValue(spellCheck_->isChecked());
    config.autoNonVnRestore.setValue(autoNonVnRestore_->isChecked());
    config.ddFreeStyle.setValue(ddFreeStyle_->isChecked());
    config.modernStyle.setValue(modernStyle_->isChecked());
    config.freeMarking.setValue(freeMarking_->isChecked());
    config.fixUinputWithAck.setValue(fixUinputWithAck_->isChecked());
    config.enableMacro.setValue(enableMacro_->isChecked());
    config.capitalizeMacro.setValue(capitalizeMacro_->isChecked());

    safeSaveAsIni(config, configPath());
    emit changed(false);
}

} // namespace fcitx::lotus
// NOLINTEND(cppcoreguidelines-owning-memory)
