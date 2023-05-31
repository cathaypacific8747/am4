cmake_minimum_required(VERSION 3.15...3.26)

project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

include(libduckdb.cmake)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED HINTS "${Python_SITELIB}/pybind11/share/cmake/pybind11" "${CMAKE_SOURCE_DIR}/.venv/Lib/site-packages/pybind11/share/cmake/pybind11")
message(STATUS "[DEBUG]\n\
   cmake binary dir ${CMAKE_BINARY_DIR}\n\
   py executable    ${Python_EXECUTABLE}\n\
   pybind11 dir     ${pybind11_DIR}\n\
   duckdb src       ${duckdb_folder_SOURCE_DIR}\n")
file(TO_CMAKE_PATH "${Python_SITELIB}/${SKBUILD_WHEEL_INSTALL_DIR}" PYTHON_SITE_PACKAGES_DIR)

pybind11_add_module(
    _core
    src/am4utils/binder.cpp
    src/am4utils/db.cpp
    src/am4utils/airport.cpp
    src/am4utils/route.cpp
)
target_include_directories(_core PRIVATE ${duckdb_folder_SOURCE_DIR})
target_compile_definitions(_core
    PRIVATE VERSION_INFO=${SKBUILD_PROJECT_VERSION}
    PRIVATE CORE_DIR=${PYTHON_SITE_PACKAGES_DIR}
)
target_link_libraries(_core PRIVATE duckdb)

install(TARGETS _core DESTINATION .)
install(FILES $<TARGET_FILE:duckdb> DESTINATION .)
install(FILES ${CMAKE_SOURCE_DIR}/src/am4utils/__init__.py DESTINATION .)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/src/am4utils/data DESTINATION .)


# debug executable: build/Release/_core_executable.exe
add_executable(_core_executable
    src/am4utils/main.cpp
    src/am4utils/db.cpp
    src/am4utils/airport.cpp
    src/am4utils/route.cpp
)
target_include_directories(_core_executable PRIVATE ${duckdb_folder_SOURCE_DIR})
target_compile_definitions(_core_executable
    PRIVATE VERSION_INFO=0.0.0-dev
    PRIVATE CORE_DIR=$<TARGET_FILE_DIR:_core_executable>
)
target_link_libraries(_core_executable PRIVATE duckdb)
add_custom_command(
    TARGET _core_executable POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:duckdb>
        $<TARGET_FILE_DIR:_core_executable>
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/src/am4utils/data
        $<TARGET_FILE_DIR:_core_executable>/data
)