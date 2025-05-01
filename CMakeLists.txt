cmake_minimum_required(VERSION 3.15)
cmake_policy(SET CMP0048 NEW)
project(dx11_renderer VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard and enable exports
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# Enable PIC for shared libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Output directories - using local package
set(OUTPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/localpackage/dx11_renderer")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR})

# Find packages
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(OpenCV REQUIRED)

# DirectX 11 libraries
if(WIN32)
    set(DX11_LIBS "d3d11.lib" "dxgi.lib" "d3dcompiler.lib")
endif()

# DirectXTK
set(DIRECTXTK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/extern/DirectXTK")
add_subdirectory(${DIRECTXTK_DIR})

# Core library
add_library(dx11_renderer_core SHARED
    src/dx11_renderer.cpp
    include/dx11_renderer.h
)

target_include_directories(dx11_renderer_core
    PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    PRIVATE
        ${OpenCV_INCLUDE_DIRS}
        ${DIRECTXTK_DIR}/Inc
)

target_compile_definitions(dx11_renderer_core
    PRIVATE
        DX11_RENDERER_EXPORTS
        _CRT_SECURE_NO_WARNINGS
)

target_link_libraries(dx11_renderer_core
    PRIVATE 
        ${DX11_LIBS}
        ${OpenCV_LIBS}
        DirectXTK
)

# Python module
pybind11_add_module(_core MODULE
    src/python_bindings.cpp
)

target_include_directories(_core
    PRIVATE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

target_link_libraries(_core
    PRIVATE
        dx11_renderer_core
        ${OpenCV_LIBS}
)

# Set output names and locations
set_target_properties(dx11_renderer_core PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${OUTPUT_DIR}"
    LIBRARY_OUTPUT_DIRECTORY "${OUTPUT_DIR}"
    ARCHIVE_OUTPUT_DIRECTORY "${OUTPUT_DIR}"
)

set_target_properties(_core PROPERTIES 
    RUNTIME_OUTPUT_DIRECTORY "${OUTPUT_DIR}"
    LIBRARY_OUTPUT_DIRECTORY "${OUTPUT_DIR}"
    ARCHIVE_OUTPUT_DIRECTORY "${OUTPUT_DIR}"
    PREFIX ""
    SUFFIX ".pyd"
)