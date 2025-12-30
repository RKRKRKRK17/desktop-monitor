# app/display.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QFontDatabase

from app import config, utils
from app.monitor import find_target_screen

class TemperatureWindow(QWidget):
    def __init__(self, sensor, app_instance):
        super().__init__()
        self.sensor = sensor
        self.app_instance = app_instance
        
        self.init_ui()
        self.init_timer()
        
    def init_ui(self):
        # Window Flags: Frameless, Always on Top, Taskbar hidden (Tool), Transparent for mouse
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool | 
            Qt.WindowTransparentForInput
        )
        
        # Attributes for mouse pass-through (Windows specific usually handled by TransparentForInput, 
        # but WA_TransparentForMouseEvents helps in Qt context)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground, True) # Enabled transparency

        # Set Background Color
        palette = self.palette()
        # Use a fully transparent color or the configured color with alpha 0 if intended
        # For "transparent black", we can use (0, 0, 0, 0)
        # We will follow config, but we need to ensure the window system respects it.
        # With WA_TranslucentBackground, setting the window background to transparent is key.
        palette.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        self.setPalette(palette)
        # self.setAutoFillBackground(True) # Often not needed or can conflict with transparency depending on OS, but usually okay.

        # Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        
        # Labels
        self.cpu_label = QLabel("CPU: --")
        self.gpu_label = QLabel("GPU: --")
        self.ram_label = QLabel("RAM: --%")
        
        # Load Custom Font
        font_id = QFontDatabase.addApplicationFont(config.FONT_PATH)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                config.FONT_FAMILY = font_families[0]
                print(f"Loaded font: {config.FONT_FAMILY}")
            else:
                print("Failed to get font family name from loaded font.")
        else:
            print(f"Failed to load font from {config.FONT_PATH}")

        font = QFont(config.FONT_FAMILY, config.FONT_SIZE_MAIN)
        font.setBold(config.FONT_WEIGHT == "Bold")
        
        for label in [self.cpu_label, self.gpu_label, self.ram_label]:
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            
        # Initial Position
        self.update_position()

    def update_position(self):
        # Find the correct screen
        target_screen = find_target_screen(self.app_instance)
        if target_screen:
            # We want to fill the specific screen or position securely
            # For now, let's just maximize/fullscreen on that screen or set fixed geometry
            geo = target_screen.geometry()
            self.setGeometry(geo)
            self.show()

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(config.UPDATE_INTERVAL_MS)
        
        # Separate timer for robust screen checking (e.g. every 5 seconds)
        self.screen_timer = QTimer(self)
        self.screen_timer.timeout.connect(self.update_position)
        self.screen_timer.start(5000)

    def update_data(self):
        data = self.sensor.get_data()
        
        # CPU Update
        cpu_val = data.get('cpu')
        self.cpu_label.setText(f"CPU: {utils.format_temp(cpu_val)}")
        cpu_color = utils.get_color_for_temp(cpu_val)
        self.cpu_label.setStyleSheet(f"color: {cpu_color};")
        
        # GPU Update
        gpu_val = data.get('gpu')
        self.gpu_label.setText(f"GPU: {utils.format_temp(gpu_val)}")
        gpu_color = utils.get_color_for_temp(gpu_val)
        self.gpu_label.setStyleSheet(f"color: {gpu_color};")

        # RAM Update
        ram_val = data.get('ram')
        
        if ram_val is not None:
            self.ram_label.setText(f"RAM: {int(ram_val)}%")
        else:
            self.ram_label.setText("RAM: --%")
        
        # For RAM color, we can reuse the temp thresholds or define new ones.
        # For now, let's just use white or normal color, or maybe extend utils to handle generic percentage color.
        # Let's map 0-100% roughly to the temp thresholds for now (60% warn, 80% crit) as they are similar scalar values.
        ram_color = utils.get_color_for_temp(ram_val)
        self.ram_label.setStyleSheet(f"color: {ram_color};")
