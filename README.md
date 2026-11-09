# 🌈 Plasma 2350W — LED FX Engine (77 Effects)

A feature-rich LED animation engine for the Pimoroni Plasma 2350W, Plasma Stick 2040, RP2040 board with WS2812/NeoPixel strip.

77 handcrafted effects, orientation-aware physics, comet particles, fireworks, waterfalls, meteors, neon beams, rain, and more.

Designed for Christmas trees, handrails, continuous ambient lighting, decorative installs.

# ✨ Features

77 unique LED effects (waves, rain, fire, explosions, neon, sparkles, spirals, digital rain…)

Orientation-aware engine
Effects automatically adapt when the 2350W is mounted at the top or bottom of the strip.

Starfield boot mode
Start with the cinematic starfield or the FX show (`BOOT_MODE` in `configuration.py`); hold BUTTON A (only supported on 2350W) on reset for the other one.

Continuous FX show with smooth transitions

Random timing & variation

# 🎛️ Hardware Requirements

- Pimoroni Plasma Stick / 2350W / 2040 - Compatible with latest Plasma firmware (v1.0.0) [Grab one here](https://shop.pimoroni.com/products/plasma-2350-w?variant=54829890601339)

- WS2812 / NeoPixel LED strip

- USB-C power supply

- Thonny or any MicroPython REPL for uploading code

# 🧭 LED Amount & Orientation System

Review the `configuration.py`:

```
ORIENTATION = "BOTTOM"   # controller at bottom, LEDs go up
#ORIENTATION = "TOP"    # controller at top, LEDs go down
```
```
NUM_LEDS = <NumberOfLEDS>
```
In `main.py`:
```
color_order=plasma.COLOR_ORDER_GRB
```
The effects are tuned for a strip that swaps red and green, so set this to your strip's real colour order with R and G swapped: an RGB strip uses `COLOR_ORDER_GRB`, a BGR strip uses `COLOR_ORDER_BRG`.

Not sure what your strip is? Run `rgb_test.py` from Thonny: it lights the whole strip red, green, blue, then white, and the colours you actually see give the order. To check the setting, effect 70 should show red and white bars (not green and white).
# 💫 Starfield Boot Mode

Choose what the board starts with in `configuration.py`:

```
BOOT_MODE = "FX"           # straight to the 77-effect automatic show (default)
#BOOT_MODE = "STARFIELD"   # starfield + comets, then the FX show when BUTTON A is pressed
```

Hold BUTTON A (only available on 2350W) while pressing RESET to start the other mode instead, just for that boot.

Starfield runs until BUTTON A is pressed, then switches to the FX show.

# 🚀 Getting Started

- Flash the Plasma 2040/2350W MicroPython firmware v1.0.0

- Copy `main.py`, `eff.py` and `configuration.py` to your board

- for Plasma 2040W: copy `eff.mpy` instead of `eff.py` - otherwise you'll get memory errors

- Reboot

- It starts in the mode set by `BOOT_MODE` (the FX show unless you change it); hold BUTTON A on boot for the other one

# 🖥️ Effect simulator

`simulator/` contains a browser-based simulator that runs the effects from `eff.py` on a virtual strip, with a virtual clock and emulation of the Plasma WS2812 firmware. See [simulator/README.md](simulator/README.md).
