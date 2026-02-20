#!/usr/bin/env bash
# Stop microphone and reset audio system

echo "Stopping AudioHub and resetting audio..."
pkill -f "python3 app.py" 2>/dev/null || true
pkill -f sounddevice 2>/dev/null || true

echo "Restarting PipeWire..."
systemctl --user restart wireplumber pipewire 2>/dev/null || systemctl --user restart pulseaudio 2>/dev/null || true

sleep 2
echo "✓ Audio reset complete — microphone should be disabled"
