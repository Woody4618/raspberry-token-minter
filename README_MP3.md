# MP3-TF-16P Player for Raspberry Pi

A Python script to control the MP3-TF-16P chip via UART to play MP3 files from an SD card.

## 🎵 Features

- Play tracks by number (1-255)
- Play tracks from specific folders
- Play files by filename
- Control volume (0-30)
- Pause/Resume/Stop playback
- Random play mode
- Loop playback
- Status monitoring

## 🔧 Hardware Setup

MP3-TF-16P: [DFPlayer Mini](https://www.amazon.de/dp/B0DRGCC1M6) (also known as DFPlayer Mini)
Speaker: [3W 8Ω](https://www.amazon.de/Lautsprecher-JST-PH2-0-Schnittstelle-Raspberry-Elektronischer/dp/B08QFTYB9Z)

### Wiring Diagram

```
MP3-TF-16P    Raspberry Pi
VCC      →     3.3V
GND      →     GND
RX       →     TX (GPIO 14)
TX       →     RX (GPIO 15)
```

### Pin Connections

- **VCC**: Connect to 3.3V power
- **GND**: Connect to ground
- **RX**: Connect to Raspberry Pi TX (GPIO 14)
- **TX**: Connect to Raspberry Pi RX (GPIO 15)

Also connect your 3W speaker to the speaker output of the MP3-TF-16P.

## 📋 Installation

1. **Install dependencies**:

   ```bash
   pip3 install pyserial
   ```

2. **Enable UART** (if not already enabled):

   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Serial Port
   # Enable serial port
   # Disable serial console
   ```

3. **Check available ports**:

   ```bash
   ls /dev/tty*
   ```

4. **Set permissions** (if needed):
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and back in
   ```

## 🎵 SD Card Setup

1. **Format SD card** as FAT32
2. **Create folders** (optional):
   ```
   /01/  (folder 1)
   /02/  (folder 2)
   /03/  (folder 3)
   ```
3. **Add MP3 files**:
   - Files must be named: `001.mp3`, `002.mp3`, etc.
   - Or use descriptive names: `song.mp3`, `music.mp3`

## 🚀 Usage

### Basic Usage

```python
from mp3_player import MP3Player

# Initialize player
player = MP3Player(port='/dev/serial0')

# Connect
if player.connect():
    # Play track 1
    player.play_track(1)

    # Set volume
    player.set_volume(20)

    # Stop
    player.stop()

    # Disconnect
    player.disconnect()
```

### Interactive Mode

```bash
python3 mp3_player.py
```

## 📚 API Reference

### MP3Player Class

#### `__init__(port='/dev/ttyUSB0', baudrate=9600, timeout=1)`

Initialize the MP3 player.

#### `connect() → bool`

Connect to the MP3-TF-16P module.

#### `disconnect()`

Disconnect from the module.

#### `play_track(track_number: int) → bool`

Play a specific track by number (1-255).

#### `play_folder_track(folder: int, track: int) → bool`

Play a track from a specific folder.

#### `play_file(filename: str) → bool`

Play a specific file by name.

#### `pause() → bool`

Pause playback.

#### `resume() → bool`

Resume playback.

#### `stop() → bool`

Stop playback.

#### `set_volume(volume: int) → bool`

Set volume (0-30, where 0 is mute).

#### `get_status() → Optional[dict]`

Get current playback status.

#### `play_random() → bool`

Play tracks in random order.

#### `play_loop(enable: bool = True) → bool`

Enable/disable loop playback.

## 🔧 Troubleshooting

### Common Issues

1. **"Permission denied" error**:

   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and back in
   ```

2. **"Device not found" error**:

   - Check wiring connections
   - Try different ports: `/dev/ttyUSB0`, `/dev/ttyAMA0`, `/dev/ttyS0`
   - Enable UART in raspi-config

3. **No sound output**:

   - Check speaker/headphone connections
   - Verify SD card is properly inserted
   - Check file format (must be MP3)

4. **Commands not working**:
   - Verify baudrate (default: 9600)
   - Check file naming convention
   - Ensure SD card is FAT32 formatted

### Debug Mode

```python
# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 File Structure

```
project/
├── mp3_player.py      # Main player script
├── requirements.txt    # Dependencies
├── README_MP3.md      # This guide
└── sounds/            # MP3 files folder
    ├── 001.mp3
    ├── 002.mp3
    └── song.mp3
```

## 🎯 Example Projects

### Simple Sound Player

```python
from mp3_player import MP3Player
import time

player = MP3Player()
if player.connect():
    player.set_volume(25)
    player.play_track(1)
    time.sleep(30)  # Play for 30 seconds
    player.stop()
    player.disconnect()
```

### Sound Effects Player

```python
def play_sound_effect(effect_name):
    player = MP3Player()
    if player.connect():
        player.play_file(f"{effect_name}.mp3")
        time.sleep(2)  # Wait for effect to finish
        player.disconnect()
```

## 📝 Notes

- **File naming**: Use 3-digit numbers (001.mp3, 002.mp3) for automatic track selection
- **Volume range**: 0-30 (0 = mute, 30 = maximum)
- **Track numbers**: 1-255
- **Folder numbers**: 1-99
- **Baudrate**: Usually 9600, but can be 38400 for some modules

## 🔗 Resources

- [MP3-TF-16P Datasheet](https://www.dfrobot.com/wiki/index.php/DFPlayer_Mini_SKU:DFR0299)
- [Raspberry Pi UART Guide](https://www.raspberrypi.org/documentation/configuration/uart.md)
- [PySerial Documentation](https://pyserial.readthedocs.io/)
