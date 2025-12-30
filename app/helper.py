# app/helper.py

"""
LibreHardwareMonitor helper process management.
Handles extraction, launching, and lifecycle of the bundled helper.
"""

import os
import sys
import time
import shutil
import subprocess
import tempfile
import atexit
import requests

# Track if we launched the helper (so we know whether to clean up)
_helper_process = None
_helper_launched_by_us = False
_extracted_path = None


def get_base_path():
    """
    Returns the base path for bundled resources.
    In development: the project root directory.
    In production (PyInstaller): sys._MEIPASS temp directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys._MEIPASS
    else:
        # Running in development
        # Go up one level from app/ to project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_lhm_source_path():
    """Returns the path to LibreHardwareMonitor in the bundle/source."""
    base = get_base_path()
    return os.path.join(base, 'LibreHardwareMonitor-net472')


def get_lhm_runtime_path():
    """
    Returns the runtime path for LibreHardwareMonitor.
    In development: use source directly.
    In production: extract to a persistent temp location.
    """
    global _extracted_path
    
    if not getattr(sys, 'frozen', False):
        # Development mode - use source directly
        return get_lhm_source_path()
    
    if _extracted_path and os.path.exists(_extracted_path):
        return _extracted_path
    
    # Production mode - extract to temp directory
    # Use a consistent location so we don't re-extract every time
    app_temp_dir = os.path.join(tempfile.gettempdir(), 'HWMonitorApp')
    lhm_dir = os.path.join(app_temp_dir, 'LibreHardwareMonitor')
    
    if not os.path.exists(lhm_dir):
        os.makedirs(app_temp_dir, exist_ok=True)
        source = get_lhm_source_path()
        shutil.copytree(source, lhm_dir)
        print(f"Extracted LibreHardwareMonitor to: {lhm_dir}")
    
    _extracted_path = lhm_dir
    return lhm_dir


def is_lhm_running():
    """Check if LibreHardwareMonitor.exe is already running."""
    try:
        # Use tasklist to check for the process
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq LibreHardwareMonitor.exe', '/NH'],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return 'LibreHardwareMonitor.exe' in result.stdout
    except Exception as e:
        print(f"Error checking if LHM is running: {e}")
        return False


def is_wmi_available():
    """Check if WMI sensors are available."""
    try:
        import wmi
        w = wmi.WMI(namespace=r"root\LibreHardwareMonitor")
        sensors = w.Sensor()
        return len(sensors) > 0
    except Exception:
        return False


def is_http_available(port=8085, timeout=1):
    """Check if LibreHardwareMonitor HTTP server is available."""
    try:
        response = requests.get(f'http://localhost:{port}/data.json', timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def start_lhm_silently():
    """
    Start LibreHardwareMonitor silently (no console, no UI).
    Returns True if started successfully or already running.
    """
    global _helper_process, _helper_launched_by_us
    
    if is_lhm_running():
        print("LibreHardwareMonitor is already running.")
        _helper_launched_by_us = False
        return True
    
    lhm_path = get_lhm_runtime_path()
    exe_path = os.path.join(lhm_path, 'LibreHardwareMonitor.exe')
    
    if not os.path.exists(exe_path):
        print(f"ERROR: LibreHardwareMonitor.exe not found at: {exe_path}")
        return False
    
    try:
        # Start minimized and hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        
        _helper_process = subprocess.Popen(
            [exe_path],
            cwd=lhm_path,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        _helper_launched_by_us = True
        print(f"Started LibreHardwareMonitor (PID: {_helper_process.pid})")
        return True
        
    except Exception as e:
        print(f"Failed to start LibreHardwareMonitor: {e}")
        return False


def wait_for_sensors(timeout=30, poll_interval=0.5):
    """
    Wait until sensors are available via WMI or HTTP.
    Returns True if sensors become available within timeout.
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Prefer HTTP if available
        if is_http_available():
            print("Sensors available via HTTP.")
            return True
        
        # Fallback to WMI
        if is_wmi_available():
            print("Sensors available via WMI.")
            return True
        
        time.sleep(poll_interval)
    
    print(f"WARNING: Sensors not available after {timeout}s timeout.")
    return False


def ensure_helper_running():
    """
    Main entry point: ensure LibreHardwareMonitor is running and sensors are available.
    Returns True if ready, False otherwise.
    """
    print("Initializing hardware monitor helper...")
    
    if not start_lhm_silently():
        print("WARNING: Could not start LibreHardwareMonitor.")
        # Continue anyway - maybe WMI is already available from a previous session
    
    # Wait for sensors to become available
    if not wait_for_sensors():
        print("WARNING: Proceeding without confirmed sensor availability.")
        return False
    
    return True


def cleanup_helper():
    """
    Cleanup function called on app exit.
    Leaves the helper running if it was already running before we started.
    """
    global _helper_process, _helper_launched_by_us
    
    # We leave the helper running - it's useful for other apps
    # and the user may want it to persist
    if _helper_launched_by_us and _helper_process:
        print("Note: LibreHardwareMonitor will continue running in the background.")
        # Uncomment below if you want to terminate it:
        # _helper_process.terminate()
        # print("Terminated LibreHardwareMonitor.")


# Register cleanup on exit
atexit.register(cleanup_helper)
