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

# Handle OpenCV from pip installation
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import os, cv2; print(os.path.dirname(cv2.__file__))"
    OUTPUT_VARIABLE OPENCV_PYTHON_PATH
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE PYTHON_OPENCV_RESULT
)

if(NOT PYTHON_OPENCV_RESULT EQUAL 0)
    message(FATAL_ERROR "Failed to locate OpenCV Python package")
endif()

execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import cv2; print(cv2.__version__)"
    OUTPUT_VARIABLE OPENCV_VERSION
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "Found OpenCV Python package at: ${OPENCV_PYTHON_PATH}")
message(STATUS "OpenCV version: ${OPENCV_VERSION}")

# Try to find OpenCV DLL in multiple locations
set(OpenCV_DLL_FOUND FALSE)

# First check in workspace directory
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/opencv_world4110.dll")
    set(OpenCV_WORLD_DLL "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/opencv_world4110.dll")
    set(OpenCV_DLL_FOUND TRUE)
    message(STATUS "Found OpenCV DLL in workspace: ${OpenCV_WORLD_DLL}")
else()
    # Get site-packages paths
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -c "import os, site; print(';'.join(site.getsitepackages()))"
        OUTPUT_VARIABLE SITE_PACKAGES_PATHS
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    # Convert paths to CMake format
    string(REPLACE "\\" "/" SITE_PACKAGES_PATHS "${SITE_PACKAGES_PATHS}")
    
    # Build search paths list
    set(OpenCV_SEARCH_PATHS
        "${OPENCV_PYTHON_PATH}"
        "${OPENCV_PYTHON_PATH}/cv2"
        "${OPENCV_PYTHON_PATH}/python-3"
        "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer"
        "${SITE_PACKAGES_PATHS}"
    )

    # Try to get DLL name from Python
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -c "import cv2, os; print([f for f in os.listdir(os.path.dirname(cv2.__file__)) if 'opencv_world' in f and f.endswith('.dll')][0])"
        OUTPUT_VARIABLE OPENCV_DLL_NAME
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE RESULT
    )

    if(RESULT EQUAL 0 AND OPENCV_DLL_NAME)
        foreach(SEARCH_PATH ${OpenCV_SEARCH_PATHS})
            message(STATUS "Searching for OpenCV DLLs in: ${SEARCH_PATH}")
            if(EXISTS "${SEARCH_PATH}/${OPENCV_DLL_NAME}")
                set(OpenCV_WORLD_DLL "${SEARCH_PATH}/${OPENCV_DLL_NAME}")
                set(OpenCV_DLL_FOUND TRUE)
                break()
            endif()
            
            # Try one level deeper
            if(EXISTS "${SEARCH_PATH}/cv2/${OPENCV_DLL_NAME}")
                set(OpenCV_WORLD_DLL "${SEARCH_PATH}/cv2/${OPENCV_DLL_NAME}")
                set(OpenCV_DLL_FOUND TRUE)
                break()
            endif()
        endforeach()
    endif()
endif()

if(NOT OpenCV_DLL_FOUND)
    message(FATAL_ERROR "Could not find OpenCV world DLL in any of the search paths. Searched in:\n${OpenCV_SEARCH_PATHS}")
endif()

