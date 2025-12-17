# fx_77_starfield_startup.py

import time
import math
import gc
from random import randrange, uniform, random, choice
from eff import *
from configuration import *

import plasma
from os import uname
from machine import Pin
from pimoroni import RGBLED

# Plasma Stick 2040 has no LED
if 'Plasma Stick 2040' not in uname().machine:
    led = RGBLED("LED_R", "LED_G", "LED_B")

class LedStrip(plasma.WS2812):
    def __init__(self, *args, brightness=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.brightness = brightness

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        print(f'changed brightness to {value}')
        self._brightness = max(0.0, min(1.0, value))

    def set_rgb(self, i, r, g, b):
        r = int(max(0, min(255, r * self.brightness)))
        g = int(max(0, min(255, g * self.brightness)))
        b = int(max(0, min(255, b * self.brightness)))
        super().set_rgb(i, r, g, b)

    def set_hsv(self, i, h, s, v):
        v = max(0, min(1, v * self.brightness))
        super().set_hsv(i, h, s, v)

    def increase_brightness(self, step=0.05):
        self.brightness += step

    def decrease_brightness(self, step=0.05):
        self.brightness -= step


# Set your led strip as R → G → B, order:
led_strip = LedStrip(
    NUM_LEDS,
    brightness=BRIGHTNESS,
    color_order=plasma.COLOR_ORDER_BRG
)
led_strip.start()


# -----------------------------
# BUTTON SETUP (Plasma 2350 W)
# -----------------------------
try:
    button_a = Pin("BUTTON_A", Pin.IN, Pin.PULL_UP)
    print("DEBUG: BUTTON_A created, initial value:", button_a.value())
except Exception as e:
    print("DEBUG: BUTTON_A not available:", e)
    button_a = None


def button_pressed():
    """Return True if BUTTON A is pressed (active-low)."""
    if button_a is None:
        return False
    # Active-low: 0 = pressed, 1 = not pressed
    return button_a.value() == 0

def wait_for_button_release():
    """Block until BUTTON A is released (goes high)."""
    if button_a is None:
        return
    while button_a.value() == 0:  # still pressed
        time.sleep_ms(10)


def wait_for_button_press():
    """Block until BUTTON A is pressed (goes low)."""
    if button_a is None:
        return
    while button_a.value() == 1:  # not pressed
        time.sleep_ms(10)



# -----------------------------
# STARFIELD STATE
# -----------------------------

star_current = [0.0] * NUM_LEDS      # current brightness
star_target = [0.0] * NUM_LEDS       # target brightness
star_hue = [0.0] * NUM_LEDS          # subtle hue variation
star_sat = [0.0] * NUM_LEDS          # subtle saturation variation


def random_star_brightness():
    """Return a brightness value with many dim stars and few bright ones."""
    x = uniform(0.0, 1.0)
    x = x * x  # bias towards lower values
    return STAR_MIN_BRIGHT + x * (STAR_MAX_BRIGHT - STAR_MIN_BRIGHT)


def init_stars():
    """Initialise all stars with random brightness and slight colour variation."""
    for i in range(NUM_LEDS):
        b = random_star_brightness()
        star_current[i] = b
        star_target[i] = random_star_brightness()

        # hue around a cool white (220°), ±STAR_HUE_SPREAD/2
        hue_offset_deg = uniform(-STAR_HUE_SPREAD / 2, STAR_HUE_SPREAD / 2)
        star_hue[i] = (220 + hue_offset_deg) / 360.0

        # tiny bit of saturation so it's not dead flat
        star_sat[i] = uniform(0.0, STAR_SATURATION_MAX)


def update_stars():
    """Move each star towards its target brightness and occasionally choose a new one."""
    for i in range(NUM_LEDS):
        # Occasionally choose a new random target brightness
        if random() < STAR_NEW_TARGET_CHANCE:
            star_target[i] = random_star_brightness()

        # Smoothly ease current brightness towards target
        cur = star_current[i]
        tgt = star_target[i]

        if cur < tgt:
            cur += STAR_FADE_SPEED
            if cur > tgt:
                cur = tgt
        elif cur > tgt:
            cur -= STAR_FADE_SPEED
            if cur < tgt:
                cur = tgt

        star_current[i] = cur

        # Draw star
        led_strip.set_hsv(i, star_hue[i], star_sat[i], cur)


def run_comet():
    """Animate a single comet gliding across the strip. Aborts if button is pressed."""
    trail_len = randrange(COMET_MIN_TRAIL, COMET_MAX_TRAIL + 1)
    if trail_len > NUM_LEDS:
        trail_len = NUM_LEDS

    # Random direction
    direction = 1 if randrange(2) == 0 else -1

    # Random speed and head brightness for variety
    comet_delay = uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)
    head_brightness = uniform(COMET_HEAD_BRIGHT_MIN, COMET_HEAD_BRIGHT_MAX)

    if direction == 1:
        head = -trail_len
        end = NUM_LEDS + trail_len
        step = 1
    else:
        head = NUM_LEDS + trail_len
        end = -trail_len
        step = -1

    while head != end:
        if button_pressed():
            # Abort comet immediately if button is pressed
            return

        # Draw background first
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, star_hue[i], star_sat[i], star_current[i])

        # Draw comet on top
        for k in range(trail_len):
            pos = head - k * direction
            if 0 <= pos < NUM_LEDS:
                # Fraction along tail: 0 at the end, 1 at the head
                frac = (trail_len - k) / float(trail_len)
                # Use squared falloff for a bright head, smooth tail
                comet_b = head_brightness * (frac * frac)

                # Slight colour gradient: head more coloured, tail whiter
                tail_sat = COMET_SAT * frac   # more saturated at head
                tail_hue = COMET_HUE

                led_strip.set_hsv(pos, tail_hue, tail_sat, comet_b)

                # Gentle afterglow: boost star brightness a little, but keep within range
                glow_boost = comet_b * AFTERGLOW_MAX
                new_star_b = min(star_current[pos] + glow_boost, STAR_MAX_BRIGHT)
                star_current[pos] = new_star_b

        time.sleep(comet_delay)
        head += step


