#!/usr/bin/env python3
"""AudioHub Pro — Debug Tool for Bluetooth and Audio Issues.

Run this script to diagnose connectivity and audio routing problems.
"""

import subprocess
import sys


def run_cmd(cmd: str, title: str = "") -> str:
    """Execute a shell command and return output."""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    result = subprocess.getoutput(cmd)
    print(result if result else "(No output)")
    return result


def main():
    print("\n" + "="*60)
    print("  AudioHub Pro — Bluetooth & Audio Debug Tool")
    print("="*60)

    # Bluetooth Status
    run_cmd("bluetoothctl show", "1. Bluetooth Controller Status")
    
    # Connected Devices
    run_cmd("bluetoothctl devices Connected", "2. Connected Bluetooth Devices")
    
    # All Devices
    run_cmd("bluetoothctl devices", "3. All Known Bluetooth Devices")
    
    # PulseAudio/PipeWire Sinks (outputs)
    run_cmd("pactl list short sinks", "4. Available Audio Sinks (Outputs)")
    
    # PulseAudio/PipeWire Sources (inputs)
    run_cmd("pactl list short sources", "5. Available Audio Sources (Inputs)")
    
    # Loaded Modules
    run_cmd("pactl list short modules | grep -i loopback", "6. Loaded Loopback Modules")
    
    # Check if module-loopback is available
    run_cmd("pactl load-module module-loopback 2>&1 | head -1", "7. Test Module Availability")
    
    print("\n" + "="*60)
    print("  Manual Testing Steps:")
    print("="*60)
    print("""
1. ENSURE iPhone is playing audio (music, video, etc.)
2. Find your TWS MAC in section 2 above
3. Find your iPhone MAC in section 2 above
4. Replace XX:XX:XX:XX:XX:XX with your MAC and test routing:

   # Find source and sink first:
   pactl list short sources | grep <iphone-mac>
   pactl list short sinks | grep <tws-mac>
   
   # Then route manually:
   pactl load-module module-loopback source=<source> sink=<sink>
   
5. If you hear audio, the issue is in app detection logic
   If you don't, check Bluetooth pairing and audio permissions
    """)
    
    print("\n" + "="*60)
    print("  Cleanup:")
    print("="*60)
    run_cmd("pactl list short modules | grep loopback", "Unload old loopback modules:")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n(Cancelled)")
        sys.exit(0)
