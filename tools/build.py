#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path


def build():
    """Build native module"""
    root = Path(__file__).parent.parent
    
    print("Building spence native module...")
    
    # Run setuptools build
    result = subprocess.run(
        [sys.executable, "setup.py", "build_ext", "--inplace"],
        cwd=root,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Build failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    
    print("Build successful!")
    print(result.stdout)


if __name__ == "__main__":
    build()
