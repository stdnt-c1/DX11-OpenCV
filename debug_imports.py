import os
import sys
from pathlib import Path

def debug_imports():
    print("Python executable:", sys.executable)
    print("Python path:", sys.path)
    print("\nLooking for dx11_renderer module...")
    
    try:
        import dx11_renderer
        print("\nModule found!")
        print("Module location:", dx11_renderer.__file__)
        print("Module contents:", dir(dx11_renderer))
    except ImportError as e:
        print("\nFailed to import:", str(e))
        
        # Check the package directory
        pkg_dir = Path(__file__).parent / "dx11_renderer"
        print("\nPackage directory contents:")
        if pkg_dir.exists():
            for item in pkg_dir.glob("*"):
                print(f"  {item.name}")
        else:
            print("  Package directory not found!")

if __name__ == "__main__":
    debug_imports()
