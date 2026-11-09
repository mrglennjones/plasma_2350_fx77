# rgb_test.py - find the colour order of the connected LED strip
#
# Run this from Thonny (open it and press F5). It does not need to be saved
# to the board, and it does not replace main.py.
#
# It sends plain RGB with NO colour-order correction and lights the WHOLE
# strip (NUM_LEDS from configuration.py) one colour at a time, 4 seconds each,
# over and over. Thonny prints which colour is being sent:
#
#     1. sent RED
#     2. sent GREEN
#     3. sent BLUE
#     4. sent WHITE
#
# Note the colour the strip ACTUALLY shows for steps 1, 2 and 3.
# Their first letters, in that order, are the strip's native order:
#     red,   green, blue  -> RGB
#     green, red,   blue  -> GRB   (most common WS2812B)
#     blue,  green, red   -> BGR
#
# Step 4 should look white. If it looks pink, green or blue instead, one of
# the three channels is not working.
#
# Brightness is kept low: the strip is lit all at once, possibly still on its
# reel, and USB power is limited.

import time
import plasma
from configuration import NUM_LEDS

LEVEL = 32        # 1/8 brightness for single colours
WHITE_LEVEL = 24  # white lights all three channels, so a bit lower
STEP_SECONDS = 4

strip = plasma.WS2812(NUM_LEDS, color_order=plasma.COLOR_ORDER_RGB)
strip.start()

steps = [
    ("RED",   (LEVEL, 0, 0)),
    ("GREEN", (0, LEVEL, 0)),
    ("BLUE",  (0, 0, LEVEL)),
    ("WHITE", (WHITE_LEVEL, WHITE_LEVEL, WHITE_LEVEL)),
]


def fill(r, g, b):
    for i in range(NUM_LEDS):
        strip.set_rgb(i, r, g, b)


print("Lighting all %d LEDs. Press Stop in Thonny to end the test." % NUM_LEDS)
print("Note the colour the strip shows at steps 1, 2 and 3;")
print("their first letters are the strip's colour order.")

try:
    while True:
        print()
        for n, (name, (r, g, b)) in enumerate(steps, 1):
            print("%d. sent %s" % (n, name))
            fill(r, g, b)
            time.sleep(STEP_SECONDS)
finally:
    fill(0, 0, 0)  # turn the strip off when stopped
