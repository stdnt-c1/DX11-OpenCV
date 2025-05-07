from setuptools import setup, Extension
from setuptools.command.develop import develop
from setuptools.command.build_ext import build_ext
import os
import platform
import subprocess
import sys
import shutil
from pathlib import Path

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def build_extension(self, ext):
        ext_dir = Path(self.get_ext_fullpath(ext.name)).parent.absolute()
        build_temp = Path("build/temp").absolute()
        build_lib = Path(self.build_lib).absolute()        # Ensure directories exist
        os.makedirs(build_temp, exist_ok=True)
        os.makedirs(build_lib, exist_ok=True)

        # Configure CMake
        cfg = 'Debug' if self.debug else 'Release'
        project_dir = Path(__file__).parent.absolute()
        output_dir = project_dir / "localpackage" / "dx11_renderer"
        os.makedirs(output_dir / "Release", exist_ok=True)
        
        cmake_args = [
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={output_dir.as_posix()}",
            f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY={output_dir.as_posix()}"
        ]

        if platform.system() == "Windows":
            cmake_args += ["-G", "Visual Studio 17 2022", "-A", "x64"]

        # Run CMake configure and build
        subprocess.run(["cmake", ext.sourcedir] + cmake_args, cwd=build_temp, check=True)
        subprocess.run(["cmake", "--build", ".", "--config", cfg], cwd=build_temp, check=True)
        
        # Copy the built files to the package directory
        # Debugging logs to locate _core.pyd
        print("\n[DEBUG] Expected output directory:", output_dir)
        print("[DEBUG] Checking for _core.pyd in:", output_dir / "Release")        # Dynamically locate _core.pyd
        pyd_file = output_dir / "Release" / "_core.pyd"
        if not pyd_file.exists():
            print("[DEBUG] _core.pyd not found in Release directory. Checking other locations...")
            for root, _, files in os.walk(output_dir):
                for file in files:
                    if file.endswith("_core.pyd"):
                        pyd_file = Path(root) / file
                        print("[DEBUG] Found _core.pyd at:", pyd_file)
                        break

        # Ensure ext_dir exists
        os.makedirs(ext_dir, exist_ok=True)

        # Dynamically locate _core.pyd
        pyd_file = output_dir / "Release" / "_core.pyd"
        if not pyd_file.exists():
            print("[DEBUG] _core.pyd not found in Release directory. Checking other locations...")
            for root, _, files in os.walk(output_dir):
                for file in files:
                    if file.endswith("_core.pyd"):
                        pyd_file = Path(root) / file
                        print("[DEBUG] Found _core.pyd at:", pyd_file)
                        break

        if pyd_file.exists():
            shutil.copy2(pyd_file, ext_dir / "_core.pyd")
            print(f"[DEBUG] Successfully copied _core.pyd to: {ext_dir / '_core.pyd'}")
        else:
            raise FileNotFoundError(f"[ERROR] _core.pyd not found in expected locations. Last checked: {pyd_file}")

        # Rename _core.pyd to match the expected naming convention
        renamed_pyd_file = ext_dir / "_core.cp312-win_amd64.pyd"
        os.rename(ext_dir / "_core.pyd", renamed_pyd_file)
        print(f"[DEBUG] Renamed _core.pyd to: {renamed_pyd_file}")

class DevelopCommand(develop):
    def run(self):
        self.run_command("build_ext")
        super().run()

setup(
    name="dx11-renderer",
    version="0.1.0",
    author="Muhammad Bilal Maulida",
    author_email="t23-bilal908@smkn7-smr.sch.id",
    description="A DirectX 11 renderer with OpenCV integration for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stdnt-c1/DX11-OpenCV",
    packages=["dx11_renderer"],
    ext_modules=[CMakeExtension("dx11_renderer._core")],
    cmdclass={
        "build_ext": CMakeBuild,
        "develop": DevelopCommand,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "opencv-python>=4.5.0",
        "pybind11>=2.10.0",
    ],
    zip_safe=False
)
