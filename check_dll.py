import os
import sys
from pathlib import Path

def check_dll_dependencies():
    """Check DLL dependencies and paths."""
    print("Python executable:", sys.executable)
    print("\nPython path:")
    for p in sys.path:
        print(f"  {p}")
    
    print("\nEnvironment PATH:")
    for p in os.environ.get("PATH", "").split(os.pathsep):
        print(f"  {p}")
    
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
        print("Renderer status:", renderer.status.__dict__)
        
    except ImportError as e:
        print("\nFailed to import:", str(e))
        
        # Try to find the module
        import importlib.util
        spec = importlib.util.find_spec("dx11_renderer")
        if spec:
            print("Module found at:", spec.origin)
        else:
            print("Module not found in sys.path")

if __name__ == "__main__":
    check_dll_dependencies()
