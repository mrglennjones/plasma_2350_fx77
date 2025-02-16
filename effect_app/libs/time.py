import time
import monotonic

def sleep(s):
    time.sleep(s)

def ticks_ms():
    return monotonic.monotonic() * 1000

def ticks_diff(a, b):
    return a - b
