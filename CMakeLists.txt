cmake_minimum_required(VERSION 3.15...3.26)

project(am4utils-build LANGUAGES CXX)

## download duckdb

set(DUCKDB_VERSION "0.8.0")
string(REGEX MATCH "(arm64|aarch64)" IS_ARM "${CMAKE_SYSTEM_PROCESSOR}")
if (IS_ARM)
    message(FATAL_ERROR "DuckDB: ARM not supported")
elseif(CMAKE_SIZEOF_VOID_P EQUAL 4)
    message(FATAL_ERROR "DuckDB: 32-bit not supported")
elseif(APPLE)
    set(DUCKDB_URL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/libduckdb-osx-universal.zip")
elseif(WIN32)
    set(DUCKDB_URL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/libduckdb-windows-amd64.zip")
elseif(UNIX)
    set(DUCKDB_URL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/libduckdb-linux-amd64.zip")
endif()


set(DUCKDB_ZIP "${CMAKE_BINARY_DIR}/duckdb.zip")
set(DUCKDB_DIR "${CMAKE_BINARY_DIR}/duckdb")

if(NOT EXISTS "${DUCKDB_DIR}/duckdb.h")
    message(STATUS "[DEBUG] duckdb does not exist")
    file(DOWNLOAD "${DUCKDB_URL}" "${DUCKDB_ZIP}")
    file(ARCHIVE_EXTRACT INPUT "${DUCKDB_ZIP}" DESTINATION "${DUCKDB_DIR}")
    file(REMOVE "${DUCKDB_ZIP}")
endif()

include_directories(${DUCKDB_DIR})
add_library(duckdb STATIC IMPORTED)
set_target_properties(
    duckdb PROPERTIES
    IMPORTED_LOCATION "${DUCKDB_DIR}/duckdb.lib"
    POSITION_INDEPENDENT_CODE ON
)

######

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
set(pybind11_DIR "${Python_SITELIB}/pybind11/share/cmake/pybind11")
# message(STATUS "[DEBUG] py: ${Python_EXECUTABLE}")
# message(STATUS "[DEBUG] pybind11: ${pybind11_DIR}")
# message(STATUS "[DEBUG] CMAKE_BINARY_DIR: ${CMAKE_BINARY_DIR}")
# message(STATUS "[DEBUG] DUCKDB_LIBRARY: ${DUCKDB_LIBRARY}")
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(am4utils src/binder.cpp)
add_library(route STATIC src/route.cpp)
add_library(airport STATIC src/airport.cpp)
target_link_libraries(
    am4utils
    PRIVATE route
    PRIVATE airport
    PRIVATE duckdb
)
target_compile_definitions(am4utils PRIVATE VERSION_INFO=0.0.3)


install(TARGETS am4utils LIBRARY DESTINATION .)