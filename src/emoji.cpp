/*
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include "emoji.h"

#include <algorithm>

#include <emoji_public.h>

EmojiLoader::EmojiLoader(fcitx::AddonManager* addonManager) {
    if (addonManager != nullptr) {
        emojiAddon_ = addonManager->addon("emoji", true);
    }
    loadFromFcitx5("en");
}

void EmojiLoader::loadFromFcitx5(const std::string& language) {
    emojiList.clear();
    if (emojiAddon_ == nullptr) {
        return;
    }

    emojiAddon_->call<fcitx::IEmoji::prefix>(language, "", true, [this](const std::string& key, const std::vector<std::string>& values) {
        for (const auto& emoji : values) {
            EmojiEntry entry;
            entry.output  = emoji;
            entry.trigger = key;
            emojiList.push_back(entry);
        }
        return true;
    });
}

std::vector<EmojiEntry> EmojiLoader::search(const std::string& prefix) {
    if (prefix.empty() || (emojiAddon_ == nullptr))
        return {};

    struct EmojiEntryFuzzy {
        EmojiEntry entry;
        int        score;
    };
    std::vector<EmojiEntryFuzzy> results;

    for (const auto& entry : emojiList) {
        int    score              = 0;
        size_t queryIndex         = 0;
        int    lastMatchIndex     = -1;
        int    consecutiveMatches = 0;
        int    firstMatchIndex    = -1;

        for (size_t i = 0; i < entry.trigger.size() && queryIndex < prefix.size(); ++i) {
            if (entry.trigger[i] == prefix[queryIndex]) {
                if (queryIndex == 0)
                    firstMatchIndex = i; // NOLINT

                if (lastMatchIndex != -1 && (int)i == lastMatchIndex + 1) {
                    ++consecutiveMatches;
                    score += (20 * consecutiveMatches);
                } else {
                    consecutiveMatches = 0;
                }

                if (i == 0 || entry.trigger[i - 1] == '_' || entry.trigger[i - 1] == '-') {
                    score += 50;
                }

                lastMatchIndex = i; // NOLINT
                ++queryIndex;
            }
        }
        if (queryIndex == prefix.size()) {
            if (firstMatchIndex == 0)
                score += 100;

            score -= static_cast<int>(entry.trigger.size());

            score -= (lastMatchIndex - firstMatchIndex);

            results.push_back({entry, score});
        }
    }

    std::sort(results.begin(), results.end(), [](const auto& a, const auto& b) {
        if (a.score != b.score)
            return a.score > b.score;
        return a.entry.trigger.size() < b.entry.trigger.size();
    });

    std::vector<EmojiEntry> finalResults;
    finalResults.reserve(results.size());
    for (const auto& result : results) {
        finalResults.push_back(result.entry);
    }
    return finalResults;
}

size_t EmojiLoader::size() const {
    return emojiList.size();
}