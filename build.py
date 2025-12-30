# build.py

"""
Build script for Hardware Monitor Application.

This script handles:
1. Installing required build dependencies
2. Running PyInstaller with the spec file
3. Verifying the output

Usage:
    python build.py
"""

import os
import sys
import subprocess
import shutil


def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n{'='*50}")
    print(f"  {description}")
    print(f"{'='*50}")
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\nERROR: {description} failed with code {result.returncode}")
        return False
    return True


def main():
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print("\n" + "="*60)
    print("  Hardware Monitor Build Script")
    print("="*60)
    
    # Step 1: Check/install dependencies
    print("\n[1/4] Checking build dependencies...")
    
    deps = ['pyinstaller', 'requests']
    for dep in deps:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', dep],
            capture_output=True
        )
        if result.returncode != 0:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep])
    
    # Step 2: Clean previous builds
    print("\n[2/4] Cleaning previous builds...")
    
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")
    
    # Step 3: Run PyInstaller
    print("\n[3/4] Running PyInstaller...")
    
    spec_file = os.path.join(project_root, 'HWMonitor.spec')
    
    if not os.path.exists(spec_file):
        print(f"ERROR: Spec file not found: {spec_file}")
        return 1
    
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        spec_file
    ])
    
    if result.returncode != 0:
        print("\nERROR: PyInstaller build failed!")
        return 1
    
    # Step 4: Verify output
    print("\n[4/4] Verifying build output...")
    
    exe_path = os.path.join(project_root, 'dist', 'HWMonitor.exe')
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n[OK] Build successful!")
        print(f"  Output: {exe_path}")
        print(f"  Size:   {size_mb:.1f} MB")
    else:
        print(f"\nERROR: Expected output not found: {exe_path}")
        return 1
    
    print("\n" + "="*60)
    print("  Build Complete!")
    print("="*60)
    print(f"\nTo run: {exe_path}")
    print("Note: Run as Administrator for sensor access.\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
