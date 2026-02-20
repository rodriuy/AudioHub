from typing import Optional, Callable
import subprocess
import threading
import time
import shutil
import numpy as np
import sounddevice as sd
from .logger import get_logger


class AudioManager:
    """Manage Bluetooth and audio routing"""

    def __init__(self, on_log: Optional[Callable[[str], None]] = None) -> None:
        self.logger = get_logger("audio_hub.backend")
        self.on_log = on_log
        self._stream: Optional[sd.InputStream] = None
        self._fft_data = np.zeros(30)
        self._running = threading.Event()
        self._module_index: Optional[int] = None
        self._monitor_device: Optional[int] = None

    def _log(self, msg: str, level: str = "info") -> None:
        if self.on_log:
            try:
                self.on_log(msg)
            except Exception:
                pass
        getattr(self.logger, level)(msg)

    def check_dependencies(self) -> bool:
        for cmd in ("pactl", "bluetoothctl"):
            if not shutil.which(cmd):
                self._log(f"Missing system dependency: {cmd}", "error")
                return False
        return True

    def power_on_bluetooth(self) -> None:
        try:
            subprocess.run(["bluetoothctl", "power", "on"], check=True)
            self._log("Bluetooth powered on")
        except subprocess.CalledProcessError as exc:
            self._log(f"Failed to power bluetooth: {exc}", "error")
            raise

    def connect_device(self, mac: str) -> bool:
        try:
            subprocess.run(["bluetoothctl", "connect", mac], check=True)
            self._log(f"Connected {mac}")
            return True
        except subprocess.CalledProcessError as exc:
            self._log(f"Error connecting {mac}: {exc}", "warning")
            return False

    def find_audio_device(self, mac_address: str, device_type: str = "source") -> Optional[str]:
        mac_pulse = mac_address.replace(":", "_")
        try:
            cmd_output = subprocess.getoutput(f"pactl list short {device_type}s")
            self._log(f"Looking for {device_type} with MAC {mac_address} (pulse format: {mac_pulse})", "debug")
            self._log(f"Available {device_type}s:\n{cmd_output}", "debug")
            
            for line in cmd_output.splitlines():
                if mac_pulse in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        device_name = parts[1]
                        self._log(f"Found {device_type} device: {device_name}", "info")
                        return device_name
            
            self._log(f"No {device_type} device found for MAC {mac_address}", "warning")
        except Exception as exc:
            self._log(f"Error finding audio device: {exc}", "error")
        return None

    def unload_loopback(self, module_index: Optional[int] = None) -> None:
        if module_index is None:
            # Best effort: unload all loopback modules
            try:
                output = subprocess.getoutput("pactl list short modules | grep loopback")
                for line in output.splitlines():
                    parts = line.split('\t')
                    if len(parts) >= 1:
                        try:
                            idx = int(parts[0])
                            subprocess.run(["pactl", "unload-module", str(idx)], check=False)
                            self._log(f"Unloaded loopback module #{idx}")
                        except (ValueError, Exception):
                            pass
            except Exception as exc:
                self._log(f"Error unloading loopback modules: {exc}", "warning")
        else:
            try:
                subprocess.run(["pactl", "unload-module", str(module_index)], check=True)
                self._log(f"Unloaded loopback module #{module_index}")
            except subprocess.CalledProcessError as exc:
                self._log(f"Failed to unload module #{module_index}: {exc}", "warning")

    def load_loopback(self, source: str, sink: str, latency_msec: int = 30) -> Optional[int]:
        try:
            self._log(f"Loading loopback: {source} -> {sink} (latency={latency_msec}ms)", "info")
            cmd = ["pactl", "load-module", "module-loopback", f"source={source}", f"sink={sink}", f"latency_msec={latency_msec}"]
            out = subprocess.getoutput(" ".join(cmd))
            self._log(f"pactl output: {out}", "debug")
            
            # Usually returns module index as number
            try:
                idx = int(out.strip())
                self._module_index = idx
                self._log(f"✓ Loopback module loaded: #{idx}")
                return idx
            except ValueError:
                self._log(f"Unexpected load-module output (expected integer): {out}", "warning")
        except Exception as exc:
            self._log(f"Failed to load loopback: {exc}", "error")
        return None

    def _audio_callback(self, indata, frames, t, status) -> None:
        try:
            fft_raw = np.abs(np.fft.rfft(indata[:, 0]))
            if len(fft_raw) >= 30:
                indices = np.linspace(0, len(fft_raw) - 1, 30, dtype=int)
                self._fft_data = fft_raw[indices] * 2.5
        except Exception:
            pass

    def start_audio_stream(self, tws_sink: Optional[str] = None) -> None:
        if self._stream is not None:
            return
        
        if not tws_sink:
            self._log("Audio visualization disabled (no TWS sink provided)", "debug")
            return
        
        try:
            devices = sd.query_devices()
            monitor_name = f"{tws_sink}.monitor"
            device_id = None
            
            for i, dev in enumerate(devices):
                if dev['name'] and monitor_name in dev['name']:
                    device_id = i
                    self._monitor_device = i
                    self._log(f"Found TWS monitor device #{i}: {dev['name']}", "debug")
                    break
            
            if device_id is None:
                self._log(f"TWS monitor device not found ({monitor_name}) — visualization disabled", "debug")
                return
            
            self._stream = sd.InputStream(
                callback=self._audio_callback,
                channels=1,
                samplerate=44100,
                device=device_id
            )
            self._stream.start()
            self._running.set()
            self._log("Audio visualizer stream started (monitoring TWS output)", "info")
        except Exception as exc:
            self._log(f"Could not start audio visualization: {exc}", "debug")

    def stop_audio_stream(self) -> None:
        try:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
                self._running.clear()
                self._log("Audio visualizer stream stopped")
        except Exception as exc:
            self._log(f"Error stopping audio stream: {exc}", "warning")

    def sync_and_mix(self, tws_mac: str, secondary_mac: str = "") -> None:
        if not self.check_dependencies():
            return

        try:
            self.power_on_bluetooth()
        except Exception:
            return

        self._log(f"Connecting TWS {tws_mac}...")
        tws_connected = self.connect_device(tws_mac)
        
        if secondary_mac and secondary_mac.strip():
            self._log(f"Connecting secondary device {secondary_mac}...")
            secondary_connected = self.connect_device(secondary_mac)
        else:
            secondary_connected = True
            self._log("(No secondary device selected)")

        self._log("Waiting for PulseAudio to register devices (this may take 5-10 seconds)...")
        time.sleep(5)

        if not tws_connected:
            self._log("ERROR: Could not connect to TWS", "error")
            return
        
        if not secondary_connected:
            self._log("Warning: secondary device may not be fully connected", "warning")

        tws_sink = None
        max_retries = 3
        for attempt in range(max_retries):
            if attempt > 0:
                self._log(f"Retry {attempt}/{max_retries - 1}: searching for TWS audio device...")
                time.sleep(2)
            tws_sink = self.find_audio_device(tws_mac, "sink")
            if tws_sink:
                break

        if tws_sink:
            self._log(f"✓ Found TWS output device: {tws_sink}")
            self._set_default_sink(tws_sink)
            self.start_audio_stream(tws_sink)
            self._log("✓ TWS is now the default audio output. Any app can play through it.")
        else:
            self._log(f"ERROR: Could not locate TWS audio device after {max_retries} attempts.", "error")
            self._log("Make sure the TWS are properly paired and powered on.", "warning")

    def _set_default_sink(self, sink_name: str) -> None:
        try:
            subprocess.run(["pactl", "set-default-sink", sink_name], check=True)
            self._log(f"Set default audio output to: {sink_name}")
        except subprocess.CalledProcessError as exc:
            self._log(f"Failed to set default sink: {exc}", "warning")

    def cleanup(self) -> None:
        self._log("Cleaning up audio resources...", "info")
        self.stop_audio_stream()
        self._log("Cleanup complete.", "info")

    def get_fft_data(self):
        return self._fft_data.copy()
