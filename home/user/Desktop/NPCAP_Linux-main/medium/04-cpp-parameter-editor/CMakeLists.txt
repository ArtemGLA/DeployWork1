cmake_minimum_required(VERSION 3.16)

project(parameter-editor VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt5 REQUIRED COMPONENTS Widgets)

set(SOURCES
    src/main.cpp
    src/mainwindow.cpp
    src/parametermodel.cpp
    # src/parameterdelegate.cpp
    src/parameterschema.cpp
)

set(HEADERS
    src/mainwindow.h
    src/parameter.h
    src/parametermodel.h
    # src/parameterdelegate.h
    # src/parameterschema.h
)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_link_libraries(${PROJECT_NAME} PRIVATE Qt5::Widgets)

# Copy data files
file(COPY data DESTINATION ${CMAKE_BINARY_DIR})
