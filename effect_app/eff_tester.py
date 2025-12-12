#!/usr/bin/env python
global NUM_LEDS
ORIENTATION = "BOTTOM"
NUM_LEDS = 100

from libs import time
from monotonic import monotonic
from random import randrange, uniform, choice
import argparse
import colorsys
import math
import random as rndm
import tkinter as tk

def random():
    return rndm.random()

def env_to_phys(env_idx: int) -> int:
    """
    Environment index:
      0             = physical bottom
      NUM_LEDS - 1  = physical top

    ORIENTATION tells us where the 2350W sits on that vertical line:
      - BOTTOM: 2350W at bottom -> env index matches physical index
      - TOP:    2350W at top    -> env index is flipped
    """
    if ORIENTATION == "BOTTOM":
        return env_idx
    else:  # "TOP"
        return NUM_LEDS - 1 - env_idx

def set_hsv_env(env_idx: int, h: float, s: float, v: float):
    """Set LED using environment coordinates (0 = bottom, NUM_LEDS-1 = top)."""
    phys = env_to_phys(env_idx)
    led_strip.set_hsv(phys, h, s, v)

def set_rgb_env(env_idx: int, r: int, g: int, b: int):
    """RGB version using environment coordinates."""
    phys = env_to_phys(env_idx)
    led_strip.set_rgb(phys, r, g, b)

def hsv_to_grb(h, s, v):
    """Converts HSV color space to GRB color space for the LED strip."""
    r, g, b = hsv_to_rgb(h, s, v)
    return g, r, b  # Swap red and green for GRB

def hsv_to_rgb(h, s, v):
    """Converts HSV color space to RGB color space."""
    if s == 0.0:
        v = int(v * 255)
        return v, v, v
    i = int(h * 6.0)  # Assume h is 0-1
    f = (h * 6.0) - i
    p = int(v * (1.0 - s) * 255)
    q = int(v * (1.0 - s * f) * 255)
    t = int(v * (1.0 - s * (1.0 - f)) * 255)
    v = int(v * 255)
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q

def effect_1(hsv_values):     
  """Color-Cycling Pulse effect."""     
  for t in range(1000):     
      for i in range(NUM_LEDS):     
          hue = (i + t) % 360 / 360.0     
          brightness = (1 + math.sin(t * 2 * math.pi / 100)) / 2     
          hsv_values[i] = (hue, 1.0, brightness)     
          led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])     
      time.sleep(0.01)     
  return hsv_values

# paste further effect functions below
# def effect_2(hsv_values):
#  ..

class EffectTesterApp:
    def __init__(self, root, effect=1):
        global led_strip
        led_strip = self
        self.effect = effect
        self.effect_start = monotonic()
        self.root = root
        self.root.title("Effect tester")
        self.root.geometry('+0+0')
        self.root.overrideredirect(True)

        # Create a canvas to draw LEDs
        self.canvas = tk.Canvas(self.root, width=NUM_LEDS * 15, height=100, bg="black")
        self.canvas.pack()

        # Initialize LED data
        self.leds = []
        self.colors = []
        self.hsv_values = [(0.0, 0.0, 0.0) for _ in range(NUM_LEDS)]
        self._create_leds()

        # Start automatic color updates
        self._auto_update_colors()

    def _create_leds(self):
        """Create LEDs in a single row."""
        for i in range(NUM_LEDS):
            x1 = 20 + i * 15
            y1 = 20
            x2 = x1 + 10
            y2 = y1 + 10
            color = '#000000' 
            led = self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")
            self.leds.append(led)
            self.colors.append(color)

    def set_hsv(self, position, h, s, v):
        """Set the color of a LED at the given position using HSV values."""
        if 0 <= position < NUM_LEDS:
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r, g, b = [min(x, 1) for x in (r, g, b)]
            # g, r, b = colorsys.hsv_to_rgb(h, s, v)
            hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            self.canvas.itemconfig(self.leds[position], fill=hex_color)
            self.colors[position] = hex_color
        self.root.update()

    def set_rgb(self, position, g, r, b):
        """Set the color of a LED at the given position using RGB values."""
        if 0 <= position < NUM_LEDS:
            hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            self.canvas.itemconfig(self.leds[position], fill=hex_color)
            self.colors[position] = hex_color
        self.root.update()

    def _auto_update_colors(self):
        """Automatically update the colors of all LEDs at regular intervals."""
        self.hsv_values = globals().get(f'effect_{self.effect}')(self.hsv_values)
        for pos, values in enumerate(self.hsv_values):
            self.set_hsv(pos, *values)
        self.root.after(10, self._auto_update_colors)  # Update every 500 milliseconds
        if monotonic() - self.effect_start > 10:
            self.root.quit()


if __name__ == "__main__":
    led_strip = None
    TIMEOUT_DURATION = 20 * 1000
    root = tk.Tk()
    parser = argparse.ArgumentParser(description="Effect tester.")
    parser.add_argument("effect", type=int, default=1, help="Effect number")
    args = parser.parse_args()
    app = EffectTesterApp(root, effect=args.effect)
    root.mainloop()
