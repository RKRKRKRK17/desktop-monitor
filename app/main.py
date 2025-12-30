# app/main.py

"""
Main entry point for the Hardware Monitor Application.

This module handles:
- Starting the LibreHardwareMonitor helper
- Initializing the sensor interface
- Launching the display UI
- Managing the system tray icon

Run in development:  python -m app.main
Run in production:   HWMonitor.exe (packaged)
"""

import sys
import signal

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.helper import ensure_helper_running, start_lhm_silently
from app.sensors import TemperatureSensor
from app.display import TemperatureWindow
from app.tray import TrayIcon


def restart_helper():
    """Callback to restart the LibreHardwareMonitor helper."""
    print("Restarting LibreHardwareMonitor helper...")
    start_lhm_silently()


def main():
    """Main application entry point."""
    
    # Allow Ctrl+C to exit (development convenience)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # --- Step 1: Ensure LibreHardwareMonitor is running ---
    print("=" * 50)
    print("Hardware Monitor - Starting Up")
    print("=" * 50)
    
    helper_ready = ensure_helper_running()
    
    if not helper_ready:
        print("WARNING: Helper may not be fully ready. Continuing anyway...")
    
    # --- Step 2: Initialize Qt Application ---
    # Set attributes before creating QApplication
    # AA_EnableHighDpiScaling is enabled by default in Qt6
    
    app = QApplication(sys.argv)
    app.setApplicationName("Hardware Monitor")
    app.setQuitOnLastWindowClosed(False)  # Keep running for tray
    
    # --- Step 3: Initialize Sensor Interface ---
    sensor = TemperatureSensor()
    
    # --- Step 4: Initialize Main Display Window ---
    window = TemperatureWindow(sensor, app)
    window.show()
    
    # --- Step 5: Initialize System Tray Icon ---
    tray = TrayIcon(app, helper_restart_callback=restart_helper)
    
    print("=" * 50)
    print("Hardware Monitor - Running")
    print("Use the system tray icon to exit.")
    print("=" * 50)
    
    # --- Step 6: Run Event Loop ---
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
