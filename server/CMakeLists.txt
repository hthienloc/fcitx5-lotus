find_package(PkgConfig REQUIRED)

pkg_check_modules(LIBINPUT REQUIRED IMPORTED_TARGET libinput)
pkg_check_modules(LIBUDEV  REQUIRED IMPORTED_TARGET libudev)

add_executable(fcitx5-lotus-server lotus-server.cpp lotus-logger.cpp)

target_link_libraries(fcitx5-lotus-server
    PkgConfig::LIBINPUT
    PkgConfig::LIBUDEV
)

find_program(FCITX5_EXECUTABLE fcitx5)
if(NOT FCITX5_EXECUTABLE)
    set(FCITX5_EXECUTABLE "/usr/bin/fcitx5")
endif()

target_compile_definitions(fcitx5-lotus-server PRIVATE
    FCITX5_EXECUTABLE_PATH=\"${FCITX5_EXECUTABLE}\"
)

install(TARGETS fcitx5-lotus-server DESTINATION ${CMAKE_INSTALL_BINDIR})
