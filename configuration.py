# -----------------------------
# LED STRIP / SETUP
# -----------------------------

NUM_LEDS = 66
# initial global brightness
BRIGHTNESS = 0.8

# -----------------------------
# ORIENTATION CONTROL
# -----------------------------
# "BOTTOM" = 2350W is at the bottom, strip goes up
# "TOP"    = 2350W is at the top, strip goes down
#ORIENTATION = "TOP"  # or "TOP"
ORIENTATION = "BOTTOM"  # or "TOP"

# Many effects use this timeout in their while-loops
#TIMEOUT_DURATION = 20000  # milliseconds (8 seconds per effect, tweak as you like)

# Many effects use this timeout in their while-loops
MIN_EFFECT_DURATION = 6000    # 6 seconds
MAX_EFFECT_DURATION = 40000   # 40 seconds
TIMEOUT_DURATION = MIN_EFFECT_DURATION  # gets overridden for timed effects

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