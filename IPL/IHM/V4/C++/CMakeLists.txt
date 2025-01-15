cmake_minimum_required(VERSION 3.5)

project(YourAppName)

find_package(Qt5 COMPONENTS Widgets REQUIRED)

set(SOURCES main.cpp)

add_executable(${PROJECT_NAME} ${SOURCES})

target_link_libraries(${PROJECT_NAME} Qt5::Widgets)