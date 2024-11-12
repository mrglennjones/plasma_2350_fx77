import plasma
from plasma import plasma2040
from pimoroni import RGBLED
import time
import math
from random import randrange, uniform, choice
import gc  # Import garbage collection module

# Set how many LEDs you have
NUM_LEDS = 66

# Define the onboard RGB LED
led = RGBLED(plasma2040.LED_R, plasma2040.LED_G, plasma2040.LED_B)
led.set_rgb(0, 0, 0)  # Start with the LED off

# Pick LED type
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma2040.DAT)  # WS2812 / NeoPixel™ LEDs

# Timeout duration in milliseconds (e.g., 10000 ms = 10 seconds)
TIMEOUT_DURATION = 20000 

# Start updating the LED strip
led_strip.start()

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

# Function to perform a smooth crossfade between effects
def crossfade_effects(effect_from, effect_to, duration=1.0, steps=50):
    gc.collect()
    """Smoothly transitions from one effect to another over the given duration."""
    for step in range(steps):
        blend = step / steps
        for i in range(NUM_LEDS):
            h1, s1, v1 = effect_from[i]
            h2, s2, v2 = effect_to[i]

            h = h1 * (1 - blend) + h2 * blend
            s = s1 * (1 - blend) + s2 * blend
            v = v1 * (1 - blend) + v2 * blend

            led_strip.set_hsv(i, h, s, v)

        time.sleep(duration / steps)

# Effect manager class
class EffectManager:
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.hsv_values = [(0.0, 0.0, 0.0) for _ in range(num_leds)]
        self.current_effect = 0
        self.random_mode = True

    def get_random_timeout_duration(self):
        """Return a random duration between 3 and 20 seconds."""
        return randrange(3000, 20001)

    def run_effect(self, effect_func):
        self.timeout_duration = self.get_random_timeout_duration()
        print(f"Effect {self.current_effect + 1} - Running for {self.timeout_duration / 1000:.2f} seconds")
        start_time = time.ticks_ms()

        while True:  # Continuously run effects without button check
            if time.ticks_diff(time.ticks_ms(), start_time) > self.timeout_duration:
                break
            self.hsv_values = effect_func(self.hsv_values)
            self.update_led_strip()

    def update_led_strip(self):
        for i, (h, s, v) in enumerate(self.hsv_values):
            led_strip.set_hsv(i, h, s, v)

    def select_next_effect(self):
        print(f"Effects list length: {len(effects)}")
        if len(effects) <= 1:
            # If there is only one effect, always select it
            self.current_effect = 0
        elif self.random_mode:
            new_effect = self.current_effect
            # Keep picking until a different effect is chosen
            while new_effect == self.current_effect:
                new_effect = randrange(len(effects))
            self.current_effect = new_effect
        else:
            # Cycle to the next effect in order
            self.current_effect = (self.current_effect + 1) % len(effects)

