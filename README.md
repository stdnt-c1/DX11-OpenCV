# DirectX 11 Renderer for Python (`dx11-renderer`)

A high-performance DirectX 11 based image processing library for Python that provides GPU-accelerated image and video processing capabilities. This library utilizes DirectX 11 compute shaders for real-time processing, integrates with OpenCV, and supports YOLO object detection.

[![PyPI version](https://badge.fury.io/py/dx11-renderer.svg)](https://pypi.org/project/dx11-renderer/)
[![Python Support](https://img.shields.io/pypi/pyversions/dx11-renderer.svg)](https://pypi.org/project/dx11-renderer/)
[![Build Status](https://github.com/stdnt-c1/DX11-OpenCV/actions/workflows/build.yml/badge.svg)](https://github.com/stdnt-c1/DX11-OpenCV/actions)

## Table of Contents
- [Installation](#installation)
- [Core Features](#core-features)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Release Process](#release-process)

## Installation

```bash
pip install dx11-renderer
```

## Core Features

### 1. DirectX 11 Renderer (`DX11Renderer`)
The core class that handles GPU-accelerated image processing:
```python
from dx11_renderer import DX11Renderer

renderer = DX11Renderer(
    width=1920,          # Default window width
    height=1080,         # Default window height
    enable_yolo=False,   # Enable YOLO integration
    model_path=None      # Path to YOLO model file
)
```

### 2. Processing Parameters (`ProcessingParams`)
Configure image processing settings:
```python
from dx11_renderer import ProcessingParams

params = ProcessingParams(
    brightness=1.0,    # Range: 0.0 to 2.0
    contrast=1.0,      # Range: 0.0 to 2.0
    saturation=1.0,    # Range: 0.0 to 2.0
    gamma=1.0,         # Range: 0.1 to 2.0
    hue=0.0           # Range: -180.0 to 180.0
)
```

### 3. Renderer Status (`RendererStatus`)
Monitor performance and status:
```python
status = renderer.status
print(f"FPS: {status.currentFPS}")
print(f"Processing Time: {status.lastProcessingTime}ms")
print(f"GPU Memory Usage: {status.gpuMemoryUsage}MB")
print(f"Is Initialized: {status.isInitialized}")
print(f"Last Error: {status.lastError}")
```

## Basic Usage

### 1. Single Image Processing
```python
import cv2
from dx11_renderer import DX11Renderer, ProcessingParams

# Initialize renderer
renderer = DX11Renderer()

# Configure processing parameters
params = ProcessingParams(brightness=1.2, contrast=1.1)
renderer.update_processing_params(params)

# Process image
image = cv2.imread("input.jpg")
result = renderer.process_frame(image)
cv2.imwrite("output.jpg", result)
```

### 2. Video Processing
```python
import cv2
from dx11_renderer import DX11Renderer

renderer = DX11Renderer()
cap = cv2.VideoCapture(0)  # Open webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    # Process frame
    processed = renderer.process_frame(frame)
    
    # Display result
    cv2.imshow("DX11 Output", processed)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 3. YOLO Object Detection
```python
from dx11_renderer import DX11Renderer

# Initialize with YOLO
renderer = DX11Renderer(
    enable_yolo=True,
    model_path="yolov8n.pt"  # Path to YOLO model
)

# Process frame with detection
frame = cv2.imread("input.jpg")
result, detections = renderer.detect_objects(
    frame,
    conf_threshold=0.5,    # Confidence threshold
    nms_threshold=0.45     # Non-maximum suppression threshold
)
```

## Advanced Usage

### Custom Shader Integration
```python
# Load and apply a custom shader
with open("my_shader.hlsl", "r") as f:
    shader_code = f.read()

renderer.load_custom_shader(shader_code)
```

### Asynchronous Frame Processing
```python
# For better throughput, especially in video processing
renderer.process_frame_async(frame)
```

## Advanced Examples

### Real-time Video Effects
```python
from dx11_renderer import DX11Renderer, ProcessingParams, EffectsPipeline
import cv2
import numpy as np

# Initialize with custom resolution
renderer = DX11Renderer(width=3840, height=2160)  # 4K support

# Create dynamic effect parameters
def create_wave_effect(frame_count):
    brightness = 1.0 + 0.2 * np.sin(frame_count * 0.05)
    contrast = 1.0 + 0.1 * np.cos(frame_count * 0.03)
    return ProcessingParams(brightness=brightness, contrast=contrast)

# Process video with dynamic effects
cap = cv2.VideoCapture("input.mp4")
frame_count = 0
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (3840, 2160))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Update parameters dynamically
    params = create_wave_effect(frame_count)
    renderer.update_processing_params(params)
    
    # Process frame
    result = renderer.process_frame(frame)
    out.write(result)
    frame_count += 1

cap.release()
out.release()
```

### Multi-threaded Batch Processing
```python
from dx11_renderer import DX11Renderer
import concurrent.futures
import glob
import os

def process_image(renderer, image_path):
    img = cv2.imread(image_path)
    result = renderer.process_frame(img)
    output_path = os.path.join("output", os.path.basename(image_path))
    cv2.imwrite(output_path, result)
    return output_path

# Process multiple images in parallel
renderer = DX11Renderer()
image_files = glob.glob("input/*.jpg")

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_image, renderer, img) 
              for img in image_files]
    
    for future in concurrent.futures.as_completed(futures):
        print(f"Processed: {future.result()}")
```

## Benchmarks

### Performance Considerations
- Performance varies significantly based on hardware configuration
- GPU acceleration can provide substantial speedup over CPU processing
- Memory usage scales with input resolution
- YOLO model performance depends on the specific model used

### System Requirements
- DirectX 11 compatible GPU
- Windows 10/11 (64-bit)
- 8GB RAM recommended
- CPU: Core i3/Ryzen 3 or better
- Storage: 1GB for installation

## Security Considerations

### Data Privacy
- No data is collected or transmitted
- All processing is performed locally
- Model weights are stored locally

### Safe Usage Guidelines
1. Always validate input sources
2. Implement proper error handling
3. Monitor GPU resource usage
4. Regular driver updates recommended

## Contributing Guidelines
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Code Style
- Pull Request Process
- Issue Reporting
- Feature Requests

---

## Disclaimers

### Hardware Compatibility
This software requires a DirectX 11 compatible GPU. Performance may vary based on your specific hardware configuration. Please test thoroughly with your target hardware before deploying in production environments.

### Third-party Dependencies
This project uses:
- DirectX Tool Kit (Microsoft)
- OpenCV (Intel Corporation)
- YOLO (Ultralytics)
- pybind11 (Wenzel Jakob)

All third-party components are used under their respective licenses.

### Performance Disclaimer
Performance metrics provided are based on testing with specific hardware configurations. Your results may vary depending on:
- Hardware specifications
- Driver versions
- System configuration
- Input data characteristics

### Commercial Use
While this software is open-source, commercial use should comply with the licenses of all included components. Users are responsible for ensuring compliance with third-party licenses.

---

## Support

### Community Support
- GitHub Issues: Bug reports and feature requests
- Discussions: Technical questions and usage help
- Wiki: Additional documentation and examples

### Professional Support
For professional support, custom development, or specific requirements, contact:
- Email: t23-bilal908@smkn7-smr.sch.id
- GitHub: [@stdnt-c1](https://github.com/stdnt-c1)

---

## License
Copyright (c) 2025 Muhammad Bilal Maulida. All rights reserved.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made by Muhammad Bilal Maulida

## Implementation Details

### Core Features
- DirectX 11 Compute Shader based image processing
- OpenCV integration for image and video handling
- YOLO object detection support
- Real-time video processing capabilities
- Customizable processing parameters

### Image Processing Operations
- Basic operations: brightness, contrast, saturation
- Color space transformations
- Custom shader support for advanced effects
- Frame buffer management for optimal performance

### Integration Features
- OpenCV compatible input/output
- YOLO model integration
- Asynchronous processing support
- Error handling and status reporting

### Technical Architecture
- C++ core with Python bindings via pybind11
- DirectX 11 compute shader pipeline
- Efficient memory management between CPU and GPU
- Thread-safe design for concurrent processing

## Best Practices

### Memory Management
```python
# Properly initialize and cleanup resources
renderer = DX11Renderer()
try:
    # Use renderer
    result = renderer.process_frame(frame)
finally:
    renderer.release()  # Always release resources
```

### Error Handling
```python
try:
    renderer = DX11Renderer()
    result = renderer.process_frame(frame)
except RuntimeError as e:
    print(f"Processing error: {e}")
    print(f"GPU Status: {renderer.status.lastError}")
```

### Resource Optimization
- Release GPU resources when not in use
- Process at appropriate resolution for your needs
- Monitor memory usage through status interface
- Implement frame skipping if needed for real-time applications
