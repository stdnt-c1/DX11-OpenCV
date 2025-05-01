import os
import sys
import site

def debug_import():
    print("Python executable:", sys.executable)
    print("\nPython path:")
    for p in sys.path:
        print(f"  {p}")
    
    print("\nSite packages:")
    for p in site.getsitepackages():
        print(f"  {p}")
    
    try:
        import dx11_renderer
        print("\nSuccessfully imported dx11_renderer")
        print("Package location:", dx11_renderer.__file__)
        
        # Try creating renderer instance
        renderer = dx11_renderer.DX11Renderer()
        print("Successfully created renderer instance")
        print("Renderer status:", renderer.status.__dict__)
        
    except ImportError as e:
        print("\nFailed to import:", str(e))
        
        # Check module location
        import importlib.util
        spec = importlib.util.find_spec("dx11_renderer")
        if spec:
            print("Module found at:", spec.origin)
        else:
            print("Module not found in sys.path")

if __name__ == "__main__":
    debug_import()
