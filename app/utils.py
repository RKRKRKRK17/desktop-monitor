# app/utils.py

"""
Shared utility functions for the Temperature Monitor Application.
"""

from app import config

def get_color_for_temp(temp):
    """
    Returns the hex color code based on the temperature value.
    
    Args:
        temp (float or int): The temperature in Celsius.
        
    Returns:
        str: Hex color string.
    """
    if temp is None:
        return config.COLOR_NORMAL # Default to green if no data (or handle differently)
        
    if temp >= config.TEMP_THRESHOLD_CRITICAL:
        return config.COLOR_CRITICAL
    elif temp >= config.TEMP_THRESHOLD_WARN:
        return config.COLOR_WARN
    else:
        return config.COLOR_NORMAL

def format_temp(temp):
    """
    Formats the temperature for display.
    
    Args:
        temp (float or None): Temperature value.
        
    Returns:
        str: Formatted string (e.g., "CPU: 45°C") or "N/A"
    """
    if temp is None:
        return "N/A"
    return f"{int(temp)}°C"