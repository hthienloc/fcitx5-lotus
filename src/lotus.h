/*
 * SPDX-FileCopyrightText: 2022-2022 CSSlayer <wengxt@gmail.com>
 * SPDX-FileCopyrightText: 2025 Võ Ngô Hoàng Thành <thanhpy2009@gmail.com>
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */
#ifndef _FCITX5_LOTUS_H_
#define _FCITX5_LOTUS_H_

#include "bamboo-core.h"
#include "lotus-config.h"
#include <cstdint>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace fcitx {

    class LotusEngine;
    class LotusState;

    /**
     * @brief RAII wrapper for CGo handle (uintptr_t).
     */
    class CGoObject {
      public:
        CGoObject(std::optional<uintptr_t> handle = std::nullopt) : handle_(handle) {}

        ~CGoObject() {
            if (handle_) {
                DeleteObject(*handle_);
            }
        }

        CGoObject(const CGoObject&)            = delete;
        CGoObject& operator=(const CGoObject&) = delete;

        CGoObject(CGoObject&& other)            = default;
        CGoObject& operator=(CGoObject&& other) = default;

        void       reset(std::optional<uintptr_t> handle = std::nullopt) {
            clear();
            handle_ = handle;
        }

        uintptr_t handle() const {
            return handle_.value_or(0);
        }

        uintptr_t release() {
            if (handle_) {
                uintptr_t v = *handle_;
                handle_     = std::nullopt;
                return v;
            }
            return 0;
        }

        explicit operator bool() const {
            return handle_.has_value() && *handle_ != 0;
        }

      private:
        void clear() {
            if (handle_) {
                DeleteObject(*handle_);
                handle_ = std::nullopt;
            }
        }

        std::optional<uintptr_t> handle_;
    };

} // namespace fcitx

#include "emoji.h"
#include "lotus-candidates.h"
#include "lotus-state.h"
#include "lotus-engine.h"

#endif // _FCITX5_LOTUS_H_