def run_starfield_until_button():
    """Run the starfield + occasional comets.

    - BUTTON A held at boot selects this mode.
    - Starfield starts animating immediately.
    - Only after the button has been released once, a *new* press will exit.
    """
    init_stars()

    exit_armed = False  # becomes True once we've seen the button released

    print("Starfield: running (will exit on BUTTON A *after* first release)")

    while True:
        update_stars()

        # Track button state for exit logic
        if not exit_armed:
            # Arm exit once we've seen it released at least once
            if not button_pressed():
                exit_armed = True
        else:
            # Once armed, a press is treated as "exit now"
            if button_pressed():
                print("Starfield: BUTTON A pressed after release -> exiting to FX show")
                # Optional: wait for release so the FX show doesn't see a 'stuck' press
                while button_pressed():
                    time.sleep_ms(10)
                break

        # Occasionally launch a comet
        comet_chance = COMET_BASE_CHANCE * uniform(0.5, 1.5)
        if random() < comet_chance:
            # Inside comet, honour the same exit logic
            head_armed = exit_armed
            trail_len = randrange(COMET_MIN_TRAIL, COMET_MAX_TRAIL + 1)
            if trail_len > NUM_LEDS:
                trail_len = NUM_LEDS

            direction = 1 if randrange(2) == 0 else -1
            comet_delay = uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)
            head_brightness = uniform(COMET_HEAD_BRIGHT_MIN, COMET_HEAD_BRIGHT_MAX)

            if direction == 1:
                head = -trail_len
                end = NUM_LEDS + trail_len
                step = 1
            else:
                head = NUM_LEDS + trail_len
                end = -trail_len
                step = -1

            while head != end:
                # Update exit arming while comet is running
                if not head_armed and not button_pressed():
                    head_armed = True
                elif head_armed and button_pressed():
                    print("Starfield: exit requested during comet")
                    while button_pressed():
                        time.sleep_ms(10)
                    return  # leave starfield immediately

                # Draw background
                for i in range(NUM_LEDS):
                    led_strip.set_hsv(i, star_hue[i], star_sat[i], star_current[i])

                # Draw comet
                for k in range(trail_len):
                    pos = head - k * direction
                    if 0 <= pos < NUM_LEDS:
                        frac = (trail_len - k) / float(trail_len)
                        comet_b = head_brightness * (frac * frac)
                        tail_sat = COMET_SAT * frac
                        tail_hue = COMET_HUE

                        led_strip.set_hsv(pos, tail_hue, tail_sat, comet_b)

                        glow_boost = comet_b * AFTERGLOW_MAX
                        new_star_b = min(star_current[pos] + glow_boost, STAR_MAX_BRIGHT)
                        star_current[pos] = new_star_b

                time.sleep(comet_delay)
                head += step

        time.sleep(TWINKLE_FRAME_DELAY)



