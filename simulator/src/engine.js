/* Virtual Plasma – simulation engine.
 * Runs MicroPython-style LED effects in Pyodide with a virtual clock.
 * Works as a Web Worker (preferred) or as a plain script on the page.
 */
(function () {
  "use strict";

  const ENGINE_PY = String.raw`
import sys, types, math, random, ast, traceback, builtins, linecache
import js
from pyodide.ffi import to_js

USER_FILES = ('<efekt>', 'eff.py', 'configuration.py')


class SimStop(BaseException):
    """Stops the simulation; BaseException so effect code can't swallow it."""
    def __init__(self, reason):
        BaseException.__init__(self, reason)
        self.reason = reason


def _u8f(x):
    """float -> uint8_t the way the RP2 firmware converts it:
    negatives give 0, bigger values wrap around (only the low byte is kept)."""
    if x != x or x <= 0.0:
        return 0
    if x >= 4294967295.0:
        return 255
    return int(x) & 0xFF


def _mp_int(x):
    # MicroPython MP_ARG_INT: ints and bools only, floats raise TypeError
    if isinstance(x, int):
        return int(x)
    if isinstance(x, float):
        raise TypeError("can't convert float to int")
    raise TypeError("can't convert %s to int" % type(x).__name__)


def _mp_float(x):
    if isinstance(x, (int, float)):
        return float(x)
    raise TypeError("can't convert %s to float" % type(x).__name__)


class Sim:
    def __init__(self, opts):
        self.now = 0.0
        self.max_ms = float(opts['max_ms'])
        self.call_cost = float(opts['call_cost_us']) / 1000.0
        self.tick_ms = 1000.0 / max(1.0, float(opts['fps']))
        self.next_tick = 0.0
        self.max_frames = int(opts['max_frames'])
        self.wall_limit = float(opts['wall_limit_ms'])
        self.wall_start = js.Date.now()
        self.last_flush = self.wall_start
        self.n = 0
        self.buf = bytearray(0)
        self.dirty = False
        self.pend_t = []
        self.pend_b = bytearray()
        self.nframes = 0
        self.writes = 0
        self.ops = 0
        self.warned = set()

    # --- strip buffer -------------------------------------------------
    def resize(self, n):
        n = int(n)
        if n != self.n:
            self.n = n
            self.buf = bytearray(n * 3)
            self.dirty = True

    def put(self, index, r, g, b):
        if 0 <= index < self.n:
            k = index * 3
            buf = self.buf
            buf[k] = r
            buf[k + 1] = g
            buf[k + 2] = b
            self.dirty = True
            self.writes += 1
        else:
            self.warn('oob', 'Write to LED index %d, but the strip only has %d LEDs (0–%d). '
                      'The firmware does not check the index; on hardware this would overwrite memory past the buffer.'
                      % (index, self.n, self.n - 1))

    def warn(self, key, msg):
        if key not in self.warned:
            self.warned.add(key)
            js_log(msg, 'warn')

    # --- frames ------------------------------------------------------------
    def frame(self, t):
        self.pend_t.append(t)
        self.pend_b += self.buf
        self.nframes += 1
        self.dirty = False
        w = js.Date.now()
        if len(self.pend_t) >= 90 or w - self.last_flush > 100:
            self.flush()
        if self.nframes >= self.max_frames:
            raise SimStop('frames')

    def flush(self):
        if self.pend_t:
            js_post_frames(to_js(self.pend_t), to_js(bytes(self.pend_b)), self.n)
            self.pend_t = []
            self.pend_b = bytearray()
        self.last_flush = js.Date.now()

    # --- virtual clock ---------------------------------------------------
    def advance(self, ms):
        end = self.now + ms
        nt = self.next_tick
        if nt <= end:
            # The DMA refresh at next_tick sends the buffer as it is right now.
            if self.dirty:
                self.frame(nt)
            k = math.floor((end - nt) / self.tick_ms) + 1
            self.next_tick = nt + k * self.tick_ms
        self.now = end
        if end > self.max_ms:
            raise SimStop('time')
        self.ops += 1
        if (self.ops & 1023) == 0 and js.Date.now() - self.wall_start > self.wall_limit:
            raise SimStop('wall')

    def sleep_ms(self, ms):
        ms = _mp_float(ms)
        if ms < 0:
            raise ValueError('sleep length must be non-negative')
        self.advance(ms)

    def finish(self):
        if self.dirty:
            try:
                self.frame(self.next_tick)
            except SimStop:
                pass
        self.flush()


class SimStrip:
    """Emulates plasma.WS2812 from the Pimoroni firmware (pimoroni-pico ws2812.cpp)."""
    def __init__(self, sim, num_leds, ledstrip=False, brightness=1.0):
        self._sim = sim
        self._ledstrip = ledstrip
        self._sim_brightness = float(brightness)
        sim.resize(num_leds)

    def start(self, fps=60):
        return None

    def clear(self):
        sim = self._sim
        for i in range(len(sim.buf)):
            sim.buf[i] = 0
        sim.dirty = True

    def get(self, index):
        k = _mp_int(index) * 3
        b = self._sim.buf
        return (b[k], b[k + 1], b[k + 2], 0)

    def set_rgb(self, index, r, g, b, w=0):
        sim = self._sim
        sim.advance(sim.call_cost)
        if self._ledstrip:
            k = self._sim_brightness
            r = int(max(0, min(255, r * k)))
            g = int(max(0, min(255, g * k)))
            b = int(max(0, min(255, b * k)))
        sim.put(_mp_int(index), _mp_int(r) & 0xFF, _mp_int(g) & 0xFF, _mp_int(b) & 0xFF)

    def set_hsv(self, index, h, s=1.0, v=1.0, w=0):
        sim = self._sim
        sim.advance(sim.call_cost)
        index = _mp_int(index)
        h = _mp_float(h)
        s = _mp_float(s)
        v = _mp_float(v)
        if self._ledstrip:
            v = max(0.0, min(1.0, v * self._sim_brightness))
        if not (math.isfinite(h) and math.isfinite(s) and math.isfinite(v)):
            sim.warn('nan', 'set_hsv got a nan or inf value, the write is ignored.')
            return
        i = math.floor(h * 6.0)
        f = h * 6.0 - i
        v *= 255.0
        p = _u8f(v * (1.0 - s))
        q = _u8f(v * (1.0 - f * s))
        t = _u8f(v * (1.0 - (1.0 - f) * s))
        vv = _u8f(v)
        ii = int(i)
        m = ii % 6 if ii >= 0 else -((-ii) % 6)   # C '%' keeps the sign
        if m == 0:
            sim.put(index, vv, t, p)
        elif m == 1:
            sim.put(index, q, vv, p)
        elif m == 2:
            sim.put(index, p, vv, t)
        elif m == 3:
            sim.put(index, p, q, vv)
        elif m == 4:
            sim.put(index, t, p, vv)
        elif m == 5:
            sim.put(index, vv, p, q)
        else:
            sim.warn('neghue', 'set_hsv with a negative hue: the firmware leaves the LED unchanged in that case.')


def make_modules(sim):
    mods = {}

    tm = types.ModuleType('time')
    def ticks_ms():
        sim.advance(0.005)
        return int(sim.now)
    def ticks_us():
        sim.advance(0.005)
        return int(sim.now * 1000)
    tm.ticks_ms = ticks_ms
    tm.ticks_us = ticks_us
    tm.ticks_cpu = ticks_us
    tm.ticks_diff = lambda a, b: a - b
    tm.ticks_add = lambda a, b: a + b
    tm.sleep = lambda s: sim.sleep_ms(_mp_float(s) * 1000.0)
    tm.sleep_ms = lambda ms: sim.sleep_ms(ms)
    tm.sleep_us = lambda us: sim.sleep_ms(_mp_float(us) / 1000.0)
    tm.time = lambda: 1767225600 + sim.now / 1000.0
    tm.time_ns = lambda: int((1767225600 + sim.now / 1000.0) * 1e9)
    tm.monotonic = lambda: sim.now / 1000.0
    mods['time'] = tm
    mods['utime'] = tm

    machine = types.ModuleType('machine')
    class Pin:
        IN = 0; OUT = 1; OPEN_DRAIN = 2; PULL_UP = 1; PULL_DOWN = 2
        IRQ_FALLING = 4; IRQ_RISING = 8
        def __init__(self, *a, **k): pass
        def value(self, *a):
            return 1 if not a else None   # buttons are active-low: 1 = not pressed
        __call__ = value
        def irq(self, *a, **k): return None
        def on(self): pass
        def off(self): pass
        def toggle(self): pass
        def init(self, *a, **k): pass
    class Timer:
        PERIODIC = 1; ONE_SHOT = 0
        def __init__(self, *a, **k): pass
        def init(self, *a, **k): pass
        def deinit(self): pass
    def _reset():
        raise SimStop('reset')
    machine.Pin = Pin
    machine.Timer = Timer
    machine.freq = lambda *a: 150000000
    machine.reset = _reset
    machine.soft_reset = _reset
    machine.unique_id = lambda: b'\x00' * 8
    mods['machine'] = machine

    pim = types.ModuleType('pimoroni')
    class RGBLED:
        def __init__(self, *a, **k): pass
        def set_rgb(self, *a, **k): pass
        def set_hsv(self, *a, **k): pass
    class Button:
        def __init__(self, *a, **k): pass
        def read(self): return False
        def raw(self): return False
        @property
        def is_pressed(self): return False
    class Analog:
        def __init__(self, *a, **k): pass
        def read_voltage(self): return 5.0
        def read_current(self): return 0.5
    pim.RGBLED = RGBLED
    pim.Button = Button
    pim.Analog = Analog
    mods['pimoroni'] = pim

    plasma = types.ModuleType('plasma')
    for k, v in (('COLOR_ORDER_RGB', 0), ('COLOR_ORDER_RBG', 1), ('COLOR_ORDER_GRB', 2),
                 ('COLOR_ORDER_GBR', 3), ('COLOR_ORDER_BRG', 4), ('COLOR_ORDER_BGR', 5)):
        setattr(plasma, k, v)
    class WS2812(SimStrip):
        def __init__(self, num_leds, *a, **k):
            SimStrip.__init__(self, sim, num_leds)
    plasma.WS2812 = WS2812
    plasma.APA102 = WS2812
    pins = types.SimpleNamespace(DAT=15, CLK=14, LED_R=16, LED_G=17, LED_B=18,
                                 USER_SW=23, BUTTON_A=12, BUTTON_B=13,
                                 CURRENT_SENSE=29, SDA=20, SCL=21)
    plasma.plasma2040 = pins
    plasma.plasma2350 = pins
    plasma.plasma_stick = pins
    mods['plasma'] = plasma

    mp = types.ModuleType('micropython')
    mp.const = lambda x: x
    mp.native = lambda f: f
    mp.viper = lambda f: f
    mp.opt_level = lambda *a: 0
    mp.mem_info = lambda *a: None
    mp.alloc_emergency_exception_buf = lambda n: None
    mods['micropython'] = mp
    return mods


def hsv_to_grb_default(h, s, v):
    r, g, b = _hsv_to_rgb01(h, s, v)
    return int(g * 255), int(r * 255), int(b * 255)


def _hsv_to_rgb01(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s); q = v * (1.0 - s * f); t = v * (1.0 - s * (1.0 - f))
    i %= 6
    return [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]


def register_source(name, src):
    linecache.cache[name] = (len(src), None, src.splitlines(True), name)


def format_error(e):
    tb = traceback.extract_tb(e.__traceback__)
    frames = [f for f in tb if f.filename in USER_FILES]
    lines = []
    if frames:
        lines.append('Traceback (most recent call last):')
        lines += [l.rstrip('\n') for l in traceback.format_list(frames)]
    lines += [l.rstrip('\n') for l in traceback.format_exception_only(type(e), e)]
    line_no = None
    if isinstance(e, SyntaxError) and e.filename == '<efekt>':
        line_no = e.lineno
    else:
        for f in reversed(frames):
            if f.filename == '<efekt>':
                line_no = f.lineno
                break
    return '\n'.join(lines), line_no


def pick_function(code, fn_name, ns):
    tree = ast.parse(code)
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    if not names:
        return None
    if fn_name and fn_name in names:
        return ns[fn_name]
    effects = [n for n in names if n.startswith('effect_')]
    return ns[(effects or names)[-1]]


def run_effect(fn, strip, sim, timeout_ms):
    n = sim.n
    hsv = [(0.0, 0.0, 0.0)] * n
    code = getattr(fn, '__code__', None)
    argc = code.co_argcount if code is not None else 2
    start = sim.now
    while True:
        t0 = sim.now
        w0 = sim.writes
        if argc >= 2:
            res = fn(hsv, strip)
        elif argc == 1:
            res = fn(hsv)
        else:
            res = fn()
        if isinstance(res, list) and len(res) == n:
            hsv = res
            if sim.writes == w0:
                # Old plasma_2040 style: the effect only returns values and
                # the manager writes them to the strip.
                for i, px in enumerate(res):
                    strip.set_hsv(i, px[0], px[1], px[2])
        if sim.now - start >= timeout_ms:
            break
        if sim.now == t0:
            sim.advance(1.0)


def run_sim(eff_src, cfg_src, code, fn_name, opts):
    if hasattr(opts, 'to_py'):
        opts = opts.to_py()
    sim = Sim(opts)
    mods = make_modules(sim)
    touched = list(mods) + ['configuration', 'eff']
    saved = {k: sys.modules.get(k) for k in touched}
    result = {'reason': 'end', 'error': None, 'error_line': None}
    random.seed(int(opts['seed']))
    try:
        sys.modules.update(mods)
        cfg = types.ModuleType('configuration')
        register_source('configuration.py', cfg_src)
        exec(compile(cfg_src, 'configuration.py', 'exec'), cfg.__dict__)
        cfg.NUM_LEDS = int(opts['num_leds'])
        cfg.ORIENTATION = str(opts['orientation'])
        cfg.TIMEOUT_DURATION = int(opts['timeout_ms'])
        cfg.BRIGHTNESS = float(opts['brightness'])
        sys.modules['configuration'] = cfg

        strip = SimStrip(sim, cfg.NUM_LEDS, ledstrip=(opts['strip_model'] == 'ledstrip'),
                         brightness=opts['brightness'])

        ns = {'__name__': 'eff', '__builtins__': builtins}
        if eff_src:
            register_source('eff.py', eff_src)
            exec(compile(eff_src, 'eff.py', 'exec'), ns)
        for k in dir(cfg):
            if not k.startswith('_'):
                ns.setdefault(k, getattr(cfg, k))
        ns.setdefault('time', mods['time'])
        ns.setdefault('math', math)
        ns.setdefault('led_strip', strip)
        ns.setdefault('read_buttons', lambda: True)
        ns.setdefault('button_pressed', lambda: False)
        ns.setdefault('hsv_to_grb', hsv_to_grb_default)

        register_source('<efekt>', code)
        exec(compile(code, '<efekt>', 'exec'), ns)
        fn = pick_function(code, fn_name, ns)
        if fn is not None:
            run_effect(fn, strip, sim, cfg.TIMEOUT_DURATION)
    except SimStop as e:
        result['reason'] = e.reason
    except Exception as e:
        result['reason'] = 'error'
        result['error'], result['error_line'] = format_error(e)
    finally:
        try:
            sim.finish()
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
    result['end_t'] = sim.now
    result['nframes'] = sim.nframes
    result['n'] = sim.n
    return to_js(result, dict_converter=js.Object.fromEntries)
`;

  function createEngine(post, indexURL) {
    let py = null;
    let readyPromise = null;
    let curId = 0;

    async function init() {
      post({ type: "status", text: "Loading Python…" });
      // The stdlib zip is published as .wasm because artifact hosting doesn't serve .zip files.
      const stdLibURL = indexURL.indexOf("cdn.jsdelivr.net") >= 0 ? undefined : indexURL + "python_stdlib.wasm";
      py = await self.loadPyodide({ indexURL, stdLibURL });
      py.setStdout({ batched: (s) => post({ type: "log", id: curId, text: s, kind: "out" }) });
      py.setStderr({ batched: (s) => post({ type: "log", id: curId, text: s, kind: "err" }) });
      py.globals.set("js_post_frames", (t, b, n) => {
        const tt = Float64Array.from(t);
        const bb = new Uint8Array(b);
        post({ type: "frames", id: curId, n, t: tt, b: bb }, [tt.buffer, bb.buffer]);
      });
      py.globals.set("js_log", (text, kind) => post({ type: "log", id: curId, text, kind }));
      py.runPython(ENGINE_PY);
      post({ type: "ready", version: py.version });
    }

    return async function onMessage(msg) {
      if (msg.type === "init") {
        readyPromise = init().catch((e) => {
          post({ type: "fatal", text: String((e && e.message) || e) });
          throw e;
        });
        return;
      }
      if (msg.type === "run") {
        try {
          await readyPromise;
        } catch (e) {
          return;
        }
        curId = msg.id;
        const t0 = Date.now();
        const runSim = py.globals.get("run_sim");
        const pyOpts = py.toPy(msg.opts);
        try {
          const res = runSim(msg.effSrc, msg.cfgSrc, msg.code, msg.fnName, pyOpts);
          post({
            type: "done", id: msg.id, wallMs: Date.now() - t0,
            reason: res.reason, error: res.error, errorLine: res.error_line,
            endT: res.end_t, nframes: res.nframes, n: res.n,
          });
        } catch (e) {
          post({ type: "done", id: msg.id, wallMs: Date.now() - t0, reason: "error",
                 error: "Simulator error: " + String((e && e.message) || e), errorLine: null,
                 endT: 0, nframes: 0, n: 0 });
        } finally {
          pyOpts.destroy();
          runSim.destroy();
        }
      }
    };
  }

  const isWorker = typeof WorkerGlobalScope !== "undefined" && self instanceof WorkerGlobalScope;
  if (isWorker) {
    let handler = null;
    self.onmessage = (e) => {
      const m = e.data;
      if (m.type === "init") {
        try {
          importScripts(m.indexURL + "pyodide.js");
        } catch (err) {
          self.postMessage({ type: "fatal", text: "Failed to load pyodide.js: " + err });
          return;
        }
        handler = createEngine((msg, tr) => self.postMessage(msg, tr || []), m.indexURL);
      }
      if (handler) handler(m);
    };
  } else {
    self.FXEngineCreate = createEngine;
  }
})();
