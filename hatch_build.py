import os
import shutil
import subprocess
import sys
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version, build_data):
        root = Path(self.root)
        src_dir = root / "src"
        rust_dir = root / "rust"

        # 1. Compile Rust library
        print("Executing Rust compilation hook: cargo build --release --lib ...")
        subprocess.run(["cargo", "build", "--release", "--lib"], cwd=rust_dir, check=True)

        target_dir = rust_dir / "target" / "release"
        dest_dir = src_dir / "cadilib" / "ionogramparser"
        dest_dir.mkdir(parents=True, exist_ok=True)

        if sys.platform == "win32":
            src_file = target_dir / "mdxreader_rs.dll"
            dest_file = dest_dir / "mdxreader_rs.pyd"
        elif sys.platform == "darwin":
            src_file = target_dir / "libmdxreader_rs.dylib"
            if not src_file.exists():
                src_file = target_dir / "libmdxreader_rs.so"
            dest_file = dest_dir / "mdxreader_rs.so"
        else:
            src_file = target_dir / "libmdxreader_rs.so"
            dest_file = dest_dir / "mdxreader_rs.so"

        if not src_file.exists():
            raise FileNotFoundError(f"Compiled Rust library not found at: {src_file}")

        print(f"Hook copying {src_file} -> {dest_file}")
        shutil.copy2(src_file, dest_file)
        
        # 2. Compile Python modules with Cython
        print("Compiling Python modules to native binaries with Cython...")
        try:
            import numpy as np
            from Cython.Build import cythonize
            from setuptools import Distribution, Extension
            from setuptools.command.build_ext import build_ext

            py_files = [p for p in (src_dir / "cadilib").rglob("*.py") if p.name != "__init__.py"]
            ext_modules = []
            for p in py_files:
                rel = p.relative_to(src_dir)
                mod_name = ".".join(rel.with_suffix("").parts)
                ext_modules.append(Extension(mod_name, [str(p)], include_dirs=[np.get_include()]))

            cythonized = cythonize(
                ext_modules,
                compiler_directives={"language_level": "3"},
                quiet=True,
            )

            dist = Distribution({"name": "cadilib", "ext_modules": cythonized})
            cmd = build_ext(dist)
            cmd.build_lib = str(src_dir)
            cmd.ensure_finalized()
            cmd.run()
            print("Cython compilation completed successfully.")
        except Exception as e:
            print(f"Error compiling Cython extensions: {e}")
            raise

        # 3. Clean up generated .c files from src
        for c_file in (src_dir / "cadilib").rglob("*.c"):
            try:
                c_file.unlink()
            except OSError:
                pass

        # Mark wheel as platform-specific native binary distribution
        build_data["pure_python"] = False
        build_data["infer_tag"] = True
