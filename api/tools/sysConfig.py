import platform
import subprocess

def get_system_unique_id():
    system = platform.system()
    if system == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            for system in c.Win32_ComputerSystemProduct():
                return system.UUID
        except Exception as e:
            print(f"Error getting UUID on Windows: {e}")
    elif system == "Linux":
        try:
            with open('/etc/machine-id', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print("File /etc/machine-id not found.")
        except Exception as e:
            print(f"Error getting machine ID on Linux: {e}")
    elif system == "Darwin":  # macOS
        try:
            command = "ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Error getting UUID on macOS: {result.stderr}")
        except Exception as e:
            print(f"Error getting UUID on macOS: {e}")
    return None
