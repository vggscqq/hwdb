import subprocess
import re
from typing import List, Dict, Optional
import json
import time

def wait_for_internet(timeout: int = 300) -> bool:
    """Wait for internet connection by pinging 8.8.8.8"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=True)
            return True
        except subprocess.CalledProcessError:
            time.sleep(1)
    return False

def upload_info(info) -> bool:
    """Upload system info to example.com"""
    import requests
    
    if not wait_for_internet():
        return False
        
    try:
        response = requests.post(
            'https://hwdb.vgscq.cc/submit',
            json=info.to_dict(),
            timeout=10
        )
        print(response.text)
        return response.ok
    except Exception as e:
        print(f"Error uploading info: {e}")
        return False

def run_command(command: List[str]) -> str:
    try:
        return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return ""

class SystemInfo:
    def __init__(self):
        self.hw_info = json.loads(self._run_command(['sudo', 'lshw', '-json']))

    def _run_command(self, cmd: List[str]) -> str:
        return subprocess.check_output(cmd, text=True)

    def _find_by_class(self, class_name: str) -> List[Dict]:
        def recursive_search(node):
            results = []
            if isinstance(node, dict):
                if node.get('class') == class_name:
                    results.append(node)
                for value in node.values():
                    results.extend(recursive_search(value))
            elif isinstance(node, list):
                for item in node:
                    results.extend(recursive_search(item))
            return results
        return recursive_search(self.hw_info)

    def get_ram(self) -> Dict:
        memory_banks = self._find_by_class('memory')
        sticks = []
        total = 0
        total_slots = 0
        used_slots = 0

        for bank in memory_banks:
            # Handle VM style memory banks
            if bank.get('id') == 'memory' and bank.get('children'):
                for child in bank.get('children', []):
                    if child.get('description', '').startswith('DIMM'):
                        total_slots += 1
                        if child.get('size', 0) > 0:
                            used_slots += 1
                            size_gb = child.get('size', 0) // (1024**3)
                            total += size_gb
                            sticks.append({
                                "size_gb": size_gb,
                                "type": child.get('description', 'Unknown')
                            })
            # Handle physical machine style memory banks
            elif bank.get('id', '').startswith('bank:'):
                total_slots += 1
                if (bank.get('size', 0) > 0 and 
                    '[empty]' not in bank.get('description', '') and 
                    bank.get('product', '') != 'NO DIMM'):
                    
                    used_slots += 1
                    size_gb = bank.get('size', 0) // (1024**3)
                    total += size_gb
                    sticks.append({
                        "size_gb": size_gb,
                        "type": bank.get('description', 'Unknown'),
                        "model": child.get('product', 'Unknown')
                    })

        return {
            "total_size_gb": total,
            "slots": f"{used_slots} / {total_slots}",
            "sticks": sticks
        }

    def _get_disk_serial(self, disk_path: str) -> str:
        try:
            output = self._run_command(['sudo', 'smartctl', '-i', disk_path])
            serial_match = re.search(r'Serial Number:\s*(.+)', output)
            return serial_match.group(1) if serial_match else "None"
        except subprocess.CalledProcessError:
            return "None"

    def get_disks(self) -> List[Dict[str, str]]:
        # Run fdisk -l and capture output
        fdisk_output = self._run_command(['fdisk', '-l'])
        disks = []
        
        # Updated regex pattern to match the actual fdisk output format
        disk_pattern = r'Disk\s+(/dev/(?:sd[a-z]|nvme\d+n\d+)):\s+([\d,.]+)\s+(?:GiB|bytes).*\nDisk model:\s+([^\n]+)'
        matches = re.finditer(disk_pattern, fdisk_output)
        
        for match in matches:
            path = match.group(1)
            size_str = match.group(2).replace(',', '.')  # Handle decimal separator
            model = match.group(3).strip()
            serial = self._get_disk_serial(path)

            # Convert size to bytes if needed
            if 'GiB' in fdisk_output[match.start():match.end()]:
                size_bytes = float(size_str) * (1024**3)
            else:
                size_bytes = float(size_str)
            
            disks.append({
                "path": path,
                "size": f"{int(size_bytes // (1024**3))}G",
                "model": model if model else "Unknown",
                "serial": serial if serial else "N/A"
            })

        return disks

    def get_cpu(self) -> str:
        cpu_info = self._find_by_class('processor')[0] if self._find_by_class('processor') else {}
        return cpu_info.get('product', 'N/A')

    def get_mainboard(self) -> str:
        baseboard_info = self._find_by_class('bus')[0] if self._find_by_class('bus')[0] else {}
        return baseboard_info.get('product', 'N/A')

    def get_resolution(self) -> str:
        fastfetch_output = self._run_command(['fastfetch', '-l', 'none'])
        display_matches = re.findall(r'Display\s+\(([^)]+)\):\s+(\d+x\d+)\s+@\s+(\d+)\s+Hz\s+in\s+(\d+)"\s+\[([^\]]+)\]', fastfetch_output)
        if display_matches:
            displays = []
            for model, resolution, refresh_rate, size, location in display_matches:
                displays.append(f"[{location}] {model}: {resolution} @ {refresh_rate} Hz in {size}\"")
            return ', '.join(displays)
        return "N/A"

    def get_host(self) -> str:
        return f"{self.hw_info.get('vendor', 'Unknown')} {self.hw_info.get('product', 'Unknown')}"
    
    def get_serial(self) -> str:
        serial = self.hw_info.get('serial', 'N/A')
        return "VM" if "QEMU" in self.get_host() else serial

    def to_dict(self) -> Dict:
        system = self.hw_info
        gpus = self._find_by_class('display')
        
        return {
            "host": self.get_host(),
            "serial": self.get_serial(),
            "mainboard": self.get_mainboard(),
            "cpu": self.get_cpu(),
            "gpus": [gpu.get('product', 'Unknown') for gpu in gpus],
            "resolution": self.get_resolution(),
            #"local_ip": "N/A",
            #"public_ip": "N/A",
            "ram": self.get_ram(),
            "disks": self.get_disks()
        }

if __name__ == "__main__":
    info = SystemInfo()
    print(json.dumps(info.to_dict(), indent=4))

    upload_info(info)