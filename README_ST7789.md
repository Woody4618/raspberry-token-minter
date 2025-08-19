# ST7789V2 Display for Raspberry Pi

A Python guide to drive the ST7789V2 TFT display over SPI using CircuitPython libraries on Raspberry Pi.

## 🖼️ Features

- 240x240 or 240x280 TFT display support (ST7789/ ST7789V2)
- SPI hardware acceleration via `board.SPI()`
- Backlight, reset, and DC pin control
- Render text with `adafruit_display_text`
- Draw shapes/images with `displayio`
- Rotation and row offset configuration

## 🔧 Hardware Setup

### Wiring Diagram (example used in this repo)

```
ST7789V2         Raspberry Pi
--------------------------------
VCC        →     3.3V
GND        →     GND
SCL/SCLK   →     SCLK (GPIO 11)
SDA/MOSI   →     MOSI (GPIO 10)
CS         →     GPIO 5   (board.D5)
DC         →     GPIO 24  (board.D24)
RES/RESET  →     GPIO 25  (board.D25)
BL/LED     →     3.3V (or PWM pin via transistor for brightness) (Not used in this project)
```

Notes:

- Keep wires short for stable SPI.
- Some ST7789 boards label pins slightly differently (e.g., `RST` vs `RES`, `DIN` vs `SDA`). Match SCLK to SCL, MOSI to SDA/DIN.

### Enable SPI on Raspberry Pi

```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

Reboot if prompted.

## 📋 Installation

Install required Python libraries:

For this project you can just install the whole requirements.txt file:

```bash
pip3 install -r requirements.txt
```

Or install the libraries individually:

```bash
pip3 install adafruit-circuitpython-st7789 adafruit-circuitpython-display-text adafruit-blinka
```

Optional (for image loading/drawing):

```bash
pip3 install pillow
```

## 🚀 Usage

### Basic Example (240x280 with rotation and row offset)

```python
import board
import displayio
from adafruit_st7789 import ST7789
from adafruit_display_text import label
import terminalio

# Always release displays before (re)initializing
displayio.release_displays()

spi = board.SPI()                 # Uses hardware SCLK/MOSI
tft_cs = board.D5                 # Chip select
tft_dc = board.D24                # Data/Command

# Create 4-wire SPI bus
display_bus = displayio.FourWire(
    spi,
    command=tft_dc,
    chip_select=tft_cs,
    reset=board.D25,             # Reset pin
)

# Create the display (width/height depend on your panel)
display = ST7789(
    display_bus,
    width=280,
    height=240,
    rowstart=20,                 # Row offset for 240x280 panels
    rotation=90                  # Rotate as needed: 0, 90, 180, 270
)

# Root group
splash = displayio.Group()
display.root_group = splash

# Background color
bg_bitmap = displayio.Bitmap(280, 240, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x303062
bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
splash.append(bg)

# Text label
text = label.Label(terminalio.FONT, text="Hello ST7789!", color=0xFFFFFF, x=40, y=60)
splash.append(text)

# Keep script running to show the display
while True:
    pass
```

### Example (matches this repo's script)

In `raspberry/button_token_mint_with_disply_and_mp3.py` we use:

- `board.SPI()` for SPI
- `board.D5` as CS, `board.D24` as DC, `board.D25` as RESET
- `ST7789(..., width=280, height=240, rowstart=20, rotation=90)`
- `adafruit_display_text.label` for on-screen text

## 📚 API Notes

- `displayio.release_displays()`: Call before re-initializing the display
- `displayio.FourWire(...)`: SPI transport with DC/CS/RESET pins
- `ST7789(...)` args to know:
  - **width/height**: Panel dimensions
  - **rotation**: 0/90/180/270
  - **rowstart/colstart**: Offsets (many 240x280 boards need `rowstart=20`)
- `display.root_group = my_group`: Set the root render group
- `displayio.Group(scale, x, y)`: Position and scale groups
- `label.Label(font, text, color, x, y)`: Render text

## 🔧 Troubleshooting

1. No image / white screen

   - Check SPI enabled
   - Verify CS/DC/RESET pins match your wiring
   - Confirm power: use 3.3V (not 5V unless your board supports it)

2. Text appears off-screen or cut off

   - Adjust `rotation`, `rowstart`, and `colstart`
   - Ensure `width/height` match your panel

3. Colors look wrong

   - Confirm your display class: `adafruit_st7789.ST7789`
   - Update libraries to latest versions

4. SPI errors / timeouts

   - Keep wires short, use good quality jumpers
   - Try slower SPI speed (advanced: via bus config)

## 📁 File Structure (relevant parts)

```
project/
├── raspberry/
│   └── button_token_mint_with_disply_and_mp3.py  # Uses ST7789 display
├── mp3_player.py
├── README_ST7789.md       # This guide
└── README_MP3.md          # MP3 guide
```

## 🔗 Resources

- Adafruit ST7789 Python Guide: https://learn.adafruit.com/2-0-inch-320-x-240-color-ips-tft-display/python-wiring-and-setup
- CircuitPython DisplayIO: https://docs.circuitpython.org/en/latest/shared-bindings/displayio/
- Adafruit `adafruit_st7789` library: https://github.com/adafruit/Adafruit_CircuitPython_ST7789
- Docs: https://docs.circuitpython.org/projects/st7789/en/latest/
- Raspberry Pi SPI docs: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#spi
