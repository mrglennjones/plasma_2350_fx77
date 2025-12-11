# fx_77_starfield_startup.py

import time
import math
import gc
from random import randrange, uniform, random, choice

import plasma
from machine import Pin

# -----------------------------
# LED STRIP / SETUP
# -----------------------------

NUM_LEDS = 66

# Set your led strip as R → G → B, order:
led_strip = plasma.WS2812(
    NUM_LEDS,
    color_order=plasma.COLOR_ORDER_BRG
)
led_strip.start()



# -----------------------------
# ORIENTATION CONTROL
# -----------------------------
# "BOTTOM" = 2350W is at the bottom, strip goes up
# "TOP"    = 2350W is at the top, strip goes down
#ORIENTATION = "TOP"  # or "TOP"
ORIENTATION = "BOTTOM"  # or "TOP"

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

# ============================================================
# STARFIELD + COMET DEFAULT EFFECT
# ============================================================

# -----------------------------
# STARFIELD CONFIG
# -----------------------------

# Overall brightness range for stars
STAR_MIN_BRIGHT = 0.02     # very dim
STAR_MAX_BRIGHT = 0.8      # brightest "hero" stars

# How fast stars change brightness (lower = smoother, slower twinkle)
STAR_FADE_SPEED = 0.01     # change per frame towards target

# How often we pick a new "target" brightness per star (probability per frame)
STAR_NEW_TARGET_CHANCE = 0.01   # 1% chance per star per frame

# Slight colour variation so "white" isn't dead flat (looks nicer)
STAR_SATURATION_MAX = 0.05  # 0.0 = pure white, up to 0.05 still looks mostly white
STAR_HUE_SPREAD = 20        # degrees around 220° (cool white / very pale blue)

# Base frame speed for star twinkling
TWINKLE_FRAME_DELAY = 0.05  # seconds between frames (~20 FPS)

# --- Comets ---

# Roughly how often a comet appears (probability per twinkle frame).
COMET_BASE_CHANCE = 0.00015

COMET_MIN_TRAIL = 3
COMET_MAX_TRAIL = 8

COMET_MIN_SPEED = 0.015     # faster comet
COMET_MAX_SPEED = 0.035     # slower comet

COMET_HEAD_BRIGHT_MIN = 0.6
COMET_HEAD_BRIGHT_MAX = 1.0

# How much brighter than the background a comet can "burn in" as afterglow
AFTERGLOW_MAX = 0.4

# Comet colour (cool white / very pale blue)
COMET_HUE = 220 / 360.0     # bluish white
COMET_SAT = 0.1             # keep low so it still feels mostly white

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

# Many effects use this timeout in their while-loops
#TIMEOUT_DURATION = 20000  # milliseconds (8 seconds per effect, tweak as you like)

# Many effects use this timeout in their while-loops
MIN_EFFECT_DURATION = 6000    # 6 seconds
MAX_EFFECT_DURATION = 40000   # 40 seconds
TIMEOUT_DURATION = MIN_EFFECT_DURATION  # gets overridden for timed effects

# Effects that should be allowed to run their full sequence and NOT be cut off by a random timer.
# Use 1-based effect numbers here (so effect_40 == 40).
FULL_RUN_EFFECTS = {
    12,   # Tetris Block Fall (runs a full stack + disperse sequence)
    40,   # Bouncing ball to the top + fade-out
    # Add more here later if you find other 'must finish' animations
}


def hsv_to_rgb(h, s, v):
    """Simple HSV → RGB converter, returns floats 0.0–1.0."""
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return r, g, b


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
            self.hsv_values = fx_fn(self.hsv_values)
        else:
            # Timed / ambient: push a random duration into the global timeout
            TIMEOUT_DURATION = get_random_timeout_duration()
            self.hsv_values = fx_fn(self.hsv_values)




# ============================================================
# 77 FX SECTION – PASTE YOUR EXISTING CODE HERE
# ============================================================

# IMPORTANT:
# - DO NOT re-define NUM_LEDS or led_strip here (they are already defined above).
# - You *can* paste hsv_to_rgb, hsv_to_grb, EffectManager, all effect_1...effect_77,
#   your "effects = [...]" list, and "manager = EffectManager(NUM_LEDS)".
# - DO NOT paste your old "while True: manager.select_next_effect()..." main loop.
#
# ---- BEGIN 77 FX BLOCK ----

# Paste everything from:
#   hsv_to_rgb(...)
#   class EffectManager:
#   def effect_1(...):
#   ...
#   def effect_77(...):
#   effects = [ ... ]
#   manager = EffectManager(NUM_LEDS)
#
# right here, below this comment.
#
# ---- END 77 FX BLOCK ----


# Individual effect implementations
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

def effect_2(hsv_values):
    """Smooth Dispersing Color Wipe effect."""
    hue = uniform(0, 1.0)
    for i in range(NUM_LEDS):
        for j in range(i):
            h, s, v = hsv_values[j]
            hsv_values[j] = (h, s, v * 0.9)
            led_strip.set_hsv(j, hsv_values[j][0], hsv_values[j][1], hsv_values[j][2])

        hsv_values[i] = (hue, 1.0, 1.0)
        led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
        time.sleep(0.05)

    for _ in range(NUM_LEDS):
        for j in range(NUM_LEDS):
            h, s, v = hsv_values[j]
            hsv_values[j] = (h, s, v * 0.9)
            led_strip.set_hsv(j, hsv_values[j][0], hsv_values[j][1], hsv_values[j][2])
        time.sleep(0.05)

    time.sleep(0.5)
    return hsv_values

