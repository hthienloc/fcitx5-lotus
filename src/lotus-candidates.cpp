/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */
#include "lotus-candidates.h"
#include "lotus-state.h"
#include "lotus-engine.h"

#include <fcitx/inputpanel.h>

namespace fcitx {

    // EmojiCandidateWord implementation
    EmojiCandidateWord::EmojiCandidateWord(Text text, LotusState* state, const std::string& emojiOutput) :
        CandidateWord(std::move(text)), state_(state), emojiOutput_(emojiOutput) {}

    void EmojiCandidateWord::select(InputContext* inputContext) const {
        inputContext->commitString(emojiOutput_);
        LOTUS_INFO("Emoji committed: " + emojiOutput_);

        state_->emojiBuffer_.clear();
        state_->emojiCandidates_.clear();

        inputContext->inputPanel().reset();
        inputContext->updateUserInterface(UserInterfaceComponent::InputPanel);
        inputContext->updatePreedit();
    }

    // AppModeCandidateWord implementation
    AppModeCandidateWord::AppModeCandidateWord(Text text, std::function<void(InputContext*)> callback) : CandidateWord(std::move(text)), callback_(std::move(callback)) {}

    void AppModeCandidateWord::select(InputContext* ic) const {
        if (callback_) {
            callback_(ic);
        }
    }

    // ClipboardCandidateWord implementation
    ClipboardCandidateWord::ClipboardCandidateWord(Text text, LotusState* state, const std::string& content) :
        CandidateWord(std::move(text)), state_(state), content_(content) {}

    void ClipboardCandidateWord::select(InputContext* ic) const {
        std::string contentToCommit = content_;
        
        // Reset the mode and close menu (input panel) first to avoid conflicts
        state_->engine_->setMode(state_->previousMode_, ic);
        state_->reset();
        
        ic->commitString(contentToCommit);
        std::string preview = contentToCommit.size() > 50 ? contentToCommit.substr(0, 50) + "..." : contentToCommit;
        LOTUS_INFO("Clipboard item committed: " + preview);

        ic->updateUserInterface(UserInterfaceComponent::InputPanel);
        ic->updatePreedit();
    }

} // namespace fcitx
