# DirectX 11 Renderer
A high-performance DirectX 11 based image processing library for Python with YOLO integration.

## Installation
```bash
pip install dx11-renderer
```

## Requirements
- Windows 10/11
- Python 3.8+
- NVIDIA/AMD/Intel GPU with DirectX 11 support
- Visual C++ Redistributable 2022
- OpenCV (installed automatically as dependency)

## Features
- Real-time image processing using DirectX 11 compute shaders
- Hardware-accelerated color correction and image enhancement
- YOLO object detection integration
- Performance monitoring and status tracking
- Easy-to-use Python API

## Usage
```python
import cv2
import numpy as np
from dx11_renderer import DX11Renderer, ProcessingParams

# Create renderer instance
renderer = DX11Renderer()

# Configure processing parameters
params = ProcessingParams()
params.brightness = 1.2
params.contrast = 1.1
params.saturation = 1.1
params.gamma = 0.9

renderer.update_processing_params(params)

# Process an image
img = cv2.imread("input.jpg")
processed = renderer.process_frame(img)

# Get performance metrics
status = renderer.status
print(f"Processing time: {status.lastProcessingTime}ms")
```

## Building from Source
Requirements:
- CMake 3.15+
- Visual Studio 2022 Build Tools
- Python development files

```bash
git clone https://github.com/yourusername/DX11-OpenCV.git
cd DX11-OpenCV
python -m pip install -e .
```