def effect_3(hsv_values):
    """Meteor Shower effect."""
    meteor_length = 8
    meteor_count = 3
    fade_rate = 0.75

    meteors = [
        {
            "position": randrange(NUM_LEDS),
            "velocity": uniform(0.1, 0.5),
            "hue": uniform(0, 1.0)
        }
        for _ in range(meteor_count)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            hsv_values[i] = (h, s, v * fade_rate)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        for meteor in meteors:
            meteor["position"] += meteor["velocity"]
            if meteor["position"] >= NUM_LEDS + meteor_length:
                meteor["position"] = -meteor_length
                meteor["hue"] = uniform(0, 1.0)

            for j in range(meteor_length):
                pos = int(meteor["position"] - j)
                if 0 <= pos < NUM_LEDS:
                    brightness = 1.0 - (j / meteor_length)
                    hsv_values[pos] = (meteor["hue"], 1.0, brightness)
                    led_strip.set_hsv(pos, hsv_values[pos][0], hsv_values[pos][1], hsv_values[pos][2])

        time.sleep(0.05)
    return hsv_values

def effect_4(hsv_values):
    """Enhanced Breathe effect."""
    start_time = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(360):
            hue = t / 360.0
            brightness = (1 + math.sin(t * 2 * math.pi / 180)) / 2
            
            for i in range(NUM_LEDS):
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(0.02)
    return hsv_values

def effect_5(hsv_values):
    """Starry Twinkle effect."""
    fade_rate = 0.9
    twinkle_chance = 0.05

    start_time = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            hsv_values[i] = (h, s, v * fade_rate)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            if uniform(0, 1) < twinkle_chance:
                twinkle_hue = uniform(0.0, 1.0)
                twinkle_brightness = uniform(0.5, 1.0)
                hsv_values[i] = (twinkle_hue, 1.0, twinkle_brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.05)
    return hsv_values

def effect_6(hsv_values):
    """Waves of Color effect."""
    wave_count = 3
    wave_speed = 0.1
    wave_length = 20

    start_time = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(360):
            for i in range(NUM_LEDS):
                brightness = 0
                for wave in range(wave_count):
                    offset = (t + wave * 120) % 360
                    wave_position = (i * 360 / NUM_LEDS + offset) % 360
                    wave_brightness = (1 + math.sin(wave_position * 2 * math.pi / wave_length)) / 2
                    brightness += wave_brightness / wave_count

                hue = (t + i) % 360 / 360.0
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(0.05)
    return hsv_values

def effect_7(hsv_values):
    """Plasma Storm effect with a balanced color spectrum."""
    speed = 0.2
    intensity_variation = 0.3
    wave_length = 15
    color_shift_speed = 0.02

    start_time = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(360):
            base_hue = (t * color_shift_speed) % 1.0

            for i in range(NUM_LEDS):
                noise1 = math.sin(i * 2 * math.pi / wave_length + t * speed)
                noise2 = math.cos(i * 2 * math.pi / (wave_length / 2) + t * speed * 1.5)
                combined_noise = (noise1 + noise2) / 2

                hue = (base_hue + combined_noise * 0.05) % 1.0
                brightness = 0.5 + combined_noise * intensity_variation

                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(0.05)
    return hsv_values

def effect_8(hsv_values):
    """Continuous Color Wave Burst effect."""
    burst_count = 3
    max_burst_size = 10
    burst_duration = 50
    burst_interval = 100
    frame_count = 0

    active_bursts = []

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for burst in active_bursts:
            burst["frame"] += 1
            burst["size"] += 1
            fade_factor = max(0, (burst_duration - burst["frame"]) / burst_duration)
            burst["brightness"] = fade_factor

            if burst["frame"] > burst_duration:
                active_bursts.remove(burst)
            else:
                for j in range(-burst["size"], burst["size"]):
                    pos = (burst["position"] + j) % NUM_LEDS
                    if 0 <= pos < NUM_LEDS:
                        distance = abs(j) / burst["size"]
                        brightness = burst["brightness"] * (1 - distance)
                        hsv_values[pos] = (burst["hue"], 1.0, brightness)
                        led_strip.set_hsv(pos, hsv_values[pos][0], hsv_values[pos][1], hsv_values[pos][2])

        if frame_count % burst_interval == 0:
            new_burst = {
                "position": randrange(NUM_LEDS),
                "hue": uniform(0, 1.0),
                "size": 0,
                "brightness": 1.0,
                "frame": 0
            }
            active_bursts.append(new_burst)

        frame_count += 1
        time.sleep(0.05)
    return hsv_values

def effect_9(hsv_values):
    """Smooth Fading Fireworks effect (orientation-aware, launch from bottom to top logically)."""
    firework_speed = 0.05
    explosion_size = 10
    launch_interval = 50
    fade_speed = 0.90
    frame_count = 0

    active_explosions = []

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # --- FADE EVERYTHING SLIGHTLY EACH FRAME ---
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            v *= fade_speed
            hsv_values[i] = (h, s, v)
            # environment → physical via set_hsv_env
            set_hsv_env(i, h, s, v)

        # --- OCCASIONALLY LAUNCH A NEW FIREWORK ---
        if frame_count % launch_interval == 0:
            # LOGICAL bottom is env index 0
            launch_pos = 0
            # Explosion somewhere in the UPPER half of the strip (env space)
            explosion_pos = randrange(NUM_LEDS // 2, NUM_LEDS)
            firework_hue = uniform(0.0, 1.0)

            firework_phase = "launch"

            # LAUNCH PHASE: move from bottom (0) upwards to explosion_pos
            while (firework_phase == "launch" and
                   time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION):

                # Clear previous launch pixel (only if we moved at least 1)
                if launch_pos > 0:
                    prev = launch_pos - 1
                    hsv_values[prev] = (0.0, 0.0, 0.0)
                    set_hsv_env(prev, 0.0, 0.0, 0.0)

                # Draw current rocket position
                hsv_values[launch_pos] = (firework_hue, 1.0, 1.0)
                set_hsv_env(launch_pos, firework_hue, 1.0, 1.0)

                # Move upwards (towards the logical top)
                launch_pos += 1

                # Reached the explosion altitude?
                if launch_pos >= explosion_pos:
                    firework_phase = "explode"
                    active_explosions.append({
                        "position": explosion_pos,
                        "hue": firework_hue,
                        "size": 1,
                        "brightness": 1.0
                    })

                time.sleep(firework_speed)

        # --- EXPLOSION PHASE(S) ---
        for explosion in active_explosions[:]:
            pos = explosion["position"]      # env index
            hue = explosion["hue"]
            size = explosion["size"]
            brightness = explosion["brightness"]

            # Draw expanding ring around explosion position
            for j in range(-size, size + 1):
                idx = pos + j
                if 0 <= idx < NUM_LEDS:
                    dist = abs(j) / float(max(1, size))
                    b = brightness * (1.0 - dist)
                    if b > 0:
                        hsv_values[idx] = (hue, 1.0, b)
                        set_hsv_env(idx, hue, 1.0, b)

            # Grow and fade the explosion
            explosion["size"] += 1
            explosion["brightness"] *= fade_speed

            # Remove once it has faded
            if explosion["brightness"] < 0.01:
                active_explosions.remove(explosion)

        frame_count += 1
        time.sleep(0.02)

    return hsv_values




#def hsv_to_grb(h, s, v):
#    """Converts HSV to GRB color space to accommodate the GRB LED strip."""
#    r, g, b = hsv_to_rgb(h, s, v)
#    return g, r, b  # Swap R and G to fit the GRB color order

def hsv_to_grb(h, s, v):
    """Converts HSV color space to GRB 0–255 ints for the LED strip."""
    r, g, b = hsv_to_rgb(h, s, v)  # r,g,b in 0.0–1.0
    return int(g * 255), int(r * 255), int(b * 255)  # GRB order as ints


def effect_10(hsv_values):
    """Improved Lava Lamp Effect with Smooth, Solid Color Blobs and Blended Overlaps (Orientation-Aware)."""
    num_blobs = 3
    base_speed = 0.05
    blob_min_size = 8
    blob_max_size = 16
    fade_factor = 0.95
    step_time = 0.02

    # Blobs operate in ENVIRONMENT space (0 = logical bottom, NUM_LEDS-1 = logical top)
    blobs = [
        {
            "position": uniform(0, NUM_LEDS),
            "size": randrange(blob_min_size, blob_max_size),
            "direction": choice([-1, 1]),
            "hue": uniform(0, 1.0),
            "speed": uniform(base_speed, base_speed * 2),
        }
        for _ in range(num_blobs)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:

        # Arrays for blended values in ENVIRONMENT space
        blended_hue = [0.0] * NUM_LEDS
        blended_brightness = [0.0] * NUM_LEDS
        total_weight = [0.0] * NUM_LEDS

        # Fade previous frame
        for env_i in range(NUM_LEDS):
            h, s, v = hsv_values[env_i]
            v *= fade_factor
            hsv_values[env_i] = (h, s, v)
            set_hsv_env(env_i, h, s, v)

        # Update blobs
        for blob in blobs:
            # Movement in ENV space
            blob["position"] += blob["direction"] * blob["speed"]

            # Bounce when hitting logical ends
            if blob["position"] < 0 or blob["position"] >= NUM_LEDS:
                blob["direction"] *= -1
                blob["position"] = max(0, min(NUM_LEDS - 1, blob["position"]))

            # Apply blob contribution
            for j in range(-blob["size"] // 2, blob["size"] // 2):
                env_pos = int(blob["position"] + j)

                if 0 <= env_pos < NUM_LEDS:
                    distance = abs(j) / (blob["size"] / 2)
                    brightness = max(0, 1.0 - distance)

                    blended_hue[env_pos] += blob["hue"] * brightness
                    blended_brightness[env_pos] += brightness
                    total_weight[env_pos] += brightness

        # Apply blended output
        for env_i in range(NUM_LEDS):
            if total_weight[env_i] > 0:
                final_hue = blended_hue[env_i] / total_weight[env_i]
                final_brightness = blended_brightness[env_i] / total_weight[env_i]

                hsv_values[env_i] = (final_hue, 1.0, final_brightness)
                set_hsv_env(env_i, final_hue, 1.0, final_brightness)

        time.sleep(step_time)

    return hsv_values




def effect_11(hsv_values):
    """Smooth Twinkle Stars effect."""
    num_stars = 20
    max_brightness = 1.0
    min_brightness = 0.2
    twinkle_speed = 0.005

    stars = [
        {
            "position": randrange(NUM_LEDS),
            "brightness": uniform(min_brightness, max_brightness),
            "direction": choice([-1, 1]),
            "hue": uniform(0, 1.0)
        }
        for _ in range(num_stars)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            hsv_values[i] = (
                hsv_values[i][0], 
                hsv_values[i][1], 
                hsv_values[i][2] * 0.95
            )
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        for star in stars:
            star["brightness"] += star["direction"] * twinkle_speed

            if star["brightness"] >= max_brightness:
                star["direction"] = -1
            elif star["brightness"] <= min_brightness:
                star["direction"] = 1

            pos = star["position"]
            hsv_values[pos] = (star["hue"], 1.0, star["brightness"])
            led_strip.set_hsv(pos, hsv_values[pos][0], hsv_values[pos][1], hsv_values[pos][2])

        time.sleep(0.05)
    return hsv_values

def effect_12(hsv_values):
    """
    Tetris Block Fall with orientation-aware ground at env index 0.

    - ORIENTATION = "BOTTOM": 2350W at physical bottom, Tetris blocks fall
      DOWN the strip towards the 2350W (env index 0).
    - ORIENTATION = "TOP": same env-space animation, mirrored by env_to_phys().
    """
    block_colors = [
        {"name": "Cyan",    "rgb": (255, 0, 255)},
        {"name": "Yellow",  "rgb": (255, 255, 0)},
        {"name": "Purple",  "rgb": (0, 255, 255)},
        {"name": "Green",   "rgb": (255, 0, 0)},
        {"name": "Blue",    "rgb": (0, 0, 255)},
        {"name": "Red",     "rgb": (0, 255, 0)},
        {"name": "Orange",  "rgb": (165, 255, 0)},
    ]

    max_block_length = 10
    min_block_length = 3
    frame_delay = 0.05

    # Ground is env index 0
    stacked_height = -1              # highest occupied env index in the stack
    blocks = []                      # list of landed blocks
    stack_pixels = [(0, 0, 0)] * NUM_LEDS  # current stacked RGB in env space

    # Clear LEDs
    for i in range(NUM_LEDS):
        hsv_values[i] = (0.0, 0.0, 0.0)
        set_rgb_env(i, 0, 0, 0)

    start_time = time.ticks_ms()

    # -----------------------------
    # STACKING PHASE
    # -----------------------------
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # If stack reaches the sky, stop stacking
        if stacked_height >= NUM_LEDS - 1:
            break

        # Remaining vertical space above current stack
        remaining = NUM_LEDS - (stacked_height + 1)
        if remaining <= 0:
            break

        block_length = randrange(min_block_length, max_block_length + 1)
        if block_length > remaining:
            block_length = remaining
        if block_length <= 0:
            break

        block = block_colors[randrange(len(block_colors))]
        print("Tetris block:", block["name"], "length:", block_length)

        # Start block at the "sky" end (env NUM_LEDS-1)
        top_env = NUM_LEDS - 1
        bottom_env = top_env - (block_length - 1)

        # If initial position already collides, stop
        if bottom_env <= stacked_height:
            break

        # Fall loop: move block down towards env 0
        while (bottom_env > stacked_height + 1 and
               time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION):

            # FULL FRAME RENDER (no flashing):
            # For each env pixel, show either stacked block color or falling block.
            for i in range(NUM_LEDS):
                r, g, b = stack_pixels[i]
                if bottom_env <= i <= top_env:
                    r, g, b = block["rgb"]
                set_rgb_env(i, r, g, b)

            time.sleep(frame_delay)

            # Move one step closer to ground
            top_env -= 1
            bottom_env -= 1

        # Landed position
        landed_start = max(0, bottom_env)
        landed_end = max(landed_start, top_env)

        # Store landed block and update stack_pixels
        blocks.append({
            "start": landed_start,
            "end": landed_end,
            "color": block["rgb"],
        })

        for j in range(landed_start, landed_end + 1):
            if 0 <= j < NUM_LEDS:
                stack_pixels[j] = block["rgb"]
                set_rgb_env(j, *block["rgb"])

        if landed_end > stacked_height:
            stacked_height = landed_end

        if stacked_height >= NUM_LEDS - 1:
            break

    print("Blocks stacked. Pausing for 3 seconds...")
    time.sleep(3)

    # -----------------------------
    # DISPERSAL PHASE
    # -----------------------------
    print("Dispersing blocks...")
    hsv_values = disperse_blocks(blocks, frame_delay, hsv_values)

    return hsv_values


def disperse_blocks(blocks, frame_delay, hsv_values):
    """
    Disperse blocks by sliding them towards env index 0 (ground), then off-strip.
    Orientation is handled by set_rgb_env -> env_to_phys().
    """
    while blocks:
        # Move each block one step towards env 0
        for block in blocks[:]:
            block["start"] -= 1
            block["end"] -= 1

            # If completely off below env 0, remove it
            if block["end"] < 0:
                blocks.remove(block)

        # FULL FRAME RENDER: rebuild stack_pixels from current blocks
        stack_pixels = [(0, 0, 0)] * NUM_LEDS
        for block in blocks:
            for j in range(block["start"], block["end"] + 1):
                if 0 <= j < NUM_LEDS:
                    stack_pixels[j] = block["color"]

        for i in range(NUM_LEDS):
            r, g, b = stack_pixels[i]
            set_rgb_env(i, r, g, b)

        time.sleep(frame_delay)

    return hsv_values



def effect_13(hsv_values):
    """Torrential rain with fast-moving blue raindrops, orientation-aware.

    Env space:
      - env index 0         = ground
      - env index NUM_LEDS-1 = sky

    Rain always falls from sky (top) down towards ground (bottom) in env space.
    ORIENTATION mapping (via set_rgb_env) flips the physical direction as needed.
    """

    num_drops = 15
    drop_color = (0, 0, 255)     # Blue in RGB
    trail_length = 3
    frame_delay = 0.01
    drops = []

    # led_state is stored in ENV coordinates
    led_state = [(0, 0, 0) for _ in range(NUM_LEDS)]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Spawn new drops near the "sky" (upper half → top)
        if len(drops) < num_drops and uniform(0, 1) < 0.5:
            start_pos = randrange(NUM_LEDS // 2, NUM_LEDS)  # upper half of env strip
            drops.append({
                "position": float(start_pos),
                "speed": uniform(0.05, 0.15),
            })

        # Fade all LEDs slightly to create trails
        for i in range(NUM_LEDS):
            r, g, b = led_state[i]
            led_state[i] = (
                int(r * 0.7),
                int(g * 0.7),
                int(b * 0.7),
            )

        # Update each drop
        for drop in drops:
            drop_pos = drop["position"]
            speed = drop["speed"]

            # Draw head + short trail above it (towards the sky / higher env index)
            for i in range(trail_length):
                pos = int(drop_pos) + i  # tail above the head
                if 0 <= pos < NUM_LEDS:
                    brightness = 1.0 - (i / trail_length)
                    r = int(drop_color[0] * brightness)
                    g = int(drop_color[1] * brightness)
                    b = int(drop_color[2] * brightness)

                    # Max blend with existing state
                    cur_r, cur_g, cur_b = led_state[pos]
                    led_state[pos] = (
                        max(cur_r, r),
                        max(cur_g, g),
                        max(cur_b, b),
                    )

            # Move the drop DOWN (towards env index 0)
            drop["position"] -= speed

        # Remove drops that are completely off the bottom
        drops = [drop for drop in drops if drop["position"] > -trail_length]

        # Push env-state to physical LEDs
        for i in range(NUM_LEDS):
            r, g, b = led_state[i]
            set_rgb_env(i, r, g, b)

        time.sleep(frame_delay)

    return hsv_values


def effect_14(hsv_values):
    """Creates a dynamic wave of colors flowing across the LED strip."""

    wave_length = 20
    speed = 0.1
    wave_height = 1.0

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(360):
            for i in range(NUM_LEDS):
                wave_position = (i + t * speed) % wave_length
                brightness = (1 + math.sin(wave_position * 2 * math.pi / wave_length)) / 2 * wave_height

                hue = (t + i) % 360 / 360.0
                led_strip.set_hsv(i, hue, 1.0, brightness)

            time.sleep(0.05)
    return hsv_values

def effect_15(hsv_values):
    """Natural flame effect: deep red at the base, transitioning to orange, then to yellow.
    
    Orientation-aware via env_to_phys():
      - Env index 0           = flame base / ground
      - Env index NUM_LEDS-1  = top of the flame
    
    ORIENTATION = "BOTTOM":
        2350W at bottom; base is physically near the 2350W.
    ORIENTATION = "TOP":
        2350W at top; base is physically near the 2350W, with strip going down.
    """
    cooling = 40      # Rate at which heat cools down
    sparking = 120    # Frequency of new sparks at the base
    speed_delay = 0.02
    heat = [0] * NUM_LEDS  # Heat array in ENV coordinates (0 = base)

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Step 1: Cool down each "cell" a little
        for i in range(NUM_LEDS):
            cooldown = randrange(0, ((cooling * 10) // NUM_LEDS) + 2)
            heat[i] = max(0, heat[i] - cooldown)

        # Step 2: Heat drifts upward and diffuses (towards higher env indices)
        for i in range(NUM_LEDS - 3, 0, -1):
            heat[i] = (heat[i - 1] + heat[i - 2] + heat[i - 3]) // 3

        # Step 3: Randomly ignite new sparks near the base (env index 0)
        if randrange(255) < sparking:
            y = randrange(0, 7)  # Positions near the base in env-space
            heat[y] = min(255, heat[y] + randrange(160, 255))

        # Step 4: Map heat to colors and write them, orientation-aware
        for env_i in range(NUM_LEDS):
            brightness = (heat[env_i] / 255.0) ** 1.5  # Adjust the brightness curve

            if brightness > 0.8:
                # Yellow: top of the flame
                r = brightness * 255
                g = brightness * 255
                b = 0
            elif brightness > 0.4:
                # Orange: middle of the flame
                r = brightness * 255
                g = brightness * 0.5 * 255
                b = 0
            else:
                # Red: base of the flame
                r = brightness * 255
                g = 0
                b = 0

            # GRB order preserved exactly as before
            phys = env_to_phys(env_i)
            led_strip.set_rgb(phys, int(g), int(r), int(b))

        time.sleep(speed_delay)

    return hsv_values





def effect_16(hsv_values):
    """Simulates a lava drip effect on a GRB/BGR strip, starting from the top and dripping downward."""

    drip_length = 5
    speed_delay = 0.02
    acceleration = 1.05
    max_brightness = 0.9
    min_brightness = 0.2

    # This is the "real" lava hue you want (red-orange)
    BASE_HUE = 0.00      # 0.0 = red, ~0.05 = orange-red
    SATURATION = 1.0

    # Extra hue offset to cancel your strip’s green bias.
    # This is the same trick as we used on effect_32.
    HUE_OFFSET = 0.33    # ~120° shift

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        position = 0      # Start from the top
        speed = speed_delay

        while position < NUM_LEDS:
            # Clear the LED strip
            for i in range(NUM_LEDS):
                led_strip.set_rgb(i, 0, 0, 0)

            # Create the drip effect
            for i in range(drip_length):
                pos = position + i
                if 0 <= pos < NUM_LEDS:
                    brightness = max_brightness - ((i / drip_length) * (max_brightness - min_brightness))

                    # 🔥 Fix: rotate hue so it appears lava-red/orange on your strip
                    display_hue = (BASE_HUE + HUE_OFFSET) % 1.0
                    r, g, b = hsv_to_rgb(display_hue, SATURATION, brightness)

                    led_strip.set_rgb(pos, int(r * 255), int(g * 255), int(b * 255))

            position += 1       # Move the drip downward
            speed *= acceleration
            time.sleep(speed)

        time.sleep(0.5)

    return hsv_values


def effect_17(hsv_values):
    """Quantum Pulse Waveforms: Rhythmic, particle-like waves that pulse with quantum uncertainty."""
    num_particles = 50
    speed_variability = 0.01
    wave_speed = 0.1
    quantum_jump_chance = 0.05

    particles = [
        {
            "position": randrange(NUM_LEDS),
            "velocity": uniform(-wave_speed, wave_speed),
            "hue": randrange(360) / 360.0,
            "brightness": uniform(0.5, 1.0)
        }
        for _ in range(num_particles)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for particle in particles:
            particle["position"] += particle["velocity"]
            if randrange(100) < quantum_jump_chance * 100:
                particle["position"] = randrange(NUM_LEDS)
                particle["velocity"] = uniform(-wave_speed, wave_speed)

            particle["position"] %= NUM_LEDS  # Wrap around
            idx = int(particle["position"])
            hsv_values[idx] = (particle["hue"], 1.0, particle["brightness"])

        # Dampen brightness for all LEDs
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            hsv_values[i] = (h, s, v * 0.95)
            led_strip.set_hsv(i, h, s, v)

        time.sleep(speed_variability)

    return hsv_values


def effect_18(hsv_values):
    """Smooth Sinusoidal Color Flow: A Perlin-like gradient animation using sine and cosine waves."""
    scale = 0.1  # Scale factor for the color waves
    speed = 0.01  # Speed of the animation
    time_offset = 0  # Time offset for animating the waves

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            # Generate a hue value using a combination of sine and cosine waves
            hue = (math.sin(i * scale + time_offset) + 1) / 2  # Map sine output to [0, 1]
            brightness = (math.cos(i * scale - time_offset) + 1) / 2  # Map cosine output to [0, 1]
            hsv_values[i] = (hue, 1.0, brightness)

        # Update the LED strip with the new HSV values
        for j in range(NUM_LEDS):
            led_strip.set_hsv(j, hsv_values[j][0], hsv_values[j][1], hsv_values[j][2])

        time_offset += speed  # Increment the time offset to animate the waves
        time.sleep(0.02)  # Adjust the delay to control the animation speed

    return hsv_values




def effect_19(hsv_values):
    """Night Sky with Twinkling Stars."""
    # Set the background to a dark blue color
    background_hue = 0.66  # Hue for blue (240 degrees on color wheel)
    background_saturation = 1.0
    background_value = 0.1  # Dim blue for the night sky

    star_twinkle_probability = 0.05  # Probability of a star twinkling each frame
    twinkle_duration = 10  # Duration of each twinkle in frames

    # Initialize the star states
    stars = [{
        "position": randrange(NUM_LEDS),
        "hue": 0.15 if randrange(2) == 0 else 0.0,  # Randomly choose between yellow (hue 0.15) and white (hue 0.0)
        "saturation": 0.0,  # Fully desaturated for white or slightly for yellow
        "twinkle_counter": 0  # Counter to manage twinkle duration
    } for _ in range(NUM_LEDS // 10)]  # Number of stars as a fraction of total LEDs

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Set the background
        for i in range(NUM_LEDS):
            hsv_values[i] = (background_hue, background_saturation, background_value)

        # Handle star twinkling
        for star in stars:
            if star["twinkle_counter"] == 0 and uniform(0, 1) < star_twinkle_probability:
                star["twinkle_counter"] = twinkle_duration

            if star["twinkle_counter"] > 0:
                brightness = uniform(0.5, 1.0)  # Random brightness for the twinkle
                hsv_values[star["position"]] = (star["hue"], star["saturation"], brightness)
                star["twinkle_counter"] -= 1

        # Update the LED strip
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.05)  # Small delay for animation smoothness

    return hsv_values

def effect_20(hsv_values):
    """Temporal Wave Collisions: Interference patterns from waves traveling in opposite directions."""
    wave_count = 5
    wave_speed = 0.2
    amplitude = 1.0

    waves = [{"position": 0, "direction": 1} for _ in range(wave_count)]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for wave in waves:
            wave["position"] += wave_speed * wave["direction"]
            if wave["position"] >= NUM_LEDS or wave["position"] <= 0:
                wave["direction"] *= -1

        for i in range(NUM_LEDS):
            brightness = sum(
                amplitude * (1 - abs(i - wave["position"]) / NUM_LEDS) for wave in waves
            )
            hue = (i % 360) / 360.0
            hsv_values[i] = (hue, 1.0, min(brightness, 1.0))
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.01)

    return hsv_values

def effect_21(hsv_values):
    """Fractal Firestorms: Advanced flame simulation using fractal patterns and turbulence."""
    fire_intensity = [0] * NUM_LEDS
    cooling = 0.2
    turbulence = 0.1

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Cool down each LED's heat intensity
        for i in range(NUM_LEDS):
            cooldown = randrange(int(cooling * 100))  # Ensure cooldown is an integer
            fire_intensity[i] = max(0, fire_intensity[i] - cooldown)
            if randrange(100) < 5:
                fire_intensity[i] = 255

        # Diffuse the heat to simulate fire spreading
        for i in range(NUM_LEDS):
            # Calculate a random index using turbulence, ensuring it's an integer
            idx_offset = randrange(int(-turbulence * 100), int(turbulence * 100)) // 100
            idx = (i + idx_offset) % NUM_LEDS
            fire_intensity[idx] = (fire_intensity[max(i - 1, 0)] + fire_intensity[min(i + 1, NUM_LEDS - 1)]) // 2

        # Set the HSV values for each LED based on the fire intensity
        for i in range(NUM_LEDS):
            hue = 0.1 + fire_intensity[i] / 255 * 0.1
            brightness = fire_intensity[i] / 255
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.03)

    return hsv_values



def effect_22(hsv_values):
    """Enhanced Pulsating Red Glow effect."""
    hue_red = 0.33  # Corrected hue for red in GRB format
    max_brightness = 1.0
    min_brightness = 0.1
    pulse_speed = 0.02

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            # Create a smooth pulsating effect
            brightness = min_brightness + (max_brightness - min_brightness) * (0.5 + 0.5 * math.sin(time.ticks_ms() * pulse_speed))
            hsv_values[i] = (hue_red, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.05)  # Short delay to control the speed of the effect

    return hsv_values


def effect_23(hsv_values):
    """Smooth single-LED bouncing lights without tails, flickering, or strobing."""
    num_bouncing_leds = 5  # Number of bouncing LEDs
    led_positions = [randrange(NUM_LEDS) for _ in range(num_bouncing_leds)]
    led_speeds = [uniform(0.1, 0.3) for _ in range(num_bouncing_leds)]
    led_directions = [choice([-1, 1]) for _ in range(num_bouncing_leds)]
    led_hues = [randrange(360) / 360.0 for _ in range(num_bouncing_leds)]  # Different colors

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Reset all LEDs to the dark state (off)
        for i in range(NUM_LEDS):
            hsv_values[i] = (0.0, 0.0, 0.0)  # Turn off all LEDs

        # Update the position and color of each bouncing LED
        for j in range(num_bouncing_leds):
            # Move the LED smoothly
            led_positions[j] += led_speeds[j] * led_directions[j]

            # Reverse direction if the LED hits the boundary
            if led_positions[j] >= NUM_LEDS - 1 or led_positions[j] <= 0:
                led_directions[j] = -led_directions[j]
                led_positions[j] = max(0, min(NUM_LEDS - 1, led_positions[j]))  # Clamp within bounds

            # Ensure LED stays at integer positions to avoid flickering
            index = int(round(led_positions[j]))

            # Set the color of the LED at the current position
            hsv_values[index] = (led_hues[j], 1.0, 1.0)  # Brightness and saturation are both 1.0

        # Apply the updated hsv_values to the LED strip
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.05)  # Delay to control the speed of the animation

    return hsv_values



def effect_24(hsv_values):
    """Aurora Borealis: Simulates the dancing lights of the Northern Lights with smooth undulations."""
    wave_speed = 0.1
    color_shift_speed = 0.01
    amplitude = 0.4
    base_hue = 0.5

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            hue_variation = math.sin(i * amplitude + time.ticks_ms() * wave_speed) * 0.1
            hue = (base_hue + hue_variation) % 1.0
            brightness = (1 + math.sin(i * amplitude - time.ticks_ms() * wave_speed)) / 2
            hsv_values[i] = (hue, 0.8, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        base_hue += color_shift_speed
        time.sleep(0.05)

    return hsv_values


def effect_25(hsv_values):
    """Hypernova Shockwave: Concentric shockwaves of color radiate outward, simulating a massive explosion."""
    shockwave_speed = 0.2
    shockwave_count = 3
    hue_shift_speed = 0.01
    base_hue = 0.0

    shockwaves = [
        {"center": randrange(NUM_LEDS), "radius": 0, "hue": (base_hue + i * 0.1) % 1.0}
        for i in range(shockwave_count)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for wave in shockwaves:
            wave["radius"] += shockwave_speed
            if wave["radius"] > NUM_LEDS:
                wave["radius"] = 0
                wave["center"] = randrange(NUM_LEDS)
                wave["hue"] = (wave["hue"] + hue_shift_speed) % 1.0

        for i in range(NUM_LEDS):
            brightness = 0
            for wave in shockwaves:
                if wave["radius"] > 0:  # Only calculate if radius is greater than zero
                    distance = abs(i - wave["center"])
                    brightness += max(0, 1 - distance / wave["radius"])
            hue = (i % 360) / 360.0
            hsv_values[i] = (hue, 1.0, min(brightness, 1.0))
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.02)

    return hsv_values



def effect_26(hsv_values):
    """Ethereal Vortex: A swirling vortex effect, with colors spiraling inwards and outwards."""
    vortex_speed = 50
    hue_variation = 0.3
    spiral_tightness = 0.05

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            angle = (i * spiral_tightness + time.ticks_ms() * vortex_speed) % (2 * math.pi)
            hue = (0.5 + math.sin(angle) * hue_variation) % 1.0
            brightness = (1 + math.cos(angle)) / 2
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.6)

    return hsv_values


def effect_27(hsv_values):
    """Cosmic Dust Storm: Particles of cosmic dust swirl and twinkle with random bursts of light."""
    dust_particles = [{"position": randrange(NUM_LEDS), "brightness": uniform(0.2, 1.0)} for _ in range(100)]
    swirl_speed = 0.03
    brightness_decay = 0.95

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for particle in dust_particles:
            particle["position"] = (particle["position"] + swirl_speed) % NUM_LEDS
            if randrange(100) < 5:
                particle["brightness"] = uniform(0.5, 1.0)

        for i in range(NUM_LEDS):
            hsv_values[i] = (0.6, 0.7, 0.1)  # Dim blue background
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        for particle in dust_particles:
            idx = int(particle["position"]) % NUM_LEDS
            hsv_values[idx] = (0.7, 0.8, particle["brightness"])
            led_strip.set_hsv(idx, hsv_values[idx][0], hsv_values[idx][1], hsv_values[idx][2])
            particle["brightness"] *= brightness_decay

        time.sleep(0.02)

    return hsv_values


def effect_28(hsv_values):
    pacman_pos = 0
    ghost_positions = [randrange(NUM_LEDS) for _ in range(3)]
    pill_positions = sorted([randrange(NUM_LEDS) for _ in range(5)])
    pacman_chasing = False
    pacman_alive = True
    dots = [True] * NUM_LEDS

    def is_pill(pos):
        return pos in pill_positions

    def is_ghost(pos):
        return pos in ghost_positions

    def move_pacman():
        nonlocal pacman_pos
        pacman_pos += 1
        if pacman_pos >= NUM_LEDS:
            pacman_pos = 0

    def move_ghosts():
        nonlocal ghost_positions
        for i in range(len(ghost_positions)):
            if pacman_chasing:
                if ghost_positions[i] > pacman_pos:
                    ghost_positions[i] -= 1
                elif ghost_positions[i] < pacman_pos:
                    ghost_positions[i] += 1
            else:
                if randrange(2) == 0:
                    ghost_positions[i] += 1
                else:
                    ghost_positions[i] -= 1
            if ghost_positions[i] >= NUM_LEDS:
                ghost_positions[i] = 0
            elif ghost_positions[i] < 0:
                ghost_positions[i] = NUM_LEDS - 1

    def update_leds():
        # Clear strip
        for i in range(NUM_LEDS):
            hsv_values[i] = (0.15, 1.0, 0.2 if dots[i] else 0.0)  # Dim yellow dots

        # Place pills
        for pos in pill_positions:
            hsv_values[pos] = (0.0, 0.0, 1.0)  # White pills

        # Place ghosts
        for pos in ghost_positions:
            if pacman_chasing:
                hsv_values[pos] = (0.55, 1.0, 1.0)  # Blue ghosts when chased
            else:
                hsv_values[pos] = (uniform(0.0, 1.0), 1.0, 1.0)  # Random colored ghosts

        # Place Pac-Man
        if pacman_alive:
            hsv_values[pacman_pos] = (0.15, 1.0, 1.0)  # Yellow Pac-Man
        else:
            hsv_values[pacman_pos] = (0.0, 0.0, 0.0)  # Pac-Man disappears when dead

        # Update LED strip
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

    def respawn_pacman():
        nonlocal pacman_pos, pacman_alive
        pacman_pos = 0  # Respawn at the start
        pacman_alive = True

    start_time = time.ticks_ms()
    pill_eaten_time = 0

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        if pacman_alive:
            move_pacman()
            move_ghosts()

            if is_pill(pacman_pos):
                pacman_chasing = True
                pill_positions.remove(pacman_pos)
                pill_eaten_time = time.ticks_ms()

            if time.ticks_diff(time.ticks_ms(), pill_eaten_time) > 5000:  # 5 seconds of power-up
                pacman_chasing = False

            if is_ghost(pacman_pos) and not pacman_chasing:
                # Pac-Man is caught by a ghost
                pacman_alive = False
                print("Pac-Man died! Respawning...")
                time.sleep(1)  # Brief pause to simulate "death"

            if is_ghost(pacman_pos) and pacman_chasing:
                ghost_positions.remove(pacman_pos)
                ghost_positions.append(randrange(NUM_LEDS))  # Respawn ghost

            dots[pacman_pos] = False

        update_leds()
        time.sleep(0.1)  # Adjust for speed of the game

        if not pacman_alive:
            time.sleep(1)  # Wait before respawn
            respawn_pacman()

    return hsv_values


def effect_29(hsv_values):
    """Matrix effect with cascading green characters, orientation-aware.

    Env space:
      - 0             = bottom (ground)
      - NUM_LEDS - 1  = top

    Visually: bright heads fall from top to bottom with fading green trails.
    ORIENTATION flips which physical side is treated as bottom/top.
    """
    trail_length = 10      # Length of the trailing effect
    fade_factor = 0.75     # Fading factor for the trails
    num_trails = 5         # Number of cascading trails

    # Head positions in ENV coordinates
    positions = [randrange(NUM_LEDS) for _ in range(num_trails)]
    speeds = [uniform(0.05, 0.2) for _ in range(num_trails)]  # kept for timing as before
    brightness_levels = [0.0] * NUM_LEDS

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # --- Fade all LEDs slightly (in env space) ---
        for env_i in range(NUM_LEDS):
            h, s, v = hsv_values[env_i]
            v *= fade_factor
            hsv_values[env_i] = (h, s, v)
            set_hsv_env(env_i, h, s, v)

        # --- Move and draw each trail ---
        for i in range(num_trails):
            position = positions[i]  # head position in env indices
            if 0 <= position < NUM_LEDS:
                brightness_levels[position] = 1.0  # head is brightest

                # Create the trailing effect above the head in env space
                for j in range(trail_length):
                    trail_pos = position + j  # larger env index = higher up
                    if trail_pos < NUM_LEDS:
                        brightness = 1.0 - (j / trail_length)
                        h = 0.00     # green hue on your strip
                        s = 1.0
                        v = brightness * fade_factor
                        hsv_values[trail_pos] = (h, s, v)
                        set_hsv_env(trail_pos, h, s, v)

            # Move the head "downwards" toward env 0 (bottom)
            positions[i] -= 1
            if positions[i] < 0:      # when it goes past bottom, respawn at top
                positions[i] = NUM_LEDS - 1

        # Timing as before
        time.sleep(min(speeds))

    return hsv_values



def effect_30(hsv_values):
    """Gravitational Wave Ripples: Smooth, undulating ripples that simulate space-time disturbances."""
    ripple_speed = 1
    ripple_amplitude = 0.001
    hue_shift_speed = 5

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            wave_phase = (i * ripple_amplitude + time.ticks_ms() * ripple_speed) % (2 * math.pi)
            hue = (0.5 + math.sin(wave_phase) * 0.1) % 1.0
            brightness = (1 + math.cos(wave_phase)) / 2
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.02)

    return hsv_values


def effect_31(hsv_values):
    """Waves of color moving down the strip."""
    wave_speed = 0.1  # Speed at which the wave moves
    wave_length = 10  # Length of the wave

    start_time = time.ticks_ms()  # Start time for the effect

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS * 2):  # Loop to animate the wave
            for i in range(NUM_LEDS):
                hue = (i % 360) / 360.0
                brightness = (1 + math.sin((i * 2 * math.pi / wave_length) + (t * wave_speed))) / 2
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(0.05)  # Control the speed of the animation

    return hsv_values


def effect_32(hsv_values):
    """Fire effect with flickering, varying intensities (ambient + timed)."""
    BASE_HUE = 0.08          # desired orange
    HUE_JITTER = 0.03
    COOLING = 0.6
    NEW_ENERGY = 0.4
    MIN_B = 0.05

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            h_prev, s_prev, v_prev = hsv_values[i]

            # cool down
            v = v_prev * COOLING

            # add flare
            target_b = uniform(0, 1)**3
            v = v * (1.0 - NEW_ENERGY) + target_b * NEW_ENERGY
            v = max(MIN_B, min(1.0, v))

            # 🔥 FIX: hue shift for GRB strip to appear orange/red
            hue = BASE_HUE + uniform(-HUE_JITTER, HUE_JITTER)
            hue = (hue + 0.33) % 1.0  # +120° hue shift to cancel GRB green shift

            hsv_values[i] = (hue, 1.0, v)
            led_strip.set_hsv(i, hue, 1.0, v)

        time.sleep(0.03)

    return hsv_values



def effect_33(hsv_values):
    """Sparkle effect with random flickers over a gently fading background."""
    FADE = 0.85                 # how fast old sparkles fade
    SPARKLE_DENSITY = 0.12      # fraction of LEDs that may sparkle per frame
    MIN_B = 0.02

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Fade existing pixels
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            v *= FADE
            if v < MIN_B:
                v = 0.0
            hsv_values[i] = (h, s, v)
            led_strip.set_hsv(i, h, s, v)

        # Add new sparkles
        num_new = max(1, int(NUM_LEDS * SPARKLE_DENSITY * random()))
        for _ in range(num_new):
            idx = randrange(NUM_LEDS)
            hue = randrange(360) / 360.0
            brightness = uniform(0.5, 1.0)
            hsv_values[idx] = (hue, 1.0, brightness)
            led_strip.set_hsv(idx, hue, 1.0, brightness)

        time.sleep(0.04)

    return hsv_values


def effect_34(hsv_values):
    """Rotating color bands that slowly drift along the strip."""
    BAND_WIDTH = 5
    FAST_BRIGHT = 1.0
    DIM_BRIGHT = 0.35
    STEP_DELAY = 0.04

    offset = 0
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            band_index = ((i + offset) // BAND_WIDTH)
            hue = (band_index % 6) / 6.0

            # Alternate bright/dim bands
            if band_index % 2 == 0:
                brightness = FAST_BRIGHT
            else:
                brightness = DIM_BRIGHT

            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        offset = (offset + 1) % (NUM_LEDS * 2)
        time.sleep(STEP_DELAY)

    return hsv_values

def effect_35(hsv_values):
    """Meteor shower with fading tails that vanish completely, orientation-aware.

    Env space:
      0             = bottom (ground)
      NUM_LEDS - 1  = top

    Visually: meteors streak from top → bottom with a fading tail.
    ORIENTATION decides which *physical* end is the top/bottom.
    """
    meteor_length = 10   # Length of the meteor's tail
    meteor_speed  = 0.1  # Speed of the meteor movement
    fade_rate     = 0.85 # Fade rate for the tail

    start_time = time.ticks_ms()

    # Start the meteor head just above the logical TOP so it "enters" the strip
    head_env = NUM_LEDS - 1 + meteor_length

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # -------------------------
        # 1) Fade existing pixels
        # -------------------------
        for env_i in range(NUM_LEDS):
            h, s, v = hsv_values[env_i]
            v *= fade_rate
            hsv_values[env_i] = (h, s, v)
            set_hsv_env(env_i, h, s, v)

        # -------------------------
        # 2) Draw meteor head + tail
        # -------------------------
        for k in range(meteor_length):
            # Tail runs *downward* from the head in env space
            tail_env = head_env - k

            if 0 <= tail_env < NUM_LEDS:
                # Tail brightness fades towards zero
                brightness = max(0.0, 1.0 - (k + 1) / meteor_length)

                if brightness > 0.0:
                    hue = 0.33  # Your original red-ish hue
                    hsv_values[tail_env] = (hue, 1.0, brightness)
                    set_hsv_env(tail_env, hue, 1.0, brightness)

        # -------------------------
        # 3) Advance meteor head
        # -------------------------
        head_env -= 1

        # When head + tail are completely off the bottom, restart above the top
        if head_env < -meteor_length:
            head_env = NUM_LEDS - 1 + meteor_length

        time.sleep(meteor_speed)

    return hsv_values



def effect_36(hsv_values):
    """Fast animated rainbow explosion effect radiating from the center outward."""
    center = NUM_LEDS // 2
    speed = 0.1  # Increased speed for faster color shift
    cycle_length = 360  # The length of the hue cycle

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000  # Time in seconds
        for i in range(NUM_LEDS):
            # Calculate the distance from the center
            distance = abs(center - i)
            # Calculate the hue based on distance and elapsed time, with GRB adjustment
            hue = (elapsed * speed * cycle_length + distance * 10) % cycle_length / 360.0
            
            # Adjust for GRB by setting green (hue 0.00) and red (hue 0.33) correctly
            if hue < 0.17 or hue >= 0.83:  # Corresponds to Green region
                adjusted_hue = 0.00
            elif 0.17 <= hue < 0.5:  # Corresponds to Blue region
                adjusted_hue = 0.66
            else:  # Corresponds to Red region
                adjusted_hue = 0.33

            brightness = max(0, 1 - distance / (NUM_LEDS / 2.0))
            hsv_values[i] = (adjusted_hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.02)  # Faster animation

    return hsv_values

def effect_37(hsv_values):
    """Breathing effect with color cycling."""
    speed = 0.05  # Breathing speed
    cycle_length = 360  # Full hue cycle length

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000  # Time in seconds
        
        for i in range(NUM_LEDS):
            # Calculate the hue based on elapsed time and GRB adjustment
            hue = (elapsed * speed * cycle_length + i) % cycle_length / 360.0
            
            # Adjust the hue to ensure correct GRB color order
            if hue < 0.17 or hue >= 0.83:  # Corresponds to Green region
                adjusted_hue = 0.00
            elif 0.17 <= hue < 0.5:  # Corresponds to Blue region
                adjusted_hue = 0.66
            else:  # Corresponds to Red region
                adjusted_hue = 0.33

            # Calculate brightness based on a sinusoidal breathing effect
            brightness = (1 + math.sin(elapsed * 2 * math.pi * speed)) / 2

            hsv_values[i] = (adjusted_hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.02)  # Small delay for smoother breathing effect

    return hsv_values


def effect_38(hsv_values):
    """Moving plasma effect."""
    speed = 0.1  # Adjust the speed of the plasma movement
    wave_length = 20  # Length of the wave for sine calculation

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000  # Time in seconds

        for i in range(NUM_LEDS):
            # Calculate the hue based on the position and elapsed time
            hue = (i * 10 + elapsed * 100) % 360 / 360.0

            # Adjust the hue for the correct GRB color order
            if hue < 0.17 or hue >= 0.83:  # Corresponds to Green region
                adjusted_hue = 0.00
            elif 0.17 <= hue < 0.5:  # Corresponds to Blue region
                adjusted_hue = 0.66
            else:  # Corresponds to Red region
                adjusted_hue = 0.33

            # Calculate brightness using a sine wave for a moving plasma effect
            brightness = (1 + math.sin(i * 2 * math.pi / wave_length + elapsed * speed)) / 2

            hsv_values[i] = (adjusted_hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.02)  # Small delay for smooth animation

    return hsv_values



def effect_39(hsv_values):
    """Multi-neon laser sweeps with independent speeds and ghost trails (orientation-aware)."""
    # Beam / laser parameters
    NUM_BEAMS = 3
    MIN_LENGTH = 8
    MAX_LENGTH = 16

    MIN_STEP = 0.35      # min movement per frame (slower beams)
    MAX_STEP = 0.95      # max movement per frame (faster beams)

    HEAD_BRIGHT = 1.0
    BG_DECAY = 0.90      # background fade
    GHOST_DECAY = 0.94   # ghost fade
    GHOST_SCALE = 0.5    # ghost brightness relative to source
    GHOST_SPAWN_CHANCE = 0.10
    MIN_VISIBLE = 0.01

    # Neon-like palette (HSV hues)
    NEON_HUES = [
        0.83,  # magenta / pink
        0.58,  # cyan
        0.72,  # purple
        0.38,  # lime / yellow-green
        0.02,  # hot red/orange
    ]

    start_time = time.ticks_ms()

    # Beam state: list of dicts
    # env space: 0 = bottom, NUM_LEDS-1 = top
    beams = []

    def new_beam(direction=None):
        """Create a new beam that starts off-strip and moves across."""
        if direction is None:
            direction = choice([-1, 1])

        length = randrange(MIN_LENGTH, MAX_LENGTH + 1)
        half_len = length / 2.0

        # Start just off one side so it sweeps fully into view
        if direction == 1:
            center = -half_len
        else:
            center = NUM_LEDS + half_len

        return {
            "center": center,                 # float env index
            "length": length,
            "half_len": half_len,
            "step": uniform(MIN_STEP, MAX_STEP),     # speed
            "direction": direction,
            "hue": choice(NEON_HUES),
        }

    # initialise beams
    for _ in range(NUM_BEAMS):
        beams.append(new_beam())

    # Ghosts: each = {"pos": float, "hue": float, "brightness": float, "drift": float}
    ghosts = []

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # -----------------------------------
        # 1) Fade background
        # -----------------------------------
        for env_idx in range(NUM_LEDS):
            h, s, v = hsv_values[env_idx]
            v *= BG_DECAY
            if v < MIN_VISIBLE:
                v = 0.0
            hsv_values[env_idx] = (h, s, v)

        # -----------------------------------
        # 2) Update ghosts
        # -----------------------------------
        new_ghosts = []
        for g in ghosts:
            g["pos"] += g["drift"]
            g["brightness"] *= GHOST_DECAY

            if g["brightness"] <= MIN_VISIBLE:
                continue

            idx = int(g["pos"])
            if 0 <= idx < NUM_LEDS:
                _, _, v_prev = hsv_values[idx]
                v = max(v_prev, g["brightness"])
                hsv_values[idx] = (g["hue"], 1.0, v)
                new_ghosts.append(g)

        ghosts = new_ghosts

        # -----------------------------------
        # 3) Draw all beams
        # -----------------------------------
        for beam in beams:
            c = beam["center"]
            half_len = beam["half_len"]
            hue = beam["hue"]

            # Go from -half_len to +half_len around center
            for k in range(-int(half_len) - 1, int(half_len) + 2):
                pos = c + k
                env_idx = int(pos)
                if 0 <= env_idx < NUM_LEDS:
                    frac = 1.0 - (abs(k) / (half_len + 0.001))
                    if frac <= 0.0:
                        continue

                    # Smooth profile; soften a bit so it’s not a harsh bar
                    brightness = HEAD_BRIGHT * (frac ** 1.4)

                    # Blend with existing
                    _, _, v_prev = hsv_values[env_idx]
                    v = max(v_prev, brightness)
                    hsv_values[env_idx] = (hue, 1.0, v)

                    # Spawn ghosts mostly from the outer third
                    if abs(k) > half_len * 0.4 and random() < GHOST_SPAWN_CHANCE:
                        ghosts.append({
                            "pos": env_idx + (random() - 0.5) * 0.4,
                            "hue": hue,
                            "brightness": brightness * GHOST_SCALE,
                            "drift": (random() - 0.5) * 0.12,
                        })

        # -----------------------------------
        # 4) Push frame to strip with orientation mapping
        # -----------------------------------
        for env_idx in range(NUM_LEDS):
            h, s, v = hsv_values[env_idx]
            set_hsv_env(env_idx, h, s, v)

        # -----------------------------------
        # 5) Advance beams, respawn if they’ve left
        # -----------------------------------
        for i, beam in enumerate(beams):
            beam["center"] += beam["direction"] * beam["step"]

            c = beam["center"]
            half_len = beam["half_len"]

            if beam["direction"] == 1 and c - half_len > NUM_LEDS + 1:
                beams[i] = new_beam(direction=-1 if randrange(3) == 0 else 1)
            elif beam["direction"] == -1 and c + half_len < -1:
                beams[i] = new_beam(direction=1 if randrange(3) == 0 else -1)

        time.sleep(0.02)

    return hsv_values


def effect_40(hsv_values):
    """Single bouncing ball whose behaviour depends on ORIENTATION.

    ORIENTATION = "BOTTOM":
        Controller at bottom (env 0).
        - Ball starts at env NUM_LEDS-1 (top)
        - Falls TOWARDS controller
        - Bounces at env 0
        - Fades out at env 0

    ORIENTATION = "TOP":
        Controller at top (env NUM_LEDS-1).
        - Ball starts at env NUM_LEDS-1 (controller side)
        - Falls AWAY from controller to env 0
        - Bounces at env 0
        - Fades out at env 0
    """
    gravity_mag = 0.03
    bounce_damping = 0.70   # how much speed is kept after each bounce
    fade_speed = 0.01
    pause_duration = 1.0

    # World coordinates: env 0 = bottom, env NUM_LEDS-1 = top
    # (env_to_phys + set_hsv_env take care of mapping to real strip)
    if ORIENTATION == "BOTTOM":
        # Controller at env 0 (bottom). Ball falls towards controller.
        start_env = NUM_LEDS - 1   # start at top
        floor_env = 0              # bounce at controller end
    else:  # ORIENTATION == "TOP"
        # Controller at env NUM_LEDS-1 (top).
        # Ball goes the OTHER WAY: away from controller, towards bottom.
        start_env = NUM_LEDS - 1   # start at controller side (top)
        floor_env = 0              # bounce at far end (bottom, away from controller)

    # Decide direction so motion goes from start_env towards floor_env
    direction = 1 if floor_env > start_env else -1
    gravity = direction * gravity_mag

    ball_position = float(start_env)
    velocity = 0.0
    hue = randrange(360) / 360.0
    ball_bouncing = True

    while ball_bouncing:
        # Clear all LEDs in env-space
        for i in range(NUM_LEDS):
            hsv_values[i] = (0.0, 0.0, 0.0)
            set_hsv_env(i, 0.0, 0.0, 0.0)

        # Physics integration
        velocity += gravity
        ball_position += velocity

        # Bounce check depending on direction
        if (direction == -1 and ball_position <= floor_env) or \
           (direction ==  1 and ball_position >= floor_env):

            ball_position = float(floor_env)
            velocity = -velocity * bounce_damping

            # If we’ve lost almost all energy, stop bouncing and fade out
            if abs(velocity) < 0.01:
                ball_bouncing = False

                env_idx = int(round(floor_env))
                # Show ball parked at floor
                hsv_values[env_idx] = (hue, 1.0, 1.0)
                set_hsv_env(env_idx, hue, 1.0, 1.0)
                time.sleep(pause_duration)

                # Fade out at the floor LED
                for step in range(100, -1, -1):
                    b = step / 100.0
                    hsv_values[env_idx] = (hue, 1.0, b)
                    set_hsv_env(env_idx, hue, 1.0, b)
                    time.sleep(fade_speed)
                break

        # Draw ball between two nearest env LEDs (smooth movement)
        pos_floor = int(ball_position)
        pos_ceil = min(pos_floor + 1, NUM_LEDS - 1)
        frac = ball_position - pos_floor

        brightness_ceil = max(0.0, min(1.0, frac))
        brightness_floor = max(0.0, min(1.0, 1.0 - frac))

        if 0 <= pos_floor < NUM_LEDS:
            hsv_values[pos_floor] = (hue, 1.0, brightness_floor)
            set_hsv_env(pos_floor, hue, 1.0, brightness_floor)

        if 0 <= pos_ceil < NUM_LEDS:
            hsv_values[pos_ceil] = (hue, 1.0, brightness_ceil)
            set_hsv_env(pos_ceil, hue, 1.0, brightness_ceil)

        time.sleep(0.02)

    # Make sure floor LED is off before returning
    env_idx = int(floor_env)
    hsv_values[env_idx] = (0.0, 0.0, 0.0)
    set_hsv_env(env_idx, 0.0, 0.0, 0.0)

    return hsv_values




def effect_41(hsv_values):
    """Rotating comet effect that appears from off one end and exits off the other (orientation-aware).

    Env space:
      0             = bottom
      NUM_LEDS - 1  = top

    ORIENTATION decides which *physical* end is bottom/top.
    """

    comet_length = 10   # Length of the comet's tail
    speed = 0.02        # Speed of the comet

    # Color for the comet head (red-ish in your GRB/HSV scheme)
    hue = 0.80
    saturation = 1.0
    brightness = 1.0

    start_time = time.ticks_ms()

    # We will repeatedly sweep the comet across the whole env space
    # head_env runs from -comet_length (fully off one side)
    # up to NUM_LEDS + comet_length (fully off the opposite side)
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for head_env in range(-comet_length, NUM_LEDS + comet_length):
            # Abort this sweep early if timeout is hit mid-animation
            if time.ticks_diff(time.ticks_ms(), start_time) >= TIMEOUT_DURATION:
                break

            for env_i in range(NUM_LEDS):
                distance = abs(env_i - head_env)
                if distance < comet_length:
                    # Tail fades smoothly to zero at the end
                    tail_brightness = brightness * (1.0 - distance / comet_length)
                else:
                    tail_brightness = 0.0

                hsv_values[env_i] = (hue, saturation, tail_brightness)
                set_hsv_env(env_i, hue, saturation, tail_brightness)

            time.sleep(speed)

    return hsv_values



def effect_42(hsv_values):
    """Spiral effect moving up the strip (from bottom to top) with a 66-LED spiral and random side-to-side hue shifts."""
    speed = 0.05  # Speed of the spiral movement
    spiral_length = NUM_LEDS  # Length of the spiral (full strip)
    hue_shift = 0.01  # Base hue change per step
    hue_range = 0.2  # Restrict hue to 10% of the spectrum

    start_time = time.ticks_ms()
    direction = 1  # Initial direction for hue shift

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS * 2):
            if randrange(100) < 10:  # 10% chance to change direction
                direction = -direction

            for i in range(NUM_LEDS):
                # Calculate the position of the spiral's "head" with inversion
                position = NUM_LEDS - (t + i) % spiral_length

                # Calculate brightness based on distance from the head of the spiral
                distance = abs(position - i)
                brightness = max(0, 1 - distance / spiral_length)

                # Apply hue shift with random side-to-side movement
                hue = ((i * hue_shift + t * hue_shift * direction) % hue_range)

                # Set the color and brightness for each LED
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(speed)

    return hsv_values




def effect_43(hsv_values):
    """Wave pulsing up and down the strip with smooth motion over time."""
    WAVE_LENGTH = 100.0   # larger = more stretched wave
    SPEED = 0.003         # affects how fast phase moves
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time)
        for i in range(NUM_LEDS):
            phase = (i * 2 * math.pi / WAVE_LENGTH) + (t * SPEED)
            brightness = (1.0 + math.sin(phase)) * 0.5

            hue = ((i * 10) % 360) / 360.0
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)

    return hsv_values


def effect_44(hsv_values):
    """Waterfall effect: flowing bands with a soft sine wave, moving 'down' the strip (orientation-aware)."""
    WAVE_LENGTH = 10.0
    SPEED = 0.006   # movement speed
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time)

        for env_i in range(NUM_LEDS):
            # Same math as original, just using env index instead of physical i
            phase = (env_i * 2 * math.pi / WAVE_LENGTH) + (t * SPEED)
            brightness = (1.0 + math.sin(phase)) * 0.5

            hue = ((env_i * 30) % 360) / 360.0
            hsv_values[env_i] = (hue, 1.0, brightness)
            set_hsv_env(env_i, hue, 1.0, brightness)

        time.sleep(0.02)

    return hsv_values


def effect_45(hsv_values):
    """Game of Life effect with white LEDs."""
    # Initialize the game board with random states (on or off)
    current_state = [randrange(2) for _ in range(NUM_LEDS)]

    def count_neighbors(index):
        """Count the number of alive neighbors for a given cell."""
        left = current_state[(index - 1) % NUM_LEDS]
        right = current_state[(index + 1) % NUM_LEDS]
        return left + right

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        next_state = [0] * NUM_LEDS

        for i in range(NUM_LEDS):
            neighbors = count_neighbors(i)

            if current_state[i] == 1:  # Cell is alive
                if neighbors == 1:  # Survival condition
                    next_state[i] = 1
            else:  # Cell is dead
                if neighbors == 1:  # Birth condition
                    next_state[i] = 1

            # Set the LED color based on the cell's state
            brightness = 1.0 if next_state[i] == 1 else 0.0
            hsv_values[i] = (0.0, 0.0, brightness)  # White LEDs
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        # Update the current state to the next state
        current_state = next_state[:]

        time.sleep(0.1)  # Adjust the speed of evolution

    return hsv_values



def effect_46(hsv_values):
    """Rainbow comet effect moving across the strip with a fading tail."""
    comet_length = 20  # Length of the comet tail
    comet_speed = 0.1  # Speed of the comet's movement
    hue_shift = 0.005  # How quickly the hue changes over time

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS + comet_length):
            for i in range(NUM_LEDS):
                distance = t - i
                if 0 <= distance < comet_length:
                    # Calculate the hue for each part of the comet
                    hue = ((i / NUM_LEDS) + (t * hue_shift)) % 1.0
                    brightness = max(0, 1 - (distance / comet_length))
                    hsv_values[i] = (hue, 1.0, brightness)
                else:
                    # Fade out the rest of the LEDs
                    hsv_values[i] = (0.0, 0.0, 0.0)
                
                # Set the LED color
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(comet_speed)

    return hsv_values


def effect_47(hsv_values):
    """Randomised, rolling color waves with multiple hues."""
    WAVE_LENGTH = 12.0
    SPEED = 0.004
    HUE_SCROLL_SPEED = 0.0008

    start_time = time.ticks_ms()
    base_hue = random()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t_ms = time.ticks_diff(time.ticks_ms(), start_time)
        t = t_ms * SPEED

        # Slowly scroll base hue over time
        base_hue = (base_hue + HUE_SCROLL_SPEED) % 1.0

        for i in range(NUM_LEDS):
            # Multi-wave interference for brightness
            phase1 = i * 2 * math.pi / WAVE_LENGTH + t
            phase2 = i * 2 * math.pi / (WAVE_LENGTH * 1.7) - t * 0.7
            brightness = (math.sin(phase1) + math.sin(phase2)) * 0.25 + 0.5
            brightness = max(0.0, min(1.0, brightness))

            # Random-ish hue spread along the strip
            hue_offset = (i * 0.03) % 1.0
            hue = (base_hue + hue_offset) % 1.0

            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)

    return hsv_values

