/*
 * SPDX-FileCopyrightText: 2022-2022 CSSlayer <wengxt@gmail.com>
 * SPDX-FileCopyrightText: 2025 Võ Ngô Hoàng Thành <thanhpy2009@gmail.com>
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */
#ifndef _FCITX5_LOTUS_STATE_H_
#define _FCITX5_LOTUS_STATE_H_

#include "lotus.h"
#include <fcitx-utils/key.h>
#include <fcitx/inputcontext.h>
#include <fcitx/inputcontextproperty.h>
#include <atomic>
#include <string>
#include <vector>

struct EmojiEntry;

namespace fcitx {
    class LotusEngine;
    class CommonCandidateList;
    class SurroundingText;

    /**
     * @brief State class for Lotus input method per input context.
     */
    class LotusState final : public InputContextProperty {
      public:
        LotusState(LotusEngine* engine, InputContext* ic);
        ~LotusState();

        void setEngine();
        void setOption();

        bool connect_uinput_server();
        int  setup_uinput();
        void send_backspace_uinput(int count);

        void replayBufferToEngine(const std::string& buffer);
        bool isAutofillCertain(const SurroundingText& s);

        void handlePreeditMode(KeyEvent& keyEvent);
        void updateEmojiPageStatus(CommonCandidateList* commonList);
        void handleEmojiMode(KeyEvent& keyEvent);
        void selectEmojiCandidate(int index);
        void updateEmojiPreedit();

        bool handleUInputKeyPress(KeyEvent& event, KeySym currentSym, int sleepTime);
        void performReplacement(const std::string& deletedPart, const std::string& addedPart);
        void checkForwardSpecialKey(KeyEvent& keyEvent, KeySym& currentSym);
        void handleUinputMode(KeyEvent& keyEvent, KeySym currentSym, bool checkEmptyPreedit, int sleepTime);
        void handleSurroundingText(KeyEvent& keyEvent, KeySym currentSym);

        void keyEvent(KeyEvent& keyEvent);
        void reset();
        void commitBuffer();
        void clearAllBuffers();
        bool isEmptyHistory();

        // Allow friend classes to access private members
        friend class EmojiCandidateWord;
        friend class LotusEngine;

      private:
        LotusEngine*     engine_;
        InputContext*    ic_;
        CGoObject        lotusEngine_;
        std::string      oldPreBuffer_;
        std::string      history_;
        size_t           expected_backspaces_     = 0;
        size_t           current_backspace_count_ = 0;
        std::string      pending_commit_string_;
        std::atomic<int> current_thread_id_{0};
        // Emoji mode variables
        std::string             emojiBuffer_;
        std::vector<EmojiEntry> emojiCandidates_;
        bool                    waitAck_ = false;
    };

} // namespace fcitx

#endif // _FCITX5_LOTUS_STATE_H_
