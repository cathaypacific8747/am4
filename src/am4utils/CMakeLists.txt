cmake_minimum_required(VERSION 3.15...3.26)

if (NOT DEFINED SKBUILD_PROJECT_VERSION)
    set(SKBUILD_PROJECT_VERSION "0.0.0-dev")
endif()

if (NOT DEFINED SKBUILD_WHEEL_INSTALL_DIR)
    set(SKBUILD_WHEEL_INSTALL_DIR "am4utils")
endif()

if (NOT DEFINED BUILD_PYBIND)
    set(BUILD_PYBIND 1)
endif()

if (NOT DEFINED COPY_DATA)
    set(COPY_DATA 0)
endif()

project(am4utils LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
include(libduckdb.cmake)

if (MSVC)
    add_compile_options(/W4 /std:c++17)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -std=c++17)
endif()

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED HINTS "${Python_SITELIB}/pybind11/share/cmake/pybind11" "${CMAKE_SOURCE_DIR}/../../.venv/Lib/site-packages/pybind11/share/cmake/pybind11")
file(TO_CMAKE_PATH "${Python_SITELIB}/${SKBUILD_WHEEL_INSTALL_DIR}" PYTHON_LIB_DIR)
message("[DEBUG]\n\
   cmake binary dir ${CMAKE_BINARY_DIR}\n\
   py executable    ${Python_EXECUTABLE}\n\
   pybind11 dir     ${pybind11_DIR}\n\
   duckdb src       ${duckdb_folder_SOURCE_DIR}\n\
   py site-packages ${PYTHON_LIB_DIR}\n")

pybind11_add_module(_core
    cpp/db.cpp
    cpp/game.cpp
    cpp/demand.cpp
    cpp/ticket.cpp
    cpp/airport.cpp
    cpp/aircraft.cpp
    cpp/route.cpp
    cpp/binder.cpp
)
target_include_directories(_core PRIVATE ${duckdb_folder_SOURCE_DIR})
target_compile_definitions(_core
    PRIVATE VERSION_INFO=${SKBUILD_PROJECT_VERSION} BUILD_PYBIND=${BUILD_PYBIND}
)
target_compile_features(_core PRIVATE cxx_std_17)

set_rpath(_core)
target_link_libraries(_core PRIVATE duckdb)

install(TARGETS _core DESTINATION .)
install(FILES $<TARGET_FILE:duckdb> DESTINATION .)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/stubs/ DESTINATION . OPTIONAL) # / is important!
install(DIRECTORY ${CMAKE_SOURCE_DIR}/py/ DESTINATION .)
if (COPY_DATA)
    install(DIRECTORY ${CMAKE_SOURCE_DIR}/data DESTINATION .)
endif()

# debug executable
add_executable(_core_executable
    cpp/db.cpp
    cpp/game.cpp
    cpp/demand.cpp
    cpp/ticket.cpp
    cpp/airport.cpp
    cpp/aircraft.cpp
    cpp/route.cpp
    cpp/main.cpp
)

target_include_directories(_core_executable PRIVATE ${duckdb_folder_SOURCE_DIR})
target_compile_definitions(_core_executable
    PRIVATE VERSION_INFO=${SKBUILD_PROJECT_VERSION} BUILD_PYBIND=0
)
target_compile_features(_core_executable PRIVATE cxx_std_17)

set_rpath(_core_executable)
target_link_libraries(_core_executable PRIVATE duckdb)

add_custom_command(
    TARGET _core_executable POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:duckdb>
        $<TARGET_FILE_DIR:_core_executable>
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/data
        $<TARGET_FILE_DIR:_core_executable>/data
)

if (EXCLUDE_EXECUTABLES)
    set_target_properties(_core_executable PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)
endif()