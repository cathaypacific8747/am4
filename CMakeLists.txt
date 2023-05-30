cmake_minimum_required(VERSION 3.15...3.26)

project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

include(libduckdb.cmake)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED HINTS "${Python_SITELIB}/pybind11/include/pybind11")
message(STATUS "[DEBUG]\n\
   cmake binary dir ${CMAKE_BINARY_DIR}\n\
   py executable    ${Python_EXECUTABLE}\n\
   pybind11 dir     ${pybind11_DIR}\n\
   duckdb src       ${duckdb_folder_SOURCE_DIR}\n")
file(TO_CMAKE_PATH "${Python_SITELIB}/${SKBUILD_WHEEL_INSTALL_DIR}" PYTHON_SITE_PACKAGES_DIR)

pybind11_add_module(_core src/am4utils/binder.cpp)
add_library(db STATIC src/am4utils/db.cpp)
add_library(route STATIC src/am4utils/route.cpp)
add_library(airport STATIC src/am4utils/airport.cpp)
target_include_directories(db PRIVATE ${duckdb_folder_SOURCE_DIR})
target_compile_definitions(db PRIVATE CORE_DIR=${PYTHON_SITE_PACKAGES_DIR})
target_compile_definitions(_core PRIVATE VERSION_INFO=${PROJECT_VERSION})
target_link_libraries(
    _core
    PRIVATE duckdb
    PRIVATE db
    PRIVATE route
    PRIVATE airport
)

# add_custom_command(
#     TARGET _core POST_BUILD
#     COMMAND ${CMAKE_COMMAND} -E copy_if_different
#         $<TARGET_FILE:duckdb>
#         $<TARGET_FILE_DIR:_core>
#     COMMAND ${CMAKE_COMMAND} -E copy_directory
#         ${CMAKE_SOURCE_DIR}/src/am4utils/data
#         $<TARGET_FILE_DIR:_core>/data
# )

install(TARGETS _core DESTINATION .)
install(FILES $<TARGET_FILE:duckdb> DESTINATION .)
install(FILES ${CMAKE_SOURCE_DIR}/src/am4utils/__init__.py DESTINATION .)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/src/am4utils/data DESTINATION .)