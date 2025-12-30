# app/sensors.py

import wmi
from app import config

class TemperatureSensor:
    def __init__(self):
        self.wmi_obj = None
        self.connected = False
        self._connect()

    def _connect(self):
        """Attempts to connect to the WMI service."""
        try:
            # Connect to LibreHardwareMonitor namespace
            self.wmi_obj = wmi.WMI(namespace=config.WMI_NAMESPACE)
            self.connected = True
        except Exception as e:
            print(f"Error connecting to WMI namespace '{config.WMI_NAMESPACE}': {e}")
            self.connected = False
            self.wmi_obj = None

    def get_data(self):
        """
        Queries WMI for CPU temp, GPU temp, and RAM usage.
        Returns a dictionary {'cpu': float|None, 'gpu': float|None, 'ram': float|None}.
        """
        data = {'cpu': None, 'gpu': None, 'ram': None}
        
        if not self.connected:
            self._connect()
            if not self.connected:
                return data

        try:
            # Query for sensors of type 'Temperature' and 'Load'
            # We can't query multiple types in one call easily with simple syntax usually, 
            # but we can try "SELECT * FROM Sensor WHERE SensorType = 'Temperature' OR SensorType = 'Load'"
            # Or just iterate over all sensors if the list isn't huge, or make two calls.
            # Two calls is safer.
            temp_sensors = self.wmi_obj.Sensor(SensorType='Temperature')
            load_sensors = self.wmi_obj.Sensor(SensorType='Load')
            
            # --- Temperatures ---
            for sensor in temp_sensors:
                name = sensor.Name
                val = sensor.Value
                
                # Check for CPU
                if any(x in name for x in config.CPU_SENSOR_NAMES):
                    if data['cpu'] is None or "Package" in name:
                        data['cpu'] = val
                
                # Check for GPU
                if any(x in name for x in config.GPU_SENSOR_NAMES):
                    if data['gpu'] is None or "Core" in name:
                        data['gpu'] = val

            # --- Load (RAM) ---
            for sensor in load_sensors:
                name = sensor.Name
                val = sensor.Value

                # Check for RAM
                # Usually "Memory" under Load is the RAM usage in %
                # We must be careful not to pick up "GPU Memory" or "Virtual Memory"
                if any(x in name for x in config.RAM_SENSOR_NAMES):
                    # Strict check to avoid "GPU Memory"
                    if "GPU" in name or "Virtual" in name:
                        continue
                        
                    if data['ram'] is None:
                        data['ram'] = val
                        
        except Exception as e:
            print(f"Error reading sensors: {e}")
            # If reading fails, assume connection lost
            self.connected = False
            
        return data
