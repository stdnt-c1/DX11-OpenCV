# DX11 Renderer Library Development Manual

## Architecture Overview

### Core Components

1. **DirectX 11 Core (`dx11_renderer_core.dll`)**
   - Hardware-accelerated rendering
   - Shader management
   - Resource handling

2. **Python Bindings (`_core.pyd`)**
   - pybind11-based interface
   - Type conversions
   - Exception handling

3. **Python Package (`dx11_renderer`)**
   - High-level interface
   - Parameter management
   - Resource lifecycle

### Directory Structure
```
dx11_renderer/
├── include/          # C++ headers
├── src/             # C++ source files
├── dx11_renderer/   # Python package
├── tests/           # Test suite
└── extern/          # External dependencies
```

## Building from Source

### Prerequisites
- Visual Studio 2019 or later
- CMake 3.15 or later
- Python 3.8-3.12 with development files
- DirectX SDK
- OpenCV Python package
- pybind11

### Build Steps

1. **Clone Repository**
```bash
git clone https://github.com/stdnt-c1/DX11-OpenCV.git
cd DX11-OpenCV
```

2. **Configure Build**
```bash
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
```

3. **Build Library**
```bash
cmake --build build --config Release
```

4. **Install Package**
```bash
pip install -e .
```

## Development Guidelines

### Adding New Features

1. **C++ Implementation**
```cpp
// In include/dx11_renderer.h
class DX11Renderer {
public:
    // Add new method declaration
    bool new_feature(const cv::Mat& input, cv::Mat& output);
};

// In src/dx11_renderer.cpp
bool DX11Renderer::new_feature(const cv::Mat& input, cv::Mat& output) {
    // Implementation
}
```

2. **Python Bindings**
```cpp
// In src/python_bindings.cpp
PYBIND11_MODULE(_core, m) {
    py::class_<DX11Renderer>(m, "DX11Renderer")
        .def("new_feature", &DX11Renderer::new_feature)
        .def_property_readonly("status", &DX11Renderer::get_status);
}
```

### Error Handling

1. **C++ Level**
```cpp
// Use exception classes for error handling
class DX11RendererError : public std::runtime_error {
public:
    explicit DX11RendererError(const char* message)
        : std::runtime_error(message) {}
};

// In methods
if (FAILED(hr)) {
    throw DX11RendererError("Operation failed");
}
```

2. **Python Level**
```python
def safe_process(frame):
    try:
        return renderer.process_frame(frame)
    except RuntimeError as e:
        logger.error(f"Processing failed: {e}")
        return None
```

### Testing

1. **Unit Tests**
```python
# In tests/test_dx11_renderer.py
def test_renderer_initialization():
    renderer = dx11_renderer.DX11Renderer()
    assert renderer.status.isInitialized
    assert not renderer.status.lastError

def test_processing_params():
    params = dx11_renderer.ProcessingParams()
    params.brightness = 1.5
    assert params.brightness == 1.5
```

2. **Integration Tests**
```python
# In tests/test_opencv_dx11.py
def test_opencv_integration():
    frame = cv2.imread("test_image.jpg")
    renderer = dx11_renderer.DX11Renderer()
    result = renderer.process_frame(frame)
    assert result is not None
    assert result.shape == frame.shape
```

### Performance Optimization

1. **Memory Management**
- Use smart pointers in C++
- Implement proper cleanup in destructors
- Monitor GPU memory usage

2. **Buffer Handling**
```cpp
// Reuse buffers when possible
if (!m_textureBuffer || m_textureSize != frameSize) {
    create_texture_buffer(frameSize);
}
```

3. **Shader Optimization**
```hlsl
// Use efficient shader techniques
[numthreads(16, 16, 1)]
void CSMain(uint3 DTid : SV_DispatchThreadID) {
    // Optimized computation
}
```

## Debugging

### Common Debug Tools

1. **DirectX Debug Layer**
```cpp
#ifdef _DEBUG
    device_flags |= D3D11_CREATE_DEVICE_DEBUG;
#endif
```

2. **Python Debug Tools**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("dx11_renderer")
```

### Troubleshooting Build Issues

1. **DLL Dependencies**
Check dependency paths:
```python
import os
os.environ["PATH"] = r"path/to/dlls;" + os.environ["PATH"]
```

2. **Build Configuration**
Verify CMake configuration:
```bash
cmake -LA
```

## Release Process

1. **Version Update**
- Update version in `setup.py`
- Update changelog
- Tag release

2. **Build Verification**
```bash
python build_verify.py
```

3. **Package and Deploy**
```bash
python -m build
twine upload dist/*
```

## Contributing

1. **Code Style**
- Follow PEP 8 for Python
- Use clang-format for C++
- Document public APIs

2. **Pull Requests**
- Include tests
- Update documentation
- Follow commit message conventions

3. **Documentation**
- Update both developer and user manuals
- Include examples
- Document breaking changes

## Support

### Getting Help
- GitHub Issues
- Documentation
- Community Discord

### Reporting Bugs
Include:
- System information
- Build configuration
- Minimal reproduction
