# ============================================================
# 77 FX SECTION – PASTE YOUR EXISTING CODE HERE
# ============================================================

# IMPORTANT:
# - DO NOT re-define NUM_LEDS or led_strip here (they are already defined above, led_strip).
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

import time
import math
from configuration import *
from random import random, randrange, uniform, choice

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

def set_hsv_env(env_idx: int, h: float, s: float, v: float, led_strip):
    """Set LED using environment coordinates (0 = bottom, NUM_LEDS-1 = top)."""
    phys = env_to_phys(env_idx)
    led_strip.set_hsv(phys, h, s, v)

def set_rgb_env(env_idx: int, r: int, g: int, b: int, led_strip):
    """RGB version using environment coordinates."""
    phys = env_to_phys(env_idx)
    led_strip.set_rgb(phys, r, g, b)

# Individual effect implementations
def effect_1(hsv_values, led_strip):
    """Color-Cycling Pulse effect."""
    for t in range(1000):
        for i in range(NUM_LEDS):
            hue = (i + t) % 360 / 360.0
            brightness = (1 + math.sin(t * 2 * math.pi / 100)) / 2
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
        time.sleep(0.01)
    return hsv_values

def effect_2(hsv_values, led_strip):
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

def effect_3(hsv_values, led_strip):
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
        # Build the whole frame first, then write each LED once. Writing the
        # faded strip and then redrawing the meteors let the background refresh
        # catch the meteors dimmed, which made them flicker.
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            hsv_values[i] = (h, s, v * fade_rate)

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

        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            led_strip.set_hsv(i, h, s, v)

        time.sleep(0.05)
    return hsv_values

def effect_4(hsv_values, led_strip):
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

def effect_5(hsv_values, led_strip):
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

def effect_6(hsv_values, led_strip):
    """Waves of Color effect: three layered waves that drift through each other."""
    wave_length = 20

    # Three waves with different lengths and speeds (one runs backwards), so
    # they interfere into a shifting pattern. (The original three waves were
    # offset by exact whole cycles, so they always lined up as a single wave.)
    base_k = 2 * math.pi * 360 / (NUM_LEDS * wave_length)  # rad per LED (original spacing)
    base_w = 2 * math.pi / wave_length                     # rad per frame (original speed)
    waves = [
        (base_k,        base_w),
        (base_k / 1.7, -base_w * 0.6),
        (base_k / 0.75, base_w * 0.35),
    ]
    wave_count = len(waves)

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(360):
            for i in range(NUM_LEDS):
                brightness = 0
                for k, w in waves:
                    brightness += (1 + math.sin(k * i + w * t)) / 2
                brightness /= wave_count
                # Averaging three waves flattens them; stretch the contrast
                # so peaks stand out and the gaps go dark.
                brightness = brightness * brightness * (3 - 2 * brightness)

                hue = (t + i) % 360 / 360.0
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(0.05)
    return hsv_values

def effect_7(hsv_values, led_strip):
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

def effect_8(hsv_values, led_strip):
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

def effect_9(hsv_values, led_strip):
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
            set_hsv_env(i, h, s, v, led_strip)

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
                    set_hsv_env(prev, 0.0, 0.0, 0.0, led_strip)

                # Draw current rocket position
                hsv_values[launch_pos] = (firework_hue, 1.0, 1.0)
                set_hsv_env(launch_pos, firework_hue, 1.0, 1.0, led_strip)

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
                        set_hsv_env(idx, hue, 1.0, b, led_strip)

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


def effect_10(hsv_values, led_strip):
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
        # (total_weight doubles as the summed brightness of all blobs).
        # Hues are blended as points on the colour wheel (x, y), so two hues
        # mix the short way round: red + purple gives red-purple, not green.
        blended_x = [0.0] * NUM_LEDS
        blended_y = [0.0] * NUM_LEDS
        total_weight = [0.0] * NUM_LEDS

        # Fade previous frame (in memory only: the whole frame is written once
        # at the end, so the background refresh never shows the blobs dimmed)
        for env_i in range(NUM_LEDS):
            h, s, v = hsv_values[env_i]
            hsv_values[env_i] = (h, s, v * fade_factor)

        # Update blobs
        for blob in blobs:
            hue_angle = blob["hue"] * 2 * math.pi
            hue_x = math.cos(hue_angle)
            hue_y = math.sin(hue_angle)
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

                    blended_x[env_pos] += hue_x * brightness
                    blended_y[env_pos] += hue_y * brightness
                    total_weight[env_pos] += brightness

        # Apply blended output
        for env_i in range(NUM_LEDS):
            if total_weight[env_i] > 0:
                final_hue = (math.atan2(blended_y[env_i], blended_x[env_i]) / (2 * math.pi)) % 1.0
                # Summed blob brightness, capped: soft edges, brighter overlaps.
                # (Dividing by total_weight, as before, always gave 1.0.)
                final_brightness = min(1.0, total_weight[env_i])

                hsv_values[env_i] = (final_hue, 1.0, final_brightness)

        # Write the finished frame, each LED once
        for env_i in range(NUM_LEDS):
            h, s, v = hsv_values[env_i]
            set_hsv_env(env_i, h, s, v, led_strip)

        time.sleep(step_time)

    return hsv_values




def effect_11(hsv_values, led_strip):
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
        # Build the frame in memory, then write each LED once (writing the
        # dimmed strip first let the background refresh catch stars dipping)
        for i in range(NUM_LEDS):
            hsv_values[i] = (
                hsv_values[i][0], 
                hsv_values[i][1], 
                hsv_values[i][2] * 0.95
            )

        for star in stars:
            star["brightness"] += star["direction"] * twinkle_speed

            if star["brightness"] >= max_brightness:
                star["direction"] = -1
            elif star["brightness"] <= min_brightness:
                star["direction"] = 1

            pos = star["position"]
            hsv_values[pos] = (star["hue"], 1.0, star["brightness"])

        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            led_strip.set_hsv(i, h, s, v)

        time.sleep(0.05)
    return hsv_values

def effect_12(hsv_values, led_strip):
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
    frame_delay = 0.05          # used by the dispersal slide
    fall_frame_delay = 0.02
    # Falling speed scales with strip length: a block drops the full height
    # of the strip in about FALL_SECONDS whatever NUM_LEDS is.
    FALL_SECONDS = 1.5
    fall_speed = NUM_LEDS / FALL_SECONDS     # LEDs per second

    # Ground is env index 0
    stacked_height = -1              # highest occupied env index in the stack
    blocks = []                      # list of landed blocks
    stack_pixels = [(0, 0, 0)] * NUM_LEDS  # current stacked RGB in env space

    # Clear LEDs
    for i in range(NUM_LEDS):
        hsv_values[i] = (0.0, 0.0, 0.0)
        set_rgb_env(i, 0, 0, 0, led_strip)

    # -----------------------------
    # STACKING PHASE
    # -----------------------------
    # Full-run effect: always stacks to the top before dispersing
    # (main.py lists 12 in FULL_RUN_EFFECTS, so no time limit here).
    while True:
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

        # Fall loop: move block down towards env 0, by elapsed time so the
        # speed doesn't depend on how long each frame takes to draw
        start_bottom = bottom_env
        landing = stacked_height + 1
        fall_start = time.ticks_ms()
        while True:
            # FULL FRAME RENDER (no flashing):
            # For each env pixel, show either stacked block color or falling block.
            for i in range(NUM_LEDS):
                r, g, b = stack_pixels[i]
                if bottom_env <= i <= top_env:
                    r, g, b = block["rgb"]
                set_rgb_env(i, r, g, b, led_strip)

            if bottom_env <= landing:
                break

            time.sleep(fall_frame_delay)

            # Move closer to ground
            fallen = int(fall_speed * time.ticks_diff(time.ticks_ms(), fall_start) / 1000)
            bottom_env = max(landing, start_bottom - fallen)
            top_env = bottom_env + block_length - 1

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
                set_rgb_env(j, *block["rgb"], led_strip)

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
    hsv_values = disperse_blocks(blocks, frame_delay, hsv_values, led_strip)

    return hsv_values


def disperse_blocks(blocks, frame_delay, hsv_values, led_strip):
    """
    Disperse blocks by sliding them towards env index 0 (ground), then off-strip.
    Orientation is handled by set_rgb_env -> env_to_phys().

    The slide is timed: the stack moves the full strip length in about
    DISPERSE_SECONDS, whatever NUM_LEDS is.
    """
    DISPERSE_SECONDS = 2.5
    speed = NUM_LEDS / DISPERSE_SECONDS      # LEDs per second
    top = max(block["end"] for block in blocks) if blocks else -1
    slide_start = time.ticks_ms()

    while True:
        offset = int(speed * time.ticks_diff(time.ticks_ms(), slide_start) / 1000)

        # FULL FRAME RENDER: rebuild stack_pixels from the shifted blocks
        stack_pixels = [(0, 0, 0)] * NUM_LEDS
        for block in blocks:
            for j in range(block["start"] - offset, block["end"] - offset + 1):
                if 0 <= j < NUM_LEDS:
                    stack_pixels[j] = block["color"]

        for i in range(NUM_LEDS):
            r, g, b = stack_pixels[i]
            set_rgb_env(i, r, g, b, led_strip)

        if top - offset < 0:      # everything has slid off the strip
            break

        time.sleep(frame_delay / 2)

    return hsv_values



