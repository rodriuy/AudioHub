from typing import Optional, List, Tuple
import customtkinter as ctk
import threading
from pathlib import Path
import logging
from .config import SettingsManager
from .backend import AudioManager
from .logger import get_logger


class TextboxLogHandler(logging.Handler):

    def __init__(self, write_callable):
        super().__init__()
        self.write = write_callable

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.write(msg + "\n")
        except Exception:
            pass


class AudioHubPro(ctk.CTk):

    def __init__(self, settings: SettingsManager, manager: AudioManager) -> None:
        super().__init__()
        self.title("AudioHub Pro — Bluetooth Audio Router")
        self.geometry("600x800")
        self.minsize(600, 600)

        self.settings = settings
        self.manager = manager
        self.logger = get_logger("audio_hub.ui")
        self._scanning = False
        self._devices: List[Tuple[str, str]] = []

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        header_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(header_frame, text="AudioHub Pro", font=("Inter", 32, "bold"), text_color="#00ffcc")
        title_label.pack(pady=16, padx=20)

        subtitle_label = ctk.CTkLabel(header_frame, text="Multipoint Bluetooth Audio Mixer", font=("Inter", 12), text_color="#888888")
        subtitle_label.pack(padx=20, pady=(0, 12))

        devices_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        devices_frame.pack(fill="x", padx=20, pady=16)

        scan_header = ctk.CTkLabel(devices_frame, text="1. Scan & Select Devices", font=("Inter", 14, "bold"))
        scan_header.pack(anchor="w", pady=(0, 10))

        scan_btn_frame = ctk.CTkFrame(devices_frame, fg_color="transparent")
        scan_btn_frame.pack(fill="x", pady=(0, 12))

        self.btn_scan = ctk.CTkButton(scan_btn_frame, text="🔍 Scan Bluetooth Devices", command=self._start_scan_thread, height=40, font=("Inter", 12, "bold"))
        self.btn_scan.pack(side="left", padx=(0, 8), fill="x", expand=True)

        self.scan_status_lbl = ctk.CTkLabel(scan_btn_frame, text="", font=("Inter", 10), text_color="#888888")
        self.scan_status_lbl.pack(side="left", padx=8)

        device_grid = ctk.CTkFrame(devices_frame, fg_color="transparent")
        device_grid.pack(fill="x")

        tws_lbl = ctk.CTkLabel(device_grid, text="📻 TWS / Speakers", font=("Inter", 11, "bold"), text_color="#cccccc")
        tws_lbl.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.tws_combo = ctk.CTkComboBox(device_grid, values=["? Scan for devices"], font=("Inter", 11))
        self.tws_combo.set("? Scan for devices")
        self.tws_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        secondary_lbl = ctk.CTkLabel(device_grid, text="🎧 Secondary Device (optional)", font=("Inter", 11, "bold"), text_color="#cccccc")
        secondary_lbl.grid(row=1, column=0, sticky="w", pady=(10, 6))

        self.iphone_combo = ctk.CTkComboBox(device_grid, values=["? Scan for devices"], font=("Inter", 11))
        self.iphone_combo.set("? Scan for devices")
        self.iphone_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0))

        device_grid.columnconfigure(1, weight=1)

        viz_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        viz_frame.pack(fill="both", expand=True, padx=20, pady=16)

        viz_lbl = ctk.CTkLabel(viz_frame, text="2. Audio Visualizer", font=("Inter", 14, "bold"))
        viz_lbl.pack(anchor="w", pady=(0, 10))

        self.canvas_width = 540
        self.canvas_height = 150
        self.canvas = ctk.CTkCanvas(viz_frame, width=self.canvas_width, height=self.canvas_height, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=8)

        build_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        build_frame.pack(fill="x", padx=20, pady=10)

        self.btn_sync = ctk.CTkButton(build_frame, text="▶ BUILD & SYNC", height=50, command=self.start_sync_thread, font=("Inter", 14, "bold"), fg_color="#1f538d", hover_color="#2b6bb8")
        self.btn_sync.pack(fill="x")

        console_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        console_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        console_lbl = ctk.CTkLabel(console_frame, text="Logs", font=("Inter", 11, "bold"))
        console_lbl.pack(anchor="w", pady=(0, 6))

        self.console = ctk.CTkTextbox(console_frame, height=100, font=("Consolas", 9), fg_color="#0a0a0a", text_color="#00ff88")
        self.console.pack(fill="both", expand=True)

        handler = TextboxLogHandler(self._write_console)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
        self.logger.addHandler(handler)
        backend_logger = get_logger("audio_hub.backend")
        backend_logger.addHandler(handler)

        footer_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=0)
        footer_frame.pack(fill="x", padx=0, pady=0, side="bottom")

        save_btn = ctk.CTkButton(footer_frame, text="💾 Save Settings", command=self.save_settings, font=("Inter", 10), height=32)
        save_btn.pack(fill="x", padx=20, pady=10)

        self._updating = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._start_ui_update_loop()

    def _write_console(self, text: str) -> None:
        self.console.insert("end", text)
        self.console.see("end")

    def _start_scan_thread(self) -> None:
        if self._scanning:
            return
        threading.Thread(target=self._scan_devices, daemon=True).start()

    def _scan_devices(self) -> None:
        self._scanning = True
        self.btn_scan.configure(state="disabled", text="🔄 Scanning...")
        self.scan_status_lbl.configure(text="Scanning...")
        
        try:
            self.logger.info("Scanning for Bluetooth devices...")
            devices = self.settings.scan_bluetooth_devices()
            self._devices = devices
            
            if not devices:
                self.logger.warning("No Bluetooth devices found")
                self.scan_status_lbl.configure(text="No devices found", text_color="#ff6600")
            else:
                self.logger.info(f"Found {len(devices)} devices")
                self.scan_status_lbl.configure(text=f"✓ {len(devices)} found", text_color="#00ff88")
                
                device_names = [f"{name} ({mac})" for mac, name in devices]
                self.tws_combo.configure(values=device_names)
                self.iphone_combo.configure(values=device_names)
        except Exception as e:
            self.logger.error(f"Scan error: {e}")
            self.scan_status_lbl.configure(text="Error", text_color="#ff3333")
        finally:
            self._scanning = False
            self.btn_scan.configure(state="normal", text="🔍 Scan Bluetooth Devices")

    def _get_selected_macs(self) -> tuple[str, str | None] | None:
        tws_str = self.tws_combo.get()
        secondary_str = self.iphone_combo.get()
        
        if not tws_str or tws_str.startswith("?"):
            return None
        
        def extract_mac(s: str) -> str | None:
            if "(" in s and ")" in s:
                return s.split("(")[1].rstrip(")")
            return None
        
        tws_mac = extract_mac(tws_str)
        secondary_mac = extract_mac(secondary_str) if secondary_str and not secondary_str.startswith("?") else None
        
        if tws_mac:
            return tws_mac, secondary_mac
        return None

    def save_settings(self) -> None:
        result = self._get_selected_macs()
        if not result:
            self.logger.warning("Select at least the TWS device before saving")
            return
        tws, secondary = result
        self.settings.set("tws_mac", tws)
        self.settings.set("iphone_mac", secondary or "")
        self.settings.save()
        self.logger.info(f"Settings saved: TWS={tws}, Secondary={secondary or '(none)'}")

    def start_sync_thread(self) -> None:
        result = self._get_selected_macs()
        if not result:
            self.logger.warning("Select at least the TWS device before syncing")
            return
        tws, secondary = result
        self.btn_sync.configure(state="disabled", text="⏳ Syncing...")
        threading.Thread(target=self._sync_with_cleanup, args=(tws, secondary or ""), daemon=True).start()

    def _sync_with_cleanup(self, tws: str, secondary: str = "") -> None:
        try:
            self.manager.sync_and_mix(tws, secondary)
        finally:
            self._update_sync_button()


    def _update_sync_button(self) -> None:
        self.btn_sync.configure(state="normal", text="▶ BUILD & SYNC")

    def _start_ui_update_loop(self) -> None:
        self._updating = True
        self._update_canvas()

    def _update_canvas(self) -> None:
        self.canvas.delete("bar")
        data = self.manager.get_fft_data()
        
        if data is None or len(data) == 0:
            self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2, 
                                   text="⏸ Waiting for audio signal...", 
                                   fill="#444444", tags="bar", font=("Inter", 12))
        else:
            bar_width = self.canvas_width / max(1, len(data))
            for i, val in enumerate(data):
                h = min(self.canvas_height - 8, max(4, val))
                ratio = h / self.canvas_height
                color = self._thermal_color(ratio)
                
                x0 = i * bar_width + 1
                y0 = self.canvas_height - h
                x1 = x0 + bar_width - 2
                y1 = self.canvas_height
                
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, tags="bar", outline="")

        if self._updating:
            self.after(60, self._update_canvas)

    def _thermal_color(self, ratio: float) -> str:
        if ratio < 0.2:
            return "#0066ff"  # Blue - cold
        if ratio < 0.4:
            return "#00ccff"  # Cyan
        if ratio < 0.6:
            return "#00ff66"  # Green - warm
        if ratio < 0.8:
            return "#ffaa00"  # Orange - hot
        return "#ff3333"      # Red - very hot

    def _on_close(self) -> None:
        self.logger.info("Shutting down...")
        self._updating = False
        try:
            self.manager.cleanup()
        except Exception:
            pass
        self.destroy()
