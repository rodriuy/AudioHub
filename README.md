# AudioHub Pro

A Linux Mint Bluetooth audio router for TWS headphones and other audio devices. Connect your speakers/TWS to Linux and route audio with a simple UI.

## Features

- Bluetooth device scanning and connection
- Route audio to multiple devices
- Real-time audio visualizer
- Save device settings
- Works with PulseAudio and PipeWire

## Requirements

- Linux (tested on Linux Mint)
- `bluetoothctl` and `pactl` installed
- Python 3.8+

## Quick start

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
./run_app.sh
# or
python3 app.py
```

3. For debugging audio & Bluetooth issues:

```bash
python3 debug_audio.py
```

This will show all connected BT devices, available audio sinks/sources, and help you identify why audio routing might fail.

## Notes

- Make sure your user has permissions to manage Bluetooth and audio devices.
- `settings.json` is created in the project folder when you save MACs from the UI.

## Troubleshooting

**"Audio is not routed to TWS"**

1. Ensure TWS are **powered on and in pairing mode**.
2. Click **🔍 Scan Bluetooth Devices** to discover them.
3. Select TWS from the dropdown and click **BUILD & SYNC**.
   - This sets the TWS as your default audio output device.
4. Open any audio app (browser, media player, etc.) and play something.
   - Audio should come out the TWS speakers.
5. Check logs in the app for error messages.

**"I see devices but audio still doesn't play"**

1. Run the debug tool to check PulseAudio status:
   ```bash
   python3 debug_audio.py
   ```
   - Look for your TWS in the "Available Audio Sinks" section
   - If missing, restart Bluetooth: `bluetoothctl power off && bluetoothctl power on`

2. Manually set default sink:
   ```bash
   pactl set-default-sink bluez_output.XX_XX_XX_XX_XX_XX.1
   ```
   (Replace `XX_XX_...` with your TWS MAC, using underscores)

3. Test audio:
   ```bash
   speaker-test -t wav -c 2
   ```

**"Audio got stuck after closing the app"**

Run the cleanup script:
```bash
bash cleanup_audio.sh
```

Or restart PulseAudio:
```bash
systemctl --user restart pulseaudio
```

## License

MIT — see `LICENSE`.