# Set OpenCV paths and verify existence
if(OpenCV_DLL_FOUND)
    get_filename_component(OpenCV_DLL_DIR ${OpenCV_WORLD_DLL} DIRECTORY)
    
    # Set OpenCV paths
    set(OpenCV_DIR "${OpenCV_DLL_DIR}")
    set(OpenCV_INCLUDE_DIRS 
        "${OpenCV_DLL_DIR}/include" 
        "${OPENCV_PYTHON_PATH}/include"
        "${OPENCV_PYTHON_PATH}"
        "${OPENCV_PYTHON_PATH}/cv2"
    )
    set(OpenCV_LIB_PATH "${OpenCV_DLL_DIR}")
    set(OpenCV_LIBS "${OpenCV_WORLD_DLL}")
    
    # Verify DLL exists and is readable
    if(NOT EXISTS "${OpenCV_LIBS}")
        message(FATAL_ERROR "OpenCV DLL not found at: ${OpenCV_LIBS}")
    endif()
    
    # Ensure the DLL can be copied
    file(COPY "${OpenCV_LIBS}" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/opencv_world4110.dll")
        message(FATAL_ERROR "Failed to copy OpenCV DLL to: ${CMAKE_CURRENT_BINARY_DIR}")
    endif()
    
    message(STATUS "OpenCV DLL verified at: ${OpenCV_WORLD_DLL}")
    message(STATUS "OpenCV include directories: ${OpenCV_INCLUDE_DIRS}")
    message(STATUS "OpenCV library path: ${OpenCV_LIB_PATH}")
else()
    message(FATAL_ERROR "Could not find OpenCV DLL. Searched in:\n${OpenCV_SEARCH_PATHS}\n\nPlease ensure opencv-python is installed correctly.")
endif()

message(STATUS "Using OpenCV DLL: ${OpenCV_LIBS}")
message(STATUS "OpenCV include dirs: ${OpenCV_INCLUDE_DIRS}")

# Ensure output directories exist
file(MAKE_DIRECTORY ${OUTPUT_DIR})
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

# Copy OpenCV DLL and its dependencies
file(COPY ${OpenCV_WORLD_DLL} DESTINATION ${OUTPUT_DIR})
file(COPY ${OpenCV_WORLD_DLL} DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

# Copy Visual C++ Runtime DLLs if they exist
set(VC_REDIST_DLLS
    "concrt140.dll"
    "msvcp140.dll"
    "msvcp140_1.dll"
    "msvcp140_2.dll"
    "msvcp140_atomic_wait.dll"
    "msvcp140_codecvt_ids.dll"
    "vccorlib140.dll"
    "vcruntime140.dll"
    "vcruntime140_1.dll"
    "vcruntime140_threads.dll"
)

foreach(DLL ${VC_REDIST_DLLS})
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/${DLL}")
        file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/${DLL}" 
             DESTINATION ${OUTPUT_DIR})
        file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/${DLL}" 
             DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
        message(STATUS "Copied ${DLL} to output directories")
    endif()
endforeach()

# Copy DirectX related DLLs
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/D3DCompiler_47.dll")
    file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/D3DCompiler_47.dll" 
         DESTINATION ${OUTPUT_DIR})
    file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/D3DCompiler_47.dll" 
         DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    message(STATUS "Copied D3DCompiler_47.dll to output directories")
endif()

include_directories(${OpenCV_INCLUDE_DIRS} ${OPENCV_PYTHON_PATH})

# Set Python and pybind11 options
set(PYBIND11_PYTHON_VERSION "${Python3_VERSION}")
set(PYBIND11_FINDPYTHON ON)
set(PYBIND11_PREFER_THIRD_PARTY_PYTHON ON)

# Try to find pybind11 from different possible locations
find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/pybind11/CMakeLists.txt")
        add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/extern/pybind11")
    else()
        message(FATAL_ERROR "pybind11 not found and not available as submodule")
    endif()
endif()

# Set MSVC-specific options
if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc /MP")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /Ob2")
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    
    # Check MSVC version and set appropriate flags
    if(MSVC_VERSION GREATER_EQUAL 1920)     # VS 2019 or newer
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Zc:__cplusplus")
    endif()
endif()

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

# Verify and copy dx11_renderer_core.dll
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/dx11_renderer_core.dll")
    file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/dx11_renderer_core.dll" DESTINATION ${OUTPUT_DIR})
    file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/dx11_renderer_core.dll" DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    message(STATUS "Copied dx11_renderer_core.dll to output directories.")
else()
    message(FATAL_ERROR "dx11_renderer_core.dll not found in dx11_renderer directory.")
endif()

# Verify and copy _core.pyd
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/_core.pyd")
    file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/_core.pyd" DESTINATION ${OUTPUT_DIR})
    file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/dx11_renderer/_core.pyd" DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    message(STATUS "Copied _core.pyd to output directories.")
else()
    message(FATAL_ERROR "_core.pyd not found in dx11_renderer directory.")
endif()

# Fallback for OpenCV detection when installed via pip
if(NOT OpenCV_DIR)
    message(WARNING "OpenCV_DIR is not set. Attempting to locate OpenCV via Python.")
    execute_process(
        COMMAND python -c "import os, cv2; print(os.path.dirname(cv2.__file__))"
        OUTPUT_VARIABLE OPENCV_PYTHON_PATH
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    if(OPENCV_PYTHON_PATH)
        set(OpenCV_DIR "${OPENCV_PYTHON_PATH}")
        message(STATUS "Using OpenCV from Python: ${OpenCV_DIR}")
    else()
        message(FATAL_ERROR "Failed to locate OpenCV. Please set OpenCV_DIR manually.")
    endif()
endif()