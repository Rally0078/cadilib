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
        rust_dir = root / "rust"

        print("Executing Rust compilation hook: cargo build --release --lib ...")
        subprocess.run(["cargo", "build", "--release", "--lib"], cwd=rust_dir, check=True)

        target_dir = rust_dir / "target" / "release"
        dest_dir = root / "src" / "cadilib" / "ionogramparser"
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

        # Mark wheel as platform-specific native binary distribution
        build_data["pure_python"] = False
        build_data["infer_tag"] = True