def effect_48(hsv_values):
    """Color pulsating wave that moves back and forth, starting/ending off-strip."""
    wave_length = 20      # Physical length of the wave
    step = 0.7           # How many LEDs the wave center moves per frame
    hue_shift = 0.01      # Hue variation along the strip

    # Start fully off the "left" side
    center = -wave_length
    direction = 1  # 1 = left→right, -1 = right→left

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Optional: fade existing content slightly instead of hard clearing
        # so this effect can blend with previous ones better.
        # Comment OUT this block if you want hard black outside the wave.
        fade_factor = 0.7
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            v *= fade_factor
            hsv_values[i] = (h, s, v)

        # Draw the wave
        for i in range(NUM_LEDS):
            distance = abs(i - center)

            if distance < wave_length:
                # Nice soft “blob” profile using a sine
                # distance 0 → peak, distance = wave_length → 0
                phase = (1.0 - distance / wave_length) * math.pi
                brightness = max(0.0, math.sin(phase))

                hue = (i * hue_shift) % 1.0
                hsv_values[i] = (hue, 1.0, brightness)
            # else: keep whatever faded value was there

            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        # Move the wave center
        center += direction * step

        # When the wave has completely left one side, reverse direction
        if direction == 1 and center - wave_length > NUM_LEDS:
            # fully off the right side → flip and start off the right
            direction = -1
            center = NUM_LEDS + wave_length
        elif direction == -1 and center + wave_length < 0:
            # fully off the left side → flip and start off the left
            direction = 1
            center = -wave_length

        time.sleep(0.03)

    return hsv_values


