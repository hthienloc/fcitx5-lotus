/*
 * SPDX-FileCopyrightText: 2025 Võ Ngô Hoàng Thành <thanhpy2009@gmail.com>
 * SPDX-FileCopyrightText: 2026 Nguyễn Hoàng Kỳ  <nhktmdzhg@gmail.com>
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */
#ifndef _FCITX5_LOTUS_UTILS_H_
#define _FCITX5_LOTUS_UTILS_H_

#include "lotus-config.h"
#include <fcitx-utils/utf8.h>
#include <cstdint>
#include <atomic>
#include <condition_variable>
#include <mutex>
#include <string>

// Forward declaration for fcitx types
typedef uint32_t KeySym;

namespace fcitx {
    enum class LotusMode;
}

// Global variables
extern fcitx::LotusMode        realMode;
extern std::atomic<bool>       needEngineReset;
extern std::string             BASE_SOCKET_PATH;
extern std::atomic<bool>       g_mouse_clicked;
extern std::atomic<bool>       is_deleting_;
extern const int               MAX_BACKSPACE_COUNT;
extern std::once_flag          monitor_init_flag;
extern std::atomic<bool>       stop_flag_monitor;
extern std::atomic<bool>       monitor_running;
extern int                     uinput_client_fd_;
extern int                     realtextLen;
extern bool                    waitAck;
extern std::atomic<int>        mouse_socket_fd;
extern std::atomic<int64_t>    replacement_start_ms_;
extern std::atomic<int>        replacement_thread_id_;
extern std::atomic<bool>       needFallbackCommit;
extern std::mutex              monitor_mutex;
extern std::condition_variable monitor_cv;

// Helper functions
std::string buildSocketPath(const char* base_path_suffix);
int64_t     now_ms();
bool        isBackspace(uint32_t sym);
std::string SubstrChar(const std::string& s, size_t start, size_t len);
int         compareAndSplitStrings(const std::string& A, const std::string& B, std::string& commonPrefix, std::string& deletedPart, std::string& addedPart);

struct KeyEntry {
    uint32_t sym;
    uint32_t state;
};

#endif // _FCITX5_LOTUS_UTILS_H_
