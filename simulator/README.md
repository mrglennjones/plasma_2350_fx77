# Virtual Plasma – effect simulator

Runs the effects from `eff.py` in a web browser and animates them on a
virtual LED strip, so you can try an effect without flashing the board.

- Python runs in the browser via [Pyodide](https://pyodide.org) inside a Web Worker.
- Time is virtual: `time.sleep()` and `ticks_ms()` are simulated and every LED
  write adds an estimated MicroPython cost, so an effect runs at the speed it
  would on the board. The strip is sampled 60 times a second, like the
  firmware's DMA refresh.
- `set_hsv()` / `set_rgb()` follow `ws2812.cpp` from pimoroni-pico: HSV→RGB
  conversion, values over 255 wrap, a negative hue leaves the LED unchanged,
  `set_rgb()` with a float raises `TypeError` (raw model), the firmware gamma
  table is applied (values below 22 don't light up), and writes past the end
  of the strip are reported.
- The effects are tuned for a strip that swaps red and green, so by default
  the display does the same. Change it under "Strip colors".
- Old plasma_2040 effects that only return `hsv_values`, and whole scripts
  with a `while True:` loop, run too.

## Build and run locally

```sh
python3 simulator/build.py          # downloads Pyodide (~14 MB) on the first run
python3 -m http.server -d simulator/site 8000
```

Open <http://localhost:8000/standalone.html>. The page needs to be served over
HTTP; opening the file directly won't start the Web Worker.

Rebuild after changing `eff.py` or `configuration.py`. You can also load a
different `eff.py` or `configuration.py` from the page itself.

## Files

- `src/template.html` – the page; `build.py` embeds `eff.py`, `configuration.py`
  and the gamma table into it
- `src/engine.js` – simulation engine: virtual clock, WS2812 emulation and
  stubs for `time`, `machine`, `plasma`, `pimoroni` and `micropython`
- `build.py` – assembles everything into `site/` (not committed)

`site/index.html` is a page fragment meant for publishing as a claude.ai
artifact together with `engine.js` and `py/`. For anything else, use
`site/standalone.html`.

## Limits

Pyodide is CPython, not MicroPython, so small differences are possible (for
example, CPython is more permissive in a few places and floats are 64-bit).
Button presses aren't simulated: buttons always read as not pressed.
