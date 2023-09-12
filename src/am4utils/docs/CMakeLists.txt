find_package(Doxygen REQUIRED)

# get all public headers of core python module
get_target_property(AM4UTILS_HEADER_DIR _core_static INTERFACE_INCLUDE_DIRECTORIES)
# file(GLOB_RECURSE AM4UTILS_PUBLIC_HEADERS ${AM4UTILS_HEADER_DIR}/*.hpp)
set(AM4UTILS_HEADERS
    cpp/include/ext/jaro.hpp
    cpp/include/db.hpp
    cpp/include/game.hpp
    cpp/include/demand.hpp
    cpp/include/ticket.hpp
    cpp/include/airport.hpp
    cpp/include/aircraft.hpp
    cpp/include/route.hpp
    cpp/include/log.hpp
)

#This will be the main output of our command
message("AM4UTILS_PUBLIC_HEADERS: ${AM4UTILS_HEADERS}")
# set(DOXYGEN_INDEX_FILE ${CMAKE_CURRENT_SOURCE_DIR}/html/index.html)

# add_custom_command(OUTPUT ${DOXYGEN_INDEX_FILE}
#                    DEPENDS ${AM4UTILS_PUBLIC_HEADERS}
#                    COMMAND ${DOXYGEN_EXECUTABLE} Doxyfile
#                    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
#                    MAIN_DEPENDENCY Doxyfile
#                    COMMENT "Generating docs")

# add_custom_target(Doxygen ALL DEPENDS ${DOXYGEN_INDEX_FILE})



# find_package(Doxygen)

# if (DOXYGEN_FOUND)
#     # set input and output files
#     set(DOXYGEN_INPUT_DIR ${PROJECT_SOURCE_DIR}/CatCutifier)
#     set(DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/docs/doxygen)
#     set(DOXYGEN_INDEX_FILE ${DOXYGEN_OUTPUT_DIR}/html/index.html)
#     set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in)
#     set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile.out)

#     # request to configure the file
#     configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
#     message("Doxygen build started")

#     # Note: do not put "ALL" - this builds docs together with application EVERY TIME!
#     add_custom_target(
#         docs
#         COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
#         WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
#         COMMENT "Generating API documentation with Doxygen"
#         VERBATIM
#     )
# else (DOXYGEN_FOUND)
#     message("Doxygen need to be installed to generate the doxygen documentation")
# endif (DOXYGEN_FOUND)