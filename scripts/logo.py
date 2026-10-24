"""Animated SVG of the Phone Harness logo (logo-animated*.svg), from the launch video's
render script (launch-yc/source/render.py): same grid, timing and curves.
Needs fonttools and Arial Bold (macOS ships it). Run via scripts/render.sh."""
import math, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "phone-harness"
GRID = [".###........###.", "###.#......#.###", "###.#......#.###", "#....######....#", "#..............#",
        ".###........###.", ".###........###.", ".....######.....", "....########....", "...##########...",
        "...##########...", "...####..####...", "...####..####...", ".##############.", ".##############.", ".##############."]
CELL = 248 / 16
RED, PARTICLE_COLORS = "#ff4438", ("#ff4438", "#ff6f59", "#da2f26")
ICON_W, GAP, TEXT_W, TEXT_H = 248.0, 49.0, 1182.0, 247.0   # gap = one space at the wordmark's size
EXPANSION = GAP + TEXT_W
REVEAL_START, REVEAL_END, RESPONSE = 0.385, 1.0, 14.0
LANDING, TILT, PIVOT = 1.25, -6.5, (41.0, 103.0)
IMPACT, GRAVITY, FPS, END = 0.24, 920.0, 60, 1.70
PARTICLES = ((-1,-155,-165,6,.30,0),(-1,-245,-235,8,.36,1),(-1,-110,-305,6,.40,0),(-1,-280,-95,5,.29,2),(-1,-185,30,7,.29,0),
             (-1,-80,-215,5,.34,1),(1,190,-185,8,.33,0),(1,270,-255,7,.38,1),(1,125,-320,6,.41,0),(1,295,-110,6,.30,2),
             (1,230,35,7,.29,0),(1,150,-65,5,.32,1),(1,80,-240,5,.37,0),(1,215,-290,4,.36,2))

def cells(rows):
    out = []
    for r in rows:
        line, c = GRID[r], 0
        while c < 16:
            if line[c] == "#":
                s = c
                while c < 16 and line[c] == "#": c += 1
                out.append(f"M{s*CELL:.2f} {r*CELL:.2f}h{(c-s)*CELL:.2f}v{CELL:.2f}h{-(c-s)*CELL:.2f}z")
            else: c += 1
    return "".join(out)

def wordmark():
    f = TTFont("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    gs, cmap, hmtx, upem = f.getGlyphSet(), f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    text, x, d = "phone-harness", 0.0, []
    names = [cmap[ord(ch)] for ch in text]
    natural = sum(hmtx[n][0] for n in names)
    size = 177.0 * 1.0
    k = size / upem
    track = (TEXT_W - natural * k) / (len(text) - 1)   # fit the source's exact width
    for n in names:
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (k, 0, 0, -k, x, 184.0)))
        d.append(pen.getCommands()); x += hmtx[n][0] * k + track
    return "".join(d)

def progress(t):
    e = max(0.0, min(REVEAL_END - REVEAL_START, t - REVEAL_START)); z, end = RESPONSE * e, RESPONSE * (REVEAL_END - REVEAL_START)
    return (1 - (1 + z) * math.exp(-z)) / (1 - (1 + end) * math.exp(-end))
def smooth(v): u = max(0.0, min(1.0, v)); return u * u * (3 - 2 * u)
def tilt(t):
    if t <= REVEAL_START or t >= LANDING: return 0.0
    u = (t - REVEAL_START) / (LANDING - REVEAL_START); return TILT * 4 * u * (1 - u)
def jolt(t):
    e = t - LANDING
    if not 0 < e < IMPACT: return 0.0, 0.0
    taper = 1 - smooth(e / IMPACT)
    return 1.6 * math.exp(-e * 24) * math.sin(e * 82) * taper, 6.5 * math.exp(-e * 18) * math.sin(e * 55) * taper

frames = [i / FPS for i in range(int(END * FPS) + 1)]
kt = ";".join(f"{t/END:.4f}" for t in frames)
icon_x = [EXPANSION / 2 * (1 - progress(t)) for t in frames]
icon_v = ";".join(f"{x + jolt(t)[0]:.2f} {jolt(t)[1]:.2f}" for x, t in zip(icon_x, frames))
text_v = ";".join(f"{x + ICON_W + EXPANSION * progress(t) - TEXT_W:.2f} 0" for x, t in zip(icon_x, frames))
clip_v = ";".join(f"{x + ICON_W:.2f} 0" for x in icon_x)
tilt_v = ";".join(f"{tilt(t):.3f} {PIVOT[0]} {PIVOT[1]}" for t in frames)
anim = lambda typ, vals: (f'<animateTransform attributeName="transform" type="{typ}" dur="{END}s" fill="freeze" '
                          f'calcMode="linear" keyTimes="{kt}" values="{vals}"/>')

parts = []
for i, (side, vx, vy, size, life, shade) in enumerate(PARTICLES):
    xs, ys, ss, os_ = [], [], [], []
    for t in frames:
        e = t - LANDING
        if e < 0 or e >= life:
            xs.append(0); ys.append(0); ss.append(0); os_.append(0); continue
        ph = e / life
        ox = (21 if side < 0 else 226); oy = 98 + (i % 3 - 1) * 3
        x, y = ox + vx * e, oy + vy * e + 0.5 * GRAVITY * e * e
        sq = max(2, round(size * (1 - .45 * ph) / 2) * 2) / 0.9      # render.py draws at 0.9 scale
        xs.append(round((x - sq / 2) / 2) * 2); ys.append(round((y - sq / 2) / 2) * 2); ss.append(sq)
        os_.append(round(1 - smooth((ph - .5) / .5), 3))
    a = lambda attr, v: f'<animate attributeName="{attr}" dur="{END}s" fill="freeze" calcMode="discrete" keyTimes="{kt}" values="{";".join(map(str, v))}"/>'
    parts.append(f'<rect fill="{PARTICLE_COLORS[shade]}" opacity="0" width="0" height="0">{a("x", xs)}{a("y", ys)}{a("width", ss)}{a("height", ss)}{a("opacity", os_)}</rect>')

def svg(ink):
    pad_l, pad_t, pad_r, pad_b = 90, 80, 90, 10   # symmetric, so the lockup is centered
    w, h = ICON_W + EXPANSION + pad_l + pad_r, TEXT_H + pad_t + pad_b
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad_l} {-pad_t} {w:.0f} {h:.0f}" width="{w/2:.0f}" height="{h/2:.0f}" role="img" aria-label="phone-harness">
<title>phone-harness</title>
<defs><clipPath id="reveal"><rect x="0" y="-80" width="2000" height="420">{anim("translate", clip_v)}</rect></clipPath></defs>
<g clip-path="url(#reveal)"><g>{anim("translate", text_v)}<path fill="{ink}" d="{wordmark()}"/></g></g>
<g>{anim("translate", icon_v)}
  <path fill="{RED}" d="{cells(range(7, 16))}"/>
  <g><path fill="{RED}" d="{cells(range(0, 7))}"/>{anim("rotate", tilt_v)}</g>
  {"".join(parts)}
</g>
</svg>
'''
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "logo-animated.svg").write_text(svg("#20231e"))
(OUT / "logo-animated-dark.svg").write_text(svg("#ecede6"))
for p in sorted(OUT.glob("logo-animated*.svg")): print(p.name, p.stat().st_size, "bytes")
