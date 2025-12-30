
import wmi

WMI_NAMESPACE = r"root\LibreHardwareMonitor"

def list_sensors():
    try:
        w = wmi.WMI(namespace=WMI_NAMESPACE)
        print("Connected to WMI namespace.")
        
        # Query all sensors
        sensors = w.Sensor()
        
        print(f"{'Name':<30} | {'SensorType':<15} | {'Value':<10}")
        print("-" * 60)
        
        for s in sensors:
            print(f"{s.Name:<30} | {s.SensorType:<15} | {s.Value}")
            
    except Exception as e:
        print(f"Error: {e}")
        # Try finding OpenHardwareMonitor just in case
        try:
            print("\nTrying OpenHardwareMonitor namespace...")
            w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
            sensors = w.Sensor()
            for s in sensors:
                print(f"{s.Name:<30} | {s.SensorType:<15} | {s.Value}")
        except Exception as e2:
            print(f"Error connecting to OHM: {e2}")

if __name__ == "__main__":
    list_sensors()
