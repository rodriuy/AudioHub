#!/usr/bin/env bash
# Cleanup script for AudioHub Pro
# Removes lingering loopback modules and resets audio to defaults

echo "AudioHub Pro — Audio Cleanup & Reset"
echo "===================================="
echo ""

# Find and unload all loopback modules
echo "1. Checking for loopback modules..."
LOOPBACK_MODULES=$(pactl list short modules | grep loopback | awk '{print $1}')

if [ -z "$LOOPBACK_MODULES" ]; then
    echo "   ✓ No loopback modules found"
else
    echo "   Found loopback modules, unloading..."
    for module_id in $LOOPBACK_MODULES; do
        echo "   - Unloading module #$module_id..."
        pactl unload-module "$module_id"
    done
fi

echo ""
echo "2. Killing any stray pactl processes..."
pkill -f "pactl load-module" 2>/dev/null || true

echo ""
echo "3. Current Bluetooth devices:"
bluetoothctl devices Connected || echo "   (No devices connected)"

echo ""
echo "4. Current audio sinks:"
pactl list short sinks | grep -E "bluez|hdmi|usb|analog" | head -5

echo ""
echo "✓ Cleanup complete"
echo ""
echo "Tips:"
echo "  - Restart PulseAudio if issues persist: systemctl --user restart pulseaudio"
echo "  - Or kill the user session: killall -9 pulseaudio pipewire"
