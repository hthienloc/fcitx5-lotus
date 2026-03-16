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
#include <QHBoxLayout>
#include <QLabel>
#include <QListWidgetItem>
#include <QVBoxLayout>

#if LOTUS_USE_MODERN_FCITX_API
#include <fcitx-utils/standardpaths.h>
#else
#include <fcitx-utils/standardpath.h>
#endif

namespace fcitx::lotus {

LotusConfigEditor::LotusConfigEditor(QWidget* parent) :
    FcitxQtConfigUIWidget(parent), sidebar_(new QListWidget(this)), pageStack_(new QStackedWidget(this)), mode_(new QComboBox(this)),
    inputMethod_(new QComboBox(this)), outputCharset_(new QComboBox(this)), useLotusIcons_(new QCheckBox(_("Use Lotus status icons"), this)),
    modeMenuKey_(new QKeySequenceEdit(this)), spellCheck_(new QCheckBox(_("Enable spell check"), this)),
    autoNonVnRestore_(new QCheckBox(_("Auto restore invalid words"), this)),
    ddFreeStyle_(new QCheckBox(_("Allow dd -> đ when auto-restore is enabled"), this)),
    modernStyle_(new QCheckBox(_("Use oà, uý instead of òa, úy"), this)), freeMarking_(new QCheckBox(_("Allow freer typing"), this)),
    fixUinputWithAck_(new QCheckBox(_("Fix Uinput mode with Ack"), this)), enableMacro_(new QCheckBox(_("Enable macro"), this)),
    capitalizeMacro_(new QCheckBox(_("Capitalize macro"), this)) {
    setMinimumSize(760, 520);


    mode_->addItems({"Uinput (Smooth)", "Uinput (Slow)", "Surrounding Text", "Preedit", "Uinput (Hardcore)", "OFF"});
    inputMethod_->setEditable(true);
    inputMethod_->addItems({"Telex", "VNI", "VIQR", "Telex 2", "Custom"});
    outputCharset_->setEditable(true);
    outputCharset_->addItem("Unicode");

    buildUI();
    setupConnections();
}

void LotusConfigEditor::buildUI() {
    auto* rootLayout = new QHBoxLayout(this);
    rootLayout->setContentsMargins(0, 0, 0, 0);

    rootLayout->addWidget(buildSidebar(), 1);

    pageStack_->addWidget(buildGeneralPage());
    pageStack_->addWidget(buildTypingPage());
    pageStack_->addWidget(buildMacroPage());
    pageStack_->addWidget(buildShortcutsPage());
    pageStack_->addWidget(buildAppearancePage());

    rootLayout->addWidget(pageStack_, 3);
}

QWidget* LotusConfigEditor::buildSidebar() {
    sidebar_->setFrameShape(QFrame::NoFrame);
    sidebar_->setSelectionMode(QAbstractItemView::SingleSelection);
    sidebar_->setSpacing(2);

    auto addSection = [this](const QString& name) {
        auto* item = new QListWidgetItem(name, sidebar_);
        item->setFlags(Qt::NoItemFlags);
    };

    auto addPage = [this](const QString& name, int pageIndex) {
        auto* item = new QListWidgetItem(QStringLiteral("  %1").arg(name), sidebar_);
        const int row            = sidebar_->count() - 1;
        sidebarRowToPageIndex_[row] = pageIndex;
        item->setData(Qt::UserRole, pageIndex);
    };

    addSection(_("Cài đặt"));
    addPage(_("Chung"), 0);
    addPage(_("Gõ phím"), 1);
    addPage(_("Macro"), 2);
    addSection(_("Nâng cao"));
    addPage(_("Phím tắt"), 3);
    addPage(_("Giao diện"), 4);

    sidebar_->setCurrentRow(1);
    return sidebar_;
}

    QWidget* LotusConfigEditor::buildGeneralPage() {
    auto* page   = new QWidget(this);
    auto* layout = new QVBoxLayout(page);


    auto* title = new QLabel(_("Chung"), page);
    title->setStyleSheet("font-size: 18px; font-weight: 600;");
    layout->addWidget(title);

    auto* subtitle = new QLabel(_("Thiết lập chế độ gõ và bộ mã mặc định."), page);
    subtitle->setStyleSheet("color: palette(mid);");
    layout->addWidget(subtitle);

    auto* form = new QFormLayout();
    form->addRow(_("Mode"), mode_);
    form->addRow(_("Input Method"), inputMethod_);
    form->addRow(_("Output Charset"), outputCharset_);
    layout->addLayout(form);
    layout->addStretch();

    return page;
}

QWidget* LotusConfigEditor::buildTypingPage() {
    auto* page   = new QWidget(this);
    auto* layout = new QVBoxLayout(page);

    auto* title = new QLabel(_("Gõ phím"), page);
    title->setStyleSheet("font-size: 18px; font-weight: 600;");
    layout->addWidget(title);

    auto* subtitle = new QLabel(_("Tùy chỉnh hành vi gõ tiếng Việt."), page);
    subtitle->setStyleSheet("color: palette(mid);");
    layout->addWidget(subtitle);

    layout->addWidget(spellCheck_);
    layout->addWidget(autoNonVnRestore_);
    layout->addWidget(ddFreeStyle_);
    layout->addWidget(modernStyle_);
    layout->addWidget(freeMarking_);
    layout->addWidget(fixUinputWithAck_);
    layout->addStretch();

    return page;
}

QWidget* LotusConfigEditor::buildMacroPage() {
    auto* page   = new QWidget(this);
    auto* layout = new QVBoxLayout(page);

    auto* title = new QLabel(_("Macro"), page);
    title->setStyleSheet("font-size: 18px; font-weight: 600;");
    layout->addWidget(title);

    layout->addWidget(enableMacro_);
    layout->addWidget(capitalizeMacro_);
    layout->addWidget(new QLabel(_("Edit macro table from Lotus > Macro option in Fcitx settings."), page));
    layout->addStretch();

    return page;
}

QWidget* LotusConfigEditor::buildShortcutsPage() {
    auto* page   = new QWidget(this);
    auto* layout = new QVBoxLayout(page);

    auto* title = new QLabel(_("Phím tắt"), page);
    title->setStyleSheet("font-size: 18px; font-weight: 600;");
    layout->addWidget(title);

    auto* form = new QFormLayout();
    form->addRow(_("Mode Menu Hotkey"), modeMenuKey_);
    layout->addLayout(form);

    layout->addWidget(new QLabel(_("Custom Keymap can be edited from Lotus > Custom Keymap."), page));
    layout->addStretch();

    return page;
}

QWidget* LotusConfigEditor::buildAppearancePage() {
    auto* page   = new QWidget(this);
    auto* layout = new QVBoxLayout(page);

    auto* title = new QLabel(_("Giao diện"), page);
    title->setStyleSheet("font-size: 18px; font-weight: 600;");
    layout->addWidget(title);

    layout->addWidget(useLotusIcons_);
    layout->addStretch();

    return page;
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


    connect(sidebar_, &QListWidget::currentRowChanged, this, [this](int row) {
        const auto pageIndex = sidebarRowToPageIndex_.value(row, -1);
        if (pageIndex >= 0) {
            pageStack_->setCurrentIndex(pageIndex);
        }
    });

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
