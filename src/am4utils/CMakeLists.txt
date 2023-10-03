cmake_minimum_required(VERSION 3.15...3.26)
project(am4utils LANGUAGES CXX)
if (NOT SKBUILD_PROJECT_VERSION)
    file(STRINGS pyproject.toml PROJECT_TOML_CONTENTS REGEX "^version =")
    string(REGEX MATCH "\"([0-9]+\\.[0-9]+\\.[0-9]+)\"" _ ${PROJECT_TOML_CONTENTS})
    set(SKBUILD_PROJECT_VERSION ${CMAKE_MATCH_1})
endif()

set(AM4UTILS_SOURCES
    cpp/db.cpp
    cpp/game.cpp
    cpp/demand.cpp
    cpp/ticket.cpp
    cpp/airport.cpp
    cpp/aircraft.cpp
    cpp/route.cpp
    cpp/log.cpp
)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
if (MSVC)
    add_compile_options(/W4 /O2 /std:c++17)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Wconversion -O3 -std=c++17)
endif()
add_subdirectory(cpp/include/ext/libduckdb)



### python bindings
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED HINTS "${Python_SITELIB}/pybind11/share/cmake/pybind11" "${CMAKE_SOURCE_DIR}/../../.venv/Lib/site-packages/pybind11/share/cmake/pybind11")
file(TO_CMAKE_PATH "${Python_SITELIB}/am4utils" PYTHON_LIB_DIR)

message("[DEBUG]\n\
    project version  ${SKBUILD_PROJECT_VERSION}\n\
    cmake binary dir ${CMAKE_BINARY_DIR}\n\
    cmake source dir ${CMAKE_SOURCE_DIR}\n\
    py executable    ${Python_EXECUTABLE}\n\
    pybind11 dir     ${pybind11_DIR}\n\
    duckdb src       ${duckdb_folder_SOURCE_DIR}\n\
    py target libdir ${PYTHON_LIB_DIR}\n")

pybind11_add_module(_core
    ${AM4UTILS_SOURCES}
    cpp/binder.cpp
)
target_include_directories(_core PUBLIC ${CMAKE_SOURCE_DIR}/cpp/include)
target_compile_definitions(_core
    PRIVATE VERSION_INFO=${SKBUILD_PROJECT_VERSION} BUILD_PYBIND=1
)

duckdb_set_rpath(_core)
target_link_libraries(_core PRIVATE duckdb)

install(TARGETS _core DESTINATION .)
install(FILES $<TARGET_FILE:duckdb> DESTINATION .)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/stubs/ DESTINATION . OPTIONAL) # / is important!
install(DIRECTORY ${CMAKE_SOURCE_DIR}/py/ DESTINATION .)
if (DEFINED COPY_DATA AND COPY_DATA)
    install(DIRECTORY ${CMAKE_SOURCE_DIR}/data DESTINATION .)
endif()



### static library
add_library(_core_static STATIC
    ${AM4UTILS_SOURCES}
)
target_compile_definitions(_core_static
    PRIVATE VERSION_INFO=${SKBUILD_PROJECT_VERSION} BUILD_PYBIND=0
)
target_link_libraries(_core_static PRIVATE duckdb)
set_target_properties(_core_static PROPERTIES OUTPUT_NAME "am4tools_static")



### debug testing executable for static library
add_executable(_core_executable
    cpp/main.cpp
)
target_compile_definitions(_core_executable
    PRIVATE VERSION_INFO=${SKBUILD_PROJECT_VERSION} BUILD_PYBIND=0
)
duckdb_set_rpath(_core_executable)
target_link_libraries(_core_executable PRIVATE duckdb)

set(VTUNE_INSTALL_DIR /opt/intel/oneapi/vtune/latest)
target_include_directories(_core_executable PRIVATE ${VTUNE_INSTALL_DIR}/sdk/include)
target_link_directories(_core_executable PRIVATE ${VTUNE_INSTALL_DIR}/sdk/lib64)
target_link_libraries(_core_executable PRIVATE ittnotify dl pthread)
target_link_libraries(_core_executable PRIVATE _core_static)

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
    set_target_properties(_core_static PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)
    set_target_properties(_core_executable PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)
endif()