def effect_49(hsv_values):
    """Gentle rolling clouds effect with soft white and blue hues."""
    cloud_color_1 = (0.50, 0.2, 0.7)  # Light blue cloud
    cloud_color_2 = (0.50, 0.1, 0.9)  # Slightly brighter blue-white cloud
    speed = 0.05  # Speed of cloud movement
    cloud_length = 20  # Length of each cloud
    fade_factor = 0.98  # Fading effect for trailing edges of clouds

    # Initialize cloud positions
    cloud_positions = [randrange(NUM_LEDS) for _ in range(3)]
    cloud_directions = [choice([-1, 1]) for _ in range(3)]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Fade the entire strip slightly to create a smooth trailing effect
        for i in range(NUM_LEDS):
            hsv_values[i] = (hsv_values[i][0], hsv_values[i][1], hsv_values[i][2] * fade_factor)

        # Move and draw clouds
        for j in range(len(cloud_positions)):
            for t in range(cloud_length):
                index = (cloud_positions[j] + t * cloud_directions[j]) % NUM_LEDS
                brightness = max(0, 1.0 - (t / cloud_length))
                hsv_values[index] = (
                    (cloud_color_1[0] * (1 - brightness) + cloud_color_2[0] * brightness),
                    (cloud_color_1[1] * (1 - brightness) + cloud_color_2[1] * brightness),
                    (cloud_color_1[2] * (1 - brightness) + cloud_color_2[2] * brightness)
                )

            # Update cloud position
            cloud_positions[j] += cloud_directions[j]
            if cloud_positions[j] >= NUM_LEDS or cloud_positions[j] < 0:
                cloud_directions[j] = -cloud_directions[j]  # Reverse direction
                cloud_positions[j] += cloud_directions[j] * 2

        # Update the LED strip with the new HSV values
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(speed)  # Control the speed of the effect

    return hsv_values

