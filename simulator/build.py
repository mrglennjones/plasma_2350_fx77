#!/usr/bin/env python3
"""Build the in-browser effect simulator ("Virtual Plasma").

Reads ../eff.py and ../configuration.py, embeds them into the page and
puts everything needed into simulator/site/:

  site/index.html       page fragment for publishing as a claude.ai artifact
                        (the host adds <!doctype>, <head> and <body>)
  site/standalone.html  the same page as a full HTML document, for local use
  site/engine.js        the simulation engine (Web Worker)
  site/py/              Pyodide runtime (downloaded once, ~14 MB)

Usage:
  python3 simulator/build.py
  python3 -m http.server -d simulator/site 8000
  # then open http://localhost:8000/standalone.html
"""
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SITE = HERE / "site"
PYODIDE_VERSION = "0.26.4"
PYODIDE_FILES = ("pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm",
                 "python_stdlib.zip", "pyodide-lock.json")

# GAMMA_8BIT from pimoroni-pico common/pimoroni_common.hpp. The WS2812 driver
# applies it in set_rgb() (gamma=true by default), so set_hsv() output goes
# through it too.
GAMMA_8BIT = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2,
    2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5,
    6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11,
    11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18,
    19, 19, 20, 21, 21, 22, 22, 23, 23, 24, 25, 25, 26, 27, 27, 28,
    29, 29, 30, 31, 31, 32, 33, 34, 34, 35, 36, 37, 37, 38, 39, 40,
    40, 41, 42, 43, 44, 45, 46, 46, 47, 48, 49, 50, 51, 52, 53, 54,
    55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 88, 89,
    90, 91, 93, 94, 95, 96, 98, 99, 100, 102, 103, 104, 106, 107, 109, 110,
    111, 113, 114, 116, 117, 119, 120, 121, 123, 124, 126, 128, 129, 131, 132, 134,
    135, 137, 138, 140, 142, 143, 145, 146, 148, 150, 151, 153, 155, 157, 158, 160,
    162, 163, 165, 167, 169, 170, 172, 174, 176, 178, 179, 181, 183, 185, 187, 189,
    191, 193, 194, 196, 198, 200, 202, 204, 206, 208, 210, 212, 214, 216, 218, 220,
    222, 224, 227, 229, 231, 233, 235, 237, 239, 241, 244, 246, 248, 250, 252, 255,
]

# Same skeleton the claude.ai artifact host wraps around index.html.
SKELETON_HEAD = (
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    "<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);"
    "padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui}"
    "img{max-width:100%}[hidden]{display:none!important}</style>\n"
)


def git(*args):
    try:
        return subprocess.run(["git", "-C", str(REPO), *args], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def check_embeddable(name, src):
    low = src.lower()
    for bad in ("</script", "<script", "<!--"):
        if bad in low:
            sys.exit(f"{name} contains '{bad}', which would break the page's embedded <script> block")


def fetch_pyodide(dest):
    """Put the Pyodide runtime into dest, from jsDelivr or, failing that, from npm."""
    missing = [f for f in PYODIDE_FILES if not (dest / f).exists()]
    if not missing:
        return
    dest.mkdir(parents=True, exist_ok=True)
    base = f"https://cdn.jsdelivr.net/npm/pyodide@{PYODIDE_VERSION}/"
    try:
        for f in missing:
            print("downloading", base + f)
            with urllib.request.urlopen(base + f, timeout=120) as r, open(dest / f, "wb") as out:
                shutil.copyfileobj(r, out)
        return
    except OSError as e:
        print(f"download from jsDelivr failed ({e}), trying npm pack…")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["npm", "pack", f"pyodide@{PYODIDE_VERSION}", "--silent"],
                       cwd=tmp, check=True, capture_output=True)
        tgz = next(Path(tmp).glob("pyodide-*.tgz"))
        with tarfile.open(tgz) as t:
            for f in missing:
                src = t.extractfile(f"package/{f}")
                with open(dest / f, "wb") as out:
                    shutil.copyfileobj(src, out)


def main():
    eff = (REPO / "eff.py").read_text(encoding="utf-8")
    cfg = (REPO / "configuration.py").read_text(encoding="utf-8")
    check_embeddable("eff.py", eff)
    check_embeddable("configuration.py", cfg)

    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    commit = git("rev-parse", "--short", "HEAD") or "?"
    dirty = " + uncommitted changes" if git("status", "--porcelain", "--", "eff.py", "configuration.py") else ""
    label = f"eff.py and configuration.py from branch {branch} ({commit}{dirty})"

    tpl = (HERE / "src" / "template.html").read_text(encoding="utf-8")
    page = (tpl.replace("{{EFF_PY}}", eff)
               .replace("{{CONFIG_PY}}", cfg)
               .replace("{{SRC_LABEL}}", label)
               .replace("{{GAMMA_JSON}}", json.dumps(GAMMA_8BIT, separators=(",", ":"))))

    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(page, encoding="utf-8")

    # standalone: <title>, <meta>, <link> and <style> go into <head>, the rest into <body>
    split = page.index("</style>") + len("</style>")
    standalone = SKELETON_HEAD + page[:split] + "\n</head>\n<body>\n" + page[split:] + "\n</body>\n</html>\n"
    (SITE / "standalone.html").write_text(standalone, encoding="utf-8")

    shutil.copy2(HERE / "src" / "engine.js", SITE / "engine.js")

    py = SITE / "py"
    fetch_pyodide(py)
    # Artifact hosting doesn't serve .zip files, so the stdlib zip is also
    # published under a .wasm name; engine.js loads it from there.
    shutil.copy2(py / "python_stdlib.zip", py / "python_stdlib.wasm")

    print(f"built {SITE / 'index.html'} ({len(page)} bytes) from {branch} {commit}{dirty}")


if __name__ == "__main__":
    main()
