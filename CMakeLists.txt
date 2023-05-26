cmake_minimum_required(VERSION 3.4...3.18)
project(am4utils)

add_library(route STATIC am4utils/route.cpp)
set_target_properties(route PROPERTIES POSITION_INDEPENDENT_CODE ON)

add_subdirectory(am4utils/include/pybind11)
pybind11_add_module(am4utils am4utils/binder.cpp)
target_link_libraries(am4utils PRIVATE route)

# target_compile_definitions(am4utils PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})