def effect_50(hsv_values):
    """Glowing Pulsar effect with bright pulses moving along the strip."""
    num_pulsars = 3  # Number of pulsars
    pulsar_length = 10  # Length of each pulsar trail
    fade_factor = 0.85  # Fading factor for the pulsar trails
    speed = 0.05  # Speed of the pulsars' movement

    # Initialize pulsar positions, directions, and hues
    pulsar_positions = [randrange(NUM_LEDS) for _ in range(num_pulsars)]
    pulsar_directions = [choice([-1, 1]) for _ in range(num_pulsars)]
    pulsar_hues = [randrange(360) / 360.0 for _ in range(num_pulsars)]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Fade the entire strip slightly to create trailing effects
        for i in range(NUM_LEDS):
            hsv_values[i] = (hsv_values[i][0], hsv_values[i][1], hsv_values[i][2] * fade_factor)

        # Move and draw pulsars
        for j in range(num_pulsars):
            for t in range(pulsar_length):
                index = (pulsar_positions[j] + t * pulsar_directions[j]) % NUM_LEDS
                brightness = max(0, 1.0 - (t / pulsar_length))
                hsv_values[index] = (
                    pulsar_hues[j],
                    1.0,
                    brightness
                )

            # Update pulsar position
            pulsar_positions[j] += pulsar_directions[j]
            if pulsar_positions[j] >= NUM_LEDS or pulsar_positions[j] < 0:
                pulsar_directions[j] = -pulsar_directions[j]  # Reverse direction
                pulsar_positions[j] += pulsar_directions[j] * 2

        # Update the LED strip with the new HSV values
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(speed)  # Control the speed of the effect

    return hsv_values



