include(FetchContent)

set(DUCKDB_VERSION "0.8.0")

string(REGEX MATCH "(arm64|aarch64)" IS_ARM "${CMAKE_SYSTEM_PROCESSOR}")
if(CMAKE_SIZEOF_VOID_P EQUAL 4 OR IS_ARM)
    message(WARNING "32-bit / ARM builds are not tested!")
endif()
if(APPLE)
    set(DUCKDB_FN "libduckdb-osx-universal")
    set(DUCKDB_DLL "libduckdb.dylib")
elseif(WIN32)
    if (CMAKE_SIZEOF_VOID_P EQUAL 4)
        set(DUCKDB_FN "libduckdb-windows-i386")
    else()
        set(DUCKDB_FN "libduckdb-windows-amd64")
    endif()
    set(DUCKDB_DLL "duckdb.dll")
elseif(UNIX)
    if (CMAKE_SIZEOF_VOID_P EQUAL 4)
        set(DUCKDB_FN "libduckdb-linux-i386")
    elseif(IS_ARM)
        set(DUCKDB_FN "libduckdb-linux-aarch64")
    else()
        set(DUCKDB_FN "libduckdb-linux-amd64")
    endif()
    set(DUCKDB_DLL "libduckdb.so")
endif()
set(DUCKDB_URL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/${DUCKDB_FN}.zip")

FetchContent_Declare(
    duckdb_folder
    URL ${DUCKDB_URL}
)
FetchContent_MakeAvailable(duckdb_folder)

add_library(duckdb SHARED IMPORTED GLOBAL)
set_target_properties(duckdb PROPERTIES
    IMPORTED_LOCATION "${duckdb_folder_SOURCE_DIR}/${DUCKDB_DLL}"
    INTERFACE_INCLUDE_DIRECTORIES "${duckdb_folder_SOURCE_DIR}"
    POSITION_INDEPENDENT_CODE ON
)
if(WIN32)
    set_target_properties(duckdb PROPERTIES
        IMPORTED_IMPLIB "${duckdb_folder_SOURCE_DIR}/duckdb.lib"
    )
endif()

# https://stackoverflow.com/questions/43330165/how-to-link-a-shared-library-with-cmake-with-relative-path
# https://github.com/pybind/cmake_example/issues/11
function(set_rpath target)
    set_target_properties(${target} PROPERTIES
        SKIP_BUILD_RPATH FALSE
        BUILD_WITH_INSTALL_RPATH TRUE
        INSTALL_RPATH_USE_LINK_PATH TRUE
    )
    if (APPLE)
        set_target_properties(${target} PROPERTIES INSTALL_RPATH "@loader_path")
    elseif(UNIX)
        set_target_properties(${target} PROPERTIES INSTALL_RPATH "$ORIGIN")
    endif()
endfunction()