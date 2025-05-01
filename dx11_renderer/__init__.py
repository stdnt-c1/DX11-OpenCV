"""DirectX 11 accelerated image processing for real-time video."""

import os
import sys
from pathlib import Path

def _find_vs_runtime():
    """Find Visual Studio runtime path."""
    possible_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Redist\MSVC\14.38.33130\x64\Microsoft.VC143.CRT",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Redist\MSVC\14.38.33130\x64\Microsoft.VC143.CRT",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Professional\VC\Redist\MSVC\14.38.33130\x64\Microsoft.VC143.CRT",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def _find_dx_runtime():
    """Find DirectX runtime paths."""
    dx_paths = [
        r"C:\Program Files (x86)\Windows Kits\10\Redist\D3D",
        r"C:\Windows\System32",
        r"C:\Program Files (x86)\Microsoft DirectX SDK (June 2010)\Redist\x64",
    ]
    
    found_paths = []
    for path in dx_paths:
        if os.path.exists(path):
            found_paths.append(path)
    return found_paths

def _initialize():
    """Initialize the module by setting up DLL search paths."""
    if sys.platform == "Windows":
        # Add the package directory to DLL search path
        module_dir = Path(__file__).parent.absolute()
        if str(module_dir) not in os.environ.get("PATH", "").split(os.pathsep):
            os.add_dll_directory(str(module_dir))
            print(f"Added module directory to DLL search path: {module_dir}")

        # Add Visual Studio runtime path
        vs_path = _find_vs_runtime()
        if vs_path:
            os.add_dll_directory(vs_path)
            print(f"Added VS runtime path: {vs_path}")

        # Add DirectX runtime paths
        dx_paths = _find_dx_runtime()
        for path in dx_paths:
            os.add_dll_directory(path)
            print(f"Added DirectX path: {path}")
            # Also add subdirectories containing D3D DLLs
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    if any(f.lower().startswith('d3d') for f in files):
                        try:
                            os.add_dll_directory(root)
                            print(f"Added DirectX subdirectory: {root}")
                        except OSError:
                            pass

        # Add DirectXTK path from our build
        dxtk_path = module_dir / "extern" / "DirectXTK" / "bin" / "Windows10-x64" / "Release"
        if dxtk_path.exists():
            os.add_dll_directory(str(dxtk_path))
            print(f"Added DirectXTK path: {dxtk_path}")

        # Diagnose missing DLLs
        _diagnose_missing_dlls()

def _diagnose_missing_dlls():
    """Diagnose missing DLLs by attempting to load them manually."""
    import ctypes
    module_dir = Path(__file__).parent

    # List of DLLs to check
    dlls_to_check = [
        "d3d11.dll",
        "dxgi.dll",
        "dx11_renderer_core.dll",
    ]

    print("\nDiagnosing missing DLLs:")
    for dll in dlls_to_check:
        try:
            ctypes.WinDLL(str(module_dir / dll))
            print(f"  Successfully loaded {dll}")
        except Exception as e:
            print(f"  Failed to load {dll}: {e}")

_initialize()

try:
    from ._core import (
        DX11Renderer,
        ProcessingParams,
        RendererStatus,
    )

    __all__ = ["DX11Renderer", "ProcessingParams", "RendererStatus"]
    __version__ = "1.0.0"

except ImportError as e:
    import sys
    print(f"Failed to import DX11Renderer components. Error: {e}", file=sys.stderr)
    print("Module directory contents:", file=sys.stderr)
    try:
        module_dir = Path(__file__).parent
        for f in module_dir.glob("*"):
            print(f"  {f.name}", file=sys.stderr)
        
        print("\nAttempting to load DLLs directly:", file=sys.stderr)
        import ctypes
        try:
            d3d11 = ctypes.WinDLL("d3d11")
            print("  Successfully loaded d3d11.dll", file=sys.stderr)
        except Exception as e:
            print(f"  Failed to load d3d11.dll: {e}", file=sys.stderr)
        
        try:
            core = ctypes.CDLL(str(module_dir / "dx11_renderer_core.dll"))
            print("  Successfully loaded dx11_renderer_core.dll", file=sys.stderr)
        except Exception as e:
            print(f"  Failed to load dx11_renderer_core.dll: {e}", file=sys.stderr)
    
    except Exception as e:
        print(f"Error during diagnostics: {e}", file=sys.stderr)
    print("Please ensure the package is installed correctly and all dependencies are available.", file=sys.stderr)
    raise
