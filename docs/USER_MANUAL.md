# DX11 Renderer Library User Manual

## Overview
The DX11 Renderer library provides hardware-accelerated image processing capabilities using DirectX 11 for Python applications. It's designed to work seamlessly with OpenCV and enables real-time video processing.

## Installation

### Prerequisites
- Windows 10 or later
- Python 3.8-3.12
- DirectX 11 compatible GPU
- Visual C++ Redistributable 2019 or later
- OpenCV-Python 4.0.0 or later

### Installing the Package
```bash
pip install dx11_renderer
```

## Basic Usage

### Importing the Library
```python
import dx11_renderer
from dx11_renderer import DX11Renderer, ProcessingParams
```

### Creating a Renderer Instance
```python
# Initialize the renderer
renderer = dx11_renderer.DX11Renderer()

# Verify initialization
if not renderer.status.isInitialized:
    print(f"Initialization failed: {renderer.status.lastError}")
    exit(1)
```

### Processing Parameters
```python
# Create and configure processing parameters
params = dx11_renderer.ProcessingParams()
params.brightness = 1.2  # Range: 0.0 - 2.0
params.contrast = 1.1    # Range: 0.0 - 2.0
params.saturation = 1.1  # Range: 0.0 - 2.0
params.gamma = 1.0      # Range: 0.1 - 2.0

# Update renderer with new parameters
renderer.update_processing_params(params)
```

### Processing Frames
```python
import cv2
import numpy as np

# Read an image or frame
frame = cv2.imread("input.jpg")
# Or capture from camera
# ret, frame = cap.read()

# Process the frame
processed_frame = renderer.process_frame(frame)

# Display or save the result
cv2.imshow("Result", processed_frame)
cv2.waitKey(0)
```

### Real-time Video Processing Example
```python
import cv2
import dx11_renderer
import time

def process_video():
    # Initialize
    cap = cv2.VideoCapture(0)
    renderer = dx11_renderer.DX11Renderer()
    
    # Set processing parameters
    params = dx11_renderer.ProcessingParams()
    params.brightness = 1.2
    params.contrast = 1.1
    params.saturation = 1.1
    params.gamma = 1.0
    renderer.update_processing_params(params)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame with DX11
        result = renderer.process_frame(frame)
        
        # Display result
        cv2.imshow("DX11 Output", result)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video()
```

## Import Variations and Constructor Usage

### Import Patterns
The library supports multiple import patterns. Choose the one that works best for your use case:

```python
# Standard import (recommended)
import dx11_renderer
renderer = dx11_renderer.DX11Renderer()

# Direct class import
from dx11_renderer import DX11Renderer, ProcessingParams
renderer = DX11Renderer()  # Note: Must use default constructor

# Core module import (advanced usage)
from dx11_renderer._core import DX11Renderer
renderer = DX11Renderer()  # Use with caution, API may change
```

### Constructor Usage

1. **Default Constructor (Recommended)**
```python
import dx11_renderer
renderer = dx11_renderer.DX11Renderer()  # Uses default initialization
```

2. **Direct Core Constructor**
```python
from dx11_renderer._core import DX11Renderer
renderer = DX11Renderer()  # Must use empty constructor
```

### Common TypeError Solutions

If you encounter this error:
```python
TypeError: __init__(): incompatible constructor arguments. The following argument types are supported:
    1. dx11_renderer._core.DX11Renderer()
```

The solution is to:
1. Use the default constructor without arguments
2. Ensure you're using one of the supported import patterns above
3. Update processing parameters after initialization:

```python
# Correct usage
import dx11_renderer
renderer = dx11_renderer.DX11Renderer()  # Create with default constructor

# Then set parameters
params = dx11_renderer.ProcessingParams()
params.brightness = 1.2
renderer.update_processing_params(params)

# Incorrect usage - will raise TypeError
renderer = dx11_renderer.DX11Renderer(  # Don't pass arguments to constructor
    brightness=1.2,
    contrast=1.1
)
```

## Troubleshooting

### Common Issues

1. **DLL Load Errors**
```
Error: DLL load failed while importing _core
```
Solution: Ensure Visual C++ Redistributable 2019 is installed and all required DLLs are in the correct path.

2. **Initialization Failures**
```
Initialization failed: Device creation failed
```
Solution: Verify DirectX 11 support on your GPU and update graphics drivers.

3. **Memory Errors**
If you encounter memory-related errors, ensure you're properly releasing resources:
```python
# Clean up resources when done
del renderer
cv2.destroyAllWindows()
```

### Import and Constructor Issues

4. **TypeError with Constructor Arguments**
```
TypeError: __init__(): incompatible constructor arguments.
```
Solution: Use the default constructor without arguments and set parameters after initialization:
```python
# Correct
renderer = dx11_renderer.DX11Renderer()
params = dx11_renderer.ProcessingParams()
params.brightness = 1.2
renderer.update_processing_params(params)
```

5. **Import Errors**
```
ImportError: DLL load failed while importing _core
```
Solution: Ensure you're using a supported import pattern and all dependencies are installed:
```python
# Try these import patterns
import dx11_renderer  # Recommended
# or
from dx11_renderer import DX11Renderer  # Alternative
# or
from dx11_renderer._core import DX11Renderer  # Advanced usage
```

### Best Practices

1. **Resource Management**
- Initialize the renderer once and reuse it
- Properly close windows and release resources
- Check initialization status before processing

2. **Performance Optimization**
- Process frames at appropriate resolutions
- Monitor processing times
- Use appropriate parameter values

3. **Error Handling**
```python
try:
    renderer = dx11_renderer.DX11Renderer()
    if not renderer.status.isInitialized:
        raise RuntimeError(f"Initialization failed: {renderer.status.lastError}")
    
    # Processing code here
    
except Exception as e:
    print(f"Error: {e}")
finally:
    # Cleanup code here
    pass
```

## API Reference

### DX11Renderer Class
```python
class DX11Renderer:
    """DirectX 11 hardware-accelerated image processing renderer."""
    
    def __init__(self):
        """Initialize the DirectX 11 renderer."""
        pass
        
    def process_frame(self, frame):
        """Process a single frame using current parameters."""
        pass
        
    def update_processing_params(self, params):
        """Update processing parameters."""
        pass
        
    @property
    def status(self):
        """Get current renderer status."""
        pass
```

### ProcessingParams Class
```python
class ProcessingParams:
    """Image processing parameters configuration."""
    
    brightness: float  # Range: 0.0 - 2.0
    contrast: float   # Range: 0.0 - 2.0
    saturation: float # Range: 0.0 - 2.0
    gamma: float      # Range: 0.1 - 2.0
```

### Status Class
```python
class Status:
    """Renderer status information."""
    
    isInitialized: bool  # Initialization status
    lastError: str      # Last error message
```

## Support and Resources

- [GitHub Repository](https://github.com/stdnt-c1/DX11-OpenCV)
- [Issue Tracker](https://github.com/stdnt-c1/DX11-OpenCV/issues)
- [Release Notes](https://github.com/stdnt-c1/DX11-OpenCV/releases)
