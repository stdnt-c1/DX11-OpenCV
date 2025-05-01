import os
import sys
import ctypes
from pathlib import Path

def list_loaded_dlls():
    """List all DLLs loaded in the current process."""
    print("\nLoaded DLLs:")
    process = ctypes.windll.kernel32.GetCurrentProcess()
    modules = (ctypes.c_void_p * 1024)()
    needed = ctypes.c_ulong()
    ctypes.windll.psapi.EnumProcessModules(
        process,
        modules,
        ctypes.sizeof(modules),
        ctypes.byref(needed)
    )
    count = needed.value // ctypes.sizeof(ctypes.c_void_p)
    
    for i in range(count):
        path = ctypes.create_string_buffer(1024)
        ctypes.windll.psapi.GetModuleFileNameExA(
            process,
            modules[i],
            path,
            ctypes.sizeof(path)
        )
        print(f"  {path.value.decode()}")

def check_dx11_deps():
    """Check DirectX 11 dependencies."""
    print("Python executable:", sys.executable)
    print("\nPython path:")
    for p in sys.path:
        print(f"  {p}")
    
    try:
        # Try loading D3D11 directly first
        print("\nTrying to load D3D11...")
        d3d11 = ctypes.WinDLL("d3d11")
        print("Successfully loaded D3D11")
    except Exception as e:
        print(f"Failed to load D3D11: {e}")
    
    try:
        import dx11_renderer
        print("\nSuccessfully imported dx11_renderer")
        print("Package location:", dx11_renderer.__file__)
        print("\nPackage directory contents:")
        pkg_dir = Path(dx11_renderer.__file__).parent
        for f in pkg_dir.glob("*"):
            print(f"  {f.name}")
        
        # Try creating renderer instance
        renderer = dx11_renderer.DX11Renderer()
        print("\nSuccessfully created renderer instance")
        print("Renderer status:")
        print(f"  isInitialized: {renderer.status.isInitialized}")
        print(f"  textureWidth: {renderer.status.textureWidth}")
        print(f"  textureHeight: {renderer.status.textureHeight}")
        print(f"  lastProcessingTime: {renderer.status.lastProcessingTime}")
        print(f"  lastError: {renderer.status.lastError}")
        
    except ImportError as e:
        print(f"\nFailed to import: {e}")
        
        # Try to find the module
        import importlib.util
        spec = importlib.util.find_spec("dx11_renderer")
        if spec:
            print("Module found at:", spec.origin)
            
            # List the directory contents
            module_dir = Path(spec.origin).parent
            print("\nModule directory contents:")
            for f in module_dir.glob("*"):
                print(f"  {f.name}")
        else:
            print("Module not found in sys.path")
    
    # Show loaded DLLs
    list_loaded_dlls()

if __name__ == "__main__":
    check_dx11_deps()
