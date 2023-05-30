include(FetchContent)

set(DUCKDB_VERSION "0.8.0")
string(REGEX MATCH "(arm64|aarch64)" IS_ARM "${CMAKE_SYSTEM_PROCESSOR}")

if (IS_ARM)
    message(FATAL_ERROR "DuckDB: ARM not supported")
elseif(CMAKE_SIZEOF_VOID_P EQUAL 4)
    message(FATAL_ERROR "DuckDB: 32-bit not supported")
elseif(APPLE)
    set(DUCKDB_URL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/libduckdb-osx-universal.zip")
    set(DUCKDB_DLL "libduckdb.dylib")
elseif(WIN32)
    set(DUCKDB_URL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/libduckdb-windows-amd64.zip")
    set(DUCKDB_DLL "duckdb.dll")
elseif(UNIX)
    set(DUCKDB_URL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/libduckdb-linux-amd64.zip")
    set(DUCKDB_DLL "duckdb.so")
endif()

FetchContent_Declare(
    duckdb_folder
    URL ${DUCKDB_URL}
)
FetchContent_MakeAvailable(duckdb_folder)

add_library(duckdb SHARED IMPORTED GLOBAL)
set_target_properties(duckdb PROPERTIES
    IMPORTED_LOCATION "${duckdb_folder_SOURCE_DIR}/${DUCKDB_DLL}"
    INTERFACE_INCLUDE_DIRECTORIES "${duckdb_folder_SOURCE_DIR}"
)
if(WIN32)
    set_target_properties(duckdb PROPERTIES
        IMPORTED_IMPLIB "${duckdb_folder_SOURCE_DIR}/duckdb.lib"
    )
endif()