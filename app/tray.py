# app/tray.py

"""
System tray icon management for the Hardware Monitor.
Provides optional tray icon with exit and restart controls.
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QSize


def create_simple_icon():
    """Create a simple colored icon for the tray."""
    pixmap = QPixmap(QSize(32, 32))
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
    
    painter = QPainter(pixmap)
    painter.setBrush(QColor(0, 200, 0))  # Green
    painter.setPen(QColor(0, 150, 0))
    painter.drawEllipse(4, 4, 24, 24)
    painter.end()
    
    return QIcon(pixmap)


class TrayIcon(QSystemTrayIcon):
    """System tray icon with basic controls."""
    
    def __init__(self, app, helper_restart_callback=None, parent=None):
        super().__init__(parent)
        
        self.app = app
        self.helper_restart_callback = helper_restart_callback
        
        # Set icon
        self.setIcon(create_simple_icon())
        self.setToolTip("Hardware Monitor")
        
        # Create context menu
        self.menu = QMenu()
        
        # Restart helper action
        if helper_restart_callback:
            restart_action = self.menu.addAction("Restart Helper")
            restart_action.triggered.connect(self._on_restart_helper)
            self.menu.addSeparator()
        
        # Exit action
        exit_action = self.menu.addAction("Exit")
        exit_action.triggered.connect(self._on_exit)
        
        self.setContextMenu(self.menu)
        
        # Show the tray icon
        self.show()
    
    def _on_restart_helper(self):
        """Restart the LibreHardwareMonitor helper."""
        if self.helper_restart_callback:
            self.helper_restart_callback()
    
    def _on_exit(self):
        """Exit the application."""
        self.hide()
        self.app.quit()