def effect_13(hsv_values, led_strip):
    """Torrential rain with fast-moving blue raindrops, orientation-aware.

    Env space:
      - env index 0         = ground
      - env index NUM_LEDS-1 = sky

    Rain always falls from sky (top) down towards ground (bottom) in env space.
    ORIENTATION mapping (via set_rgb_env) flips the physical direction as needed.

    Speed, drop count and streak length scale with NUM_LEDS, so it looks the
    same on any strip. Drops splash when they reach the ground.
    """

    # Scaled to strip length
    num_drops = max(6, NUM_LEDS // 8)           # at most 12 drops on 100 LEDs
    spawn_chance = 0.25                         # per frame: lower = sparser rain
    trail_length = max(4, NUM_LEDS // 16)       # 6-LED streaks on 100 LEDs
    # A drop falls the full strip in FALL_MIN_S..FALL_MAX_S seconds
    FALL_MIN_S = 1.0
    FALL_MAX_S = 2.0

    drop_color = (0, 0, 255)          # Blue in RGB
    splash_color = (140, 140, 255)    # pale blue-white flash
    splash_size = 3                   # LEDs lit at the ground by a splash
    frame_delay = 0.01
    drops = []

    # led_state is stored in ENV coordinates
    led_state = [(0, 0, 0) for _ in range(NUM_LEDS)]

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        # Spawn new drops near the "sky" (upper half -> top)
        if len(drops) < num_drops and uniform(0, 1) < spawn_chance:
            start_pos = randrange(NUM_LEDS // 2, NUM_LEDS)  # upper half of env strip
            drops.append({
                "position": float(start_pos),
                "speed": NUM_LEDS / uniform(FALL_MIN_S, FALL_MAX_S),  # LEDs per second
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
        landed = 0
        for drop in drops:
            drop_pos = drop["position"]

            # Draw head + streak above it (towards the sky / higher env index)
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
            new_pos = drop_pos - drop["speed"] * dt
            if drop_pos >= 0 > new_pos:
                landed += 1
            drop["position"] = new_pos

        # Splash: drops that reached the ground this frame flash the bottom LEDs
        if landed:
            for i in range(min(splash_size, NUM_LEDS)):
                k = 1.0 - i / splash_size
                sr = int(splash_color[0] * k)
                sg = int(splash_color[1] * k)
                sb = int(splash_color[2] * k)
                cur_r, cur_g, cur_b = led_state[i]
                led_state[i] = (max(cur_r, sr), max(cur_g, sg), max(cur_b, sb))

        # Remove drops that are completely off the bottom
        drops = [drop for drop in drops if drop["position"] > -trail_length]

        # Push env-state to physical LEDs
        for i in range(NUM_LEDS):
            r, g, b = led_state[i]
            set_rgb_env(i, r, g, b, led_strip)

        time.sleep(frame_delay)

    return hsv_values


def effect_14(hsv_values, led_strip):
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

def effect_15(hsv_values, led_strip):
    """Natural flame effect: deep red at the base, transitioning to orange, then to yellow.
    
    Orientation-aware via env_to_phys():
      - Env index 0           = flame base / ground
      - Env index NUM_LEDS-1  = top of the flame
    
    ORIENTATION = "BOTTOM":
        2350W at bottom; base is physically near the 2350W.
    ORIENTATION = "TOP":
        2350W at top; base is physically near the 2350W, with strip going down.
    """
    # Flame height, ferocity and speed are tuned to look the same on any
    # strip length: the flame burns roughly 55-60% of the way up, with
    # flickering tips reaching ~70%. (Higher cool_max = shorter flame,
    # higher sparking = fiercer.)
    rise_steps = max(1, round(NUM_LEDS / 50))   # heat climbs this many LEDs per frame
    cool_max = 20 if NUM_LEDS <= 120 else 16    # max cooling per LED per frame
    sparking = 130                              # chance (/255) of each spark per frame
    sparks_per_frame = 2
    spark_zone = max(7, NUM_LEDS // 12)         # sparks ignite in the bottom LEDs
    speed_delay = 0.02
    heat = [0] * NUM_LEDS  # Heat array in ENV coordinates (0 = base)

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Step 1: Cool down each "cell" a little
        for i in range(NUM_LEDS):
            heat[i] = max(0, heat[i] - randrange(0, cool_max + 1))

        # Step 2: Heat drifts upward and diffuses (towards higher env indices).
        # Stops at index 2 so it never reads below the base (negative indices
        # used to wrap round and pull heat from the top of the strip).
        for _ in range(rise_steps):
            for k in range(NUM_LEDS - 1, 1, -1):
                heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) // 3

        # Step 3: Randomly ignite new sparks near the base (env index 0)
        for _ in range(sparks_per_frame):
            if randrange(255) < sparking:
                y = randrange(0, spark_zone)
                heat[y] = min(255, heat[y] + randrange(160, 255))

        # Step 4: Map heat to a smooth colour ramp and write, orientation-aware:
        # black -> deep red -> orange (most of the flame) -> yellow only at
        # the very hottest spots
        for env_i in range(NUM_LEDS):
            t = heat[env_i] * 191 // 255       # 0..191
            if t > 160:
                r, g = 255, 140 + (t - 160) * 115 // 31   # orange -> yellow
            elif t > 64:
                r, g = 255, (t - 64) * 140 // 96          # red -> orange
            else:
                r, g = t * 4, 0                           # black -> red
            b = 0

            # The effects swap R and G for this strip setup (see main.py)
            phys = env_to_phys(env_i)
            led_strip.set_rgb(phys, g, r, b)

        time.sleep(speed_delay)

    return hsv_values




def effect_16(hsv_values, led_strip):
    """Simulates a lava drip effect on a GRB/BGR strip, always falling from ENV top to ENV bottom.
    
    With the env/orientation system:
      - ORIENTATION = "BOTTOM": controller at ENV 0 → lava falls TOWARDS the 2350W.
      - ORIENTATION = "TOP":    controller at ENV NUM_LEDS-1 → lava falls AWAY from the 2350W.
    """

    drip_length = max(5, NUM_LEDS // 20)   # head + tail, scaled with strip length
    frame_delay = 0.02
    FALL_SECONDS = 1.8     # time for a drip to fall the full strip, any length
    # Constant acceleration (gravity) so the drop covers NUM_LEDS in FALL_SECONDS
    gravity = 2.0 * NUM_LEDS / (FALL_SECONDS * FALL_SECONDS)   # LEDs / s^2
    max_brightness = 0.9
    min_brightness = 0.2

    # This is the "real" lava hue you want (red-orange)
    BASE_HUE = 0.00      # 0.0 = red, ~0.05 = orange-red
    SATURATION = 1.0

    # Extra hue offset to cancel your strip's green bias.
    # This is the same trick as we used on effect_32.
    HUE_OFFSET = 0.33    # ~120° shift

    # Drip colour per tail position (fixed, so work it out once)
    display_hue = (BASE_HUE + HUE_OFFSET) % 1.0
    tail_rgb = []
    for i in range(drip_length):
        brightness = max_brightness - ((i / drip_length) * (max_brightness - min_brightness))
        r, g, b = hsv_to_rgb(display_hue, SATURATION, brightness)
        tail_rgb.append((int(r * 255), int(g * 255), int(b * 255)))

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # In ENV space, always start at the logical TOP and fall towards logical BOTTOM.
        # Falls under gravity: starts slowly and speeds up.
        drop_start = time.ticks_ms()
        top = NUM_LEDS - 1

        while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
            t = time.ticks_diff(time.ticks_ms(), drop_start) / 1000.0
            position = int(top - 0.5 * gravity * t * t)   # head, ENV index

            # Build the whole frame, then write each LED once (clearing the strip
            # first and drawing the drip after it made the drip flicker)
            frame = [(0, 0, 0)] * NUM_LEDS
            for i in range(drip_length):
                env_pos = position + i        # tail trails ABOVE the falling head
                if 0 <= env_pos < NUM_LEDS:
                    frame[env_pos] = tail_rgb[i]
            for env_i in range(NUM_LEDS):
                r, g, b = frame[env_i]
                set_rgb_env(env_i, r, g, b, led_strip)

            if position + drip_length <= 0:   # whole drip has left the strip
                break
            time.sleep(frame_delay)

        time.sleep(0.5)

    return hsv_values


def effect_17(hsv_values, led_strip):
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


def effect_18(hsv_values, led_strip):
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

def effect_19(hsv_values, led_strip):
    """Night Sky with Twinkling Stars: a deep blue sky with white and warm
    yellow stars that fade gently in and out."""
    # Deep blue sky, kept just above the point where the firmware's gamma
    # curve stops lighting it (0.1 left the sky black at the default brightness).
    background_hue = 0.66  # Hue for blue (240 degrees on color wheel)
    background_saturation = 1.0
    background_value = 0.14

    # Star colours. The effects swap red and green for this strip setup, so
    # warm yellow is hue ~0.23 here rather than 0.15.
    WHITE = (0.0, 0.0)          # (hue, saturation)
    WARM_YELLOW = (0.23, 0.55)

    star_twinkle_probability = 0.03  # chance per frame that a resting star starts a twinkle
    twinkle_frames = 30              # length of a slow fade in + out (~1.5-2 s)
    quick_twinkle_chance = 0.35      # share of twinkles that are quick glints instead
    quick_frames_min = 6             # quick glint: ~0.3-0.7 s
    quick_frames_max = 12

    # Initialize the star states
    stars = []
    for _ in range(NUM_LEDS // 10):  # Number of stars as a fraction of total LEDs
        hue, sat = WHITE if randrange(2) == 0 else WARM_YELLOW
        stars.append({
            "position": randrange(NUM_LEDS),
            "hue": hue,
            "saturation": sat,
            "peak": uniform(0.6, 1.0),   # how bright this star gets
            "frame": 0,                  # 0 = resting, else frames into the twinkle
            "length": twinkle_frames,    # frames in the current twinkle
        })

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Set the background
        for i in range(NUM_LEDS):
            hsv_values[i] = (background_hue, background_saturation, background_value)

        # Handle star twinkling: a smooth sine fade up and back down
        for star in stars:
            if star["frame"] == 0 and uniform(0, 1) < star_twinkle_probability:
                star["frame"] = 1
                if uniform(0, 1) < quick_twinkle_chance:
                    star["length"] = randrange(quick_frames_min, quick_frames_max + 1)
                else:
                    star["length"] = twinkle_frames

            if star["frame"] > 0:
                k = star["frame"] / star["length"]
                brightness = star["peak"] * math.sin(math.pi * k)
                if brightness > background_value:     # stay on top of the sky
                    hsv_values[star["position"]] = (star["hue"], star["saturation"], brightness)
                star["frame"] += 1
                if star["frame"] >= star["length"]:
                    star["frame"] = 0

        # Update the LED strip
        for i in range(NUM_LEDS):
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.05)  # Small delay for animation smoothness

    return hsv_values

def effect_20(hsv_values, led_strip):
    """Temporal Wave Collisions: Interference patterns from waves traveling in opposite directions."""
    wave_count = 5
    amplitude = 0.6                       # overlapping waves add up and glow brighter
    wave_width = max(4, NUM_LEDS // 8)    # half-width of each wave in LEDs

    # Each wave gets its own start, speed and direction. (They all used to
    # start at 0 with the same speed, so they moved as one wave, and each one
    # spanned the whole strip, which lit every LED at full brightness.)
    waves = [
        {
            "position": uniform(0, NUM_LEDS - 1),
            "speed": uniform(0.1, 0.4),
            "direction": choice([-1, 1]),
        }
        for _ in range(wave_count)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for wave in waves:
            wave["position"] += wave["speed"] * wave["direction"]
            if wave["position"] >= NUM_LEDS - 1 or wave["position"] <= 0:
                wave["direction"] *= -1
                wave["position"] = max(0, min(NUM_LEDS - 1, wave["position"]))

        for i in range(NUM_LEDS):
            brightness = sum(
                amplitude * max(0, 1 - abs(i - wave["position"]) / wave_width) for wave in waves
            )
            hue = (i % 360) / 360.0
            hsv_values[i] = (hue, 1.0, min(brightness, 1.0))
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.01)

    return hsv_values

def effect_21(hsv_values, led_strip):
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



def effect_22(hsv_values, led_strip):
    """Glowing Embers: a slow deep-red breathing glow with ember spots that
    flare up orange-red and slowly fade, like the bed of a dying fire."""
    # Hues for this strip setup (the effects swap red and green, so red is
    # 0.33 here and warmer orange-reds sit just below it)
    HUE_RED = 0.33
    HUE_EMBER = 0.27            # orange-red at the hottest point of a flare

    # Base glow: a slow breath (~4 s) that rolls gently along the strip
    base_level = 0.28
    base_swing = 0.08           # base glows between 0.20 and 0.36
    breath_speed = 1.6          # rad/s
    roll = 0.15                 # phase shift per LED, so the breath rolls

    # Embers
    ember_rate = NUM_LEDS / 20.0  # new embers per second, scaled to the strip (5/s on 100, ~7 glowing at once)
    embers = []

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        # Spawn embers (on average ember_rate per second)
        expected = ember_rate * dt
        while expected > 0:
            if uniform(0, 1) < expected:
                embers.append({
                    "pos": randrange(NUM_LEDS),
                    "width": randrange(1, 4),          # 1-3 LEDs each side
                    "born": elapsed,
                    "rise": uniform(0.15, 0.35),       # quick flare up
                    "fall": uniform(0.8, 2.2),         # slow fade
                    "peak": uniform(0.6, 1.0),
                })
            expected -= 1

        # Ember heat per LED (0..1), strongest ember wins
        heat = [0.0] * NUM_LEDS
        alive = []
        for e in embers:
            age = elapsed - e["born"]
            if age < e["rise"]:
                env = age / e["rise"]
            else:
                k = (age - e["rise"]) / e["fall"]
                if k >= 1.0:
                    continue                           # fully faded
                env = (1.0 - k) * (1.0 - k)
            alive.append(e)
            strength = env * e["peak"]
            w = e["width"]
            for j in range(-w, w + 1):
                i = e["pos"] + j
                if 0 <= i < NUM_LEDS:
                    v = strength * (1.0 - abs(j) / (w + 1))
                    if v > heat[i]:
                        heat[i] = v
        embers = alive

        # Build the frame and write each LED once
        for i in range(NUM_LEDS):
            base = base_level + base_swing * math.sin(elapsed * breath_speed + i * roll)
            h = heat[i]
            v = base + (1.0 - base) * h
            hue = HUE_RED + (HUE_EMBER - HUE_RED) * h
            hsv_values[i] = (hue, 1.0, v)
            led_strip.set_hsv(i, hue, 1.0, v)

        time.sleep(0.02)

    return hsv_values


def effect_23(hsv_values, led_strip):
    """Smooth bouncing lights without tails: each light glides between LEDs,
    and lights that cross blend their colours."""
    num_bouncing_leds = 5  # Number of bouncing lights
    lights = []
    for _ in range(num_bouncing_leds):
        hue = randrange(360) / 360.0
        r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
        lights.append({
            "pos": uniform(0, NUM_LEDS - 1),
            "speed": uniform(2.0, 6.0),          # LEDs per second
            "dir": choice([-1, 1]),
            "hue": hue,
            "rgb": (r, g, b),
        })

    # Gliding: a light sits on one LED for most of its travel and hands over to
    # the next LED in a short soft cross-fade, so it still reads as a single dot.
    # HANDOFF = share of the way between LEDs spent cross-fading
    #   (0 = old step-by-step jumps, 1 = fully smooth but looks like two dots).
    HANDOFF = 0.4
    # The firmware's gamma curve dims a light shared between two LEDs; raising
    # the weights to this power partly makes up for it (1.0 = no boost).
    GLIDE_POWER = 0.6

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        frame_r = [0.0] * NUM_LEDS
        frame_g = [0.0] * NUM_LEDS
        frame_b = [0.0] * NUM_LEDS
        top_w = [0.0] * NUM_LEDS     # strongest light on each LED, for hsv_values
        top_hue = [0.0] * NUM_LEDS

        for L in lights:
            # Move, bouncing off the ends
            L["pos"] += L["speed"] * L["dir"] * dt
            if L["pos"] >= NUM_LEDS - 1:
                L["pos"] = 2 * (NUM_LEDS - 1) - L["pos"]
                L["dir"] = -1
            elif L["pos"] <= 0:
                L["pos"] = -L["pos"]
                L["dir"] = 1
            L["pos"] = max(0.0, min(NUM_LEDS - 1.0, L["pos"]))

            # Split the light between the two LEDs it sits between
            i0 = int(L["pos"])
            frac = L["pos"] - i0
            # squeeze the cross-fade into the middle HANDOFF part of the gap
            frac = (frac - (1.0 - HANDOFF) / 2) / HANDOFF
            frac = max(0.0, min(1.0, frac))
            frac = frac * frac * (3 - 2 * frac)     # smooth start and end
            r, g, b = L["rgb"]
            for idx, w in ((i0, 1.0 - frac), (i0 + 1, frac)):
                if 0 <= idx < NUM_LEDS and w > 0:
                    w = w ** GLIDE_POWER
                    # Additive: crossing lights mix their colours
                    frame_r[idx] += r * w
                    frame_g[idx] += g * w
                    frame_b[idx] += b * w
                    if w > top_w[idx]:
                        top_w[idx] = w
                        top_hue[idx] = L["hue"]

        # Write the finished frame, each LED once
        for i in range(NUM_LEDS):
            r = min(1.0, frame_r[i])
            g = min(1.0, frame_g[i])
            b = min(1.0, frame_b[i])
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))
            hsv_values[i] = (top_hue[i], 1.0, max(r, g, b))

        time.sleep(0.02)

    return hsv_values



def effect_24(hsv_values, led_strip):
    """Aurora Borealis: Simulates the dancing lights of the Northern Lights with smooth undulations."""
    wave_speed = 1.5            # radians per second (was 0.1 per ms: ~5 rad per frame, looked like flicker)
    color_shift_speed = 0.01
    amplitude = 0.4
    base_hue = 0.5

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Seconds since the effect started, not since boot (32-bit floats)
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        for i in range(NUM_LEDS):
            hue_variation = math.sin(i * amplitude + t * wave_speed) * 0.1
            hue = (base_hue + hue_variation) % 1.0
            brightness = (1 + math.sin(i * amplitude - t * wave_speed)) / 2
            hsv_values[i] = (hue, 0.8, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        base_hue += color_shift_speed
        time.sleep(0.05)

    return hsv_values


def effect_25(hsv_values, led_strip):
    """Hypernova Shockwave: bursts flash at random points and send bright rings
    racing outwards in both directions, fading as they spread. Each burst has
    its own colour, and rings mix where they cross."""
    max_bursts = 4
    burst_gap_min = 0.4          # seconds between bursts
    burst_gap_max = 1.4
    ring_width = max(2, NUM_LEDS // 30)    # glow behind the ring front, in LEDs
    core_time = 0.25             # seconds the centre flash lasts

    bursts = []
    start_time = time.ticks_ms()
    next_burst = 0.0

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0

        # Start a new burst at random intervals
        if t >= next_burst and len(bursts) < max_bursts:
            hue = uniform(0, 1.0)
            bursts.append({
                "center": randrange(NUM_LEDS),
                "born": t,
                "speed": NUM_LEDS / uniform(0.8, 1.4),   # crosses the strip in ~1 s
                "rgb": hsv_to_rgb(hue, 1.0, 1.0),
                "hue": hue,
            })
            next_burst = t + uniform(burst_gap_min, burst_gap_max)

        frame_r = [0.0] * NUM_LEDS
        frame_g = [0.0] * NUM_LEDS
        frame_b = [0.0] * NUM_LEDS
        top_v = [0.0] * NUM_LEDS
        top_hue = [0.0] * NUM_LEDS

        alive = []
        for burst in bursts:
            age = t - burst["born"]
            radius = age * burst["speed"]
            if radius > NUM_LEDS + 3 * ring_width:
                continue                       # gone off both ends
            alive.append(burst)

            fade = max(0.0, 1.0 - radius / NUM_LEDS)
            fade = fade ** 1.5                 # rings dim as they spread
            core = max(0.0, 1.0 - age / core_time)
            c = burst["center"]
            r, g, b = burst["rgb"]

            lo = max(0, int(c - radius - 2))
            hi = min(NUM_LEDS - 1, int(c + radius + 2))
            for i in range(lo, hi + 1):
                x = radius - abs(i - c)        # >0: inside the ring, <0: ahead of it
                if x < 0:
                    v = max(0.0, 1.0 + x)      # soft 1-LED leading edge
                else:
                    v = max(0.0, 1.0 - x / (3.0 * ring_width))   # glow behind
                v *= fade
                if core > 0 and abs(i - c) <= 2:
                    v = max(v, core)           # the initial flash
                if v <= 0:
                    continue
                frame_r[i] += r * v
                frame_g[i] += g * v
                frame_b[i] += b * v
                if v > top_v[i]:
                    top_v[i] = v
                    top_hue[i] = burst["hue"]
        bursts = alive

        # Write the finished frame, each LED once
        for i in range(NUM_LEDS):
            r = min(1.0, frame_r[i])
            g = min(1.0, frame_g[i])
            b = min(1.0, frame_b[i])
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))
            hsv_values[i] = (top_hue[i], 1.0, max(r, g, b))

        time.sleep(0.01)

    return hsv_values



def effect_26(hsv_values, led_strip):
    """Ethereal Vortex: A swirling vortex effect, with colors spiraling inwards and outwards."""
    vortex_speed = 1.2          # radians per second (was 50 per ms: random every frame)
    hue_variation = 0.3
    spiral_tightness = 0.05

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Seconds since the effect started, not since boot: on the board's
        # 32-bit floats the uptime-based angle collapsed to one colour.
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        for i in range(NUM_LEDS):
            angle = (i * spiral_tightness + t * vortex_speed) % (2 * math.pi)
            hue = (0.5 + math.sin(angle) * hue_variation) % 1.0
            brightness = (1 + math.cos(angle)) / 2
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        time.sleep(0.03)   # was 0.6 s: too slow a frame rate for a smooth swirl

    return hsv_values


def effect_27(hsv_values, led_strip):
    """Cosmic Dust Storm: specks of dust swirl back and forth over a dim blue
    sky, flaring up now and then and fading."""
    num_particles = max(10, NUM_LEDS // 3)     # scaled so dark gaps show
    burst_rate = 0.8          # flare-ups per particle per second
    decay_per_s = 0.08        # brightness kept after 1 s (fast fade after a flare)

    # Dim blue sky, just above where the firmware's gamma curve stops lighting
    # it (0.1 left it black).
    BG = (0.6, 0.7, 0.14)
    DUST_HUE, DUST_SAT = 0.7, 0.8

    dust = []
    for _ in range(num_particles):
        dust.append({
            "pos": uniform(0, NUM_LEDS),
            "drift": uniform(-2.0, 2.0),          # LEDs/s steady drift
            "swirl": uniform(2.0, 6.0),           # LEDs/s back-and-forth swing
            "freq": uniform(0.5, 1.5),            # rad/s of the swing
            "phase": uniform(0, 2 * math.pi),
            "v": uniform(0.2, 1.0),
        })

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now
        keep = decay_per_s ** dt

        # Background, then dust on top: all in memory first
        for i in range(NUM_LEDS):
            hsv_values[i] = BG

        for p in dust:
            speed = p["drift"] + p["swirl"] * math.sin(t * p["freq"] + p["phase"])
            p["pos"] = (p["pos"] + speed * dt) % NUM_LEDS
            if uniform(0, 1) < burst_rate * dt:
                p["v"] = uniform(0.5, 1.0)
            else:
                p["v"] *= keep
            idx = int(p["pos"]) % NUM_LEDS
            if p["v"] > hsv_values[idx][2]:
                hsv_values[idx] = (DUST_HUE, DUST_SAT, p["v"])

        # Write the finished frame, each LED once (no flicker)
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            led_strip.set_hsv(i, h, s, v)

        time.sleep(0.02)

    return hsv_values

def effect_28(hsv_values, led_strip):

    # Pac-Man (1D LED strip)
    # -----------------------------
    # TUNING / CONSTANTS
    # -----------------------------
    FRAME_DELAY = 0.08

    # Colours: the effects swap red and green for this strip setup, so hues
    # are chosen for what the strip actually shows (red = 0.33 here).
    DOT_HUE = 0.1667   # yellow
    DOT_BRIGHT = 0.20

    PILL_HUE = 0.0
    PILL_SAT = 0.0
    PILL_BRIGHT = 1.0

    PAC_HUE = 0.1667   # yellow
    PAC_BRIGHT = 1.0

    GHOST_BRIGHT = 1.0
    GHOST_SCARED_HUE = 0.6667  # blue

    SCARED_DURATION_MS = 5000

    NUM_GHOSTS = 3
    NUM_PILLS = 4              # energizers
    RESPAWN_DELAY_MS = 900      # “death pause” before respawn

    # NEW: Arcade-like “READY” grace window after respawn
    RESPAWN_GRACE_MS = 1500     # invulnerable after respawn

    # Optional: anti-spawn-camping behaviour
    ENABLE_SPAWN_CLEAR = True
    SPAWN_CLEAR_RADIUS = 4

    # Ghost colours as shown on the strip: red, pink, cyan (arcade style;
    # orange left out as it's too close to Pac-Man's yellow on LEDs)
    GHOST_HUES = [0.333, 0.4167, 0.8333]

    # -----------------------------
    # HELPERS
    # -----------------------------
    def wrap(i: int) -> int:
        return i % NUM_LEDS

    def reseed_level(level: int):
        # Fresh dots everywhere
        dots = [True] * NUM_LEDS

        # Energizer pills
        pill_positions = set()
        while len(pill_positions) < min(NUM_PILLS, NUM_LEDS):
            pill_positions.add(randrange(NUM_LEDS))

        # Ensure Pac-Man spawn isn't immediately a pill
        pac_spawn = NUM_LEDS // 2
        if pac_spawn in pill_positions:
            pill_positions.remove(pac_spawn)

        return dots, sorted(list(pill_positions))

    def fade_in_level(dots, pill_positions, duration_ms=700, steps=30):
        """Fade in dots + pills from black without flashing."""
        for i in range(NUM_LEDS):
            hsv_values[i] = (0.0, 0.0, 0.0)
            led_strip.set_hsv(i, 0.0, 0.0, 0.0)

        step_delay = max(1, duration_ms // steps)

        for step in range(steps + 1):
            k = step / float(steps)

            for i in range(NUM_LEDS):
                if dots[i]:
                    hsv_values[i] = (DOT_HUE, 1.0, DOT_BRIGHT * k)
                else:
                    hsv_values[i] = (0.0, 0.0, 0.0)

            for p in pill_positions:
                hsv_values[p] = (PILL_HUE, PILL_SAT, PILL_BRIGHT * k)

            for i in range(NUM_LEDS):
                h, s, v = hsv_values[i]
                led_strip.set_hsv(i, h, s, v)

            time.sleep_ms(step_delay)

    def spawn_ghosts(pac_pos):
        """Spawn ghosts away from Pac-Man."""
        ghosts = []
        for gi in range(NUM_GHOSTS):
            while True:
                pos = randrange(NUM_LEDS)
                if abs(pos - pac_pos) > max(3, NUM_LEDS // 6):
                    ghosts.append(pos)
                    break
        return ghosts

    def move_towards(src, dst):
        """1D shortest-step towards target on a ring. Returns +1 or -1."""
        cw = (dst - src) % NUM_LEDS
        ccw = (src - dst) % NUM_LEDS
        if cw == ccw:
            return 1 if randrange(2) == 0 else -1
        return 1 if cw < ccw else -1

    def draw_frame(dots, pill_positions, pac_pos, ghosts, scared):
        # Base: dots (dim) or black
        for i in range(NUM_LEDS):
            if dots[i]:
                hsv_values[i] = (DOT_HUE, 1.0, DOT_BRIGHT)
            else:
                hsv_values[i] = (0.0, 0.0, 0.0)

        # Pills on top
        for p in pill_positions:
            hsv_values[p] = (PILL_HUE, PILL_SAT, PILL_BRIGHT)

        # Ghosts
        for gi, gp in enumerate(ghosts):
            if scared:
                hsv_values[gp] = (GHOST_SCARED_HUE, 1.0, GHOST_BRIGHT)
            else:
                hsv_values[gp] = (GHOST_HUES[gi % len(GHOST_HUES)], 1.0, GHOST_BRIGHT)

        # Pac-Man on top
        hsv_values[pac_pos] = (PAC_HUE, 1.0, PAC_BRIGHT)

        # Push to strip
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            led_strip.set_hsv(i, h, s, v)

    # -----------------------------
    # GAME STATE
    # -----------------------------
    level = 1
    dots, pill_positions = reseed_level(level)

    pacman_pos = NUM_LEDS // 2
    pac_dir = 1  # constant direction (no surprise flips)

    ghosts = spawn_ghosts(pacman_pos)

    scared = False
    scared_until = 0

    pac_alive = True

    # NEW: respawn invulnerability timer
    respawn_until_ms = 0

    # Fade-in initial level
    fade_in_level(dots, pill_positions)

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:

        now = time.ticks_ms()

        # “Safe” means we are within the respawn grace window
        safe = time.ticks_diff(respawn_until_ms, now) > 0

        # End scared mode if timer elapsed
        if scared and time.ticks_diff(now, scared_until) >= 0:
            scared = False

        # -----------------------------
        # MOVE PAC-MAN (wrap at ends)
        # -----------------------------
        pac_prev = pacman_pos
        ghost_prev = list(ghosts)

        if pac_alive:
            pacman_pos = wrap(pacman_pos + pac_dir)

            # Eat pill? (energizer)
            if pacman_pos in pill_positions:
                pill_positions.remove(pacman_pos)
                scared = True
                scared_until = time.ticks_add(now, SCARED_DURATION_MS)

            # Eat dot
            if dots[pacman_pos]:
                dots[pacman_pos] = False

        # -----------------------------
        # MOVE GHOSTS
        # -----------------------------
        for gi in range(len(ghosts)):
            gpos = ghosts[gi]

            if scared:
                # Run away
                step = -move_towards(gpos, pacman_pos)
            else:
                # Chase
                step = move_towards(gpos, pacman_pos)

            # Small randomness
            if randrange(100) < 15:
                step = 1 if randrange(2) == 0 else -1

            ghosts[gi] = wrap(gpos + step)

        # -----------------------------
        # COLLISIONS (true-to-arcade core rule)
        # -----------------------------
        # A ghost meets Pac-Man if they land on the same LED OR swap places
        # this frame (moving towards each other they used to pass through).
        hits = [
            gi for gi in range(len(ghosts))
            if ghosts[gi] == pacman_pos
            or (ghosts[gi] == pac_prev and ghost_prev[gi] == pacman_pos)
        ]

        if pac_alive and hits:
            if scared:
                # Eat the ghost(s): respawn each away from Pac-Man
                for idx in hits:
                    while True:
                        rp = randrange(NUM_LEDS)
                        if abs(rp - pacman_pos) > max(3, NUM_LEDS // 6) and rp not in ghosts:
                            ghosts[idx] = rp
                            break
            else:
                # Ghost kills Pac-Man, BUT NOT during respawn grace
                if not safe:
                    pac_alive = False
                    draw_frame(dots, pill_positions, pacman_pos, ghosts, scared=False)
                    time.sleep_ms(RESPAWN_DELAY_MS)

        # -----------------------------
        # LEVEL COMPLETE?
        # -----------------------------
        if (not any(dots)) and (len(pill_positions) == 0):
            level += 1
            dots, pill_positions = reseed_level(level)

            pacman_pos = NUM_LEDS // 2
            pac_dir = 1
            ghosts = spawn_ghosts(pacman_pos)

            scared = False
            respawn_until_ms = 0  # clear any grace timer

            fade_in_level(dots, pill_positions)

        # -----------------------------
        # RESPAWN PAC-MAN IF DEAD
        # -----------------------------
        if not pac_alive:
            pacman_pos = NUM_LEDS // 2
            pac_dir = 1
            pac_alive = True

            # Start invulnerability window (“READY”)
            respawn_until_ms = time.ticks_add(time.ticks_ms(), RESPAWN_GRACE_MS)

            # Optional: push ghosts away if they’re camping the spawn
            if ENABLE_SPAWN_CLEAR:
                for gi in range(len(ghosts)):
                    d = abs(ghosts[gi] - pacman_pos)
                    d = min(d, NUM_LEDS - d)  # wrap-aware distance
                    if d <= SPAWN_CLEAR_RADIUS:
                        ghosts[gi] = wrap(pacman_pos + SPAWN_CLEAR_RADIUS + 2 + gi)

            # Important: do NOT re-enable dots/pills here.

        # -----------------------------
        # DRAW
        # -----------------------------
        draw_frame(dots, pill_positions, pacman_pos, ghosts, scared)

        time.sleep(FRAME_DELAY)

    return hsv_values


def effect_29(hsv_values, led_strip):
    """Matrix effect with cascading green characters, orientation-aware.

    Env space:
      - 0             = bottom (ground)
      - NUM_LEDS - 1  = top

    Visually: bright pale heads fall from top to bottom with fading green
    trails, each at its own speed. ORIENTATION flips which physical side is
    treated as bottom/top.
    """
    GREEN = 0.00           # green hue on this strip (red and green are swapped)
    num_trails = max(4, NUM_LEDS // 20)        # 5 on 100 LEDs
    min_len = 6
    max_len = max(8, NUM_LEDS // 8)            # 12 on 100 LEDs
    fall_min_s = 1.5       # seconds for a trail to fall the full strip
    fall_max_s = 4.0

    def new_trail(start_anywhere=False):
        top = NUM_LEDS - 1
        return {
            # start just above the top (or anywhere, for the first frame)
            "pos": uniform(0, top) if start_anywhere else top + randrange(0, NUM_LEDS // 4 + 1),
            "speed": NUM_LEDS / uniform(fall_min_s, fall_max_s),   # LEDs per second
            "len": randrange(min_len, max_len + 1),
            "wait": 0.0 if start_anywhere else uniform(0.0, 0.8),  # pause before falling
        }

    trails = [new_trail(start_anywhere=True) for _ in range(num_trails)]

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        # Build the frame in memory: brightness and saturation per env LED
        val = [0.0] * NUM_LEDS
        sat = [1.0] * NUM_LEDS

        for k in range(num_trails):
            tr = trails[k]
            if tr["wait"] > 0:
                tr["wait"] -= dt
                continue
            tr["pos"] -= tr["speed"] * dt          # fall towards env 0
            head = int(tr["pos"])
            if head + tr["len"] < 0:               # fully off the bottom
                trails[k] = new_trail()
                continue

            # Bright, pale head
            if 0 <= head < NUM_LEDS:
                val[head] = 1.0
                sat[head] = 0.35
            # Green trail fading out above it
            for j in range(1, tr["len"]):
                p = head + j
                if 0 <= p < NUM_LEDS:
                    v = 0.8 * (1.0 - j / tr["len"]) ** 1.5
                    if v > val[p]:
                        val[p] = v
                        sat[p] = 1.0

        # Write the finished frame, each LED once (no flicker)
        for env_i in range(NUM_LEDS):
            hsv_values[env_i] = (GREEN, sat[env_i], val[env_i])
            set_hsv_env(env_i, GREEN, sat[env_i], val[env_i], led_strip)

        time.sleep(0.02)

    return hsv_values

def effect_30(hsv_values, led_strip):
    """Gravitational Wave Ripples: Smooth, undulating ripples that simulate space-time disturbances."""
    ripple_speed = 1.0          # now "cycles-ish per second" scale, not ms
    ripple_amplitude = 0.25     # spatial frequency (bigger = more ripples along strip)
    hue_shift_speed = 0.15      # subtle hue drift speed

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0  # seconds since start

        for i in range(NUM_LEDS):
            wave_phase = (i * ripple_amplitude + t * ripple_speed) % (2 * math.pi)
            hue = (0.5 + math.sin(wave_phase) * 0.1 + t * hue_shift_speed) % 1.0
            brightness = (1 + math.cos(wave_phase)) / 2

            hsv_values[i] = (hue, 1.0, brightness)
            set_hsv_env(i, hue, 1.0, brightness, led_strip)

        time.sleep(0.02)

    return hsv_values

def effect_31(hsv_values, led_strip):
    """Waves of color moving down the strip: each band carries its own colour
    and swells and narrows as it travels."""
    wave_length = 10       # LEDs from one band to the next
    speed = 8.0            # LEDs per second
    GOLDEN = 0.618034      # spreads band colours evenly round the colour wheel
    width_min = 0.25       # band width, as a share of wave_length
    width_max = 0.75
    breathe_speed = 1.3    # rad/s
    hue_base = uniform(0, 1.0)

    start_time = time.ticks_ms()  # Start time for the effect

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        offset = speed * t

        for i in range(NUM_LEDS):
            x = (i + offset) / wave_length
            k = int(math.floor(x))             # which band this LED is in
            u = x - k                          # 0..1 across the band slot
            # Each band breathes on its own rhythm
            w = width_min + (width_max - width_min) * (0.5 + 0.5 * math.sin(t * breathe_speed + k * 0.9))
            d = abs(u - 0.5)
            if d < w / 2:
                c = math.cos(math.pi * d / w)
                brightness = c * c
            else:
                brightness = 0.0
            hue = (hue_base + k * GOLDEN) % 1.0
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)

    return hsv_values


def effect_32(hsv_values, led_strip):
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



def effect_33(hsv_values, led_strip):
    """Themed glitter: each pass picks a colour family, lays a soft drifting
    glow in it, and scatters glitter that also sweeps along in bursts."""
    # Colour families as REAL hues (centre, spread, saturation). The effects
    # swap red and green for this strip setup, so they're converted below.
    THEMES = [
        (0.125, 0.04, 0.85),   # gold
        (0.58, 0.05, 0.55),    # icy blue
        (0.92, 0.04, 0.65),    # pink
        (0.36, 0.05, 0.90),    # emerald
        (0.78, 0.05, 0.80),    # violet
        (0.05, 0.04, 1.00),    # fire
    ]
    centre, spread, sat = THEMES[randrange(len(THEMES))]

    def strip_hue(real_hue):
        # Swapping red and green mirrors the colour wheel around 60 degrees
        return (1.0 / 3.0 - real_hue) % 1.0

    # Glow: soft wash that drifts along the strip
    glow_min = 0.16
    glow_swing = 0.10
    # Glitter
    sparkle_rate = NUM_LEDS * 0.15      # random sparkles per second everywhere
    sparkle_keep = 0.02                 # brightness left after 1 s (fast fade)
    # Sweeping bursts
    burst_gap = (1.0, 2.5)              # seconds between bursts
    burst_reach = 3                     # LEDs either side of the burst head
    burst_density = 0.35                # chance per LED near the head per frame

    spark_v = [0.0] * NUM_LEDS
    spark_h = [0.0] * NUM_LEDS
    spark_s = [0.0] * NUM_LEDS
    bursts = []
    start_time = time.ticks_ms()
    last = start_time
    next_burst = uniform(0.2, 1.0)

    def add_spark(i):
        spark_v[i] = uniform(0.6, 1.0)
        spark_h[i] = strip_hue(centre + uniform(-spread, spread) * 1.5)
        spark_s[i] = sat * uniform(0.3, 0.8)   # glints are paler than the glow

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now
        keep = sparkle_keep ** dt

        # Fade glitter
        for i in range(NUM_LEDS):
            spark_v[i] *= keep

        # Random glitter
        expected = sparkle_rate * dt
        while expected > 0:
            if uniform(0, 1) < expected:
                add_spark(randrange(NUM_LEDS))
            expected -= 1

        # Bursts sweeping along the strip
        if t >= next_burst:
            direction = choice([-1, 1])
            bursts.append({
                "pos": 0.0 if direction > 0 else NUM_LEDS - 1.0,
                "dir": direction,
                "speed": NUM_LEDS / uniform(1.0, 2.0),
            })
            next_burst = t + uniform(burst_gap[0], burst_gap[1])
        alive = []
        for bu in bursts:
            bu["pos"] += bu["dir"] * bu["speed"] * dt
            if -burst_reach <= bu["pos"] < NUM_LEDS + burst_reach:
                alive.append(bu)
                c = int(bu["pos"])
                for i in range(max(0, c - burst_reach), min(NUM_LEDS, c + burst_reach + 1)):
                    if uniform(0, 1) < burst_density:
                        add_spark(i)
        bursts = alive

        # Build and write the frame: glitter over the glow, each LED once
        for i in range(NUM_LEDS):
            gv = glow_min + glow_swing * (0.5 + 0.5 * math.sin(i * 0.12 + t * 0.7))
            if spark_v[i] > gv:
                h, s_, v = spark_h[i], spark_s[i], spark_v[i]
            else:
                h = strip_hue(centre + spread * math.sin(i * 0.05 - t * 0.3))
                s_, v = sat, gv
            hsv_values[i] = (h, s_, v)
            led_strip.set_hsv(i, h, s_, v)

        time.sleep(0.02)

    return hsv_values


def effect_34(hsv_values, led_strip):
    """Rotating color bands that drift smoothly along the strip."""
    BAND_WIDTH = max(8, NUM_LEDS // 10)   # 10 LEDs on 100 (was a fixed 5)
    FAST_BRIGHT = 1.0
    DIM_BRIGHT = 0.35
    SPEED = 8.0          # LEDs per second
    SOFT = 0.3           # share of each band that blends into the next

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        # Wrap at a whole number of colour cycles (6 bands) so it never jumps
        offset = (SPEED * t) % (BAND_WIDTH * 6)

        for i in range(NUM_LEDS):
            x = (i + offset) / BAND_WIDTH
            band_index = int(x)
            u = x - band_index                  # 0..1 across this band

            hue = (band_index % 6) / 6.0
            # Alternate bright/dim bands
            brightness = FAST_BRIGHT if band_index % 2 == 0 else DIM_BRIGHT

            # Soft edge: blend into the next band over the last SOFT of this one
            if u > 1.0 - SOFT:
                w = (u - (1.0 - SOFT)) / SOFT
                w = w * w * (3 - 2 * w)
                next_bright = DIM_BRIGHT if band_index % 2 == 0 else FAST_BRIGHT
                hue = (hue + w / 6.0) % 1.0     # next band is 1/6 further round
                brightness += (next_bright - brightness) * w

            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)

    return hsv_values

def effect_35(hsv_values, led_strip):
    """Meteor shower with fading tails that vanish completely, orientation-aware.

    Env space:
      0             = bottom (ground)
      NUM_LEDS - 1  = top

    Visually: a red meteor streaks from top -> bottom with a fading tail
    behind it, leaving a brief afterglow. ORIENTATION decides which
    *physical* end is the top/bottom.
    """
    HUE = 0.33                                  # red on this strip
    meteor_length = max(10, NUM_LEDS // 10)     # tail length, scaled to the strip
    fall_min_s, fall_max_s = 2.0, 3.0           # seconds to fall the full strip
    gap_min_s, gap_max_s = 0.2, 0.8             # pause between meteors
    afterglow_keep = 0.05                       # afterglow left after 1 s

    def new_meteor():
        return {
            "head": float(NUM_LEDS - 1),
            "speed": NUM_LEDS / uniform(fall_min_s, fall_max_s),   # LEDs per second
            "wait": uniform(gap_min_s, gap_max_s),
        }

    meteor = new_meteor()
    meteor["wait"] = 0.0
    glow = [0.0] * NUM_LEDS

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        # 1) Fade the afterglow (in memory)
        keep = afterglow_keep ** dt
        for env_i in range(NUM_LEDS):
            glow[env_i] *= keep

        # 2) Move the meteor and draw head + tail (tail trails ABOVE the head)
        if meteor["wait"] > 0:
            meteor["wait"] -= dt
        else:
            meteor["head"] -= meteor["speed"] * dt
            head = int(meteor["head"])
            for k in range(meteor_length):
                env_i = head + k
                if 0 <= env_i < NUM_LEDS:
                    v = (1.0 - k / meteor_length) ** 1.5
                    if v > glow[env_i]:
                        glow[env_i] = v
            # When head + tail are completely off the bottom, start the next one
            if head + meteor_length < 0:
                meteor = new_meteor()

        # 3) Write the finished frame, each LED once (no flicker)
        for env_i in range(NUM_LEDS):
            hsv_values[env_i] = (HUE, 1.0, glow[env_i])
            set_hsv_env(env_i, HUE, 1.0, glow[env_i], led_strip)

        time.sleep(0.01)

    return hsv_values



def effect_36(hsv_values, led_strip):
    """Fast animated rainbow explosion radiating from the center outward, with
    white-hot pulses bursting out every couple of seconds."""
    center = (NUM_LEDS - 1) / 2.0
    half = max(1.0, NUM_LEDS / 2.0)

    ring_speed = 0.7 * half            # rainbow moves outwards, LEDs/s (35 on 100 LEDs)
    rainbows = 1.5                     # rainbows from the centre to each end
    hue_per_led = rainbows / half
    edge_level = 0.15                  # brightness left at the ends

    pulse_time = 0.6                   # seconds for a pulse to reach the ends
    pulse_width = max(2.0, NUM_LEDS / 35.0)
    pulse_gap = (1.5, 2.5)             # seconds between pulses

    start_time = time.ticks_ms()  # Record the start time
    pulse_start = 0.0
    next_pulse = uniform(pulse_gap[0], pulse_gap[1])

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000  # Time in seconds

        if t >= next_pulse:
            pulse_start = t
            next_pulse = t + uniform(pulse_gap[0], pulse_gap[1])
        pulse_age = t - pulse_start
        pulse_r = pulse_age / pulse_time * half
        pulse_on = pulse_r <= half + pulse_width
        pulse_fade = max(0.0, 1.0 - pulse_r / (half + pulse_width))

        for i in range(NUM_LEDS):
            d = abs(i - center)
            # Rainbow rings travel outwards: hue grows with distance, shrinks with time
            hue = (d * hue_per_led - t * ring_speed * hue_per_led) % 1.0
            sat = 1.0
            v = edge_level + (1.0 - edge_level) * max(0.0, 1.0 - d / half)

            # White-hot pulse on top
            if pulse_on:
                p = max(0.0, 1.0 - abs(d - pulse_r) / pulse_width) * pulse_fade
                if p > 0:
                    sat = 1.0 - 0.85 * p
                    v = max(v, p)

            hsv_values[i] = (hue, sat, v)
            led_strip.set_hsv(i, hue, sat, v)

        time.sleep(0.02)  # Faster animation

    return hsv_values

def effect_37(hsv_values, led_strip):
    """Breathing effect with color cycling: a two-colour blend drifts round
    the colour wheel while a slow breath rolls gently through it."""
    hue_speed = 0.05        # colour wheel turns per second (one turn every 20 s)
    hue_span = 0.15         # share of the colour wheel across the strip:
                            # small enough that only ~2 neighbouring colours show
    breath_period = 4.5     # seconds per breath
    floor = 0.12            # low glow at the bottom of each breath
    roll = 0.6              # share of a breath spread along the strip, so it rolls

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000  # Time in seconds
        breath_phase = 2 * math.pi * elapsed / breath_period

        for i in range(NUM_LEDS):
            pos = i / NUM_LEDS
            # Gentle blend of ~2 neighbouring colours, drifting round the wheel
            hue = (elapsed * hue_speed + pos * hue_span) % 1.0
            # Breath that rolls along the strip
            b = 0.5 + 0.5 * math.sin(breath_phase - pos * roll * 2 * math.pi)
            brightness = floor + (1.0 - floor) * b

            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)  # Small delay for smoother breathing effect

    return hsv_values


def effect_38(hsv_values, led_strip):
    """Moving plasma effect: overlapping waves at different speeds and
    directions make the colours swirl and morph along the strip."""
    two_pi = 2 * math.pi
    # Wave lengths scale with the strip so the plasma looks the same on any length
    k1 = two_pi / (NUM_LEDS / 3.0)
    k2 = two_pi / (NUM_LEDS / 5.3)
    k3 = two_pi / (NUM_LEDS / 2.1)
    w1, w2, w3 = 0.9, 1.4, 0.6     # rad/s; wave 2 runs the other way
    hue_drift = 0.02               # whole palette turns slowly (once per 50 s)
    floor = 0.25                   # gentle glow in the darkest parts

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000  # Time in seconds
        wobble = 2.0 * math.sin(t * 0.3)   # slowly bends wave 3

        for i in range(NUM_LEDS):
            v1 = math.sin(i * k1 + t * w1)
            v2 = math.sin(i * k2 - t * w2)
            v3 = math.sin(i * k3 + t * w3 + wobble)

            # Colour: the waves combined spread over the whole colour wheel
            hue = ((v1 + v2 + v3) / 6.0 + 0.5 + t * hue_drift) % 1.0
            # Brightness: a different mix, so light and colour move separately
            b = 0.5 + 0.5 * math.sin((v1 - v3) * 1.5 + v2)
            brightness = floor + (1.0 - floor) * b

            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)  # Small delay for smooth animation

    return hsv_values

def effect_39(hsv_values, led_strip):
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

    # Neon-like palette. The effects swap red and green for this strip setup,
    # which mirrors the colour wheel, so each real hue h is sent as (1/3 - h).
    NEON_HUES = [(1.0 / 3.0 - h) % 1.0 for h in (
        0.83,  # magenta / pink
        0.58,  # cyan
        0.72,  # purple
        0.38,  # lime / yellow-green
        0.02,  # hot red/orange
    )]

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
            set_hsv_env(env_idx, h, s, v, led_strip)

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


def effect_40(hsv_values, led_strip):
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
    # Time-based physics: the first drop takes FALL_SECONDS on any strip length.
    FALL_SECONDS = 1.5
    bounce_damping = 0.70   # how much speed is kept after each bounce
    pause_duration = 1.0
    fade_duration = 1.0

    # World coordinates: env 0 = bottom (floor), env NUM_LEDS-1 = top.
    # Both orientations fall towards env 0; env_to_phys / set_hsv_env map it
    # to the real strip.
    height = float(NUM_LEDS - 1)
    gravity = 2.0 * height / (FALL_SECONDS * FALL_SECONDS)   # LEDs / s^2
    floor_env = 0

    # Gliding: the ball sits on one LED for most of its travel and hands over
    # in a short cross-fade, so it reads as a single dot with steady brightness
    # (same tuning as effect 23).
    HANDOFF = 0.4
    GLIDE_POWER = 0.6

    ball_y = height          # height above the floor, in LEDs
    velocity = 0.0           # LEDs per second (negative = falling)
    hue = randrange(360) / 360.0

    def draw(y, brightness=1.0):
        frame = [0.0] * NUM_LEDS
        i0 = int(y)
        frac = y - i0
        frac = (frac - (1.0 - HANDOFF) / 2) / HANDOFF
        frac = max(0.0, min(1.0, frac))
        frac = frac * frac * (3 - 2 * frac)
        for idx, w in ((i0, 1.0 - frac), (i0 + 1, frac)):
            if 0 <= idx < NUM_LEDS and w > 0:
                frame[idx] = brightness * (w ** GLIDE_POWER)
        # Write the whole frame once (clearing first made the ball flicker)
        for i in range(NUM_LEDS):
            v = frame[i]
            hsv_values[i] = (hue, 1.0, v) if v > 0 else (0.0, 0.0, 0.0)
            set_hsv_env(i, hue, 1.0, v, led_strip)

    last = time.ticks_ms()
    while True:
        now = time.ticks_ms()
        dt = min(0.05, time.ticks_diff(now, last) / 1000.0)
        last = now

        # Physics integration
        velocity -= gravity * dt
        ball_y += velocity * dt

        if ball_y <= floor_env:
            ball_y = float(floor_env)
            velocity = -velocity * bounce_damping
            # Stop once the next bounce would rise less than about one LED
            # (the old rule waited for near-zero speed: seconds of jitter)
            if velocity * velocity / (2 * gravity) < 1.0:
                break

        draw(ball_y)
        time.sleep(0.01)

    # Ball parked at the floor, then fade out
    draw(float(floor_env))
    time.sleep(pause_duration)
    fade_start = time.ticks_ms()
    while True:
        k = time.ticks_diff(time.ticks_ms(), fade_start) / 1000.0 / fade_duration
        if k >= 1.0:
            break
        draw(float(floor_env), 1.0 - k)
        time.sleep(0.01)

    # Make sure the strip is dark before returning
    draw(float(floor_env), 0.0)

    return hsv_values




def effect_41(hsv_values, led_strip):
    """Rotating comet effect that appears from off one end and exits off the other (orientation-aware).

    Env space:
      0             = bottom
      NUM_LEDS - 1  = top

    ORIENTATION decides which *physical* end is bottom/top.
    """

    tail_length = max(15, NUM_LEDS // 5)     # 20 LEDs on 100, scaled with the strip
    sweep_seconds = 3.5                      # time for the head to cross the strip
    speed = NUM_LEDS / sweep_seconds         # LEDs per second
    saturation = 1.0

    start_time = time.ticks_ms()

    # Repeatedly sweep the comet across the whole env space, from bottom to
    # top: the head enters at the bottom and the tail follows it off the top.
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        hue = uniform(0, 1.0)                # new colour for every sweep
        sweep_start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
            head = -1.0 + speed * time.ticks_diff(time.ticks_ms(), sweep_start) / 1000.0
            if head - tail_length > NUM_LEDS:
                break                        # whole comet has left the top

            for env_i in range(NUM_LEDS):
                d = head - env_i             # >0: behind the head (tail side)
                if 0.0 <= d < tail_length:
                    v = (1.0 - d / tail_length) ** 1.6
                elif -1.0 < d < 0.0:
                    v = 1.0 + d              # soft leading edge: smooth gliding
                else:
                    v = 0.0
                hsv_values[env_i] = (hue, saturation, v)
                set_hsv_env(env_i, hue, saturation, v, led_strip)

            time.sleep(0.01)

    return hsv_values



def effect_42(hsv_values, led_strip):
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




def effect_43(hsv_values, led_strip):
    """Wave pulsing along the strip with smooth motion over time, over a
    narrow band of colour that slowly drifts round the colour wheel."""
    WAVE_LENGTH = float(NUM_LEDS)   # one wave across the strip, any length
    SPEED = 3.0                     # rad/s (the wave crosses the strip in ~2 s)
    HUE_SPAN = 0.2                  # share of the colour wheel along the strip (was ~3 rainbows)
    HUE_DRIFT = 0.02                # colour band turns once every 50 s
    hue_base = uniform(0, 1.0)
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        for i in range(NUM_LEDS):
            phase = (i * 2 * math.pi / WAVE_LENGTH) + (t * SPEED)
            brightness = (1.0 + math.sin(phase)) * 0.5

            hue = (hue_base + t * HUE_DRIFT + HUE_SPAN * i / NUM_LEDS) % 1.0
            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)

    return hsv_values


def effect_44(hsv_values, led_strip):
    """Waterfall effect: water-coloured bands flowing 'down' the strip with a
    faster shimmer on top, pale highlights and a soft mist at the base
    (orientation-aware)."""
    two_pi = 2 * math.pi
    WAVE_LENGTH = 10.0      # main bands, LEDs
    SPEED = 6.0             # rad/s  (~9.5 LEDs/s downwards)
    SHIMMER_LENGTH = 4.3    # faster, finer ripples on top
    SHIMMER_SPEED = 14.0
    # Real hues, converted for this strip's red/green swap (h -> 1/3 - h)
    DEEP = 0.64             # deep blue in the troughs
    TEAL = 0.52             # teal in the bright parts
    MIST_LEN = max(3, NUM_LEDS // 20)    # mist glow at the base
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0

        for env_i in range(NUM_LEDS):
            # Phases grow with height and time, so bands move towards env 0
            b1 = 0.5 + 0.5 * math.sin(env_i * two_pi / WAVE_LENGTH + t * SPEED)
            b2 = 0.5 + 0.5 * math.sin(env_i * two_pi / SHIMMER_LENGTH + t * SHIMMER_SPEED)
            level = 0.7 * b1 + 0.3 * b2
            brightness = 0.2 + 0.8 * level

            real_hue = DEEP + (TEAL - DEEP) * b1
            sat = 1.0
            if level > 0.8:                      # light catching the water
                sat = 1.0 - (level - 0.8) / 0.2 * 0.7

            # Mist at the base
            if env_i < MIST_LEN:
                m = (1.0 - env_i / MIST_LEN) * (0.75 + 0.25 * math.sin(t * 7 + env_i * 1.7))
                if m * 0.7 > brightness * 0.5:
                    sat = min(sat, 0.4)
                brightness = max(brightness, m)

            hue = (1.0 / 3.0 - real_hue) % 1.0
            hsv_values[env_i] = (hue, sat, brightness)
            set_hsv_env(env_i, hue, sat, brightness, led_strip)

        time.sleep(0.02)

    return hsv_values


def effect_45(hsv_values, led_strip):
    """Game of Life effect (1D), tamed: slow generations, cells fade in and out
    in a soft cool white, and it reseeds if the pattern dies or repeats."""
    GEN_SECONDS = 0.3       # time between generations (~3 per second)
    FADE_TIME = 0.15        # seconds for a cell to fade most of the way
    PEAK = 0.6              # brightness of a live cell
    # Soft cool white (real hue 0.58, converted for the strip's red/green swap)
    HUE = (1.0 / 3.0 - 0.58) % 1.0
    SAT = 0.15
    HISTORY = 8             # generations remembered to spot repeats

    def seed():
        return [1 if randrange(100) < 35 else 0 for _ in range(NUM_LEDS)]

    current_state = seed()
    history = []
    shown = [0.0] * NUM_LEDS

    start_time = time.ticks_ms()
    last = start_time
    next_gen = 0.0

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        if t >= next_gen:
            next_gen = t + GEN_SECONDS
            # Rule: a cell is alive next if exactly one neighbour is alive
            next_state = [0] * NUM_LEDS
            for i in range(NUM_LEDS):
                left = current_state[(i - 1) % NUM_LEDS]
                right = current_state[(i + 1) % NUM_LEDS]
                if left + right == 1:
                    next_state[i] = 1
            # Dead or stuck in a loop? Start again with a new seed.
            key = bytes(next_state)
            if not any(next_state) or key in history:
                next_state = seed()
                history = []
            history.append(key)
            if len(history) > HISTORY:
                history.pop(0)
            current_state = next_state

        # Fade each LED towards its cell's state
        k = min(1.0, dt / FADE_TIME)
        for i in range(NUM_LEDS):
            target = PEAK if current_state[i] else 0.0
            shown[i] += (target - shown[i]) * k
            hsv_values[i] = (HUE, SAT, shown[i])
            led_strip.set_hsv(i, HUE, SAT, shown[i])

        time.sleep(0.02)

    return hsv_values



def effect_46(hsv_values, led_strip):
    """Two-way comet traffic: several comets in a small palette of neighbouring
    shades travel in both directions and mix colours where they cross."""
    num_comets = max(3, NUM_LEDS // 30)        # 3 on 100 LEDs
    tail_length = max(8, NUM_LEDS // 8)        # 12 on 100 LEDs
    cross_min_s, cross_max_s = 2.0, 4.0        # seconds to cross the strip
    gap_max_s = 0.8                            # pause before a comet returns

    # Palette for this pass: three neighbouring shades around a random hue
    # (real hues, converted for the strip's red/green swap)
    base = uniform(0, 1.0)
    palette = []
    for off in (-0.06, 0.0, 0.06):
        h = (1.0 / 3.0 - (base + off)) % 1.0
        palette.append((h, hsv_to_rgb(h, 1.0, 1.0)))

    def new_comet(first=False):
        d = choice([-1, 1])
        h, rgb = palette[randrange(len(palette))]
        if first:
            pos = uniform(0, NUM_LEDS - 1)
        else:
            pos = -1.0 if d > 0 else NUM_LEDS
        return {
            "pos": pos,
            "dir": d,
            "speed": NUM_LEDS / uniform(cross_min_s, cross_max_s),   # LEDs per second
            "hue": h,
            "rgb": rgb,
            "wait": 0.0 if first else uniform(0.0, gap_max_s),
        }

    comets = [new_comet(first=True) for _ in range(num_comets)]

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS
        top_v = [0.0] * NUM_LEDS
        top_h = [0.0] * NUM_LEDS

        for k in range(num_comets):
            c = comets[k]
            if c["wait"] > 0:
                c["wait"] -= dt
                continue
            c["pos"] += c["dir"] * c["speed"] * dt
            head = c["pos"]
            # Gone past the far end, tail and all? Send in a new one.
            if (c["dir"] > 0 and head - tail_length > NUM_LEDS) or                (c["dir"] < 0 and head + tail_length < 0):
                comets[k] = new_comet()
                continue

            r, g, b = c["rgb"]
            lo = int(head - tail_length) if c["dir"] > 0 else int(head) - 1
            hi = int(head) + 1 if c["dir"] > 0 else int(head + tail_length) + 1
            for i in range(max(0, lo), min(NUM_LEDS, hi + 1)):
                d = (head - i) * c["dir"]          # >0: in the tail behind the head
                if 0.0 <= d < tail_length:
                    v = (1.0 - d / tail_length) ** 1.6
                elif -1.0 < d < 0.0:
                    v = 1.0 + d                    # soft leading edge
                else:
                    continue
                # Additive: comets crossing mix their colours
                fr[i] += r * v
                fg[i] += g * v
                fb[i] += b * v
                if v > top_v[i]:
                    top_v[i] = v
                    top_h[i] = c["hue"]

        # Write the finished frame, each LED once
        for i in range(NUM_LEDS):
            r = min(1.0, fr[i])
            g = min(1.0, fg[i])
            b = min(1.0, fb[i])
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))
            hsv_values[i] = (top_h[i], 1.0, max(r, g, b))

        time.sleep(0.01)

    return hsv_values


def effect_47(hsv_values, led_strip):
    """Randomised, rolling color waves with multiple hues."""
    WAVE_LENGTH = 12.0
    SPEED = 0.004
    HUE_DRIFT = 0.02        # colour band turns round the wheel once every 50 s
    HUE_SPAN = 0.15         # share of the colour wheel along the strip (was 3 rainbows)

    start_time = time.ticks_ms()
    base_hue = random()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t_ms = time.ticks_diff(time.ticks_ms(), start_time)
        t = t_ms * SPEED

        # Slowly drift the colour band round the wheel (time-based)
        hue_now = (base_hue + t_ms / 1000.0 * HUE_DRIFT) % 1.0

        for i in range(NUM_LEDS):
            # Multi-wave interference for brightness
            phase1 = i * 2 * math.pi / WAVE_LENGTH + t
            phase2 = i * 2 * math.pi / (WAVE_LENGTH * 1.7) - t * 0.7
            brightness = (math.sin(phase1) + math.sin(phase2)) * 0.25 + 0.5
            brightness = max(0.0, min(1.0, brightness))

            # Narrow band of neighbouring shades along the strip, swaying
            # slightly with the brightness waves
            hue = (hue_now + HUE_SPAN * i / NUM_LEDS + 0.03 * math.sin(phase2)) % 1.0

            hsv_values[i] = (hue, 1.0, brightness)
            led_strip.set_hsv(i, hue, 1.0, brightness)

        time.sleep(0.02)

    return hsv_values

def effect_48(hsv_values, led_strip):
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


def effect_49(hsv_values, led_strip):
    """Gentle rolling clouds: soft white clouds of different sizes drift slowly
    across a calm sky-blue background, gently changing shape as they go."""
    # Sky blue (real hue 0.58, converted for the strip's red/green swap)
    SKY_HUE = (1.0 / 3.0 - 0.58) % 1.0
    SKY_SAT = 0.85
    SKY_V = 0.22
    CLOUD_SAT = 0.05                    # clouds are nearly white

    num_clouds = max(3, NUM_LEDS // 25)          # 4 on 100 LEDs
    width_min = 6
    width_max = max(10, NUM_LEDS // 7)           # 14 on 100 LEDs
    wind = choice([-1, 1])                       # all clouds drift the same way

    def new_cloud(anywhere=False):
        w = uniform(width_min, width_max)
        if anywhere:
            pos = uniform(0, NUM_LEDS)
        else:
            pos = -w if wind > 0 else NUM_LEDS + w   # enter from the upwind end
        return {
            "pos": pos,
            "width": w,
            "speed": uniform(1.5, 4.0),          # LEDs per second
            "peak": uniform(0.55, 0.85),
            "morph": uniform(0.3, 0.8),          # rad/s: how fast it changes shape
            "phase": uniform(0, 2 * math.pi),
        }

    clouds = [new_cloud(anywhere=True) for _ in range(num_clouds)]

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        cover = [0.0] * NUM_LEDS      # 0 = clear sky, 1 = full cloud
        peak = [0.0] * NUM_LEDS

        for k in range(num_clouds):
            c = clouds[k]
            c["pos"] += wind * c["speed"] * dt
            # Width breathes slowly so the cloud changes shape
            w = c["width"] * (1.0 + 0.2 * math.sin(t * c["morph"] + c["phase"]))
            if (wind > 0 and c["pos"] - w > NUM_LEDS) or (wind < 0 and c["pos"] + w < 0):
                clouds[k] = new_cloud()
                continue
            lo = max(0, int(c["pos"] - w))
            hi = min(NUM_LEDS - 1, int(c["pos"] + w))
            for i in range(lo, hi + 1):
                d = abs(i - c["pos"]) / w
                if d >= 1.0:
                    continue
                amount = 0.5 + 0.5 * math.cos(math.pi * d)        # soft rounded edge
                # A little lumpy texture so it looks puffy
                amount *= 0.85 + 0.15 * math.sin(i * 0.9 + t * c["morph"] * 2 + c["phase"])
                if amount > cover[i]:
                    cover[i] = amount
                    peak[i] = c["peak"]

        # Blend sky and cloud, then write each LED once
        for i in range(NUM_LEDS):
            a_ = cover[i]
            sat = SKY_SAT + (CLOUD_SAT - SKY_SAT) * a_
            v = SKY_V + (peak[i] - SKY_V) * a_
            hsv_values[i] = (SKY_HUE, sat, v)
            led_strip.set_hsv(i, SKY_HUE, sat, v)

        time.sleep(0.03)

    return hsv_values

def effect_50(hsv_values, led_strip):
    """Glowing Pulsars: a few fixed stars, each glowing softly and ticking out
    short beams of light in both directions on its own steady rhythm."""
    num_pulsars = max(3, NUM_LEDS // 30)         # 3 on 100 LEDs
    reach = max(6, NUM_LEDS // 8)                # how far a beam travels, LEDs
    beam_time = 0.8                              # seconds for a beam to reach its end
    beam_speed = reach / beam_time               # LEDs per second
    flash_time = 0.3                             # centre flash length, seconds
    base_glow = 0.15                             # resting glow of each pulsar

    # Cool whites and pale blue-violets (real hues, converted for the strip's
    # red/green swap). (real hue, saturation)
    SHADES = [(0.60, 0.0), (0.60, 0.35), (0.70, 0.40), (0.66, 0.25)]

    spacing = NUM_LEDS / num_pulsars
    pulsars = []
    for k in range(num_pulsars):
        real_h, sat = SHADES[randrange(len(SHADES))]
        h = (1.0 / 3.0 - real_h) % 1.0
        pulsars.append({
            "pos": int((k + 0.5) * spacing + uniform(-spacing / 6, spacing / 6)),
            "period": uniform(1.8, 4.0),           # seconds between pulses
            "phase": uniform(0, 1.0),
            "rgb": hsv_to_rgb(h, sat, 1.0),
            "hue": h,
            "sat": sat,
        })

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0

        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS
        top_v = [0.0] * NUM_LEDS
        top_p = [0] * NUM_LEDS

        for pi in range(num_pulsars):
            p = pulsars[pi]
            r, g, b = p["rgb"]
            # Time since this pulsar's latest pulse
            age = (t / p["period"] + p["phase"]) % 1.0 * p["period"]

            def add(i, v):
                if 0 <= i < NUM_LEDS and v > 0:
                    fr[i] += r * v
                    fg[i] += g * v
                    fb[i] += b * v
                    if v > top_v[i]:
                        top_v[i] = v
                        top_p[i] = pi

            # Resting glow plus the flash at each pulse
            flash = max(0.0, 1.0 - age / flash_time)
            centre = base_glow + (1.0 - base_glow) * flash
            add(p["pos"], centre)
            add(p["pos"] - 1, centre * 0.35)
            add(p["pos"] + 1, centre * 0.35)

            # Beams travelling out both ways, fading as they go
            if age < beam_time * 1.2:
                front = age * beam_speed
                fade = max(0.0, 1.0 - front / reach)
                for off in range(1, reach + 2):
                    x = front - off                 # >0: behind the beam front
                    if x < -1.0:
                        break
                    if x < 0:
                        v = 1.0 + x                 # soft leading edge
                    else:
                        v = max(0.0, 1.0 - x / 3.0) # short glow behind the front
                    v *= fade
                    add(p["pos"] + off, v)
                    add(p["pos"] - off, v)

        # Write the finished frame, each LED once
        for i in range(NUM_LEDS):
            r = min(1.0, fr[i])
            g = min(1.0, fg[i])
            b = min(1.0, fb[i])
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))
            p = pulsars[top_p[i]]
            hsv_values[i] = (p["hue"], p["sat"], max(r, g, b))

        time.sleep(0.01)

    return hsv_values



def effect_51(hsv_values, led_strip):
    """Northern Lights: slow, layered curtains of green and teal light with
    violet and pink at their edges, drifting and brightening, with an
    occasional shimmer running along them."""
    two_pi = 2 * math.pi
    # Real hues (converted below for the strip's red/green swap)
    GREEN, TEAL, VIOLET = 0.36, 0.47, 0.80
    SAT = 0.85
    FLOOR = 0.13             # faint glow between curtains

    # Three curtain layers: lengths scale with the strip, own speeds/directions
    layers = [
        (two_pi / (NUM_LEDS / 2.5),  0.35, uniform(0, two_pi)),
        (two_pi / (NUM_LEDS / 4.0), -0.50, uniform(0, two_pi)),
        (two_pi / (NUM_LEDS / 1.6),  0.22, uniform(0, two_pi)),
    ]

    shimmer_speed = max(15.0, NUM_LEDS * 0.25)   # LEDs per second
    shimmer_width = max(3.0, NUM_LEDS / 25.0)
    shimmer = None
    next_shimmer = uniform(1.5, 4.0)

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0

        # Occasional shimmer running along the curtains
        if shimmer is None and t >= next_shimmer:
            d = choice([-1, 1])
            shimmer = {"start": t, "dir": d, "from": 0.0 if d > 0 else NUM_LEDS - 1.0}
        shimmer_pos = None
        if shimmer is not None:
            shimmer_pos = shimmer["from"] + shimmer["dir"] * shimmer_speed * (t - shimmer["start"])
            if shimmer_pos < -shimmer_width * 3 or shimmer_pos > NUM_LEDS + shimmer_width * 3:
                shimmer = None
                shimmer_pos = None
                next_shimmer = t + uniform(3.0, 7.0)

        bends = [1.5 * math.sin(t * 0.2 + n) for n in range(3)]

        for i in range(NUM_LEDS):
            c = []
            for n in range(3):
                k, w, ph = layers[n]
                c.append(0.5 + 0.5 * math.sin(i * k + t * w + ph + bends[n]))
            curtain = (c[0] * c[1] + 0.6 * c[2]) / 1.6
            curtain = curtain ** 1.8                     # crisper curtains

            if shimmer_pos is not None:
                x = (i - shimmer_pos) / shimmer_width
                curtain += 0.35 * curtain * math.exp(-x * x)

            brightness = FLOOR + (1.0 - FLOOR) * min(1.0, curtain)

            # Green to teal along the curtains, violet/pink tint at their edges
            real_hue = GREEN + (TEAL - GREEN) * c[2]
            if 0.08 < curtain < 0.45:
                edge = (0.45 - curtain) / 0.37 * 0.7
                real_hue = real_hue + (VIOLET - real_hue) * edge
            hue = (1.0 / 3.0 - real_hue) % 1.0

            hsv_values[i] = (hue, SAT, brightness)
            led_strip.set_hsv(i, hue, SAT, brightness)

        time.sleep(0.03)

    return hsv_values


def effect_52(hsv_values, led_strip):
    """Fireworks Burst: shells burst at random heights into sparks that fly
    out, slow down, droop under gravity and crackle as they fade
    (orientation-aware: sparks fall towards the base)."""
    burst_speed = NUM_LEDS * 0.5         # initial spark speed, LEDs/s (bigger bursts)
    gravity = NUM_LEDS * 0.15            # LEDs/s^2 towards env 0 (gentle, floaty fall)
    drag_keep = 0.15                     # speed left after 1 s of air drag
    max_bursts = 4
    flash_time = 0.1
    launch_min_s, launch_max_s = 0.6, 1.0   # rocket climb time from the base
    trail_len = 3

    def real(h):
        return (1.0 / 3.0 - h) % 1.0     # real hue -> strip hue (R/G swap)

    def shell_colours():
        kind = random()
        if kind < 0.70:                  # single colour
            h = uniform(0, 1.0)
            return [hsv_to_rgb(real(h), 1.0, 1.0)], 0.25
        if kind < 0.85:                  # two colours
            h = uniform(0, 1.0)
            h2 = (h + uniform(0.25, 0.5)) % 1.0
            return [hsv_to_rgb(real(h), 1.0, 1.0), hsv_to_rgb(real(h2), 1.0, 1.0)], 0.25
        if random() < 0.5:               # gold crackle
            return [hsv_to_rgb(real(0.11), 0.75, 1.0)], 0.55
        return [hsv_to_rgb(real(0.6), 0.05, 1.0)], 0.55     # silver crackle

    bursts = []
    rockets = []
    start_time = time.ticks_ms()
    last = start_time
    next_burst = 0.2

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        # Launch a rocket from the base now and then
        if t >= next_burst and len(bursts) + len(rockets) < max_bursts:
            rockets.append({
                "born": t,
                "height": uniform(0.45, 0.9) * (NUM_LEDS - 1),
                "climb": uniform(launch_min_s, launch_max_s),
            })
            next_burst = t + uniform(0.6, 1.6)

        # Rockets that reach their height burst into a shell
        flying = []
        for rk in rockets:
            if t - rk["born"] < rk["climb"]:
                flying.append(rk)
                continue
            colours, crackle = shell_colours()
            height = rk["height"]
            sparks = []
            n = randrange(8, 15)
            for k in range(n):
                sparks.append({
                    "pos": height,
                    "vel": uniform(-1.0, 1.0) * burst_speed,
                    "life": uniform(2.0, 3.0),
                    "rgb": colours[k % len(colours)],
                })
            bursts.append({"born": t, "height": height, "sparks": sparks,
                           "crackle": crackle, "flash": colours[0]})
        rockets = flying

        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS

        def add(i, rgb, v):
            if 0 <= i < NUM_LEDS and v > 0:
                fr[i] += rgb[0] * v
                fg[i] += rgb[1] * v
                fb[i] += rgb[2] * v

        # Climbing rockets: warm gold head slowing near the top, sparkly trail
        ROCKET = hsv_to_rgb(real(0.10), 0.6, 1.0)
        for rk in rockets:
            k = (t - rk["born"]) / rk["climb"]
            pos = rk["height"] * (1.0 - (1.0 - k) * (1.0 - k))   # eases out
            i = int(pos)
            add(i, ROCKET, 0.9)
            for j in range(1, trail_len + 1):
                add(i - j, ROCKET, (0.5 / j) * uniform(0.4, 1.0))

        drag = drag_keep ** dt
        alive_bursts = []
        for bu in bursts:
            age = t - bu["born"]
            # Bright flash at the burst point
            if age < flash_time:
                f = 1.0 - age / flash_time
                c = int(bu["height"])
                add(c, (1.0, 1.0, 1.0), f)
                add(c - 1, (1.0, 1.0, 1.0), f * 0.5)
                add(c + 1, (1.0, 1.0, 1.0), f * 0.5)

            live = False
            for sp in bu["sparks"]:
                if age >= sp["life"]:
                    continue
                live = True
                sp["vel"] = sp["vel"] * drag - gravity * dt
                sp["pos"] += sp["vel"] * dt
                k = age / sp["life"]
                v = (1.0 - k) ** 1.3
                # Crackle: sparks twinkle as they burn out
                if k > 0.6 and random() < bu["crackle"]:
                    v *= 0.15
                i = int(sp["pos"])
                add(i, sp["rgb"], v)
                # short trail behind the spark
                back = 1 if sp["vel"] < 0 else -1
                add(i + back, sp["rgb"], v * 0.35)
            if live:
                alive_bursts.append(bu)
        bursts = alive_bursts

        # Write the finished frame, each LED once (env -> physical)
        for env_i in range(NUM_LEDS):
            r = min(1.0, fr[env_i])
            g = min(1.0, fg[env_i])
            b = min(1.0, fb[env_i])
            hsv_values[env_i] = (0.0, 0.0, max(r, g, b))
            set_rgb_env(env_i, int(r * 255), int(g * 255), int(b * 255), led_strip)

        time.sleep(0.01)

    return hsv_values

def effect_53(hsv_values, led_strip):
    """Explosion (supernova): the centre gathers a flickering glow, detonates in
    a white-hot flash that races outwards, then cools through yellow, orange
    and red into dying embers. Each explosion plays through once started."""
    CHARGE_S = 1.5          # glow gathering at the centre
    BLAST_S = 1.2           # time for the blast front to reach the ends
    COOL_S = 1.0            # how fast debris cools after the front passes
    REST_S = 1.0            # darkness before the next one
    center = (NUM_LEDS - 1) / 2.0
    half = max(1.0, NUM_LEDS / 2.0)

    def heat_rgb(T):
        """Real colour for a temperature 0..1: dark -> red -> orange -> yellow -> white."""
        if T <= 0:
            return 0, 0, 0
        x = T * 255
        if x < 85:
            return x * 3, 0, 0                               # black -> red
        if x < 170:
            return 255, (x - 85) * 2, 0                      # red -> orange/yellow
        w = (x - 170) / 85.0
        return 255, 170 + 85 * w, 255 * w * 0.9              # yellow -> white

    def write(frame):
        for env_i in range(NUM_LEDS):
            r, g, b = frame[env_i]
            r = int(max(0, min(255, r)))
            g = int(max(0, min(255, g)))
            b = int(max(0, min(255, b)))
            hsv_values[env_i] = (0.0, 0.0, max(r, g, b) / 255.0)
            # The effects swap red and green for this strip setup
            set_rgb_env(env_i, g, r, b, led_strip)

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Each LED gets its own ember lifetime for this explosion
        ember = [uniform(0.6, 1.6) for _ in range(NUM_LEDS)]
        seq_start = time.ticks_ms()
        total = CHARGE_S + BLAST_S + COOL_S * 4 + REST_S

        while True:
            age = time.ticks_diff(time.ticks_ms(), seq_start) / 1000.0
            if age >= total:
                break
            frame = [(0, 0, 0)] * NUM_LEDS

            if age < CHARGE_S:
                # Charge: a small, brightening, flickering glow at the centre
                k = age / CHARGE_S
                width = 1.0 + 3.0 * k
                level = 0.1 + 0.7 * k * k
                for i in range(NUM_LEDS):
                    d = abs(i - center)
                    if d < width:
                        T = level * (1.0 - d / width) * uniform(0.8, 1.0)
                        frame[i] = heat_rgb(0.55 + 0.45 * T) if T > 0.02 else (0, 0, 0)
                        r, g, b = frame[i]
                        frame[i] = (r * T, g * T, b * T)
            else:
                blast_age = age - CHARGE_S
                kb = min(1.0, blast_age / BLAST_S)
                front = half * (1.0 - (1.0 - kb) ** 2.5)     # fast, then slowing
                for i in range(NUM_LEDS):
                    d = abs(i - center)
                    if d > front + 1.5:
                        continue
                    if d > front:
                        T = 1.0 - (d - front) / 1.5          # soft leading edge
                        weight = T
                        T = 1.0
                    else:
                        # When did the front reach this LED? (invert the easing)
                        reach = BLAST_S * (1.0 - (1.0 - min(1.0, d / half)) ** 0.4)
                        since = max(0.0, blast_age - reach)
                        T = math.exp(-since / COOL_S)
                        T *= 1.0 - 0.4 * d / half            # weaker further out
                        # Embers: flicker, and die out at their own time
                        if since > ember[i] * COOL_S * 2:
                            T *= max(0.0, 1.0 - (since - ember[i] * COOL_S * 2) / COOL_S)
                        if since > 0.3:
                            T *= uniform(0.7, 1.0)
                        weight = 1.0
                    r, g, b = heat_rgb(T)
                    frame[i] = (r * weight, g * weight, b * weight)

            write(frame)
            time.sleep(0.01)

    return hsv_values

def effect_54(hsv_values, led_strip):
    """Larson Scanner (Knight Rider): a short bright red eye sweeps back and
    forth, easing as it turns, leaving a fading afterglow behind it."""
    HUE = 0.33              # red on this strip
    PASS_S = 1.5            # seconds per sweep, any strip length
    EYE_HALF = 2.0          # eye half-width in LEDs (~4 LEDs lit)
    TRAIL_S = 0.35          # afterglow falls to 10% in this time
    keep_per_s = 0.1 ** (1.0 / TRAIL_S)

    glow = [0.0] * NUM_LEDS
    span = NUM_LEDS - 1
    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        # Ping-pong position with cosine easing: slows down as it turns
        phase = (t / PASS_S) % 2.0
        if phase > 1.0:
            phase = 2.0 - phase
        x = span * (0.5 - 0.5 * math.cos(math.pi * phase))

        # Afterglow fades; the eye relights where it is now
        keep = keep_per_s ** dt
        lo = int(x - EYE_HALF) - 1
        hi = int(x + EYE_HALF) + 1
        for i in range(NUM_LEDS):
            g = glow[i] * keep
            if lo <= i <= hi:
                v = 1.0 - abs(i - x) / EYE_HALF
                if v > g:
                    g = v
            glow[i] = g
            hsv_values[i] = (HUE, 1.0, g)
            led_strip.set_hsv(i, HUE, 1.0, g)

        time.sleep(0.01)

    return hsv_values

def effect_55(hsv_values, led_strip):
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


def effect_56(hsv_values, led_strip):
    """Paint splashes: soft, rounded splashes of colour bloom at random spots,
    each at its own pace, blending where they overlap. Each pass uses a small
    palette of neighbouring shades."""
    num_splashes = max(3, NUM_LEDS // 25)       # 4 on 100 LEDs
    scale = NUM_LEDS / 100.0
    r_min, r_max = 8 * scale, 18 * scale         # final splash radius, LEDs

    # Palette for this pass: three neighbouring shades (real hues, converted
    # for the strip's red/green swap)
    base = uniform(0, 1.0)
    palette = [hsv_to_rgb((1.0 / 3.0 - (base + off)) % 1.0, 1.0, 1.0) for off in (-0.08, 0.0, 0.08)]
    palette_h = [(1.0 / 3.0 - (base + off)) % 1.0 for off in (-0.08, 0.0, 0.08)]

    def new_splash(t, delay=True):
        k = randrange(len(palette))
        radius = uniform(r_min, r_max)
        grow = uniform(8.0, 25.0) * max(0.5, scale)     # LEDs per second: own pace
        return {
            "c": uniform(0, NUM_LEDS - 1),
            "born": t + (uniform(0.0, 0.5) if delay else uniform(-1.0, 0.0)),
            "radius": radius,
            "grow_s": radius / grow,
            "fade_s": uniform(0.6, 1.2),
            "rgb": palette[k],
            "hue": palette_h[k],
        }

    splashes = [new_splash(0.0, delay=False) for _ in range(num_splashes)]
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS
        top_v = [0.0] * NUM_LEDS
        top_h = [0.0] * NUM_LEDS

        for k in range(num_splashes):
            sp = splashes[k]
            age = t - sp["born"]
            if age < 0:
                continue
            if age > sp["grow_s"] + sp["fade_s"]:
                splashes[k] = new_splash(t)
                continue
            # Bloom: grows quickly then eases; fades after it finishes growing
            g = min(1.0, age / sp["grow_s"])
            r = sp["radius"] * (1.0 - (1.0 - g) ** 2)
            level = 1.0 if age <= sp["grow_s"] else 1.0 - (age - sp["grow_s"]) / sp["fade_s"]
            level *= 0.85
            if r <= 0.5:
                r = 0.5
            cr, cg, cb = sp["rgb"]
            lo = max(0, int(sp["c"] - r) - 1)
            hi = min(NUM_LEDS - 1, int(sp["c"] + r) + 1)
            for i in range(lo, hi + 1):
                d = abs(i - sp["c"]) / r
                if d >= 1.0:
                    continue
                v = level * (0.5 + 0.5 * math.cos(math.pi * d))     # soft rounded edge
                # Additive: overlapping splashes blend their colours
                fr[i] += cr * v
                fg[i] += cg * v
                fb[i] += cb * v
                if v > top_v[i]:
                    top_v[i] = v
                    top_h[i] = sp["hue"]

        # Write the finished frame, each LED once (no wrap-around at the ends)
        for i in range(NUM_LEDS):
            r = min(1.0, fr[i])
            g = min(1.0, fg[i])
            b = min(1.0, fb[i])
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))
            hsv_values[i] = (top_h[i], 1.0, max(r, g, b))

        time.sleep(0.02)

    return hsv_values

# 
def effect_57(hsv_values, led_strip):
    """Colorful Larson Scanner: the effect 54 scanner (short bright eye,
    fading afterglow, eased turns) whose eye moves to a neighbouring shade
    at every turn, so the afterglow briefly shows two tones."""
    PASS_S = 1.5            # seconds per sweep, any strip length
    EYE_HALF = 2.0          # eye half-width in LEDs (~4 LEDs lit)
    TRAIL_S = 0.35          # afterglow falls to 10% in this time
    HUE_STEP = 0.07         # colour change at each turn (neighbouring shade)
    keep_per_s = 0.1 ** (1.0 / TRAIL_S)

    base_hue = uniform(0, 1.0)
    glow = [0.0] * NUM_LEDS
    glow_hue = [base_hue] * NUM_LEDS
    span = NUM_LEDS - 1
    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        sweep = int(t / PASS_S)                 # which sweep we are on
        eye_hue = (base_hue + sweep * HUE_STEP) % 1.0

        # Ping-pong position with cosine easing: slows down as it turns
        phase = (t / PASS_S) % 2.0
        if phase > 1.0:
            phase = 2.0 - phase
        x = span * (0.5 - 0.5 * math.cos(math.pi * phase))

        keep = keep_per_s ** dt
        lo = int(x - EYE_HALF) - 1
        hi = int(x + EYE_HALF) + 1
        for i in range(NUM_LEDS):
            g = glow[i] * keep
            if lo <= i <= hi:
                v = 1.0 - abs(i - x) / EYE_HALF
                if v > g:
                    g = v
                    glow_hue[i] = eye_hue       # afterglow keeps its old colour
            glow[i] = g
            hsv_values[i] = (glow_hue[i], 1.0, g)
            led_strip.set_hsv(i, glow_hue[i], 1.0, g)

        time.sleep(0.01)

    return hsv_values

def effect_58(hsv_values, led_strip):
    """Rapid Fireworks with crackle: small, quick bursts go off all over the
    strip, throwing short sparks that droop and fade, then finish with soft
    gold crackles. No white flashes or hard blinks, so it never strobes."""
    gap_min, gap_max = 0.25, 0.6               # seconds between bursts
    spark_speed = max(8.0, NUM_LEDS * 0.15)    # LEDs/s
    gravity = NUM_LEDS * 0.10                  # gentle droop towards env 0
    drag_keep = 0.2                            # speed left after 1 s
    bloom_s = 0.15                             # soft coloured bloom at the burst

    def real(h, sat=1.0):
        return hsv_to_rgb((1.0 / 3.0 - h) % 1.0, sat, 1.0)   # R/G-swap aware
    GOLD = real(0.11, 0.75)

    bursts = []
    crackles = []
    start_time = time.ticks_ms()
    last = start_time
    next_burst = 0.1

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        if t >= next_burst:
            rgb = real(uniform(0, 1.0))
            c = uniform(0.15, 0.95) * (NUM_LEDS - 1)
            sparks = []
            for _ in range(randrange(4, 8)):
                sparks.append({"pos": c, "vel": uniform(-1.0, 1.0) * spark_speed,
                               "life": uniform(0.6, 1.0), "crackled": False})
            bursts.append({"born": t, "c": c, "rgb": rgb, "sparks": sparks})
            next_burst = t + uniform(gap_min, gap_max)

        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS

        def add(i, rgb, v):
            if 0 <= i < NUM_LEDS and v > 0:
                fr[i] += rgb[0] * v
                fg[i] += rgb[1] * v
                fb[i] += rgb[2] * v

        drag = drag_keep ** dt
        alive = []
        for bu in bursts:
            age = t - bu["born"]
            if age < bloom_s:
                # soft bloom in the burst's own colour (no white flash)
                x = age / bloom_s
                v = 0.8 * math.sin(math.pi * x)
                ci = int(bu["c"])
                add(ci, bu["rgb"], v)
                add(ci - 1, bu["rgb"], v * 0.4)
                add(ci + 1, bu["rgb"], v * 0.4)
            live = False
            for sp in bu["sparks"]:
                if age >= sp["life"]:
                    if not sp["crackled"]:
                        sp["crackled"] = True
                        # finish with a few soft gold crackles near where it died
                        for _ in range(randrange(1, 4)):
                            crackles.append({"pos": int(sp["pos"] + uniform(-1.5, 1.5)),
                                             "born": t + uniform(0.0, 0.25),
                                             "life": uniform(0.2, 0.4)})
                    continue
                live = True
                sp["vel"] = sp["vel"] * drag - gravity * dt
                sp["pos"] += sp["vel"] * dt
                k = age / sp["life"]
                v = (1.0 - k) ** 1.5
                i = int(sp["pos"])
                add(i, bu["rgb"], v)
                add(i + (1 if sp["vel"] < 0 else -1), bu["rgb"], v * 0.3)
            if live:
                alive.append(bu)
        bursts = alive

        # Soft crackles: quick smooth twinkle up and down
        still = []
        for cr in crackles:
            age = t - cr["born"]
            if age >= cr["life"]:
                continue
            still.append(cr)
            if age >= 0:
                add(cr["pos"], GOLD, 0.6 * math.sin(math.pi * age / cr["life"]))
        crackles = still

        # Write the finished frame, each LED once (env -> physical)
        for env_i in range(NUM_LEDS):
            r = min(1.0, fr[env_i])
            g = min(1.0, fg[env_i])
            b = min(1.0, fb[env_i])
            hsv_values[env_i] = (0.0, 0.0, max(r, g, b))
            set_rgb_env(env_i, int(r * 255), int(g * 255), int(b * 255), led_strip)

        time.sleep(0.01)

    return hsv_values

def effect_59(hsv_values, led_strip):
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

def effect_60(hsv_values, led_strip):
    """Ice Meteor Storm: thin, fast blue-white meteors fall towards the base at
    different speeds, leaving icy glints that twinkle out; now and then a
    cluster arrives together (orientation-aware)."""
    meteor_rate = 1.5                          # meteors per second on average
    tail_len = max(5, NUM_LEDS // 16)          # short, sharp tails
    fall_min_s, fall_max_s = 1.0, 1.8          # seconds to fall the full strip
    glint_chance = 0.25                        # per LED a meteor passes

    def ice():
        # Real icy blues, converted for the strip's red/green swap
        return hsv_to_rgb((1.0 / 3.0 - uniform(0.53, 0.60)) % 1.0, uniform(0.2, 0.45), 1.0)
    GLINT = hsv_to_rgb((1.0 / 3.0 - 0.58) % 1.0, 0.15, 1.0)

    meteors = []
    glints = []

    def spawn(t, delay=0.0):
        meteors.append({
            "head": NUM_LEDS - 1 + uniform(0, tail_len),
            "speed": NUM_LEDS / uniform(fall_min_s, fall_max_s),
            "start": t + delay,
            "rgb": ice(),
            "last": None,
        })

    start_time = time.ticks_ms()
    last = start_time
    next_cluster = uniform(3.0, 6.0)

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        if random() < meteor_rate * dt:
            spawn(t)
        if t >= next_cluster:
            for _ in range(randrange(3, 5)):
                spawn(t, uniform(0.0, 0.25))
            next_cluster = t + uniform(3.0, 6.0)

        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS

        def add(i, rgb, v):
            if 0 <= i < NUM_LEDS and v > 0:
                fr[i] += rgb[0] * v
                fg[i] += rgb[1] * v
                fb[i] += rgb[2] * v

        alive = []
        for m in meteors:
            if t < m["start"]:
                alive.append(m)
                continue
            m["head"] -= m["speed"] * dt
            head = int(m["head"])
            if head + tail_len < 0:
                continue
            alive.append(m)
            # Icy glints left behind on the LEDs it just passed
            prev = m["last"] if m["last"] is not None else head + 1
            for i in range(head + 1, prev + 1):
                if 0 <= i < NUM_LEDS and random() < glint_chance:
                    glints.append({"pos": i, "born": t + uniform(0.0, 0.15),
                                   "life": uniform(0.3, 0.6)})
            m["last"] = head
            # Head + short tail above it
            for k in range(tail_len):
                add(head + k, m["rgb"], (1.0 - k / tail_len) ** 1.8)
        meteors = alive

        still = []
        for g in glints:
            age = t - g["born"]
            if age >= g["life"]:
                continue
            still.append(g)
            if age >= 0:
                add(g["pos"], GLINT, 0.4 * math.sin(math.pi * age / g["life"]))
        glints = still

        for env_i in range(NUM_LEDS):
            r = min(1.0, fr[env_i])
            g = min(1.0, fg[env_i])
            b = min(1.0, fb[env_i])
            hsv_values[env_i] = (0.0, 0.0, max(r, g, b))
            set_rgb_env(env_i, int(r * 255), int(g * 255), int(b * 255), led_strip)

        time.sleep(0.01)

    return hsv_values

def effect_61(hsv_values, led_strip):
    """Floating Lanterns: warm orange paper lanterns rise slowly from the base,
    bobbing and flickering softly inside, and fade away near the top
    (orientation-aware)."""
    max_lanterns = max(3, NUM_LEDS // 25)       # 4 on 100 LEDs
    scale = NUM_LEDS / 100.0
    gap_min, gap_max = 1.5, 3.5                 # seconds between launches
    half_width = 1.5                            # lantern size (about 3 LEDs)
    fade_in_s = 0.6
    fade_zone = 0.3                             # top share of the strip where they fade

    def warm():
        # Real warm orange, converted for the strip's red/green swap
        return hsv_to_rgb((1.0 / 3.0 - uniform(0.06, 0.09)) % 1.0, 0.9, 1.0)

    lanterns = []
    start_time = time.ticks_ms()
    last = start_time
    next_launch = 0.0

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        if t >= next_launch and len(lanterns) < max_lanterns:
            lanterns.append({
                "y": 0.0,
                "speed": uniform(3.0, 7.0) * max(0.5, scale),   # LEDs per second
                "born": t,
                "phase": uniform(0, 2 * math.pi),
                "bob": uniform(1.0, 2.0),                       # rad/s
                "flick": uniform(5.0, 9.0),
                "peak": uniform(0.65, 0.95),
                "rgb": warm(),
            })
            next_launch = t + uniform(gap_min, gap_max)

        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS
        fade_start = NUM_LEDS * (1.0 - fade_zone)

        alive = []
        for L in lanterns:
            L["y"] += L["speed"] * dt
            if L["y"] >= NUM_LEDS:
                continue
            alive.append(L)
            age = t - L["born"]
            y = L["y"] + 0.8 * math.sin(age * L["bob"] + L["phase"])     # gentle bob
            v = L["peak"]
            v *= min(1.0, age / fade_in_s)                                # light up at the base
            if y > fade_start:                                            # fade away near the top
                v *= max(0.0, 1.0 - (y - fade_start) / (NUM_LEDS - fade_start))
            # soft flicker of the flame inside
            v *= 0.85 + 0.15 * math.sin(age * L["flick"] + L["phase"]) * math.sin(age * L["flick"] * 1.7)
            r, g, b = L["rgb"]
            lo = int(y - half_width) - 1
            hi = int(y + half_width) + 1
            for i in range(max(0, lo), min(NUM_LEDS, hi + 1)):
                d = abs(i - y) / (half_width + 0.5)
                if d < 1.0:
                    w = 0.5 + 0.5 * math.cos(math.pi * d)
                    fr[i] += r * v * w
                    fg[i] += g * v * w
                    fb[i] += b * v * w
        lanterns = alive

        for env_i in range(NUM_LEDS):
            r = min(1.0, fr[env_i])
            g = min(1.0, fg[env_i])
            b = min(1.0, fb[env_i])
            hsv_values[env_i] = (0.0, 0.0, max(r, g, b))
            set_rgb_env(env_i, int(r * 255), int(g * 255), int(b * 255), led_strip)

        time.sleep(0.02)

    return hsv_values

def effect_62(hsv_values, led_strip):
    """Fireflies: soft coloured fireflies in the dark, each slowly glowing up,
    drifting a little and fading away, then resting before glowing again
    somewhere new in a new colour."""
    num_flies = max(5, NUM_LEDS // 12)        # 8 on 100 LEDs

    def fly_rgb():
        # Any colour, slightly soft (saturation 0.8)
        return hsv_to_rgb(uniform(0, 1.0), 0.8, 1.0)

    def new_fly(t, first=False):
        return {
            "pos": uniform(0, NUM_LEDS - 1),
            "vel": uniform(-1.5, 1.5),            # LEDs per second, gentle drift
            "start": t + (uniform(0.0, 3.0) if first else uniform(0.5, 4.0)),
            "rise": uniform(0.4, 0.8),
            "hold": uniform(0.2, 0.6),
            "fade": uniform(0.8, 1.5),
            "peak": uniform(0.6, 1.0),
            "rgb": fly_rgb(),
        }

    flies = [new_fly(0.0, first=True) for _ in range(num_flies)]
    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        fr = [0.0] * NUM_LEDS
        fg = [0.0] * NUM_LEDS
        fb = [0.0] * NUM_LEDS

        for k in range(num_flies):
            f = flies[k]
            age = t - f["start"]
            if age < 0:
                continue                           # resting in the dark
            total = f["rise"] + f["hold"] + f["fade"]
            if age >= total:
                flies[k] = new_fly(t)              # rest, then glow somewhere new
                continue

            # Smooth glow envelope: ease up, hold, ease down
            if age < f["rise"]:
                x = age / f["rise"]
                v = x * x * (3 - 2 * x)
            elif age < f["rise"] + f["hold"]:
                v = 1.0
            else:
                x = 1.0 - (age - f["rise"] - f["hold"]) / f["fade"]
                v = x * x * (3 - 2 * x)
            v *= f["peak"]

            # Drift, wandering slightly
            f["vel"] += uniform(-2.0, 2.0) * dt
            f["vel"] = max(-2.0, min(2.0, f["vel"]))
            f["pos"] = max(0.0, min(NUM_LEDS - 1.0, f["pos"] + f["vel"] * dt))

            # Soft glow spread over the two nearest LEDs, with a faint halo
            i0 = int(f["pos"])
            frac = f["pos"] - i0
            r, g, b = f["rgb"]
            for idx, w in ((i0, 1.0 - frac), (i0 + 1, frac), (i0 - 1, 0.15), (i0 + 2, 0.15)):
                if 0 <= idx < NUM_LEDS:
                    fr[idx] += r * v * w
                    fg[idx] += g * v * w
                    fb[idx] += b * v * w

        for i in range(NUM_LEDS):
            r = min(1.0, fr[i])
            g = min(1.0, fg[i])
            b = min(1.0, fb[i])
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))
            hsv_values[i] = (0.0, 0.0, max(r, g, b))

        time.sleep(0.02)

    return hsv_values

def effect_63(hsv_values, led_strip):
    """Pulsating Red and White effect with smooth transitions and breathing brightness."""
    pulse_speed = 1.5   # radians per second: one breath about every 4 s
                        # (was 0.05 per s from boot: a 2-minute cycle that
                        # could leave the strip dark for a whole run)
    min_brightness = 0.15
    move_speed = 0.1    # Speed at which the colors move across the strip

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Seconds since the effect started; starts at full brightness
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        brightness = min_brightness + (1 - min_brightness) * (1 + math.cos(elapsed * pulse_speed)) / 2

        for t in range(NUM_LEDS):
            # Alternate between red and white based on position
            if t % 2 == 0:
                hue = 0.33  # Red
            else:
                hue = 0.0  # White with lower saturation

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


def effect_64(hsv_values, led_strip):
    """Colorful Snake: a snake with a bright head and a tapering, rippling
    body slithers along the strip, changing speed and turning now and then.
    It turns round at the ends, takes a new colour and grows a little at each
    turn, then resets."""
    base_len = max(10, NUM_LEDS // 8)          # 12 LEDs on 100
    max_len = int(base_len * 2.5)
    grow = 2
    base_speed = max(6.0, NUM_LEDS / 10.0)     # LEDs per second (10 on 100)
    turn_chance = 0.15                         # random turns per second
    HUE_SPAN = 0.12                            # head-to-tail colour gradient

    def strip_hue(real_h):
        return (1.0 / 3.0 - real_h) % 1.0      # real hue -> strip (R/G swap)

    head = uniform(base_len, NUM_LEDS - 1.0)
    direction = choice([-1, 1])
    length = base_len
    real_base = uniform(0, 1.0)
    trail = [head]                             # past head positions, newest first

    def turn():
        nonlocal direction, length, real_base
        direction = -direction
        real_base = (real_base + uniform(0.08, 0.2)) % 1.0     # neighbouring colour
        length += grow
        if length > max_len:
            length = base_len

    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        # Speed wanders between ~60% and ~140%
        speed = base_speed * (1.0 + 0.4 * math.sin(t * 0.9) * math.sin(t * 0.37 + 1.0))
        if random() < turn_chance * dt:
            turn()
        head += direction * speed * dt
        if head < 0:
            head = -head
            turn()
        elif head > NUM_LEDS - 1:
            head = 2 * (NUM_LEDS - 1) - head
            turn()

        # Record the path so the body follows it, folding back at turns
        if abs(head - trail[0]) >= 0.5:
            trail.insert(0, head)
            if len(trail) > max_len * 2 + 4:
                trail.pop()

        frame_v = [0.0] * NUM_LEDS
        frame_h = [0.0] * NUM_LEDS
        frame_s = [1.0] * NUM_LEDS
        points = [head] + trail[1:length * 2]   # trail samples are ~0.5 LED apart
        n = len(points)
        for k in range(n):
            seg = k / 2.0                        # LEDs behind the head
            if seg > length:
                break
            f = seg / length
            v = 0.9 * (1.0 - f) ** 0.7
            v *= 0.8 + 0.2 * math.sin(seg * 1.3 - t * 6.0)    # segmented ripple
            sat = 1.0
            if k == 0:
                v, sat = 1.0, 0.6                # bright, paler head
            i = int(points[k] + 0.5)
            if 0 <= i < NUM_LEDS and v > frame_v[i]:
                frame_v[i] = v
                frame_h[i] = strip_hue(real_base + HUE_SPAN * f)
                frame_s[i] = sat

        for i in range(NUM_LEDS):
            hsv_values[i] = (frame_h[i], frame_s[i], frame_v[i])
            led_strip.set_hsv(i, frame_h[i], frame_s[i], frame_v[i])

        time.sleep(0.02)

    return hsv_values

def effect_65(hsv_values, led_strip):
    """Rising Bubbles: soft aqua bubbles of different sizes rise from the base
    through dim water, wobbling as they go, and pop near the top
    (orientation-aware)."""
    scale = NUM_LEDS / 100.0
    bubble_rate = 1.2 * max(0.6, scale)     # new bubbles per second
    pop_s = 0.18

    def strip(real_h, sat, v=1.0):
        return hsv_to_rgb((1.0 / 3.0 - real_h) % 1.0, sat, v)   # R/G-swap aware
    WATER = strip(0.55, 0.9)                # deep teal-blue water
    WATER_V = 0.14
    POP = strip(0.5, 0.2)                   # pale pop flash

    bubbles = []
    pops = []
    start_time = time.ticks_ms()
    last = start_time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        now = time.ticks_ms()
        t = time.ticks_diff(now, start_time) / 1000.0
        dt = time.ticks_diff(now, last) / 1000.0
        last = now

        if random() < bubble_rate * dt:
            size = uniform(0.8, 2.5)                     # radius in LEDs
            bubbles.append({
                "y": -size,
                "size": size,
                "speed": (4.0 + 3.0 * size) * max(0.6, scale),   # big ones rise faster
                "wob": uniform(2.0, 4.0),
                "phase": uniform(0, 2 * math.pi),
                "pop_at": uniform(0.7, 0.95) * (NUM_LEDS - 1),
                "rgb": strip(uniform(0.46, 0.52), uniform(0.5, 0.7)),
            })

        # Water background
        fr = [WATER[0] * WATER_V] * NUM_LEDS
        fg = [WATER[1] * WATER_V] * NUM_LEDS
        fb = [WATER[2] * WATER_V] * NUM_LEDS

        def add(i, rgb, v):
            if 0 <= i < NUM_LEDS and v > 0:
                fr[i] += rgb[0] * v
                fg[i] += rgb[1] * v
                fb[i] += rgb[2] * v

        alive = []
        for bu in bubbles:
            bu["y"] += bu["speed"] * dt
            if bu["y"] >= bu["pop_at"]:
                pops.append({"y": bu["y"], "born": t})
                continue
            alive.append(bu)
            y = bu["y"] + 0.4 * math.sin(t * bu["wob"] + bu["phase"])   # wobble
            r = bu["size"]
            lo = int(y - r) - 1
            hi = int(y + r) + 1
            for i in range(lo, hi + 1):
                d = abs(i - y) / (r + 0.5)
                if d >= 1.0:
                    continue
                if r > 1.5:
                    v = 0.35 + 0.55 * d          # bigger bubbles: bright rim, clear middle
                    v *= 1.0 - max(0.0, d - 0.8) / 0.2
                else:
                    v = 0.8 * (1.0 - d)          # small bubbles: a soft dot
                add(i, bu["rgb"], v)
        bubbles = alive

        still = []
        for pp in pops:
            age = t - pp["born"]
            if age >= pop_s:
                continue
            still.append(pp)
            k = age / pop_s
            spread = 1.0 + 2.0 * k
            for off in range(-3, 4):
                d = abs(off) / spread
                if d < 1.0:
                    add(int(pp["y"]) + off, POP, (1.0 - k) * (1.0 - d) * 0.8)
        pops = still

        for env_i in range(NUM_LEDS):
            r = min(1.0, fr[env_i])
            g = min(1.0, fg[env_i])
            b = min(1.0, fb[env_i])
            hsv_values[env_i] = (0.0, 0.0, max(r, g, b))
            set_rgb_env(env_i, int(r * 255), int(g * 255), int(b * 255), led_strip)

        time.sleep(0.02)

    return hsv_values

def effect_66(hsv_values, led_strip):
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

def effect_67(hsv_values, led_strip):
    """Thunderstorm: dark blue-grey clouds roll slowly along the strip; every
    few seconds lightning strikes a stretch of it with a sharp flash and a few
    after-flickers, or sheet lightning glows softly across the clouds."""
    def strip(real_h, sat):
        return hsv_to_rgb((1.0 / 3.0 - real_h) % 1.0, sat, 1.0)   # R/G-swap aware
    CLOUD = strip(0.62, 0.35)
    BOLT = strip(0.62, 0.08)          # white with a hint of blue
    SHEET = strip(0.70, 0.30)         # pale violet-blue
    two_pi = 2 * math.pi

    def new_strike(t):
        if random() < 0.7:
            # Bolt: a sharp flash on a stretch of strip, then after-flickers
            width = uniform(NUM_LEDS / 10.0, NUM_LEDS / 4.0)
            flashes = [(0.0, 1.0, 0.08)]
            off = 0.0
            for _ in range(randrange(2, 5)):
                off += uniform(0.08, 0.2)
                flashes.append((off, uniform(0.4, 0.9), uniform(0.03, 0.06)))
            return {"kind": "bolt", "born": t, "c": uniform(0, NUM_LEDS - 1),
                    "w": width, "flashes": flashes, "end": off + 0.5,
                    "jag": [uniform(0.6, 1.0) for _ in range(NUM_LEDS)]}
        # Sheet lightning: a soft wide glow that swells once or twice
        swells = randrange(1, 3)
        return {"kind": "sheet", "born": t, "c": uniform(0, NUM_LEDS - 1),
                "w": NUM_LEDS * uniform(0.4, 0.8), "swells": swells,
                "end": 0.6 * swells}

    def gap():
        return uniform(6.0, 10.0) if random() < 0.25 else uniform(2.0, 6.0)

    strike = None
    next_strike = uniform(1.0, 3.0)
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0

        if strike is None and t >= next_strike:
            strike = new_strike(t)
        level = 0.0
        if strike is not None:
            age = t - strike["born"]
            if age > strike["end"]:
                strike = None
                next_strike = t + gap()
            elif strike["kind"] == "bolt":
                for start, inten, dur in strike["flashes"]:
                    d = age - start
                    if d < 0:
                        continue
                    v = inten if d < dur else inten * math.exp(-(d - dur) / 0.05)
                    level = max(level, v)
                # dim afterglow after the main flash
                level = max(level, 0.25 * math.exp(-age / 0.35))
            else:
                k = age / 0.6
                level = 0.5 * math.sin(math.pi * (k % 1.0))

        for i in range(NUM_LEDS):
            # Rolling clouds: two slow waves give shifting dark and lighter patches
            cv = 0.10 + 0.05 * math.sin(i * two_pi / (NUM_LEDS / 2.3) + t * 0.4)                       + 0.04 * math.sin(i * two_pi / (NUM_LEDS / 5.1) - t * 0.7)
            r, g, b = CLOUD[0] * cv, CLOUD[1] * cv, CLOUD[2] * cv
            if level > 0 and strike is not None:
                d = abs(i - strike["c"]) / strike["w"]
                if d < 1.0:
                    w = 0.5 + 0.5 * math.cos(math.pi * d)
                    if strike["kind"] == "bolt":
                        w *= strike["jag"][i]
                        col = BOLT
                    else:
                        col = SHEET
                    v = level * w
                    r += col[0] * v
                    g += col[1] * v
                    b += col[2] * v
            r = min(1.0, r)
            g = min(1.0, g)
            b = min(1.0, b)
            hsv_values[i] = (0.0, 0.0, max(r, g, b))
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))

        time.sleep(0.01)

    return hsv_values

def effect_68(hsv_values, led_strip):
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

def effect_69(hsv_values, led_strip):
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
            set_hsv_env(env_i, h, s, v, led_strip)

        time.sleep(0.02)

    return hsv_values



def effect_70(hsv_values, led_strip):
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


def effect_71(hsv_values, led_strip):
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
def effect_72(hsv_values, led_strip):
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


def effect_73(hsv_values, led_strip):
    """Pond ripples: drops land at random spots on calm water and send gentle
    concentric rings spreading outwards. The rings fade as they spread, and
    where ripples cross they interfere like real water."""
    scale = max(0.5, NUM_LEDS / 100.0)
    ring_speed = 10.0 * scale          # LEDs per second
    wavelength = 5.0 * scale           # LEDs between rings
    k = 2 * math.pi / wavelength
    ring_count = 3.5                   # wavelengths in each ripple packet
    life_s = 3.5                       # a ripple dies out over this time
    drop_gap = (0.8, 2.0)              # seconds between drops
    splash_s = 0.2

    def strip(real_h, sat):
        return hsv_to_rgb((1.0 / 3.0 - real_h) % 1.0, sat, 1.0)   # R/G-swap aware
    WATER = strip(0.57, 0.85)          # calm blue water
    CREST = strip(0.52, 0.35)          # pale aqua light on the crests
    BASE_V = 0.2

    drops = []
    start_time = time.ticks_ms()
    next_drop = 0.2

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        t = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0

        if t >= next_drop:
            drops.append({"c": uniform(0, NUM_LEDS - 1), "born": t, "amp": uniform(0.6, 1.0)})
            next_drop = t + uniform(drop_gap[0], drop_gap[1])
        drops = [d for d in drops if t - d["born"] < life_s]

        for i in range(NUM_LEDS):
            h = 0.0                    # water surface height at this LED
            splash = 0.0
            for d in drops:
                age = t - d["born"]
                dist = abs(i - d["c"])
                front = ring_speed * age
                behind = front - dist   # how far inside the packet this LED is
                if 0.0 <= behind < ring_count * wavelength:
                    # Rings: a sine packet, soft at both ends, weaker as it spreads
                    env = math.sin(math.pi * behind / (ring_count * wavelength))
                    fade = (1.0 - age / life_s) / (1.0 + dist / (8.0 * scale))
                    h += d["amp"] * env * fade * math.cos(k * behind)
                if age < splash_s and dist < 1.5:
                    splash = max(splash, (1.0 - age / splash_s) * (1.0 - dist / 1.5))

            crest = max(0.0, h)                      # crests catch the light
            v = BASE_V * max(0.3, 1.0 + 0.8 * h)     # troughs dip, crests lift
            mix = min(1.0, crest * 0.9 + splash)
            r = WATER[0] * v + CREST[0] * mix * 0.7
            g = WATER[1] * v + CREST[1] * mix * 0.7
            b = WATER[2] * v + CREST[2] * mix * 0.7
            r = min(1.0, r)
            g = min(1.0, g)
            b = min(1.0, b)
            hsv_values[i] = (0.0, 0.0, max(r, g, b))
            led_strip.set_rgb(i, int(r * 255), int(g * 255), int(b * 255))

        time.sleep(0.01)

    return hsv_values



def effect_74(hsv_values, led_strip):
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


def effect_75(hsv_values, led_strip):
    """Random colour blend: each round picks 2-6 random colours, blends them
    smoothly along the strip (the short way round the colour wheel, no seams)
    and rolls a brightness wave through them while the palette drifts.
    Time-based, so it is smooth whatever the random speeds."""
    start_time = time.ticks_ms()

    def blend(h1, h2, r):
        d = ((h2 - h1 + 0.5) % 1.0) - 0.5      # shortest way round the wheel
        return (h1 + d * r) % 1.0

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # New random round
        wave_speed = uniform(0.5, 3.0)          # rad/s of the brightness wave
        hue_drift = uniform(0.02, 0.2)          # palette turns per second
        level = uniform(0.4, 1.0) * uniform(0.7, 0.95)
        num_colors = choice([2, 3, 4, 5, 6])
        hues = [randrange(360) / 360.0 for _ in range(num_colors)]
        round_s = uniform(6.0, 12.0)
        section = NUM_LEDS / float(num_colors)  # fractional: no seam at the end
        round_start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
            rt = time.ticks_diff(time.ticks_ms(), round_start) / 1000.0
            if rt >= round_s:
                break
            shift = rt * hue_drift
            for i in range(NUM_LEDS):
                x = i / section
                k = int(x) % num_colors
                ratio = x - int(x)
                ratio = ratio * ratio * (3 - 2 * ratio)          # soft transitions
                hue = (blend(hues[k], hues[(k + 1) % num_colors], ratio) + shift) % 1.0
                brightness = (1 + math.sin(i * 2 * math.pi / NUM_LEDS + rt * wave_speed)) / 2 * level
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hue, 1.0, brightness)

            time.sleep(0.02)

    return hsv_values


def effect_76(hsv_values, led_strip):
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



def effect_77(hsv_values, led_strip):
    """Random formula wave: each round picks random colours (a blend of 1-4
    colours, or a moving rainbow), a speed and one of four brightness
    patterns. Time-based and smooth throughout; colours blend the short way
    round the colour wheel."""
    two_pi = 2 * math.pi
    start_time = time.ticks_ms()
    direction = choice([-1, 1])

    def blend(h1, h2, r):
        d = ((h2 - h1 + 0.5) % 1.0) - 0.5      # shortest way round the wheel
        return (h1 + d * r) % 1.0

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # New random round
        w = uniform(0.5, 3.0)                   # rad/s
        rot = uniform(0.05, 0.25)               # turns/s for the rotating half
        level = uniform(0.5, 1.0) * uniform(0.8, 0.99)
        rainbow = randrange(5) == 0
        rainbow_drift = uniform(0.02, 0.1)      # turns/s
        num_hues = choice([1, 2, 3, 4])
        hues = [randrange(360) / 360.0 for _ in range(num_hues)]
        pattern = randrange(4)
        round_s = uniform(8.0, 15.0)
        section = NUM_LEDS / float(max(1, num_hues - 1)) if num_hues > 1 else NUM_LEDS
        round_start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
            t = time.ticks_diff(time.ticks_ms(), round_start) / 1000.0
            if t >= round_s:
                break
            for i in range(NUM_LEDS):
                x = i / NUM_LEDS
                # Colour
                if rainbow:
                    hue = (x + t * rainbow_drift) % 1.0
                elif num_hues == 1:
                    hue = hues[0]
                else:
                    pos = i / section
                    k = min(int(pos), num_hues - 2)
                    r = pos - k
                    r = r * r * (3 - 2 * r)
                    hue = blend(hues[k], hues[k + 1], r)

                # Brightness patterns (all kept within 0..1)
                if pattern == 0:      # rolling wave
                    b = 0.5 + 0.5 * math.sin(two_pi * x + direction * w * t)
                elif pattern == 1:    # rotating half, with soft edges
                    c = math.cos(two_pi * (x + direction * rot * t))
                    b = max(0.0, min(1.0, 0.5 + 1.5 * c)) * 0.75
                elif pattern == 2:    # fixed wave whose strength pulses
                    b = 0.5 + 0.5 * math.sin(two_pi * x) * (0.5 + 0.5 * math.sin(w * t))
                else:                 # slow drifting wave
                    b = 0.5 - 0.5 * math.sin(two_pi * x + direction * 0.25 * w * t)

                v = b * level
                hsv_values[i] = (hue, 1.0, v)
                led_strip.set_hsv(i, hue, 1.0, v)

            time.sleep(0.02)

        # Occasionally reverse the direction
        if randrange(100) < 5:
            direction = -direction

    return hsv_values
