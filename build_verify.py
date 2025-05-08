import os
import sys
import glob
import platform
import ctypes

def check_dll_dependencies(dll_path):
    try:
        dll = ctypes.WinDLL(dll_path)
        print(f"✓ Successfully loaded {os.path.basename(dll_path)}")
        return True
    except Exception as e:
        print(f"✗ Failed to load {os.path.basename(dll_path)}: {e}")
        return False

def verify_build_outputs():
    required_files = {
        'core': ['dx11_renderer_core.dll', '_core.pyd'],
        'opencv': ['opencv_world4110.dll'],
        'vc_redist': [
            'concrt140.dll', 'msvcp140.dll', 'msvcp140_1.dll',
            'msvcp140_2.dll', 'vcruntime140.dll'
        ],
        'directx': ['D3DCompiler_47.dll']
    }

    build_paths = ['build', 'dx11_renderer', 'localpackage/dx11_renderer']
    
    for category, files in required_files.items():
        print(f"\nChecking {category} files:")
        for file in files:
            found = False
            for path in build_paths:
                file_path = os.path.join(path, file)
                if os.path.exists(file_path):
                    found = True
                    check_dll_dependencies(file_path)
                    break
            if not found:
                print(f"✗ Missing file: {file}")

if __name__ == '__main__':
    print("Verifying build outputs...")
    verify_build_outputs()
