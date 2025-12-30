# app/config.py

"""
Configuration settings for the Temperature Monitor Application.
Users can edit this file to change display behavior.
"""

# Target Monitor Settings
# The app will try to find a monitor matching this resolution first.
# If not found, it falls back to the primary monitor.
TARGET_MONITOR_RESOLUTION = (480, 1080)  # Width, Height

# Target Monitor Index (Optional backup if resolution is not unique)
# 0 = Primary, 1 = Secondary, etc. - Use resolution preference first.
TARGET_MONITOR_INDEX_PREF = 1 

# Update Interval
# How often to poll sensors and update the display (in milliseconds).
UPDATE_INTERVAL_MS = 1000

# Text Settings
import os
import sys

def get_base_dir():
    """Get base directory, works for both dev and PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - resources are in app/ subfolder
        return os.path.join(sys._MEIPASS, 'app')
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
resources_dir = os.path.join(BASE_DIR, 'resources', 'soloist')
FONT_PATH = os.path.join(resources_dir, 'soloist1.ttf')

# FONT_FAMILY = "Segoe UI" # Default
FONT_FAMILY = "Soloist" # Fallback name, though we will load it dynamically
FONT_SIZE_MAIN = 50  # Large readable text
FONT_WEIGHT = "Bold"


# Temperature Thresholds (Celsius)
# Color coding: Green < WARN < Yellow < CRITICAL < Red
TEMP_THRESHOLD_WARN = 60
TEMP_THRESHOLD_CRITICAL = 80

# Colors (Hex strings)
COLOR_NORMAL = "#00FF00"   # Green
COLOR_WARN = "#FFFF00"     # Yellow
COLOR_CRITICAL = "#FF0000" # Red
COLOR_BACKGROUND = "#000000" # Black

# WMI Namespace for LibreHardwareMonitor
WMI_NAMESPACE = r"root\LibreHardwareMonitor"

# Sensor Names to search for (partial matches allowed)
# These are fallback names if specific IDs are not found.
CPU_SENSOR_NAMES = ["CPU Package", "Internal", "Tctl/Tdie"]
GPU_SENSOR_NAMES = ["GPU Core", "GPU Temperature"]
RAM_SENSOR_NAMES = ["Memory"]