def effect_51(hsv_values):
    """Northern Lights effect with flowing waves of green, blue, and purple hues."""
    wave_speed = 0.001  # Speed at which the waves move
    hue_shift_speed = 0.001  # Speed of hue shift over time
    wave_amplitude = 0.5  # Amplitude of the sine wave
    base_hue = 0.5  # Starting hue (around cyan/purple)

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            # Calculate the hue based on position and time
            position_offset = (i / NUM_LEDS) * math.pi * 2
            time_offset = time.ticks_diff(time.ticks_ms(), start_time) * wave_speed
            hue_variation = math.sin(position_offset + time_offset) * wave_amplitude
            hue = (base_hue + hue_variation) % 1.0
            
            # Set brightness based on the sine wave for a wavy effect
            brightness = (1 + math.sin(position_offset + time_offset)) / 2
            
            # Apply a gentle saturation for a more muted color palette
            saturation = 0.6

            hsv_values[i] = (hue, saturation, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        # Gradually shift the base hue to create a slowly changing color palette
        base_hue = (base_hue + hue_shift_speed) % 1.0

        time.sleep(0.05)

    return hsv_values


def effect_52(hsv_values):
    """Fireworks Burst"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(50):
            center = randrange(NUM_LEDS)
            for i in range(NUM_LEDS):
                distance = abs(center - i)
                hue = randrange(360) / 360.0
                brightness = max(0, 1 - distance / 10)
                if brightness > 0:
                    hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.1)
    return hsv_values

def effect_53(hsv_values):
    """Explosion"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS // 2):
            center = NUM_LEDS // 2
            for i in range(NUM_LEDS):
                distance = abs(center - i)
                hue = randrange(360) / 360.0
                brightness = max(0, 1 - (distance - t) / 10)
                if brightness > 0:
                    hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_54(hsv_values):
    """Larson Scanner (Knight Rider)"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS * 2):
            position = t % NUM_LEDS if t < NUM_LEDS else NUM_LEDS - (t % NUM_LEDS) - 1
            for i in range(NUM_LEDS):
                brightness = max(0, 1 - abs(i - position) / 10)
                hsv_values[i] = (0.33, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_55(hsv_values):
    """Cinematic comet with long tail, embers and ambient glow.
       Each new comet has its own narrow hue band. No shockwave."""
    
    TAIL_LENGTH = 18
    BASE_FADE = 0.82
    BG_DECAY = 0.96
    EMBER_CHANCE = 0.18
    EMBER_DECAY_MIN = 0.002
    EMBER_DECAY_MAX = 0.01
    EMBER_POP_CHANCE = 0.01

    HUE_SPREAD = 0.10      # width of hue band per comet (0–1 scale)
    HUE_JITTER = 0.01      # small per-pixel variation

    start_time = time.ticks_ms()

    # Ambient fog (warm/cool based on comet hue)
    bg_glow = [0.0] * NUM_LEDS

    # Ember list
    embers = []  # each: {"pos": float, "hue": float, "brightness": float, "decay": float}

    def time_left():
        return time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION

    while time_left():
        # Pick a new hue band for THIS comet
        center = random()
        hue_min = max(0.0, center - HUE_SPREAD / 2)
        hue_max = min(1.0, center + HUE_SPREAD / 2)

        def rand_hue():
            return uniform(hue_min, hue_max)

        # Direction: 1 = left→right, -1 = right→left
        direction = 1 if randrange(2) == 0 else -1

        if direction == 1:
            head = -TAIL_LENGTH
            def done(h): return h > NUM_LEDS + TAIL_LENGTH
        else:
            head = NUM_LEDS + TAIL_LENGTH
            def done(h): return h < -TAIL_LENGTH

        base_hue = rand_hue()

        # Speed easing
        speed_start = uniform(0.09, 0.16)
        speed_end   = uniform(0.03, 0.06)
        t_step = 0

        # -----------------------------
        #   COMET TRAVEL PHASE
        # -----------------------------
        while not done(head) and time_left():

            # Fade old pixels + fog
            for i in range(NUM_LEDS):
                h, s, v = hsv_values[i]
                v *= BASE_FADE
                bg_glow[i] *= BG_DECAY
                v = max(v, bg_glow[i])
                hsv_values[i] = (h, s, v)

            # Update embers
            max_emb = 0.0
            for e in embers[:]:
                e["brightness"] -= e["decay"]
                if e["brightness"] <= 0:
                    embers.remove(e)
                    continue

                # Chance of ember "pop"
                if e["brightness"] < 0.4 and random() < EMBER_POP_CHANCE:
                    e["brightness"] = min(1.0, e["brightness"] + uniform(0.3, 0.7))

                pos = int(e["pos"])
                if 0 <= pos < NUM_LEDS:
                    _, _, old_v = hsv_values[pos]
                    v = max(old_v, e["brightness"])
                    hsv_values[pos] = (e["hue"], 1.0, v)
                    if v > max_emb:
                        max_emb = v

            # Draw comet head + tail
            for k in range(TAIL_LENGTH):
                pos = int(round(head - direction * k))
                if 0 <= pos < NUM_LEDS:

                    frac = 1.0 - (k / TAIL_LENGTH)
                    brightness = frac * frac

                    hue = base_hue + uniform(-HUE_JITTER, HUE_JITTER)
                    hue = max(hue_min, min(hue_max, hue))

                    _, _, existing_v = hsv_values[pos]
                    v = max(existing_v, brightness)
                    hsv_values[pos] = (hue, 1.0, v)

                    # Ambient glow accumulation
                    bg_glow[pos] = max(bg_glow[pos], brightness * 0.25)

                    # Spawn ember?
                    if brightness > 0.25 and random() < EMBER_CHANCE:
                        e_hue = base_hue + uniform(-HUE_JITTER, HUE_JITTER)
                        e_hue = max(hue_min, min(hue_max, e_hue))
                        embers.append({
                            "pos": pos + uniform(-0.3, 0.3),
                            "hue": e_hue,
                            "brightness": brightness * uniform(0.4, 0.9),
                            "decay": uniform(EMBER_DECAY_MIN, EMBER_DECAY_MAX),
                        })

            # Push frame to LEDs
            for i in range(NUM_LEDS):
                h, s, v = hsv_values[i]
                led_strip.set_hsv(i, h, s, v)

            # Easing speed
            t_step += 1
            lerp = min(1.0, t_step / float(NUM_LEDS + TAIL_LENGTH))
            speed = speed_start + (speed_end - speed_start) * lerp

            head += direction
            time.sleep(speed)

        # -----------------------------
        #   DECAY PHASE (embers + fog)
        # -----------------------------
        while embers and time_left():

            max_b = 0.0

            # fade trails + fog
            for i in range(NUM_LEDS):
                h, s, v = hsv_values[i]
                v *= BASE_FADE
                bg_glow[i] *= BG_DECAY
                v = max(v, bg_glow[i])
                hsv_values[i] = (h, s, v)

            # update embers
            for e in embers[:]:
                e["brightness"] -= e["decay"]
                if e["brightness"] <= 0:
                    embers.remove(e)
                    continue

                if e["brightness"] < 0.002 and random() < EMBER_POP_CHANCE:
                    e["brightness"] = min(1.0, e["brightness"] + uniform(0.2, 0.5))

                pos = int(e["pos"])
                if 0 <= pos < NUM_LEDS:
                    _, _, old_v = hsv_values[pos]
                    v = max(old_v, e["brightness"])
                    hsv_values[pos] = (e["hue"], 1.0, v)
                    if v > max_b:
                        max_b = v

            # push frame
            for i in range(NUM_LEDS):
                h, s, v = hsv_values[i]
                led_strip.set_hsv(i, h, s, v)

            # break when scene is basically empty
            if max_b < 0.05 and max(bg_glow) < 0.05:
                break

            time.sleep(0.05)

    return hsv_values


def effect_56(hsv_values):
    """Colorful Fireworks Burst effect with expanding colorful bursts."""
    num_fireworks = 5  # Number of fireworks bursts
    burst_duration = 20  # Duration of each burst
    fade_factor = 0.9  # Fading factor for the trails

    # Initialize bursts with random positions and hues
    bursts = [
        {
            "position": randrange(NUM_LEDS),
            "hue": randrange(360) / 360.0,
            "timer": randrange(burst_duration),
            "speed": uniform(0.05, 0.15)
        }
        for _ in range(num_fireworks)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Fade the entire strip slightly to create trailing effects
        for i in range(NUM_LEDS):
            hsv_values[i] = (hsv_values[i][0], hsv_values[i][1], hsv_values[i][2] * fade_factor)

        # Update and draw each firework burst
        for burst in bursts:
            burst_position = burst["position"]
            burst_hue = burst["hue"]
            burst_timer = burst["timer"]
            brightness = max(0, (burst_duration - burst_timer) / burst_duration)

            # Draw expanding burst
            for i in range(-burst_timer, burst_timer + 1):
                index = (burst_position + i) % NUM_LEDS
                if 0 <= index < NUM_LEDS:
                    hsv_values[index] = (burst_hue, 1.0, brightness)

            burst["timer"] += 1

            # Reset burst if it has completed its duration
            if burst["timer"] >= burst_duration:
                burst["position"] = randrange(NUM_LEDS)
                burst["hue"] = randrange(360) / 360.0
                burst["timer"] = 0

        # Update the LED strip with the new HSV values
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.05)  # Control the speed of the effect

    return hsv_values


def effect_57(hsv_values):
    """Colorful Larson Scanner"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS * 2):
            position = t % NUM_LEDS if t < NUM_LEDS else NUM_LEDS - (t % NUM_LEDS) - 1
            hue = t % 360 / 360.0
            for i in range(NUM_LEDS):
                brightness = max(0, 1 - abs(i - position) / 10)
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_58(hsv_values):
    """Rapid Fireworks"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(20):
            burst_center = randrange(NUM_LEDS)
            hue = randrange(360) / 360.0
            for i in range(NUM_LEDS):
                distance = abs(burst_center - i)
                brightness = max(0, 1 - distance / 5)
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_59(hsv_values):
    """Starry Night"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for _ in range(100):
            index = randrange(NUM_LEDS)
            hue = randrange(360) / 360.0
            brightness = uniform(0.5, 1.0)
            hsv_values[index] = (hue, 1.0, brightness)
            led_strip.set_hsv(index, hsv_values[index][0], hsv_values[index][1], hsv_values[index][2])
            time.sleep(0.1)
    return hsv_values

def effect_60(hsv_values):
    """Meteor Shower"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS):
            for i in range(NUM_LEDS):
                hue = 0.6
                brightness = max(0, 1 - abs(t - i) / 10)
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_61(hsv_values):
    """Random Sparkles"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for _ in range(NUM_LEDS // 10):
            index = randrange(NUM_LEDS)
            hue = randrange(360) / 360.0
            brightness = 1.0
            hsv_values[index] = (hue, 1.0, brightness)
            led_strip.set_hsv(index, hsv_values[index][0], hsv_values[index][1], hsv_values[index][2])
            time.sleep(0.05)
    return hsv_values

def effect_62(hsv_values):
    """Fireflies"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS):
            index = randrange(NUM_LEDS)
            hue = randrange(360) / 360.0
            brightness = (1 + math.sin(t * 2 * math.pi / NUM_LEDS)) / 2
            hsv_values[index] = (hue, 1.0, brightness)
            led_strip.set_hsv(index, hsv_values[index][0], hsv_values[index][1], hsv_values[index][2])
            time.sleep(0.05)
    return hsv_values

def effect_63(hsv_values):
    """Pulsating Red and White effect with smooth transitions and breathing brightness."""
    pulse_speed = 0.05  # Speed of the pulsing effect
    move_speed = 0.1    # Speed at which the colors move across the strip

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS):
            # Alternate between red and white based on position
            if t % 2 == 0:
                hue = 0.33  # Red
            else:
                hue = 0.0  # White with lower saturation

            # Pulsating brightness
            brightness = (1 + math.sin(time.ticks_ms() * pulse_speed / 1000)) / 2

            # Set HSV values, with saturation adjusted for white
            if hue == 0.0 and t % 2 != 0:
                hsv_values[t] = (hue, 0.0, brightness)  # White
            else:
                hsv_values[t] = (hue, 1.0, brightness)  # Red

        # Update the LED strip with the new HSV values
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.02)  # Control the speed of the effect

    return hsv_values


def effect_64(hsv_values):
    """Colorful Snake"""
    snake_length = 10
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS * 2):
            for i in range(NUM_LEDS):
                hue = (i * 10) % 360 / 360.0
                brightness = 1.0 if abs(i - t % NUM_LEDS) < snake_length else 0.0
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_65(hsv_values):
    """Comet Streak"""
    comet_length = 15
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS * 2):
            for i in range(NUM_LEDS):
                hue = (i * 10) % 360 / 360.0
                brightness = max(0, 1 - abs(t % NUM_LEDS - i) / comet_length)
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_66(hsv_values):
    """Twinkling Stars"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS):
            index = randrange(NUM_LEDS)
            hue = randrange(360) / 360.0
            brightness = 1.0 if t % 2 == 0 else 0.0
            hsv_values[index] = (hue, 1.0, brightness)
            led_strip.set_hsv(index, hsv_values[index][0], hsv_values[index][1], hsv_values[index][2])
            time.sleep(0.05)
    return hsv_values

def effect_67(hsv_values):
    """Thunderstorm"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS):
            brightness = 1.0 if randrange(100) < 10 else 0.0
            hsv_values[t] = (0.0, 0.0, brightness)
            led_strip.set_hsv(t, hsv_values[t][0], hsv_values[t][1], hsv_values[t][2])
        time.sleep(0.05)
    return hsv_values

def effect_68(hsv_values):
    """Flickering Candle"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS):
            hue = 0.1
            brightness = uniform(0.7, 1.0)
            hsv_values[t] = (hue, 1.0, brightness)
            led_strip.set_hsv(t, hsv_values[t][0], hsv_values[t][1], hsv_values[t][2])
        time.sleep(0.05)
    return hsv_values

def effect_69(hsv_values):
    """Sparkling Waterfall (orientation-aware, calmer, softer sparkles)."""

    waterfall_speed = 0.05
    sparkle_chance = 0.02      # MUCH lower chance of sparkles
    sparkle_fade = 0.92        # Slower fade for sparkles
    base_fade = 0.88           # General background fade
    max_water_brightness = 0.4 # Reduce overall brightness for a calmer look

    # Track sparkle intensities separately
    sparkles = [0.0] * NUM_LEDS

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()

        for env_i in range(NUM_LEDS):

            # --- BASE WATERFALL MOTION ---
            hue = 0.60  # blue
            wave = (
                1
                + math.sin(
                    env_i * 2 * math.pi / 12.0
                    + now * waterfall_speed / 1000.0
                )
            ) / 2
            base_brightness = wave * max_water_brightness

            # Apply soft fade
            base_brightness *= base_fade

            # --- SPARKLES ---
            # Chance to spawn a subtle sparkle
            if sparkles[env_i] <= 0.01 and random() < sparkle_chance:
                sparkles[env_i] = 0.6  # sparkle intensity

            # Sparkles fade gradually
            sparkles[env_i] *= sparkle_fade

            # Sparkle overrides base brightness but gently
            brightness = max(base_brightness, sparkles[env_i])

            hsv_values[env_i] = (hue, 1.0, brightness)

        # Push to LED strip
        for env_i in range(NUM_LEDS):
            h, s, v = hsv_values[env_i]
            set_hsv_env(env_i, h, s, v)

        time.sleep(0.02)

    return hsv_values



def effect_70(hsv_values):
    """Scrolling Red and White Bars effect."""
    BAR_LENGTH = 10  # Length of each colored bar
    SCROLL_SPEED = 0.05  # Speed of the scrolling

    # Colors (hue values in GRB format)
    RED_HUE = 0.33  # Red
    WHITE_HUE = 0.0  # White (hue = 0, saturation = 0)

    start_time = time.ticks_ms()

    offset = 0  # Initialize offset for scrolling

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            # Calculate the position with offset
            position = (i + offset) % (2 * BAR_LENGTH)
            if position < BAR_LENGTH:
                hsv_values[i] = (RED_HUE, 1.0, 1.0)  # Red bar
            else:
                hsv_values[i] = (WHITE_HUE, 0.0, 1.0)  # White bar

        # Update the LED strip with the new HSV values
        for j in range(NUM_LEDS):
            led_strip.set_hsv(j, hsv_values[j][0], hsv_values[j][1], hsv_values[j][2])

        offset += 1  # Increment offset to scroll the pattern
        time.sleep(SCROLL_SPEED)  # Control the speed of the scrolling effect

    return hsv_values


def effect_71(hsv_values):
    NUM_LEDS_MOVING = 5  # Number of moving LEDs
    TRAIL_LENGTH = 10
    BRIGHTNESS = 0.5
    fade_factor = 0.8

    positions = [randrange(NUM_LEDS) for _ in range(NUM_LEDS_MOVING)]
    directions = [choice([-1, 1]) for _ in range(NUM_LEDS_MOVING)]
    speeds = [uniform(0.05, 0.2) for _ in range(NUM_LEDS_MOVING)]
    brightness_levels = [0] * NUM_LEDS

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            brightness_levels[i] *= fade_factor

        for i in range(NUM_LEDS_MOVING):
            if randrange(100) < 2:
                hue = randrange(0, 360) / 360
                hsv_values[int(positions[i])] = (hue, 1.0, BRIGHTNESS)
            else:
                brightness_levels[int(positions[i])] = BRIGHTNESS

            positions[i] += directions[i] * speeds[i]
            if positions[i] >= NUM_LEDS or positions[i] < 0:
                directions[i] = -directions[i]
                positions[i] = max(0, min(NUM_LEDS - 1, positions[i]))

        for j in range(NUM_LEDS):
            hsv_values[j] = (0.0, 0.0, brightness_levels[j])
            led_strip.set_hsv(j, 0, 0, brightness_levels[j])

        time.sleep(min(speeds))

    return hsv_values


# Effect 72: Glenn's Shooting Stars with Twinkling Starry Night
def effect_72(hsv_values):
    NUM_LEDS_MOVING = 5
    BRIGHTNESS = 0.5
    fade_factor = 0.8

    positions = [randrange(NUM_LEDS) for _ in range(NUM_LEDS_MOVING)]
    directions = [choice([-1, 1]) for _ in range(NUM_LEDS_MOVING)]
    speeds = [uniform(0.05, 0.5) for _ in range(NUM_LEDS_MOVING)]
    color_durations = [0 for _ in range(NUM_LEDS_MOVING)]
    color_hues = [0 for _ in range(NUM_LEDS_MOVING)]
    brightness_levels = [0.0] * NUM_LEDS

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            brightness_levels[i] *= fade_factor

        for i in range(NUM_LEDS_MOVING):
            if color_durations[i] > 0:
                color_durations[i] -= 1
                hsv_values[positions[i]] = (color_hues[i], 1.0, BRIGHTNESS)
            else:
                if randrange(100) < 20:
                    color_hues[i] = randrange(0, 360) / 360.0
                    color_durations[i] = randrange(10, 30)
                    hsv_values[positions[i]] = (color_hues[i], 1.0, BRIGHTNESS)
                else:
                    brightness_levels[positions[i]] = BRIGHTNESS

            positions[i] += directions[i]
            if positions[i] >= NUM_LEDS or positions[i] < 0:
                directions[i] = -directions[i]
                positions[i] += directions[i] * 2

        for j in range(NUM_LEDS):
            if brightness_levels[j] > 0.01:
                hsv_values[j] = (hsv_values[j][0], hsv_values[j][1], brightness_levels[j])
            else:
                hsv_values[j] = (0.0, 0.0, 0.0)

            led_strip.set_hsv(j, hsv_values[j][0], hsv_values[j][1], hsv_values[j][2])

        if randrange(100) < 10:
            speeds = [uniform(0.05, 0.5) for _ in range(NUM_LEDS_MOVING)]

        time.sleep(min(speeds))

    return hsv_values


def effect_73(hsv_values):
    """Cascading ripple effect with fading trails."""
    NUM_RIPPLES = 3  # Number of simultaneous ripples
    TRAIL_LENGTH = 15  # Length of the trailing effect
    FADE_FACTOR = 0.85  # Fading factor for the trails
    hue_range = 0.1  # Restrict hue range to 10%

    # Initialize positions for ripples
    positions = [randrange(NUM_LEDS) for _ in range(NUM_RIPPLES)]
    directions = [choice([-1, 1]) for _ in range(NUM_RIPPLES)]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Dim all LEDs slightly to create fading trails
        for i in range(NUM_LEDS):
            hsv_values[i] = (hsv_values[i][0], hsv_values[i][1], hsv_values[i][2] * FADE_FACTOR)

        # Move and light up ripples
        for r in range(NUM_RIPPLES):
            # Choose a hue for the ripple within the restricted range
            base_hue = 0.8  # Central hue
            hue = base_hue + uniform(-hue_range / 2, hue_range / 2)  # Restrict hue shift

            for t in range(TRAIL_LENGTH):
                index = (positions[r] + t * directions[r]) % NUM_LEDS
                brightness = max(0, 1.0 - (t / TRAIL_LENGTH))
                hsv_values[index] = (hue, 1.0, brightness)

            # Update position of the ripple
            positions[r] += directions[r]
            if positions[r] >= NUM_LEDS or positions[r] < 0:
                directions[r] = -directions[r]  # Reverse direction
                positions[r] += directions[r] * 2  # Ensure we stay within bounds

        # Update the LED strip with the new HSV values
        for j in range(NUM_LEDS):
            led_strip.set_hsv(j, hsv_values[j][0], hsv_values[j][1], hsv_values[j][2])

        time.sleep(0.05)  # Adjust speed of the ripple effect

    return hsv_values



def effect_74(hsv_values):
    """Cascading ripple effect with GRB-corrected colors."""
    NUM_RIPPLES = 3  # Number of simultaneous ripples
    TRAIL_LENGTH = 15  # Length of the trailing effect
    FADE_FACTOR = 0.85  # Fading factor for the trails
    MIN_BRIGHTNESS = 0.05  # Minimum brightness to avoid complete darkness

    # Initialize positions for ripples
    positions = [randrange(NUM_LEDS) for _ in range(NUM_RIPPLES)]
    directions = [choice([-1, 1]) for _ in range(NUM_RIPPLES)]

    # Use GRB-corrected RGB values for white, cyan, and blue
    colors = [
        (0.0, 0.0, 1.0),  # White
        (0.5, 1.0, 1.0),  # Cyan
        (0.6, 1.0, 1.0)   # Blue
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Dim all LEDs slightly to create fading trails
        for i in range(NUM_LEDS):
            hsv_values[i] = (
                hsv_values[i][0],
                hsv_values[i][1],
                max(hsv_values[i][2] * FADE_FACTOR, MIN_BRIGHTNESS)
            )

        # Move and light up ripples
        for r in range(NUM_RIPPLES):
            color = colors[r % len(colors)]  # Cycle through the white, cyan, blue colors
            for t in range(TRAIL_LENGTH):
                index = (positions[r] + t * directions[r]) % NUM_LEDS
                brightness = max(0, 1.0 - (t / TRAIL_LENGTH))
                hsv_values[index] = (color[0], color[1], brightness)

            # Update position of the ripple
            positions[r] += directions[r]
            if positions[r] >= NUM_LEDS or positions[r] < 0:
                directions[r] = -directions[r]  # Reverse direction
                positions[r] += directions[r] * 2  # Ensure we stay within bounds

        # Update the LED strip with the new values
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.05)  # Adjust speed of the ripple effect

    return hsv_values



def effect_75(hsv_values):
    start_time = time.ticks_ms()

    # Main effect loop
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        speed = uniform(0.05, 0.3)  # Random speed for effect transitions
        fade_factor = uniform(0.7, 0.95)  # Determines how colors fade over time
        brightness_variation = uniform(0.4, 1.0)  # Brightness variation factor

        # Randomly choose the number of colors to mix and generate initial hues
        num_colors = choice([2, 3, 4, 5, 6])
        hues = [randrange(360) / 360.0 for _ in range(num_colors)]
        hue_shift = uniform(0.01, 0.05)  # Slow hue shifting speed

        # Animation loop for smooth color transitions
        for t in range(NUM_LEDS * 5):
            if time.ticks_diff(time.ticks_ms(), start_time) > TIMEOUT_DURATION:
                break

            for i in range(NUM_LEDS):
                # Calculate color mixing for each LED
                section = NUM_LEDS // num_colors
                base_hue_index = (i // section) % num_colors
                next_hue_index = (base_hue_index + 1) % num_colors
                ratio = (i % section) / section
                hue = (hues[base_hue_index] * (1 - ratio) + hues[next_hue_index] * ratio + t * hue_shift) % 1.0

                # Calculate brightness and apply fade factor
                brightness = (1 + math.sin(i * 2 * math.pi / NUM_LEDS + t * speed)) / 2 * brightness_variation
                hsv_values[i] = (hue, 1.0, brightness * fade_factor)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(speed)

        # Gradually change hues over time
        hues = [(hue + hue_shift) % 1.0 for hue in hues]

    return hsv_values


def effect_76(hsv_values):
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Ensure all variables are defined before use
        pattern_type = choice([
            'wave', 'sparkle', 'chase', 'pulse', 'subtle_rainbow',
            'breathing', 'meteor_shower', 'rotating_comet', 'falling_stars',
            'larson_scanner', 'color_fade', 'random_flash', 'twinkle', 
            'rotating_bands', 'wave_pulsing', 'waterfall', 'spinning_wheel',
            'color_bounce', 'sparkling_pulse', 'plasma_wave', 'cascading_ripples',
            'expanding_circles', 'glowing_embers', 'flashing_comet', 'waving_rainbow'
        ])
        speed = uniform(0.01, 0.2)
        hue_shift = uniform(0.01, 0.1)
        brightness_variation = uniform(0.5, 1.0)
        fade_factor = uniform(0.8, 0.99)
        direction = choice([-1, 1])

        # Initialize variables that might not be properly set
        num_hues = choice([1, 2, 3, 4, 360])
        hues = sorted([randrange(360) / 360.0 for _ in range(num_hues)])

        for t in range(NUM_LEDS * 10):
            if time.ticks_diff(time.ticks_ms(), start_time) > TIMEOUT_DURATION:
                break

            for i in range(NUM_LEDS):
                # Hue Calculation
                if num_hues == 360:
                    hue = (i / NUM_LEDS + t * speed) % 1.0
                else:
                    index = int(i / NUM_LEDS * (num_hues - 1))
                    next_index = (index + 1) % num_hues
                    ratio = (i / NUM_LEDS * (num_hues - 1)) % 1.0
                    hue = hues[index] * (1 - ratio) + hues[next_index] * ratio

                # Different pattern effects
                if pattern_type == 'wave':
                    brightness = (1 + math.sin(i * 2 * math.pi / NUM_LEDS + t * direction * speed)) / 2 * brightness_variation
                elif pattern_type == 'sparkle':
                    brightness = brightness_variation if randrange(100) < 10 else 0.0
                elif pattern_type == 'waving_rainbow':
                    hue = (i / NUM_LEDS + t * speed) % 1.0
                    brightness = max(0, (1 + math.sin(i * 2 * math.pi / NUM_LEDS + t * speed)) / 2) * brightness_variation
                else:
                    brightness = (1 + math.sin(i * 2 * math.pi / NUM_LEDS + t * direction * speed)) / 2 * brightness_variation

                hsv_values[i] = (hue, 1.0, brightness * fade_factor)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(speed)

        # Occasionally reverse the direction
        if randrange(100) < 5:
            direction = -direction

    return hsv_values



def effect_77(hsv_values):
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        speed = uniform(0.01, 0.2)
        hue_shift = uniform(0.01, 0.1)
        brightness_variation = uniform(0.5, 1.0)
        fade_factor = uniform(0.8, 0.99)
        direction = choice([-1, 1])

        num_hues = choice([1, 2, 3, 4, 360])
        hues = sorted([randrange(360) / 360.0 for _ in range(num_hues)])

        # Randomly choose a mathematical formula for brightness
        pattern_formula = choice([
            lambda i, t: 0.5 + 0.5 * math.sin(i * 2 * math.pi / NUM_LEDS + t * direction * speed),
            lambda i, t: 1.0 if (i + int(t * speed * NUM_LEDS)) % NUM_LEDS < NUM_LEDS // 2 else 0.0,
            lambda i, t: 0.5 + 0.5 * math.sin(i * 2 * math.pi / NUM_LEDS) * (1 + math.sin(t * speed)),
            # (Additional formulas are included here)
            lambda i, t: (1.0 - math.sin(i * 2 * math.pi / NUM_LEDS + t * speed * 0.1)) * 0.5
        ])

        for t in range(NUM_LEDS * 10):
            if time.ticks_diff(time.ticks_ms(), start_time) > TIMEOUT_DURATION:
                break

            for i in range(NUM_LEDS):
                # Hue Calculation
                if num_hues == 360:
                    hue = (i / NUM_LEDS + t * speed) % 1.0
                else:
                    index = int(i / NUM_LEDS * (num_hues - 1))
                    next_index = (index + 1) % num_hues
                    ratio = (i / NUM_LEDS * (num_hues - 1)) % 1.0
                    hue = hues[index] * (1 - ratio) + hues[next_index] * ratio

                # Apply chosen formula for brightness
                brightness = pattern_formula(i, t) * brightness_variation * fade_factor

                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(speed)

        # Occasionally reverse the direction
        direction = -direction if randrange(100) < 5 else direction

    return hsv_values


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


