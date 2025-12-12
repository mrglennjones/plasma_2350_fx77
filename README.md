# 🌈 Plasma 2350W — LED FX Engine (77 Effects)

A feature-rich LED animation engine for the Pimoroni Plasma 2350W, Plasma Stick 2040, RP2040 board with WS2812/NeoPixel strip.

77 handcrafted effects, orientation-aware physics, comet particles, fireworks, waterfalls, meteors, neon beams, rain, and more.

Designed for Christmas trees, handrails, continuous ambient lighting, decorative installs.

# ✨ Features

77 unique LED effects (waves, rain, fire, explosions, neon, sparkles, spirals, digital rain…)

Orientation-aware engine
Effects automatically adapt when the 2350W is mounted at the top or bottom of the strip.

Starfield boot mode
Hold BUTTON A on reset to launch the cinematic starfield mode.

Continuous FX show with smooth transitions

Random timing & variation

# 🎛️ Hardware Requirements

Pimoroni Plasma Stick / 2350W / 2040 - Compatible with latest Plasma firmware (v1.0.0) [Grab one here](https://shop.pimoroni.com/products/plasma-2350-w?variant=54829890601339)

WS2812 / NeoPixel LED strip

USB-C power supply

Thonny or any MicroPython REPL for uploading code

# 🧭 LED Amount & Orientation System

Set in your script:

```
ORIENTATION = "BOTTOM"   # controller at bottom, LEDs go up
#ORIENTATION = "TOP"    # controller at top, LEDs go down
```
```
NUM_LEDS = <NumberOfLEDS>
```

# 💫 Starfield Boot Mode

Hold BUTTON A while pressing RESET:

Held: boot into the starfield + comets mode

Not held: proceed to the 77-effect automatic show

Starfield runs until the button is pressed again.

# 🚀 Getting Started

Flash the Plasma 2350W MicroPython firmware v1.0.0

Copy main.py to your board

Reboot

Hold BUTTON A on boot for starfield mode

Otherwise enjoy the full FX show

Effects can be previewed [here](effects_preview.md) - please note that the actual speed of the effect may differ.