# Add your effect functions here...


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
    """Smooth Fading Fireworks effect (launching from the opposite end)."""
    firework_speed = 0.3
    explosion_size = 10
    launch_interval = 50
    fade_speed = 0.9
    frame_count = 0

    active_explosions = []

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        if frame_count % launch_interval == 0:
            launch_pos = NUM_LEDS - 1  # Start from the last LED
            explosion_pos = randrange(NUM_LEDS // 2)  # Explosion occurs in the first half
            firework_hue = uniform(0, 1.0)
            firework_phase = "launch"

            # Launch phase
            while firework_phase == "launch":
                if launch_pos < NUM_LEDS - 1:
                    hsv_values[launch_pos + 1] = (0.0, 0.0, 0.0)  # Clear the previous LED
                    led_strip.set_hsv(launch_pos + 1, 0.0, 0.0, 0.0)

                hsv_values[launch_pos] = (firework_hue, 1.0, 1.0)  # Set current LED
                led_strip.set_hsv(launch_pos, firework_hue, 1.0, 1.0)

                launch_pos -= 1  # Move backward

                if launch_pos <= explosion_pos:
                    firework_phase = "explode"
                    active_explosions.append({
                        "position": explosion_pos,
                        "hue": firework_hue,
                        "size": 1,
                        "brightness": 1.0
                    })
                time.sleep(0.05)

        # Explosion phase
        for explosion in active_explosions[:]:
            for j in range(-explosion["size"], explosion["size"]):
                pos = explosion["position"] + j
                if 0 <= pos < NUM_LEDS:
                    brightness = explosion["brightness"] * (1.0 - abs(j) / explosion["size"])
                    hsv_values[pos] = (explosion["hue"], 1.0, brightness)
                    led_strip.set_hsv(pos, hsv_values[pos][0], hsv_values[pos][1], hsv_values[pos][2])

            explosion["size"] += 1
            explosion["brightness"] *= fade_speed

            if explosion["brightness"] < 0.01:
                active_explosions.remove(explosion)

        frame_count += 1
        time.sleep(0.05)
    return hsv_values


def hsv_to_grb(h, s, v):
    """Converts HSV to GRB color space to accommodate the GRB LED strip."""
    r, g, b = hsv_to_rgb(h, s, v)
    return g, r, b  # Swap R and G to fit the GRB color order

def effect_10(hsv_values):
    """Improved Lava Lamp Effect with Smooth, Solid Color Blobs and Blended Overlaps (GRB Compatible)."""
    num_blobs = 3  # Number of blobs in the effect
    base_speed = 0.05  # Base speed for the blobs
    blob_min_size = 8  # Minimum size of the blobs
    blob_max_size = 16  # Maximum size of the blobs
    fade_factor = 0.95  # How quickly the previous color fades
    step_time = 0.02  # Delay between animation steps

    # Initialize blobs with position, size, direction, hue, and speed
    blobs = [
        {
            "position": uniform(0, NUM_LEDS),
            "size": randrange(blob_min_size, blob_max_size),
            "direction": choice([-1, 1]),
            "hue": uniform(0, 1.0),
            "speed": uniform(base_speed, base_speed * 2)
        }
        for _ in range(num_blobs)
    ]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Initialize arrays for blended hue, saturation, and brightness
        blended_hue = [0.0] * NUM_LEDS
        blended_brightness = [0.0] * NUM_LEDS
        total_weight = [0.0] * NUM_LEDS  # Track the sum of brightness weights for blending

        # Fade all LEDs to create a trailing effect
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            v = v * fade_factor
            hsv_values[i] = (h, s, v)
            r, g, b = hsv_to_grb(h, s, v)
            led_strip.set_rgb(i, r, g, b)

        # Update each blob and calculate blending for overlaps
        for blob in blobs:
            # Update position and reverse direction at strip ends
            blob["position"] += blob["direction"] * blob["speed"]
            if blob["position"] < 0 or blob["position"] >= NUM_LEDS:
                blob["direction"] *= -1
                blob["position"] = max(0, min(NUM_LEDS - 1, blob["position"]))

            # Apply the blob's color and brightness, blending with existing values
            for j in range(-blob["size"] // 2, blob["size"] // 2):
                pos = int(blob["position"] + j)
                if 0 <= pos < NUM_LEDS:
                    distance = abs(j) / (blob["size"] / 2)
                    brightness = max(0, 1.0 - distance)  # Blob brightness decreases from center to edges

                    # Blend the hue and brightness for overlaps
                    blended_hue[pos] += blob["hue"] * brightness
                    blended_brightness[pos] += brightness
                    total_weight[pos] += brightness

        # Set the final blended color for each LED
        for i in range(NUM_LEDS):
            if total_weight[i] > 0:
                # Calculate the average hue and brightness based on the blending
                final_hue = blended_hue[i] / total_weight[i]
                final_brightness = blended_brightness[i] / total_weight[i]
                hsv_values[i] = (final_hue, 1.0, final_brightness)
                r, g, b = hsv_to_grb(final_hue, 1.0, final_brightness)
                led_strip.set_rgb(i, r, g, b)

        time.sleep(step_time)

    return hsv_values

def hsv_to_grb(h, s, v):
    """Converts HSV color space to GRB color space for the LED strip."""
    r, g, b = hsv_to_rgb(h, s, v)
    return g, r, b  # Swap red and green for GRB


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
    """Tetris Block Fall (Top-Down) with Standard Tetris Colors in GRB format and Dispersal."""
    block_colors = [
        {"name": "Cyan",    "rgb": (255, 0, 255)}, 
        {"name": "Yellow",  "rgb": (255, 255, 0)}, 
        {"name": "Purple",  "rgb": (0, 255, 255)}, 
        {"name": "Green",   "rgb": (255, 0, 0)},   
        {"name": "Blue",    "rgb": (0, 0, 255)},   
        {"name": "Red",     "rgb": (0, 255, 0)},   
        {"name": "Orange",  "rgb": (165, 255, 0)}  
    ]
    
    max_block_length = 10
    min_block_length = 3
    frame_delay = 0.05
    stacked_height = 0
    blocks = []

    for i in range(NUM_LEDS):
        hsv_values[i] = (0.0, 0.0, 0.0)
        led_strip.set_rgb(i, 0, 0, 0)

    start_time = time.ticks_ms()

    while stacked_height < NUM_LEDS:
        block = block_colors[randrange(len(block_colors))]
        block_length = randrange(min_block_length, max_block_length + 1)
        
        print(f"Block Color: {block['name']}, Length: {block_length}")

        block_position = NUM_LEDS - 1

        while block_position - block_length + 1 > stacked_height:
            if block_position + 1 < NUM_LEDS:
                for j in range(block_position - block_length + 2, block_position + 2):
                    if 0 <= j < NUM_LEDS:
                        led_strip.set_rgb(j, 0, 0, 0)

            for j in range(block_position, block_position - block_length, -1):
                if 0 <= j < NUM_LEDS:
                    led_strip.set_rgb(j, *block["rgb"])

            block_position -= 1
            time.sleep(frame_delay)

        blocks.append({"start": stacked_height, "end": stacked_height + block_length, "color": block["rgb"]})
        stacked_height += block_length

    print("Blocks stacked. Pausing for 3 seconds...")
    time.sleep(3)

    print("Dispersing blocks...")
    hsv_values = disperse_blocks(blocks, frame_delay, hsv_values)

    return hsv_values

def disperse_blocks(blocks, frame_delay, hsv_values):
    """Disperse blocks randomly after stacking."""
    while blocks:
        for block in blocks:
            speed = uniform(0.02, 0.1)
            if block["start"] > 0:
                for j in range(block["end"] - 1, block["start"] - 1, -1):
                    if j < NUM_LEDS:
                        led_strip.set_rgb(j, 0, 0, 0)
                        if j - 1 >= 0:
                            led_strip.set_rgb(j - 1, *block["color"])

                block["start"] -= 1
                block["end"] -= 1
            else:
                blocks.remove(block)

        time.sleep(frame_delay)
    return hsv_values

def effect_13(hsv_values):
    """Simulates torrential rain with fast-moving blue raindrops on the LED strip."""

    num_drops = 15
    drop_color = (0, 0, 255)
    trail_length = 3
    frame_delay = 0.01
    drops = []

    led_state = [(0, 0, 0) for _ in range(NUM_LEDS)]

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        if len(drops) < num_drops and uniform(0, 1) < 0.5:
            start_pos = randrange(0, NUM_LEDS - 1)
            drops.append({"position": start_pos, "speed": uniform(0.05, 0.15)})

        for i in range(NUM_LEDS):
            led_state[i] = tuple(int(c * 0.7) for c in led_state[i])

        for drop in drops:
            drop_pos = drop["position"]
            speed = drop["speed"]

            for i in range(trail_length):
                pos = int(drop_pos) - i
                if 0 <= pos < NUM_LEDS:
                    brightness = 1.0 - (i / trail_length)
                    led_state[pos] = (
                        max(led_state[pos][0], int(drop_color[0] * brightness)),
                        max(led_state[pos][1], int(drop_color[1] * brightness)),
                        max(led_state[pos][2], int(drop_color[2] * brightness))
                    )

            drop["position"] += speed

        for i in range(NUM_LEDS):
            led_strip.set_rgb(i, *led_state[i])

        drops = [drop for drop in drops if drop["position"] < NUM_LEDS]

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
    """Simulates a natural flame effect: deep red at the base, transitioning to orange, then to yellow."""
    cooling = 40  # Rate at which heat cools down
    sparking = 120  # Frequency of new sparks at the base
    speed_delay = 0.02  # Speed of the flame effect
    heat = [0] * NUM_LEDS  # Initialize heat array

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Step 1: Cool down each LED a little
        for i in range(NUM_LEDS):
            cooldown = randrange(0, ((cooling * 10) // NUM_LEDS) + 2)
            heat[i] = max(0, heat[i] - cooldown)

        # Step 2: Heat drifts upward and diffuses
        for i in range(NUM_LEDS - 3, 0, -1):
            heat[i] = (heat[i - 1] + heat[i - 2] + heat[i - 3]) // 3

        # Step 3: Randomly ignite new sparks near the base
        if randrange(255) < sparking:
            y = randrange(0, 7)  # Position of the new spark, near the base
            heat[y] = min(255, heat[y] + randrange(160, 255))

        # Step 4: Map heat to colors (red -> orange -> yellow)
        for i in range(NUM_LEDS):
            brightness = (heat[i] / 255.0) ** 1.5  # Adjust the brightness curve

            if brightness > 0.8:
                # Yellow: top of the flame
                r = brightness * 255  # Full red
                g = brightness * 255  # Full green
                b = 0  # No blue
            elif brightness > 0.4:
                # Orange: middle of the flame
                r = brightness * 255  # Full red
                g = brightness * 0.5 * 255  # Medium green for orange
                b = 0  # No blue
            else:
                # Red: base of the flame
                r = brightness * 255  # Full red
                g = 0  # No green
                b = 0  # No blue

            # Set the color on the GRB LED strip
            led_strip.set_rgb(NUM_LEDS - 1 - i, int(g), int(r), int(b))  # Note: GRB order

        # Pause briefly to control the speed of the flame
        time.sleep(speed_delay)

    return hsv_values




def effect_16(hsv_values):
    """Simulates a lava drip effect on a GRB LED strip, starting from the top and dripping downward."""

    drip_length = 5
    speed_delay = 0.02
    acceleration = 1.05
    max_brightness = 0.9
    min_brightness = 0.2
    hue = 0.05  # Lava-like red-orange hue
    saturation = 1.0

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        position = 0  # Start from the top
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
                    r, g, b = hsv_to_rgb(hue, saturation, brightness)
                    led_strip.set_rgb(pos, int(r * 255), int(g * 255), int(b * 255))

            position += 1  # Move the drip downward
            speed *= acceleration  # Increase the speed
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
    vortex_speed = 0.15
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

        time.sleep(0.02)

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
    """Matrix effect with cascading green characters falling from bottom to top."""
    trail_length = 10  # Length of the trailing effect
    fade_factor = 0.75  # Fading factor for the trails
    num_trails = 5  # Number of cascading trails

    # Initialize positions and speeds for the trails
    positions = [randrange(NUM_LEDS) for _ in range(num_trails)]
    speeds = [uniform(0.05, 0.2) for _ in range(num_trails)]
    brightness_levels = [0.0] * NUM_LEDS

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Fade all LEDs slightly
        for i in range(NUM_LEDS):
            hsv_values[i] = (hsv_values[i][0], hsv_values[i][1], hsv_values[i][2] * fade_factor)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        # Move and update each trail
        for i in range(num_trails):
            position = positions[i]
            brightness_levels[position] = 1.0  # Set the head of the trail to full brightness

            # Create the trail effect
            for j in range(trail_length):
                trail_pos = position + j  # Move the trail upwards
                if trail_pos < NUM_LEDS:
                    brightness = 1.0 - (j / trail_length)
                    hsv_values[trail_pos] = (0.00, 1.0, brightness * fade_factor)  # Green color (0.00)
                    led_strip.set_hsv(trail_pos, hsv_values[trail_pos][0], hsv_values[trail_pos][1], hsv_values[trail_pos][2])

            positions[i] -= 1  # Move the trail position upwards
            if positions[i] < 0:  # Reset position if it goes above the strip
                positions[i] = NUM_LEDS - 1

        time.sleep(min(speeds))  # Control the speed of the trails

    return hsv_values


def effect_30(hsv_values):
    """Gravitational Wave Ripples: Smooth, undulating ripples that simulate space-time disturbances."""
    ripple_speed = 0.05
    ripple_amplitude = 0.3
    hue_shift_speed = 0.005

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
    """Fire effect with varying intensities."""
    for i in range(NUM_LEDS):
        hue = 0.3 + randrange(-10, 10) / 100.0
        brightness = randrange(50, 100) / 100.0
        hsv_values[i] = (hue, 1.0, brightness)
    return hsv_values

def effect_33(hsv_values):
    """Sparkle effect with random flickers."""
    for i in range(NUM_LEDS):
        hsv_values[i] = (0.0, 0.0, 0.0)
    for i in range(NUM_LEDS):
        if randrange(100) < 10:
            hue = randrange(360) / 360.0
            hsv_values[i] = (hue, 1.0, 1.0)
    return hsv_values

def effect_34(hsv_values):
    """Rotating color bands."""
    band_width = 5
    for i in range(NUM_LEDS):
        hue = ((i // band_width) % 6) / 6.0
        brightness = 1.0 if (i // band_width) % 2 == 0 else 0.5
        hsv_values[i] = (hue, 1.0, brightness)
    return hsv_values

def effect_35(hsv_values):
    """Meteor shower with fading tails that vanish completely, moving from top to bottom."""
    meteor_length = 10  # Length of the meteor's tail
    meteor_speed = 0.1  # Speed of the meteor movement
    fade_rate = 0.85    # Adjusted fade rate for a smoother fade-out

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        # Fade out the existing LED strip values
        for i in range(NUM_LEDS):
            h, s, v = hsv_values[i]
            hsv_values[i] = (h, s, v * fade_rate)
            led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

        # Move the meteor across the strip (from top to bottom)
        for pos in reversed(range(NUM_LEDS)):
            for i in range(meteor_length):
                index = (pos + i) % NUM_LEDS  # Moving downwards (top to bottom)
                brightness = max(0, 1 - ((i + 1) / meteor_length))  # Ensure the tail fades to zero
                hsv_values[index] = (0.33, 1.0, brightness)  # Use 0.33 for a red hue (GRB format)
                led_strip.set_hsv(index, hsv_values[index][0], hsv_values[index][1], hsv_values[index][2])

            time.sleep(meteor_speed)  # Control the speed of the meteor

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
    """Binary counter effect with 3-pixel wide groups, toggling LEDs on and off."""
    counter = 0  # Initialize the binary counter
    group_size = 3  # Each bit controls 3 consecutive LEDs

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS // group_size):
            # Calculate the state of the LED group based on the binary counter
            if counter & (1 << i):
                hue = 0.00  # Green in GRB format
                brightness = 1.0  # LEDs on
            else:
                hue = 0.00  # Ensure hue is still defined
                brightness = 0.0  # LEDs off

            # Set the HSV values for each LED in the group
            for j in range(group_size):
                idx = i * group_size + j
                if idx < NUM_LEDS:
                    hsv_values[idx] = (hue, 1.0, brightness)
                    led_strip.set_hsv(idx, hsv_values[idx][0], hsv_values[idx][1], hsv_values[idx][2])

        counter += 1  # Increment the binary counter
        time.sleep(0.01)  # Reduced delay for faster animation

        # If the counter exceeds the number of LED groups, reset it to keep the effect continuous
        if counter >= (1 << (NUM_LEDS // group_size)):
            counter = 0

    return hsv_values

def effect_40(hsv_values):
    gravity = 0.03  # Gravity to pull the ball upward
    bounce_damping = 0.85
    fade_speed = 0.01
    pause_duration = 1.0

    start_time = time.ticks_ms()  # Record the start time
    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        ball_position = 0.0  # Start at the bottom
        velocity = 0.0  # Initial velocity
        hue = randrange(360) / 360.0  # Random hue for each ball
        ball_bouncing = True  # Flag to keep the ball bouncing

        while ball_bouncing and time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
            # Clear the LED strip
            for i in range(NUM_LEDS):
                hsv_values[i] = (0.0, 0.0, 0.0)

            # Update velocity and position
            velocity += gravity
            ball_position += velocity

            # Check if the ball reaches the top and bounces back
            if ball_position >= NUM_LEDS - 1:
                ball_position = NUM_LEDS - 1  # Clamp the position at the top
                velocity = -velocity * bounce_damping  # Reverse and reduce velocity

                # If the bounce is too small, stop the animation
                if abs(velocity) < 0.01:
                    ball_bouncing = False

                    # Show the ball at the top and fade it out
                    hsv_values[NUM_LEDS - 1] = (hue, 1.0, 1.0)
                    led_strip.set_hsv(NUM_LEDS - 1, hue, 1.0, 1.0)
                    time.sleep(pause_duration)

                    # Fade out effect
                    for brightness in [i / 100 for i in range(100, -1, -1)]:
                        if time.ticks_diff(time.ticks_ms(), start_time) >= TIMEOUT_DURATION:
                            break
                        hsv_values[NUM_LEDS - 1] = (hue, 1.0, brightness)
                        led_strip.set_hsv(NUM_LEDS - 1, hue, 1.0, brightness)
                        time.sleep(fade_speed)
                    break

            # Smoothly interpolate between LEDs
            pos_floor = int(ball_position)
            pos_ceil = min(pos_floor + 1, NUM_LEDS - 1)
            brightness_ceil = ball_position - pos_floor
            brightness_floor = 1.0 - brightness_ceil

            # Set the brightness for both positions
            if 0 <= pos_floor < NUM_LEDS:
                hsv_values[pos_floor] = (hue, 1.0, brightness_floor)
            if 0 <= pos_ceil < NUM_LEDS:
                hsv_values[pos_ceil] = (hue, 1.0, brightness_ceil)

            # Update the LED strip
            for i in range(NUM_LEDS):
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            # Short delay for a smoother animation
            time.sleep(0.02)

        # Make sure the top LED is off before the next drop
        hsv_values[NUM_LEDS - 1] = (0.0, 0.0, 0.0)
        led_strip.set_hsv(NUM_LEDS - 1, 0.0, 0.0, 0.0)

        # Brief pause before the next ball
        time.sleep(0.1)

    return hsv_values



def effect_41(hsv_values):
    """Rotating comet effect that appears from off the end of the LED strip and exits off the start."""
    comet_length = 10  # Length of the comet's tail
    speed = 0.02  # Speed of the comet

    # Color values for the comet's head (initially set to red in GRB format)
    hue = 0.33
    saturation = 1.0
    brightness = 1.0

    total_length = NUM_LEDS + comet_length  # Total length including off-strip space

    start_time = time.ticks_ms()  # Record the start time

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(total_length * 2):  # Loop over the total length, including off-strip
            for i in range(NUM_LEDS):
                # Calculate the reversed position of the comet's head relative to the LED strip
                position = total_length - (t - comet_length)

                # Determine the distance of each LED from the comet's head
                distance = abs(position - i)

                if 0 <= position < NUM_LEDS and distance < comet_length:
                    # Adjust the brightness based on the distance from the comet's head
                    tail_brightness = brightness * (1 - distance / comet_length)
                else:
                    tail_brightness = 0.0  # LEDs outside the comet's range are off

                hsv_values[i] = (hue, saturation, tail_brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            time.sleep(speed)

            # Ensure the tail fades out completely at the start of the strip
            if t == total_length * 2 - 1:
                for i in range(NUM_LEDS):
                    hsv_values[i] = (hue, saturation, 0.0)
                    led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

    return hsv_values


def effect_42(hsv_values):
    """Spiral effect moving up the strip (from bottom to top) with a 66-LED spiral and random side-to-side hue shifts."""
    speed = 0.05  # Speed of the spiral movement
    spiral_length = 66  # Length of the spiral (full strip)
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
    """Wave pulsing up and down the strip."""
    for i in range(NUM_LEDS):
        brightness = (1 + math.sin(i * 2 * math.pi / 100.0)) / 2
        hue = (i * 10) % 360 / 360.0
        hsv_values[i] = (hue, 1.0, brightness)
    return hsv_values

def effect_44(hsv_values):
    """Waterfall effect with random colors."""
    for i in range(NUM_LEDS):
        hue = (i * 30) % 360 / 360.0
        brightness = (1 + math.sin(i * 2 * math.pi / 10.0)) / 2
        hsv_values[i] = (hue, 1.0, brightness)
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
    """Random wave effect with multiple hues."""
    for i in range(NUM_LEDS):
        hue = randrange(360) / 360.0
        brightness = (1 + math.sin(i * 2 * math.pi / 10.0)) / 2
        hsv_values[i] = (hue, 1.0, brightness)
    return hsv_values

def effect_48(hsv_values):
    """Color pulsating wave that moves back and forth across the strip."""
    wave_length = 20  # Length of the wave
    wave_speed = 0.05  # Speed of the wave's movement
    hue_shift = 0.01  # How quickly the hue changes over time

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS * 2):
            for i in range(NUM_LEDS):
                distance = abs((t % NUM_LEDS) - i)
                if distance < wave_length:
                    # Calculate the hue and brightness for each part of the wave
                    hue = (i * hue_shift) % 1.0
                    brightness = (1 + math.sin(distance * math.pi / wave_length)) / 2
                    hsv_values[i] = (hue, 1.0, brightness)
                else:
                    # Set LEDs outside the wave to be off
                    hsv_values[i] = (0.0, 0.0, 0.0)
                
                # Set the LED color
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])

            # Reverse the wave's direction after it reaches the end
            if t == NUM_LEDS:
                wave_speed = -wave_speed

            time.sleep(abs(wave_speed))

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
                hsv_values[i] = (0.0, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
            time.sleep(0.05)
    return hsv_values

def effect_55(hsv_values):
    """Comet Trail"""
    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for t in range(NUM_LEDS):
            for i in range(NUM_LEDS):
                distance = abs(t - i)
                hue = 0.5
                brightness = max(0, 1 - distance / 10)
                hsv_values[i] = (hue, 1.0, brightness)
                led_strip.set_hsv(i, hsv_values[i][0], hsv_values[i][1], hsv_values[i][2])
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
    """Sparkling Waterfall effect with dynamic blue hues and white sparkles."""
    waterfall_speed = 0.05  # Speed of the waterfall movement
    sparkle_chance = 0.1    # Probability of a sparkle occurring
    fade_factor = 0.9       # How quickly the sparkles fade

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < TIMEOUT_DURATION:
        for i in range(NUM_LEDS):
            # Generate a blue hue with slight variations to simulate water
            hue = 0.6  # Blue
            brightness = (1 + math.sin(i * 2 * math.pi / 10.0 + time.ticks_ms() * waterfall_speed / 1000)) / 2
            
            # Apply the blue hue to the waterfall
            hsv_values[i] = (hue, 1.0, brightness * fade_factor)

            # Occasionally add a white sparkle
            if uniform(0, 1) < sparkle_chance:
                hsv_values[i] = (0.0, 0.0, 1.0)  # White sparkle

            # Gradually fade the sparkles
            else:
                hsv_values[i] = (hsv_values[i][0], hsv_values[i][1], hsv_values[i][2] * fade_factor)

        # Update the LED strip with the new HSV values
        for j in range(NUM_LEDS):
            led_strip.set_hsv(j, hsv_values[j][0], hsv_values[j][1], hsv_values[j][2])

        time.sleep(0.02)  # Control the speed of the effect

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
'''
effects = [
    effect_40
    ]
'''
# List of effects
effects = [
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


# Initialize effect manager
manager = EffectManager(NUM_LEDS)

# Main loop to cycle through effects
while True:    
    manager.select_next_effect()
    manager.run_effect(effects[manager.current_effect])
    gc.collect()
    
    

## use the adafruit apds9960 light sensor to detect the darkness

# Initialize the light sensor with a darkness threshold
'''
light_sensor = LightSensor(threshold=10)

while True:
    if light_sensor.is_dark():
        print("It's dark enough, running the lighting effects...")
        
        # Insert your lighting effects code here
        manager.select_next_effect()
        manager.run_effect(effects[manager.current_effect])
    else:
        print("It's too bright, skipping the lighting effects.")

    sleep(0.25)
'''
