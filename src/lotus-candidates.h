/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */
#ifndef _FCITX5_LOTUS_CANDIDATES_H_
#define _FCITX5_LOTUS_CANDIDATES_H_

#include <fcitx/candidatelist.h>
#include <fcitx/inputcontext.h>
#include <functional>
#include <string>

namespace fcitx {

    class LotusState;

    /**
     * @brief Candidate word class for emoji selection.
     */
    class EmojiCandidateWord : public CandidateWord {
      public:
        EmojiCandidateWord(Text text, LotusState* state, const std::string& emojiOutput);
        void select(InputContext* inputContext) const override;

      private:
        LotusState* state_;
        std::string emojiOutput_;
    };

    /**
     * @brief Custom candidate word class for app mode selection menu.
     */
    class AppModeCandidateWord : public CandidateWord {
      public:
        AppModeCandidateWord(Text text, std::function<void(InputContext*)> callback);
        void select(InputContext* ic) const override;

      private:
        std::function<void(InputContext*)> callback_;
    };

} // namespace fcitx

#endif // _FCITX5_LOTUS_CANDIDATES_H_