# ------------------------------------------------
# COMMON UTILS FOR 77-FX SECTION
# ------------------------------------------------

# Effects that should be allowed to run their full sequence and NOT be cut off by a random timer.
# Use 1-based effect numbers here (so effect_40 == 40).
FULL_RUN_EFFECTS = {
    12,   # Tetris Block Fall (runs a full stack + disperse sequence)
    40,   # Bouncing ball to the top + fade-out
    # Add more here later if you find other 'must finish' animations
}


class EffectManager:
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.current_effect = -1
        self.hsv_values = [(0.0, 0.0, 0.0)] * num_leds

    def select_next_effect(self):
        """Choose a different random effect each time."""
        if len(effects) <= 1:
            self.current_effect = 0
            return

        new_fx = self.current_effect
        while new_fx == self.current_effect:
            new_fx = randrange(len(effects))
        self.current_effect = new_fx

    def run_current_effect(self):
        """Run the currently selected effect.

        - For 'timed' effects: set a random TIMEOUT_DURATION, let the effect honour it.
        - For 'full-run' effects: just let them do their thing once.
        """
        global TIMEOUT_DURATION

        fx_index = self.current_effect          # 0-based
        fx_number = fx_index + 1                # 1–77
        fx_fn = effects[fx_index]

        if fx_number in FULL_RUN_EFFECTS:
            # Full-run: effect controls its own duration completely.
            self.hsv_values = fx_fn(self.hsv_values, led_strip)
        else:
            # Timed / ambient: push a random duration into the global timeout
            TIMEOUT_DURATION = get_random_timeout_duration()
            self.hsv_values = fx_fn(self.hsv_values, led_strip)


#def hsv_to_grb(h, s, v):
#    """Converts HSV to GRB color space to accommodate the GRB LED strip."""
#    r, g, b = hsv_to_rgb(h, s, v)
#    return g, r, b  # Swap R and G to fit the GRB color order

def hsv_to_grb(h, s, v):
    """Converts HSV color space to GRB 0–255 ints for the LED strip."""
    r, g, b = hsv_to_rgb(h, s, v)  # r,g,b in 0.0–1.0
    return int(g * 255), int(r * 255), int(b * 255)  # GRB order as ints


# tester

#effects = [effect_40]

