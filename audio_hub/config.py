import json
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess


class SettingsManager:

    def __init__(self, path: Path = None) -> None:
        self.path = Path(path or Path.cwd() / "settings.json")
        self._data = {"tws_mac": "", "iphone_mac": ""}
        self.load()

    def load(self) -> None:
        try:
            if self.path.exists():
                with self.path.open("r", encoding="utf-8") as fh:
                    self._data.update(json.load(fh))
        except Exception:
            # Keep defaults on error
            pass

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    def get(self, key: str) -> str:
        return self._data.get(key, "")

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def scan_bluetooth_devices(self) -> List[Tuple[str, str]]:
        try:
            output = subprocess.getoutput("bluetoothctl devices")
            devices = []
            for line in output.splitlines():
                parts = line.strip().split(" ", 2)
                if len(parts) >= 3 and parts[0] == "Device":
                    mac = parts[1]
                    name = parts[2]
                    devices.append((mac, name))
            return devices
        except Exception:
            return []
