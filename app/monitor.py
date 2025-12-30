# app/monitor.py

from PySide6.QtGui import QScreen
from app import config

def find_target_screen(app_instance):
    """
    Finds the target monitor based on resolution settings in config.
    Fallback to primary monitor if not found.
    
    Args:
        app_instance (QApplication): The main application instance.
        
    Returns:
        QScreen: The selected screen object.
    """
    screens = app_instance.screens()
    target_res = config.TARGET_MONITOR_RESOLUTION
    
    # Priority 1: Match by exact resolution
    for screen in screens:
        size = screen.size()
        if (size.width(), size.height()) == target_res:
            return screen
            
    # Priority 2: Use configured index if available
    try:
        idx = config.TARGET_MONITOR_INDEX_PREF
        if 0 <= idx < len(screens):
            return screens[idx]
    except Exception:
        pass

    # Priority 3: Fallback to primary
    return app_instance.primaryScreen()

def get_screen_geometry(screen):
    """
    Returns the geometry of the given screen.
    """
    return screen.geometry()