# List of effects
effects = [globals()[f"effect_{i}"] for i in range(1, 78)]
'''effects = [
    effect_1, effect_2, effect_3, effect_4, effect_5,
    effect_6, effect_7, effect_8, effect_9, effect_10,
    effect_11, effect_12, effect_13, effect_14, effect_15,
    effect_16, effect_17, effect_18, effect_19, effect_20,
    effect_21, effect_22, effect_23, effect_24, effect_25,
    effect_26, effect_27, effect_28, effect_29, effect_30,
    effect_31, effect_32, effect_33, effect_34, effect_35,
    effect_36, effect_37, effect_38, effect_39, effect_40,
    effect_41, effect_42, effect_43, effect_44, effect_45,
    effect_46, effect_47, effect_48, effect_49, effect_50,
    effect_51, effect_52, effect_53, effect_54, effect_55,
    effect_56, effect_57, effect_58, effect_59, effect_60,
    effect_61, effect_62, effect_63, effect_64, effect_65,
    effect_66, effect_67, effect_68, effect_69, effect_70,
    effect_71, effect_72, effect_73, effect_74, effect_75,
    effect_76, effect_77
]
'''

manager = EffectManager(NUM_LEDS)
# ============================================================
# MAIN CONTROL FLOW
# ============================================================
def get_random_timeout_duration():
    return randrange(MIN_EFFECT_DURATION, MAX_EFFECT_DURATION)


def run_full_effect_show():
    """Endless loop cycling through your 77 effects, printing FX + runtime."""
    while True:
        manager.select_next_effect()
        fx_index = manager.current_effect          # 0-based
        fx_number = fx_index + 1                   # 1–77
        fx_fn = effects[fx_index]

        start_ms = time.ticks_ms()
        print("Starting FX", fx_number, "-", fx_fn.__name__)

        manager.run_current_effect()

        end_ms = time.ticks_ms()
        elapsed_ms = time.ticks_diff(end_ms, start_ms)
        elapsed_s = elapsed_ms / 1000.0
        print("FX", fx_number, "runtime:", elapsed_ms, "ms (", elapsed_s, "s )")

        gc.collect()

def choose_boot_mode():
    """Check for BUTTON A during a short window after reset to choose startup mode."""
    # Let hardware settle
    time.sleep(0.05)

    BOOT_WINDOW_MS = 1200
    start = time.ticks_ms()

    print("Boot: hold BUTTON A for STARFIELD; release for FX SHOW")

    while time.ticks_diff(time.ticks_ms(), start) < BOOT_WINDOW_MS:
        if button_pressed():
            print("Boot: BUTTON A detected -> STARFIELD MODE")
            return "starfield"
        time.sleep(0.01)

    print("Boot: no button -> FX SHOW")
    return "fx"

# button A adds brightness initially
brightness_direction = 1

def change_brightness(pin):
    step = 0.1
    global brightness_direction
    global led

    if led_strip.brightness >= 1:
        brightness_direction = -1
    elif led_strip.brightness <= step:
        brightness_direction = 1
    
    new_brightness = led_strip.brightness + step * brightness_direction
    led_strip.brightness = new_brightness

    # provide a visual indication that a limit has been reached
    # and the direction of change will be reversed
    if new_brightness >= 1.0:
        # red
        for i in range(10):
            led.set_rgb(255, 0, 0)
            time.sleep_ms(75)
            led.set_rgb(0, 0, 0)
            time.sleep_ms(75)
    elif new_brightness <= step:
        # green
        for i in range(10):
            led.set_rgb(0, 255, 0)
            time.sleep_ms(75)
            led.set_rgb(0, 0, 0)
            time.sleep_ms(75)

# Button_A
btn_up = Pin('GPIO12', Pin.IN, Pin.PULL_UP)
btn_up.irq(trigger=Pin.IRQ_FALLING, handler=change_brightness)

if __name__ == "__main__":
    # Small delay so the pin and USB etc have time to settle after reset
    time.sleep(0.3)

    if button_a is not None:
        print("DEBUG: BUTTON_A at start of boot:", button_a.value())

    mode = choose_boot_mode()

    if mode == "starfield":
        print("MODE: STARFIELD (BUTTON A at boot)")
        run_starfield_until_button()
        print("Starfield exited -> switching to FX SHOW")
    else:
        print("MODE: FX SHOW (default)")

    run_full_effect_show()
