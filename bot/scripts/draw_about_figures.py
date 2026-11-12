"""Draw the figures for the site's About dialog, which walk through how swell and wind are worked out, from the
bot's own data. Colours are the site's CSS variables, so they follow light and dark mode when inlined.

  uv run --group build python scripts/draw_about_figures.py   # needs coastline.json from build_swell_windows.py
  uv run --group build python scripts/draw_about_figures.py sessions warmth   # just these (no coastline needed)

Writes web/src/about/*.svg:
  sessions.svg  a 24-hour clock: the morning, midday and evening sessions every day
  window.svg  North Bondi: rays cast from the beach, open ocean vs the headland's shadow
  window-wide.svg  the same, zoomed out to Maroubra: where the southern rays land
  wrap.svg    Collaroy: how far round Long Reef an 8 s and a 14 s swell reach
  share.svg   North Bondi: how much of a NE, E, SE and S swell gets in
  period.svg  Breaking height of a 1.5 m swell by period, at a beach and at a surf break
  swell-types.svg  side-on: wind swell vs groundswell, true to scale, and the depth each starts to feel the seabed
  chop.svg    from above: the same 1.5 m as a wind swell and a groundswell reaching a beach, and how big each breaks
  refraction.svg  plan view: 8 s and 14 s crests bending round a made-up headland (eikonal solve over its seabed)
  wind.svg    Coogee: which winds are offshore, cross-shore and onshore
  wind-water.svg  side-on: the same swell under an offshore and an onshore wind
  water.svg   how much rain in a day each eastern beach can take
  warmth.svg  a day going to 30 with a southerly: the temperature and the warmth the score counts
  sky.svg     what rain, cloud, storms and air and water temperature do to a score
  pools.svg   a day's tide: when swell washes over the pool walls, and the low-tide pools
  bluebottles.svg  Maroubra: the winds that blow bluebottles in

Coastline © OpenStreetMap contributors.
"""

import functools
import heapq
import json
import math
import sys
from pathlib import Path

import numpy as np
import shapely
from shapely import LineString, MultiLineString, Polygon, box, line_merge, polygonize, unary_union

from beach_bot import swell
from beach_bot.beaches import EASTERN, NORTHERN
from beach_bot.geo import wind_kind

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "web" / "src" / "about"
BEACH = {b.name: b for r in (EASTERN, NORTHERN) for b in r.beaches}


@functools.cache
def coastline():
    """OSM coastline ways, read on first use so figures without a map don't need the file."""
    return json.loads((HERE / "coastline.json").read_text())


WIDTH = 400


def rad(a):
    return math.radians(a)


def toward(x, y, bearing, r):
    return x + r * math.sin(rad(bearing)), y - r * math.cos(rad(bearing))


def path(pts, close=True):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ("Z" if close else "")


def wedge(cx, cy, a0, a1, r, step=2):
    return path([(cx, cy), *(toward(cx, cy, a, r) for a in range(a0, a1 + 1, step))])


class Map:
    """A lat/lon box drawn WIDTH pixels wide, with the land filled in."""

    def __init__(self, s, w, n, e):
        self.s, self.w, self.n, self.e = s, w, n, e
        self.kx = math.cos(rad((s + n) / 2))
        self.scale = WIDTH / ((e - w) * self.kx)
        self.height = round((n - s) * self.scale)
        self.m_per_px = (e - w) * self.kx * 111_320 / WIDTH

    def px(self, lat, lon):
        return (lon - self.w) * self.kx * self.scale, (self.n - lat) * self.scale

    def land(self):
        """The box cut up by the coastline, keeping the pieces on the land side (odd crossings going east)."""
        frame = box(self.w, self.s, self.e, self.n)
        ways = [LineString([(lon, lat) for lat, lon in w]) for w in coastline() if len(w) > 1]
        coast = [c for c in (w.intersection(frame) for w in ways) if not c.is_empty]
        lines = MultiLineString([list(w.coords) for w in ways])
        out = []
        for f in polygonize(list(unary_union([frame.boundary, *coast]).geoms)).geoms:
            p = f.representative_point()
            odd = 0
            for dx, dy in ((1.0, 0.07), (1.0, -0.23), (1.0, 0.31)):  # three rays out to sea, majority wins
                hit = LineString([(p.x, p.y), (p.x + dx, p.y + dy)]).intersection(lines)
                odd += (0 if hit.is_empty else len(getattr(hit, "geoms", [hit]))) % 2
            if odd >= 2:
                out.append(path([self.px(lat, lon) for lon, lat in f.exterior.coords]))
        return [f'<path d="{d}" fill="var(--hs-land)" stroke="var(--line)" stroke-width="1"/>' for d in out]

    def scale_bar(self, metres):
        w = metres / self.m_per_px
        x, y = WIDTH - 14 - w, self.height - 14
        label = f"{metres // 1000} km" if metres >= 1000 else f"{metres} m"
        return [
            f'<path d="M{x:.1f},{y - 4}V{y}H{x + w:.1f}V{y - 4}" fill="none" stroke="var(--text)" stroke-width="1.5"/>',
            f'<text x="{x + w / 2:.1f}" y="{y - 7}" text-anchor="middle" class="hs-small">{label}</text>',
        ]


def svg(name, width, height, title, desc, body):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
        f'aria-labelledby="{name}-t {name}-d" class="how-swell">',
        f'<title id="{name}-t">{title}</title>',
        f'<desc id="{name}-d">{desc}</desc>',
        *body,
        "</svg>",
    ]
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{name}.svg"
    out.write_text("\n".join(parts) + "\n")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


def arrow_defs(prefix, colours):
    return (
        "<defs>"
        + "".join(
            f'<marker id="{prefix}-{c}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" '
            f'orient="auto-start-reverse"><path d="M0,0L10,5L0,10Z" fill="var(--{c})"/></marker>'
            for c in colours
        )
        + "</defs>"
    )


def pin(m, lat, lon, label, anchor="end", dx=-10, dy=-9):
    x, y = m.px(lat, lon)
    return [
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="var(--text)" stroke="var(--surface)" stroke-width="2"/>',
        f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" class="hs-place">{label}</text>',
    ]


def place(m, lat, lon, label):
    x, y = m.px(lat, lon)
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" class="hs-place hs-italic">{label}</text>'


def open_arc(key):
    spot = swell.WINDOWS["spots"][key]
    bearings = [i * swell.WINDOWS["step"] for i, km in enumerate(spot["km"]) if km >= swell.WINDOWS["cap_km"]]
    return min(bearings), max(bearings)


BONDI = Map(-33.9010, 151.2690, -33.8810, 151.2980)
BONDI_KEY = "Bondi (north end)"


def window_fig():
    """Rays every 4 degrees from just off North Bondi: the ones that reach open ocean, and the ones that hit land."""
    m, spot = BONDI, swell.WINDOWS["spots"][BONDI_KEY]
    ox, oy = m.px(*spot["from"])
    reach = 700  # px: past the edge of the box
    rays, far, labels = [], [], []
    for i, km in enumerate(spot["km"]):
        b = i * swell.WINDOWS["step"]
        if b % 4:
            continue
        r = min(km * 1000 / m.m_per_px, reach)
        x, y = toward(ox, oy, b, r)
        if km >= swell.WINDOWS["cap_km"]:
            rays.append(
                f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--accent)" '
                'stroke-width="1.3" opacity=".85"/>'
            )
        elif r > 30 and abs(swell.wrap(b - BEACH[BONDI_KEY].facing)) < 100:  # headlands, not the sand behind
            rays.append(
                f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--muted)" '
                'stroke-width="1" stroke-dasharray="2 2" opacity=".8"/>'
            )
            if 0 <= x <= WIDTH and 0 <= y <= m.height:
                rays.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="var(--r-red)"/>')
            else:
                far.append((b, km))
    a0, a1 = open_arc(BONDI_KEY)
    lx, ly = toward(ox, oy, (a0 + a1) / 2, 105)
    if far:  # blocked, but by coast beyond the frame: say where
        b_mid = sum(b for b, _ in far) / len(far)
        fx, fy = toward(ox, oy, b_mid, (m.height - 30 - oy) / -math.cos(rad(b_mid)))
        lo, hi = min(km for _, km in far), max(km for _, km in far)
        labels.append(
            f'<text x="{fx - 8:.1f}" y="{fy:.1f}" text-anchor="end" class="hs-small">'
            f'<tspan x="{fx - 8:.1f}">hit the coast</tspan><tspan x="{fx - 8:.1f}" dy="13">'
            f"{lo:.0f}–{hi:.0f} km south</tspan></text>"
        )
    body = [
        f'<rect width="{WIDTH}" height="{m.height}" fill="var(--hs-sea)"/>',
        *rays,
        *m.land(),
        *labels,
        f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" class="hs-label">open ocean</text>',
        f'<text x="{lx:.1f}" y="{ly + 15:.1f}" text-anchor="middle" class="hs-small">{a0}°–{a1}°</text>',
        place(m, -33.8893, 151.2852, "Ben Buckler"),
        *pin(m, *spot["from"], "North Bondi"),
        *m.scale_bar(500),
    ]
    svg(
        "window",
        WIDTH,
        m.height,
        "Finding North Bondi's swell window",
        f"Lines drawn from just off North Bondi every 4 degrees. Solid lines reach 30 km of open ocean, between "
        f"{a0} and {a1} degrees. Dashed lines stop at land with a dot, most of them on Ben Buckler, the headland "
        f"to the north-east; a few to the south-south-west cross the bay and hit the coast further south.",
        body,
    )


def window_wide_fig():
    """The same rays zoomed out to Maroubra: where the ones that leave the close-up end up."""
    m, spot = Map(-33.9700, 151.2400, -33.8820, 151.3120), swell.WINDOWS["spots"][BONDI_KEY]
    ox, oy = m.px(*spot["from"])
    facing = BEACH[BONDI_KEY].facing
    rays = []
    for i, km in enumerate(spot["km"]):
        b = i * swell.WINDOWS["step"]
        if b % 4 or abs(swell.wrap(b - facing)) >= 100:
            continue
        x, y = toward(ox, oy, b, min(km * 1000 / m.m_per_px, 900))
        if km >= swell.WINDOWS["cap_km"]:
            rays.append(
                f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--accent)" '
                'stroke-width="1.1" opacity=".85"/>'
            )
        elif km > 1:  # the near misses on Ben Buckler are in the close-up
            rays += [
                f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--muted)" '
                'stroke-width="1" stroke-dasharray="3 2" opacity=".9"/>',
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="var(--r-red)"/>',
            ]
    (bx0, by0), (bx1, by1) = m.px(BONDI.n, BONDI.w), m.px(BONDI.s, BONDI.e)
    a0, a1 = open_arc(BONDI_KEY)
    lx, ly = toward(ox, oy, (a0 + a1) / 2, 300)
    names = (
        ("Bronte", -33.9035, 151.2625),
        ("Clovelly", -33.9140, 151.2590),
        ("Coogee", -33.9210, 151.2500),
        ("Maroubra", -33.9480, 151.2490),
    )
    body = [
        f'<rect width="{WIDTH}" height="{m.height}" fill="var(--hs-sea)"/>',
        *rays,
        *m.land(),
        f'<rect x="{bx0:.1f}" y="{by0:.1f}" width="{bx1 - bx0:.1f}" height="{by1 - by0:.1f}" fill="none" '
        'stroke="var(--text)" stroke-width="1" stroke-dasharray="3 3" opacity=".6"/>',
        f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" class="hs-label">open ocean</text>',
        *(place(m, lat, lon, n) for n, lat, lon in names),
        *pin(m, *spot["from"], "North Bondi", dy=-10),
        *m.scale_bar(2000),
    ]
    svg(
        "window-wide",
        WIDTH,
        m.height,
        "North Bondi's swell window, zoomed out",
        "The same lines from North Bondi on a map running south to Maroubra. The lines just west of south cross "
        "Bondi's bay and stop on the coast between Bronte and Maroubra, so swell from there runs along the coast "
        "rather than in from the open ocean. The dashed box is the close-up.",
        body,
    )


def wrap_fig():
    """Share of an 8 s and a 14 s swell that reaches Collaroy, by direction: the window's soft edges, and long
    swell wrapping round Long Reef."""
    b, key = BEACH["Collaroy"], "Collaroy"
    w, h, left, right, top, bottom = WIDTH, 240, 40, 14, 22, 46
    d0, d1 = 0, 210

    def xy(d, share):
        return left + (d - d0) / (d1 - d0) * (w - left - right), top + (1 - share) * (h - top - bottom)

    body = []
    a0, a1 = open_arc(key)
    (x0, _), (x1, _) = xy(max(a0, d0), 0), xy(min(a1, d1), 0)
    body.append(
        f'<rect x="{x0:.1f}" y="{top}" width="{x1 - x0:.1f}" height="{h - top - bottom}" '
        'fill="var(--accent)" opacity=".1"/>'
    )
    body.append(
        f'<text x="{(x0 + x1) / 2:.1f}" y="{top - 8}" text-anchor="middle" class="hs-small">'
        "open ocean from Collaroy</text>"
    )
    for v in (0, 0.25, 0.5, 0.75, 1):
        _, y = xy(d0, v)
        body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="var(--line)"/>')
        body.append(f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end" class="hs-small">{round(v * 100)}%</text>')
    for d, label in ((0, "N"), (45, "NE"), (90, "E"), (135, "SE"), (180, "S")):
        x, _ = xy(d, 0)
        body.append(f'<text x="{x:.1f}" y="{h - bottom + 16}" text-anchor="middle" class="hs-small">{label}</text>')
    ds = range(d0, d1 + 1, 2)
    for period, style in ((14, 'stroke="var(--accent)"'), (8, 'stroke="var(--r-amber)" stroke-dasharray="6 3"')):
        pts = [xy(d, swell.exposure(b, key, d, period)) for d in ds]
        body.append(f'<path d="{path(pts, close=False)}" fill="none" {style} stroke-width="2.5"/>')
    d = 158
    e8, e14 = swell.exposure(b, key, d, 8), swell.exposure(b, key, d, 14)
    x, y14 = xy(d, e14)
    _, y8 = xy(d, e8)
    body += [
        f'<line x1="{x:.1f}" y1="{y14:.1f}" x2="{x:.1f}" y2="{y8:.1f}" stroke="var(--text)" stroke-width="1"/>',
        f'<text x="{x + 6:.1f}" y="{y14 - 6:.1f}" class="hs-label">14 s: {round(e14 * 100)}%</text>',
        f'<text x="{x + 6:.1f}" y="{y8 + 14:.1f}" class="hs-label">8 s: {round(e8 * 100)}%</text>',
        f'<path d="M{left},{h - 8}h18" stroke="var(--accent)" stroke-width="2.5"/>',
        f'<text x="{left + 24}" y="{h - 4}" class="hs-small">14 s groundswell</text>',
        f'<path d="M{left + 130},{h - 8}h18" stroke="var(--r-amber)" stroke-width="2.5" stroke-dasharray="6 3"/>',
        f'<text x="{left + 154}" y="{h - 4}" class="hs-small">8 s swell</text>',
    ]
    svg(
        "wrap",
        w,
        h,
        "Long swell wraps further into Collaroy",
        f"Line chart of how much of a swell reaches Collaroy from each direction, north round to south. Both lines "
        f"fade out at the edges of the open ocean rather than stopping dead. From the south-south-east, round Long "
        f"Reef, about {round(e8 * 100)}% of an 8 second swell gets in and {round(e14 * 100)}% of a 14 second one.",
        body,
    )


def share_fig():
    """North Bondi: a line every 4 degrees, coloured by the share of a 10 s swell from that direction that gets in,
    with NE, E, SE and S labelled."""
    m, b = BONDI, BEACH[BONDI_KEY]
    spot = swell.WINDOWS["spots"][BONDI_KEY]
    ox, oy = m.px(*spot["from"])

    def colour(share):
        return "r-green" if share >= 0.6 else "r-amber" if share >= 0.25 else "r-red"

    rays = []
    for d in range(32, 212, 8):  # north-east round to south-south-west: the sea side
        share = swell.exposure(b, BONDI_KEY, d, 10)
        x, y = toward(ox, oy, d, 150)
        dash = "" if share >= 0.25 else ' stroke-dasharray="3 3"'
        rays.append(
            f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--{colour(share)})" '
            f'stroke-width="1.4" opacity=".85"{dash}/>'
        )
    a0, a1 = open_arc(BONDI_KEY)
    edges = [
        f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--accent)" '
        'stroke-width="1.2" stroke-dasharray="4 3"/>'
        for x, y in (toward(ox, oy, a, 600) for a in (a0, a1))
    ]
    body = [
        f'<rect width="{WIDTH}" height="{m.height}" fill="var(--hs-sea)"/>',
        f'<path d="{wedge(ox, oy, a0, a1, 600)}" fill="var(--accent)" opacity=".18"/>',
        *edges,
        *m.land(),
        *rays,
    ]
    for deg, label, r in ((45, "NE", 152), (90, "E", 152), (135, "SE", 152), (170, "S", 150)):
        share = swell.exposure(b, BONDI_KEY, deg, 10)
        east = math.sin(rad(deg)) > 0.3
        tx, ty = toward(ox, oy, deg, r + (8 if east else 16))
        tx, ty = min(max(tx, 30), WIDTH - 60), min(max(ty + 5, 14), m.height - 8)
        body.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{"start" if east else "middle"}" '
            f'class="hs-label">{label} <tspan class="hs-num" fill="var(--{colour(share)})">'
            f"{round(share * 100)}%</tspan></text>"
        )
    legend = (("r-green", "most gets in (60%+)"), ("r-amber", "some (25–60%)"), ("r-red", "little (under 25%)"))
    for i, (c, words) in enumerate(legend):
        y = 22 + i * 16
        dash = ' stroke-dasharray="3 3"' if c == "r-red" else ""
        body.append(f'<path d="M14,{y - 4}h18" stroke="var(--{c})" stroke-width="2.5"{dash}/>')
        body.append(f'<text x="38" y="{y}" class="hs-small">{words}</text>')
    body += [place(m, -33.8893, 151.2852, "Ben Buckler"), *pin(m, *spot["from"], "North Bondi")]
    svg(
        "share",
        WIDTH,
        m.height,
        "How much swell reaches North Bondi",
        f"North Bondi with its open ocean shaded, {a0} to {a1} degrees, and a line every 8 degrees out to sea, "
        "coloured by how much of a 10 second swell from that "
        "direction reaches the north end: red (under 25%) from the north-east and east, which Ben Buckler blocks, "
        "amber as it opens up, and green from the south-east round to the south.",
        body,
    )


def period_fig():
    """Breaking height of a 1.5 m swell against period: a swimming beach and a surf break."""
    w, h, left, right, top, bottom = WIDTH, 220, 44, 16, 16, 34
    t0, t1, y0, y1 = 6, 16, 0.75, 2.25

    def xy(t, hgt):
        return (left + (t - t0) / (t1 - t0) * (w - left - right), top + (y1 - hgt) / (y1 - y0) * (h - top - bottom))

    body = []
    for v in (1.0, 1.5, 2.0):
        _, y = xy(t0, v)
        body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="var(--line)"/>')
        body.append(f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end" class="hs-small">{v:g}m</text>')
    for t in range(6, 17, 2):
        x, _ = xy(t, y0)
        body.append(f'<text x="{x:.1f}" y="{h - bottom + 16}" text-anchor="middle" class="hs-small">{t} s</text>')
    body.append(f'<text x="{w - right}" y="{h - 4}" text-anchor="end" class="hs-small">swell period</text>')
    ts = [t0 + i * 0.25 for i in range(int((t1 - t0) / 0.25) + 1)]
    beach = [xy(t, swell.breaker(1.5, t)) for t in ts]
    surf = [xy(t, swell.breaker(1.5, t, exponent=0.7, ref=10)) for t in ts]
    body += [
        f'<path d="{path(beach, close=False)}" fill="none" stroke="var(--accent)" stroke-width="2.5"/>',
        f'<path d="{path(surf, close=False)}" fill="none" stroke="var(--r-amber)" stroke-width="2.5" '
        'stroke-dasharray="6 3"/>',
    ]
    bx, by = xy(9, swell.breaker(1.5, 9))
    sx, sy = xy(7, swell.breaker(1.5, 7, exponent=0.7, ref=10))
    body += [
        f'<text x="{bx:.1f}" y="{by - 10:.1f}" text-anchor="middle" class="hs-label">swimming beach</text>',
        f'<text x="{sx + 8:.1f}" y="{sy + 16:.1f}" class="hs-label">surf break</text>',
    ]
    svg(
        "period",
        w,
        h,
        "Longer swell breaks bigger",
        "Line chart of how big a 1.5 metre swell breaks, by its period from 6 to 16 seconds. At a swimming beach it "
        f"grows gently, from {swell.breaker(1.5, 6):.1f}m at 6 seconds to {swell.breaker(1.5, 16):.1f}m at 16. "
        "At a surf break it grows faster, and short swell is weaker there.",
        body,
    )


G = 9.81


def deep_length(t):
    """Deep-water wavelength (m) of a wave with period t (s): g t^2 / 2 pi, about 1.56 t^2."""
    return G * t * t / (2 * math.pi)


def group_kmh(t):
    """How fast a swell's energy crosses deep water (km/h): half the crest speed, g t / 4 pi."""
    return G * t / (4 * math.pi) * 3.6


def chop_fig():
    """From above, side by side: 1.5 m of 6 s wind swell and 1.5 m of 13 s groundswell coming in to a beach. The
    wind swell is short, broken crests from two directions with whitecaps; the groundswell long, even lines that bend
    to the sand. The crests are spaced for reading rather than to scale (the swell-types figure has that). Under
    each, how big it breaks at a swimming beach, from the score's own formula."""
    import random

    w, gap = WIDTH, 12
    pw = (w - gap) / 2  # each panel
    sea_top, sea_h, sand_h = 30, 150, 16
    body = []
    rnd = random.Random(7)
    for k, (t, name, rough) in enumerate(((6, "Wind swell", True), (13, "Groundswell", False))):
        x0 = k * (pw + gap)
        clip = f"chop-clip-{k}"
        body.append(
            f'<clipPath id="{clip}"><rect x="{x0:.1f}" y="{sea_top}" width="{pw:.1f}" height="{sea_h}" rx="8"/>'
            "</clipPath>"
        )
        body.append(f'<rect x="{x0:.1f}" y="{sea_top}" width="{pw:.1f}" height="{sea_h}" rx="8" fill="var(--hs-sea)"/>')
        g = [f'<g clip-path="url(#{clip})">']
        beach_y = sea_top + sea_h - sand_h
        lam = 17 if rough else 38  # px between crests: short and close, against long and well apart
        if rough:
            # two trains crossing: short wobbly crest pieces at two angles, and whitecaps
            for ang, phase in ((-12, 0.0), (20, 0.5)):
                y = sea_top - 20 + phase * lam
                while y < beach_y:
                    xx = x0 - 20
                    while xx < x0 + pw + 20:
                        seg = rnd.uniform(10, 20)
                        dy = math.tan(math.radians(ang)) * seg
                        yy = y + math.tan(math.radians(ang)) * (xx - x0) + rnd.uniform(-2, 2)
                        g.append(
                            f'<path d="M{xx:.1f},{yy:.1f} q{seg / 2:.1f},{-2.5:.1f} {seg:.1f},{dy:.1f}" fill="none" '
                            'stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round" opacity=".85"/>'
                        )
                        if rnd.random() < 0.12:
                            g.append(
                                f'<path d="M{xx + seg * 0.3:.1f},{yy - 1:.1f} h{rnd.uniform(4, 8):.1f}" '
                                'stroke="#fff" stroke-width="2" stroke-linecap="round"/>'
                            )
                        xx += seg + rnd.uniform(12, 22)
                    y += lam
            # messy white water all along the sand
            xx = x0
            while xx < x0 + pw:
                seg = rnd.uniform(6, 14)
                g.append(
                    f'<path d="M{xx:.1f},{beach_y - rnd.uniform(1, 5):.1f} h{seg:.1f}" stroke="#fff" '
                    'stroke-width="2.5" stroke-linecap="round" opacity=".9"/>'
                )
                xx += seg + rnd.uniform(2, 8)
        else:
            # long, even lines bending a little to the sand, and one clean line of white water
            y = sea_top + 8
            while y < beach_y - 6:
                bow = 6 * (1 - (y - sea_top) / sea_h)
                g.append(
                    f'<path d="M{x0 - 5:.1f},{y + bow:.1f} Q{x0 + pw / 2:.1f},{y - bow:.1f} '
                    f'{x0 + pw + 5:.1f},{y + bow:.1f}" fill="none" stroke="var(--accent)" stroke-width="2"/>'
                )
                y += lam
            g.append(
                f'<path d="M{x0 + 6:.1f},{beach_y - 4:.1f} Q{x0 + pw / 2:.1f},{beach_y - 8:.1f} {x0 + pw - 6:.1f},'
                f'{beach_y - 4:.1f}" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>'
            )
        g.append(f'<rect x="{x0:.1f}" y="{beach_y:.1f}" width="{pw:.1f}" height="{sand_h + 2}" fill="var(--hs-land)"/>')
        g.append("</g>")
        body += g
        hb = swell.breaker(1.5, t)
        body += [
            f'<text x="{x0 + 2:.1f}" y="{sea_top - 10}" class="hs-label">{name} · {t} s</text>',
            f'<text x="{x0 + 2:.1f}" y="{sea_top + sea_h + 18}" class="hs-label">'
            f'Breaks about <tspan class="hs-num">{hb:.1f}m</tspan></text>',
            f'<text x="{x0 + 2:.1f}" y="{sea_top + sea_h + 34}" class="hs-small">'
            f"{'Choppy and crumbly, from two ways' if rough else 'Clean lines, well spaced'}</text>",
        ]
    svg(
        "chop",
        w,
        sea_top + sea_h + 40,
        "The same 1.5m, two different days",
        "Two views from above of 1.5 metres of swell reaching a beach. On the left, a 6-second wind swell: short, "
        f"broken crests close together from two directions, whitecaps, and messy white water; it breaks about "
        f"{swell.breaker(1.5, 6):.1f} metres at a swimming beach. On the right, a 13-second groundswell: long, even "
        f"lines well apart, bending to the sand, and one clean line of white water; it breaks about "
        f"{swell.breaker(1.5, 13):.1f} metres.",
        body,
    )


def swell_types_fig():
    """Side-on, to scale: a 6 s wind swell and a 14 s groundswell over the same 600 m of sea, and below, how deep
    each one starts to feel the seabed (half its wavelength) on a Sydney-like shelf."""
    w = WIDTH
    left, right = 10, 10
    span = 600  # metres of sea shown in each wave row
    sx = (w - left - right) / span
    body = []

    def row(y0, t, label, words, rough):
        lam = deep_length(t)
        amp = 9 if rough else 11
        pts = []
        for i in range(int(w - left - right) + 1):
            x = i / sx
            if rough:  # wind swell: short and steep, from more than one direction at once
                z = (
                    math.sin(2 * math.pi * x / lam)
                    + 0.45 * math.sin(2 * math.pi * x / (lam * 0.62) + 1.3)
                    + 0.3 * math.sin(2 * math.pi * x / (lam * 1.7) + 0.4)
                )
                z /= 1.6
            else:  # groundswell: long, even lines
                z = math.sin(2 * math.pi * x / lam + 1.0)
            # a touch of the trochoid: sharper crests, flatter troughs
            pts.append((left + i, y0 - amp * z - (2.5 if rough else 1.5) * z * abs(z)))
        sea = pts + [(w - right, y0 + 26), (left, y0 + 26)]
        out = [f'<path d="{path(sea)}" fill="var(--hs-sea)" stroke="var(--accent)" stroke-width="1.6"/>']
        # wavelength bracket between two crests
        # between two crests: sin peaks at x = lam (1/4 - phase/2pi)
        x0 = left + lam * ((2.25 if rough else 0.25 - 1.0 / (2 * math.pi)) % 1 + (2 if rough else 0)) * sx
        x1 = x0 + lam * sx
        yb = y0 - amp - 12
        out += [
            f'<path d="M{x0:.1f},{yb + 4}V{yb}H{x1:.1f}V{yb + 4}" fill="none" stroke="var(--text)" stroke-width="1"/>',
            f'<text x="{(x0 + x1) / 2:.1f}" y="{yb - 4}" text-anchor="middle" class="hs-small">'
            f"{lam:.0f} m between crests</text>",
            f'<text x="{left}" y="{y0 - 38}" class="hs-label">{label}</text>',
            f'<text x="{left}" y="{y0 + 42}" class="hs-small">{words}</text>',
        ]
        return out

    body += row(
        56, 6, "Wind swell · 6 s", f"Made nearby. Short, steep and messy. Travels about {group_kmh(6):.0f} km/h.", True
    )
    body += row(
        168,
        14,
        "Groundswell · 14 s",
        f"Made by a storm far away. Long, clean lines. Travels about {group_kmh(14):.0f} km/h.",
        False,
    )

    # The seabed, side-on: Sydney's shelf drops to about 150 m some 30 km out
    top, base, km = 262, 370, 36
    gx = (w - left - right) / km

    def depth(xkm):  # metres, coast at 0 km: steep near shore, then the long gentle shelf
        return min(170, 30 * (1 - math.exp(-xkm / 1.2)) + 4.1 * xkm)

    dmax = 170
    dy = (base - top) / dmax
    floor = [(left + i * gx / 4, top + depth(i / 4) * dy) for i in range(km * 4 + 1)]
    body += [
        f'<text x="{left}" y="{top - 22}" class="hs-label">Where each starts to feel the seabed</text>',
        f'<line x1="{left}" y1="{top}" x2="{w - right}" y2="{top}" stroke="var(--accent)" stroke-width="1.6"/>',
        f'<path d="{path([(left, top), *floor, (w - right, base + 4), (left, base + 4)])}" fill="var(--hs-land)"/>',
        f'<text x="{left + 2}" y="{top - 6}" class="hs-small">beach</text>',
        f'<text x="{w - right}" y="{top - 6}" text-anchor="end" class="hs-small">{km} km out</text>',
    ]
    for t, c, dash in ((6, "r-amber", ' stroke-dasharray="5 3"'), (14, "accent", "")):
        d = deep_length(t) / 2
        xkm = next(i / 20 for i in range(km * 20 + 1) if depth(i / 20) >= d)
        x, y = left + xkm * gx, top + d * dy
        body += [
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--{c})" stroke-width="2"{dash}/>',
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="var(--{c})"/>',
            f'<text x="{x + (8 if t == 6 else -8):.1f}" y="{y + (14 if t == 6 else -8):.1f}" '
            f'text-anchor="{"start" if t == 6 else "end"}" class="hs-small">{t} s: {d:.0f} m deep, ~{xkm:.0f} km out'
            "</text>",
        ]
    svg(
        "swell-types",
        w,
        base + 6,
        "Wind swell and groundswell",
        f"Two side-on wave trains over the same 600 metres of sea, to scale. A 6-second wind swell has crests "
        f"{deep_length(6):.0f} metres apart and is short and messy; a 14-second groundswell has crests "
        f"{deep_length(14):.0f} metres apart in long, even lines, and travels more than twice as fast. Below, a "
        "side-on seabed out to 36 km: a wave starts to feel the bottom at half its wavelength, so the groundswell "
        "starts "
        "slowing and bending about 30 km out and the wind swell only a couple of kilometres from the beach.",
        body,
    )


def phase_speed(t, d):
    """Crest speed (m/s) of period t in depth d, from linear wave theory (Eckart's approximation)."""
    k0h = 4 * math.pi**2 * d / (G * t * t)
    kh = k0h / math.sqrt(math.tanh(k0h))
    return G * t / (2 * math.pi) * math.tanh(kh)


def crest_lines(tt, level, ox, oy, scale):
    """Marching squares over the arrival-time grid tt (NaN on land): the crest at time `level`, as SVG paths."""
    ny, nx = tt.shape
    segs = []
    for i in range(ny - 1):
        for j in range(nx - 1):
            a, b, c, d = tt[i, j], tt[i, j + 1], tt[i + 1, j + 1], tt[i + 1, j]
            if np.isnan(a) or np.isnan(b) or np.isnan(c) or np.isnan(d):
                continue
            corners = [(a, j, i), (b, j + 1, i), (c, j + 1, i + 1), (d, j, i + 1)]
            pts = []
            for k in range(4):
                v0, x0, y0 = corners[k]
                v1, x1, y1 = corners[(k + 1) % 4]
                if (v0 < level) != (v1 < level):
                    f = (level - v0) / (v1 - v0)
                    pts.append((x0 + f * (x1 - x0), y0 + f * (y1 - y0)))
            if len(pts) == 2:
                segs.append(tuple(pts))
            elif len(pts) == 4:
                segs += [(pts[0], pts[1]), (pts[2], pts[3])]
    lines = MultiLineString([[(ox + x * scale, oy + y * scale) for x, y in sg] for sg in segs])
    merged = line_merge(lines).simplify(0.5)
    geoms = getattr(merged, "geoms", [merged])
    return [path(list(g.coords), close=False) for g in geoms if g.length > 6]


def rays(tt, wet, dx, ux, uy, W, H, scale, oy, spacing=120.0, step=6.0):
    """Wave rays traced up the arrival-time gradient from evenly spaced starts along the deep edges. The energy
    between two rays stays the same (Salmon, Introduction to Ocean Waves, ch. 6), so where they close up the waves
    grow and where they spread apart the waves shrink."""
    gy, gx = np.gradient(tt, dx)
    ny, nx = tt.shape

    def grad(x, y):
        j, i = x / dx, y / dx
        j0, i0 = int(j), int(i)
        if not (0 <= j0 < nx - 1 and 0 <= i0 < ny - 1):
            return None
        fj, fi = j - j0, i - i0
        out = []
        for g in (gx, gy):
            v = (
                g[i0, j0] * (1 - fj) * (1 - fi)
                + g[i0, j0 + 1] * fj * (1 - fi)
                + g[i0 + 1, j0] * (1 - fj) * fi
                + g[i0 + 1, j0 + 1] * fj * fi
            )
            out.append(v)
        if any(np.isnan(out)) or not wet[round(i), round(j)]:
            return None
        n = math.hypot(*out)
        return (out[0] / n, out[1] / n) if n else None

    starts = [(W - dx, y) for y in np.arange(spacing / abs(ux) / 2, H, spacing / abs(ux))]
    starts += [(x, H - dx) for x in np.arange(W - spacing / abs(uy) / 2, 0, -spacing / abs(uy))]
    out = []
    for x, y in starts:
        pts = [(x, y)]
        for _ in range(3000):
            g = grad(x, y)
            if g is None:
                break
            x, y = x + step * g[0], y + step * g[1]
            pts.append((x, y))
        if len(pts) > 5:
            line = LineString([(px_ * scale, oy + py * scale) for px_, py in pts]).simplify(0.4)
            out.append(path(list(line.coords), close=False))
    return out


def refraction_fig():
    """Plan view of a made-up headland: where 8 s and 14 s crests are, swell coming from the south-east. The seabed
    deepens away from the coast, each period's crest speed comes from the depth (linear wave theory), and the
    arrival time over the whole bay is solved on a grid (Dijkstra, 16 directions); each crest is a line of equal
    arrival time, one period apart."""
    w = WIDTH
    W, H, dx = 3000.0, 1800.0, 15.0  # metres; north is up, the coast runs along the top
    nx, ny = int(W / dx) + 1, int(H / dx) + 1
    # A broad point sticking out south, a curved bay to its west, and straighter coast to the east
    bay = [(0, 330), (250, 420), (550, 470), (850, 470), (1150, 430), (1400, 380)]
    point = [
        (1500, 480),
        (1560, 760),
        (1640, 1000),
        (1760, 1180),
        (1900, 1250),
        (2040, 1200),
        (2120, 1040),
        (2180, 800),
        (2260, 560),
        (2400, 420),
    ]
    east = [(2700, 360), (3000, 340)]
    land = Polygon([(0, 0), *bay, *point, *east, (3000, 0)]).buffer(80).buffer(-80)  # rounded off
    xs, ys = np.meshgrid(np.arange(nx) * dx, np.arange(ny) * dx)
    pts = shapely.points(xs.ravel(), ys.ravel())
    dist = shapely.distance(pts, land).reshape(ny, nx)
    wet = dist > 0
    depth = np.clip(1.0 + 0.04 * dist, 0, 55)

    heading = math.radians(290)  # travelling west-north-west: from the east-south-east
    ux, uy = math.sin(heading), -math.cos(heading)  # y down
    steps = [
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
        (1, 2),
        (2, 1),
        (-1, 2),
        (-2, 1),
        (1, -2),
        (2, -1),
        (-1, -2),
        (-2, -1),
    ]

    def arrival(t):
        speed = np.vectorize(lambda d: phase_speed(t, d) if d > 0 else np.nan)(depth)
        c0 = G * t / (2 * math.pi)
        tt = np.full((ny, nx), np.inf)
        heap = []
        for i in range(ny):
            for j in range(nx):
                if wet[i, j] and (i == ny - 1 or j == nx - 1):  # the deep open edges: a straight swell front
                    tt[i, j] = (j * dx * ux + i * dx * uy) / c0
                    heapq.heappush(heap, (tt[i, j], i, j))
        done = np.zeros((ny, nx), bool)
        while heap:
            t0, i, j = heapq.heappop(heap)
            if done[i, j]:
                continue
            done[i, j] = True
            for di, dj in steps:
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < ny and 0 <= j2 < nx) or not wet[i2, j2] or done[i2, j2]:
                    continue
                if abs(di) == 2 or abs(dj) == 2:  # a knight's move mustn't cut across land
                    if not wet[i + di // 2 if abs(di) == 2 else i, j + dj // 2 if abs(dj) == 2 else j]:
                        continue
                cost = dx * math.hypot(di, dj) * (1 / speed[i, j] + 1 / speed[i2, j2]) / 2
                if t0 + cost < tt[i2, j2]:
                    tt[i2, j2] = t0 + cost
                    heapq.heappush(heap, (tt[i2, j2], i2, j2))
        tt[~wet] = np.nan
        tt[np.isinf(tt)] = np.nan
        return tt

    pw, gap = w, 14
    scale = pw / W  # px per metre
    ph = H * scale
    body = [arrow_defs("hs-rf", ("text",))]
    for row, (t, label, c) in enumerate(((8, "8 s wind swell", "r-amber"), (14, "14 s groundswell", "accent"))):
        oy = row * (ph + gap)
        tt = arrival(t)
        lo = np.nanmin(tt)
        body.append(f'<rect x="0" y="{oy:.1f}" width="{pw}" height="{ph:.1f}" fill="var(--hs-sea)"/>')
        for dd in (10, 25, 45):  # depth contours, faint
            for d_ in crest_lines(np.where(wet, depth, np.nan), dd, 0, oy, dx * scale):
                body.append(
                    f'<path d="{d_}" fill="none" stroke="var(--muted)" stroke-width=".8" '
                    'stroke-dasharray="2 3" opacity=".6"/>'
                )
        # crests, one period apart
        k = 1
        while lo + k * t < np.nanmax(tt):
            for d_ in crest_lines(tt, lo + k * t, 0, oy, dx * scale):
                body.append(f'<path d="{d_}" fill="none" stroke="var(--{c})" stroke-width="1.4"/>')
            k += 1
        # rays: the paths the energy takes, square to the crests. Bunched up means bigger waves, spread out smaller
        for d_ in rays(tt, wet, dx, ux, uy, W, H, scale, oy):
            body.append(f'<path d="{d_}" fill="none" stroke="var(--text)" stroke-width=".9" opacity=".45"/>')
        body.append(
            f'<path d="{path([(x * scale, oy + y * scale) for x, y in land.exterior.coords])}" '
            'fill="var(--hs-land)" stroke="var(--muted)" stroke-width="1"/>'
        )
        body.append(f'<text x="8" y="{oy + ph - 10:.1f}" class="hs-label">{label}</text>')
        body.append(
            f'<text x="{1900 * scale:.1f}" y="{oy + 1350 * scale:.1f}" text-anchor="middle" '
            'class="hs-place">the point</text>'
        )
        body.append(
            f'<text x="{700 * scale:.1f}" y="{oy + 340 * scale:.1f}" text-anchor="middle" '
            'class="hs-place">the bay</text>'
        )
        ax, ay = (W - 60) * scale, oy + 1500 * scale
        body.append(
            f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax - 50:.1f}" y2="{ay - 18:.1f}" stroke="var(--text)" '
            'stroke-width="2" marker-end="url(#hs-rf-text)"/>'
        )
        body.append(f'<text x="{ax:.1f}" y="{ay + 16:.1f}" text-anchor="end" class="hs-small">swell from ESE</text>')
    svg(
        "refraction",
        w,
        2 * ph + gap,
        "Swell bending round a headland",
        "Plan view of a made-up headland with swell coming from the east-south-east, drawn twice. Each line is a wave "
        "crest. Over deep water the crests are straight; as the seabed shallows they slow and turn to face the shore. "
        "Both wrap round the point, but the 14-second groundswell feels the bottom further out and bends more, so "
        "in the bay its crests run almost along the beach while the 8-second wind swell's still come in at an angle.",
        body,
    )


KIND_COLOUR = {"offshore": "r-green", "cross": "r-amber", "onshore": "r-red"}


def wind_fig():
    """Coogee: an arrow blowing in from every 15 degrees, coloured by how that wind crosses the beach."""
    m = Map(-33.9290, 151.2470, -33.9130, 151.2740)
    b = BEACH["Coogee"]
    lat, lon = -33.9208, 151.2582
    fx, fy = m.px(lat, lon)
    arrows = []
    for d in range(0, 360, 15):
        kind = wind_kind(d, b.facing)
        c = KIND_COLOUR[kind]
        x0, y0 = toward(fx, fy, d, 150)
        x1, y1 = toward(fx, fy, d, 26)
        dash = ' stroke-dasharray="4 3"' if kind == "onshore" else ""
        arrows.append(
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="var(--{c})" stroke-width="2" '
            f'opacity=".9" marker-end="url(#hs-wind-{c})"{dash}/>'
        )
    labels = []
    for d, words, c in (
        (b.facing + 180, "offshore", "r-green"),
        (b.facing, "onshore", "r-red"),
        (b.facing - 90, "cross-shore", "r-amber"),
        (b.facing + 90, "cross-shore", "r-amber"),
    ):
        x, y = toward(fx, fy, d, 150)
        x, y = min(max(x, 44), WIDTH - 44), min(max(y + 4, 14), m.height - 8)
        labels.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" class="hs-label" fill="var(--{c})">{words}</text>'
        )
    body = [
        arrow_defs("hs-wind", ("r-green", "r-amber", "r-red")),
        f'<rect width="{WIDTH}" height="{m.height}" fill="var(--hs-sea)"/>',
        *m.land(),
        *arrows,
        *labels,
        *pin(m, lat, lon, "Coogee", anchor="end", dx=-10, dy=-8),
        *m.scale_bar(500),
    ]
    svg(
        "wind",
        WIDTH,
        m.height,
        "Which winds are offshore at Coogee",
        f"Arrows blow in to Coogee from every direction. Coogee faces {b.facing} degrees, a little south of east, so "
        "winds from the south-west round to the north-west, off the land, are offshore (green); winds from the "
        "north-east round to the south-east, off the sea, are onshore (red, dashed); the rest are cross-shore "
        "(amber).",
        body,
    )


def wind_water_fig():
    """Side-on: the same swell under an offshore and an onshore wind."""
    w, h, gap = WIDTH, 150, 12
    pw = (w - gap) / 2
    base = 92

    def panel(x0, offshore):
        c = "r-green" if offshore else "r-red"
        out = [
            f'<rect x="{x0:.1f}" y="0" width="{pw:.1f}" height="{h}" rx="6" fill="var(--surface)" '
            'stroke="var(--line)"/>'
        ]
        shore = x0 + 46
        sea = [(shore, base + 6)]
        for i in range(int(pw - 50) + 1):
            x = shore + i
            t = (x - shore) / (pw - 50)
            swell_ = 6 * math.sin((x - shore) / 13) * (0.5 + 0.5 * t)  # waves grow away from the sand
            chop = 0 if offshore else 2.6 * math.sin(x / 2.3) + 1.8 * math.sin(x / 1.4 + 1)
            sea.append((x, base - swell_ - chop))
        bottom = [(x0 + pw, h - 1), (shore - 10, h - 1)]
        out.append(f'<path d="{path(sea + bottom)}" fill="var(--hs-sea)" stroke="var(--accent)" stroke-width="1.5"/>')
        # sand rising to the left, the land the wind comes off (or blows onto)
        out.append(
            f'<path d="M{x0 + 1:.1f},{base - 18}Q{shore - 14:.1f},{base - 16} {shore + 8:.1f},{base + 10}'
            f'L{shore + 8:.1f},{h - 1}L{x0 + 1:.1f},{h - 1}Z" fill="var(--hs-land)"/>'
        )
        if not offshore:
            for x, y in sea[20::22]:
                out.append(
                    f'<path d="M{x - 3:.1f},{y - 1:.1f}l3,-3l3,3" fill="none" stroke="var(--text)" '
                    'stroke-width="1.2" opacity=".7"/>'
                )
        for row, y in enumerate((30, 48)):
            for k in range(3):
                xa = x0 + 22 + k * 52 + row * 24
                xb = xa + 36
                if not offshore:
                    xa, xb = xb, xa
                out.append(
                    f'<line x1="{xa:.1f}" y1="{y}" x2="{xb:.1f}" y2="{y}" stroke="var(--{c})" '
                    f'stroke-width="2.5" marker-end="url(#hs-ww-{c})"/>'
                )
        out.append(
            f'<text x="{x0 + 10:.1f}" y="16" class="hs-label" fill="var(--{c})">'
            f"{'Offshore: clean' if offshore else 'Onshore: choppy'}</text>"
        )
        out.append(
            f'<text x="{x0 + pw - 8:.1f}" y="{h - 10}" text-anchor="end" class="hs-small">'
            f"{'smooth, clear water' if offshore else 'chop, stirred-up water'}</text>"
        )
        return out

    body = [arrow_defs("hs-ww", ("r-green", "r-red")), *panel(0, True), *panel(pw + gap, False)]
    svg(
        "wind-water",
        w,
        h,
        "What offshore and onshore wind do to the water",
        "Two side-on drawings of the same beach and swell. With an offshore wind blowing from the land out to sea, "
        "the water is smooth and clear. With an onshore wind blowing in from the sea, the surface is broken up by "
        "chop and whitecaps.",
        body,
    )


def axis_chart(w, h, left, right, top, bottom, x0, x1, y0, y1):
    """A function mapping data (x, y) to pixels for a simple chart."""

    def xy(x, y):
        return (
            left + (x - x0) / (x1 - x0) * (w - left - right),
            top + (y1 - y) / (y1 - y0) * (h - top - bottom),
        )

    return xy


def hour_label(hr):
    return "noon" if hr == 12 else f"{hr % 12 or 12}{'am' if hr < 12 else 'pm'}"


def poo(cx, base):
    """A turd floating at (cx, base): a lumpy, slightly bent log, half in the water."""
    brown, dark = "#6b4423", "#4a2e16"
    n, length = 48, 42
    top, bottom, centre = [], [], []
    for i in range(n + 1):
        t = i / n
        x = cx - length / 2 + t * length
        y = base - 1 + 3 * math.sin(math.pi * t) - 2 * math.sin(2 * math.pi * t)  # a gentle S bend
        r = (4.4 + 0.7 * math.cos(t * 2 * math.pi * 3)) * (math.sin(math.pi * t) ** 0.5)  # three lumps
        top.append((x, y - r))
        bottom.append((x, y + r))
        centre.append((x, y))
    out = [
        f'<path d="{path(top + bottom[::-1])}" fill="{brown}" stroke="{dark}" stroke-width=".8" '
        'stroke-linejoin="round"/>'
    ]
    for i in (8, 24, 40):  # creases between the lumps
        (x, y), (_, yt), (_, yb) = centre[i], top[i], bottom[i]
        out.append(
            f'<path d="M{x - 0.8:.1f},{yt + 0.6:.1f}Q{x + 1.2:.1f},{y:.1f} {x - 0.4:.1f},{yb - 0.6:.1f}" '
            f'fill="none" stroke="{dark}" stroke-width=".9" opacity=".8"/>'
        )
    shine = [(x, y - (y - yt) * 0.55) for (x, y), (_, yt) in zip(centre[6:42], top[6:42], strict=True)]
    out.append(
        f'<path d="{path(shine, close=False)}" fill="none" stroke="#fff" stroke-width="1" opacity=".22" '
        'stroke-linecap="round"/>'
    )
    # ripples where it sits in the water
    out.append(
        f'<path d="M{cx - length / 2 - 4:.1f},{base + 6:.1f}q4,-2 8,0t8,0M{cx + 8:.1f},{base + 6:.1f}q4,-2 8,0t8,0" '
        'fill="none" stroke="var(--accent)" stroke-width="1" opacity=".7"/>'
    )
    return out


def stormwater_scene(w, h):
    """Rain on the hill, a stormwater drain on the sand, and what comes out of it."""
    sea_y = 62
    out = [f'<rect x="0" y="0" width="{w}" height="{h - 8}" rx="6" fill="var(--hs-sea)" opacity=".35"/>']
    # cloud and rain over the land
    for cx, cy, r in ((52, 20, 12), (68, 14, 14), (86, 20, 11), (68, 24, 12)):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="var(--muted)" opacity=".75"/>')
    for x in range(44, 98, 9):
        out.append(
            f'<line x1="{x}" y1="36" x2="{x - 4}" y2="48" stroke="var(--accent)" stroke-width="1.5" '
            'stroke-linecap="round"/>'
        )
    # land sloping down to the sand, and the sea
    out.append(
        f'<path d="M0,44 Q60,46 110,{sea_y - 4} L150,{sea_y + 4} L150,{h - 8} L0,{h - 8}Z" fill="var(--hs-land)"/>'
    )
    sea = [(140, sea_y + 2)] + [(x, sea_y + 2 * math.sin(x / 9)) for x in range(140, w + 1, 4)]
    out.append(f'<path d="{path(sea + [(w, h - 8), (140, h - 8)])}" fill="var(--hs-sea)"/>')
    out.append(f'<path d="{path(sea, close=False)}" fill="none" stroke="var(--accent)" stroke-width="1.5"/>')
    # the drain, and its plume spreading out from the beach
    out.append(f'<rect x="112" y="{sea_y - 6}" width="30" height="9" rx="2" fill="var(--muted)"/>')
    out.append(f'<ellipse cx="205" cy="{sea_y + 12}" rx="70" ry="10" fill="#8a5a2b" opacity=".45"/>')
    out.append(f'<ellipse cx="185" cy="{sea_y + 10}" rx="38" ry="7" fill="#8a5a2b" opacity=".45"/>')
    out += poo(228, sea_y + 6)
    out.append(f'<text x="{w - 10}" y="22" text-anchor="end" class="hs-label">After rain, stormwater</text>')
    out.append(f'<text x="{w - 10}" y="38" text-anchor="end" class="hs-label">drains onto the beach</text>')
    return out


def water_fig():
    """How much rain in a day rules each eastern beach out, and from how much it starts to count."""
    beaches = sorted([b for b in EASTERN.beaches if not b.harbour], key=lambda b: (b.rain_often, b.rain_occ, b.name))
    row, left, right, top = 20, 112, 16, 26
    w, h = WIDTH, top + row * len(beaches) + 30
    xmax = 25
    xy = axis_chart(w, h, left, right, top, 30, 0, xmax, 0, 1)
    body = []
    for v in (0, 5, 10, 15, 20, 25):
        x, _ = xy(v, 0)
        body.append(f'<line x1="{x:.1f}" y1="{top - 4}" x2="{x:.1f}" y2="{h - 26}" stroke="var(--line)"/>')
        body.append(f'<text x="{x:.1f}" y="{h - 12}" text-anchor="middle" class="hs-small">{v}mm</text>')
    for i, b in enumerate(beaches):
        y = top + i * row + 4
        x0, _ = xy(0, 0)
        xo, _ = xy(b.rain_occ, 0)
        xf, _ = xy(b.rain_often, 0)
        xe, _ = xy(xmax, 0)
        body += [
            f'<text x="{left - 8}" y="{y + 9}" text-anchor="end" class="hs-small">{b.name.replace(" (north end)", "")}'
            f"{' *' if b.poor_grade else ''}</text>",
            f'<rect x="{x0:.1f}" y="{y}" width="{xo - x0:.1f}" height="12" fill="var(--r-green)" opacity=".75"/>',
            f'<rect x="{xo:.1f}" y="{y}" width="{xf - xo:.1f}" height="12" fill="var(--r-amber)" opacity=".75"/>',
            f'<rect x="{xf:.1f}" y="{y}" width="{xe - xf:.1f}" height="12" fill="var(--r-red)" opacity=".75"/>',
        ]
    legend = (("r-green", "fine"), ("r-amber", "loses points"), ("r-red", "ruled out"))
    for i, (c, words) in enumerate(legend):
        x = left + i * 92
        body.append(f'<rect x="{x}" y="6" width="10" height="10" rx="2" fill="var(--{c})" opacity=".75"/>')
        body.append(f'<text x="{x + 15}" y="15" class="hs-small">{words}</text>')
    scene_h = 96
    body = [*stormwater_scene(w, scene_h), f'<g transform="translate(0,{scene_h})">', *body, "</g>"]
    h += scene_h
    svg(
        "water",
        w,
        h,
        "How much rain each beach can take",
        "Bar chart of rain in the last 24 hours against each eastern beach: green where it's fine, amber where it "
        "loses points, red where it's ruled out. Enclosed and lightly flushed beaches like Tamarama and Malabar are "
        "ruled out after 5mm; Bondi, Clovelly and Maroubra take 20mm.",
        body,
    )


def rain_fig():
    """Rain still to come is a vote of eight models (R-RF1): Friday night, 13 Nov 2026, as each model had it two
    days out. Three wet, five dry: the third wettest is the forecast, and Clovelly stays under its 10mm limit."""
    models = [  # mm, 9am Fri to 9am Sat at Clovelly, from the 12 Nov forecasts
        ("ECMWF (Europe)", 13.5),
        ("GEM (Canada)", 12.9),
        ("ECMWF AI", 6.0),
        ("Météo-France", 2.4),
        ("ICON (Germany)", 2.1),
        ("GFS (US)", 1.5),
        ("UK Met Office", 1.5),
        ("JMA (Japan)", 0.6),
    ]
    row, left, right, top = 20, 112, 60, 26
    w, h = WIDTH, top + row * len(models) + 30
    xmax = 15
    xy = axis_chart(w, h, left, right, top, 30, 0, xmax, 0, 1)
    body = []
    for v in (0, 5, 10, 15):
        x, _ = xy(v, 0)
        body.append(f'<line x1="{x:.1f}" y1="{top - 4}" x2="{x:.1f}" y2="{h - 26}" stroke="var(--line)"/>')
        body.append(f'<text x="{x:.1f}" y="{h - 12}" text-anchor="middle" class="hs-small">{v}mm</text>')
    x0, _ = xy(0, 0)
    for i, (name, mm) in enumerate(models):
        y = top + i * row + 4
        x1, _ = xy(mm, 0)
        third = i == 2
        body += [
            f'<text x="{left - 8}" y="{y + 9}" text-anchor="end" class="hs-small">{name}</text>',
            f'<rect x="{x0:.1f}" y="{y}" width="{max(1, x1 - x0):.1f}" height="12" rx="2" '
            f'fill="var(--{"accent" if third else "muted"})" opacity="{1 if third else 0.45}"/>',
            f'<text x="{x1 + 5:.1f}" y="{y + 10}" class="hs-small{" hs-num" if third else ""}">{mm:g}mm'
            f"{'  ← the forecast' if third else ''}</text>",
        ]
    xl, _ = xy(10, 0)
    body += [
        f'<line x1="{xl:.1f}" y1="{top - 8}" x2="{xl:.1f}" y2="{h - 26}" stroke="var(--r-red)" stroke-width="1.5" '
        'stroke-dasharray="4 3"/>',
        f'<text x="{xl:.1f}" y="{top - 12}" text-anchor="middle" class="hs-small">Clovelly\'s limit</text>',
    ]
    svg(
        "rain",
        w,
        h,
        "Eight models vote on the rain",
        "Bar chart of the rain eight weather models forecast for Friday night, 13 November 2026: ECMWF 13.5mm and "
        "Canada's GEM 12.9mm, then ECMWF's AI model 6mm, and the other five 2.4mm or less. The third wettest, 6mm, "
        "is the forecast, under Clovelly's 10mm limit.",
        body,
    )


def sessions_fig():
    """Every day's three sessions on a 24-hour clock, noon at the top: night shaded, sunrise and sunset loose."""
    from beach_bot.config import SESSIONS, SLOT_NAMES

    w, h = WIDTH, 316
    cx, cy, r, band = w / 2, 138, 100, 30
    rise, sset = 5.75, 19.5  # around now (summer); they move through the year, so the edges are dashed

    def at(hr, rad_):  # noon at the top, clockwise
        return toward(cx, cy, (hr - 12) * 15, rad_)

    def arc(h0, h1, r0, r1):
        n = max(2, int((h1 - h0) * 4))
        outer = [at(h0 + (h1 - h0) * i / n, r1) for i in range(n + 1)]
        inner = [at(h1 - (h1 - h0) * i / n, r0) for i in range(n + 1)]
        return path(outer + inner)

    body = [
        f'<circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="var(--surface)" stroke="var(--line)"/>',
        # night: sunset round through midnight to sunrise
        f'<path d="{arc(sset, rise + 24, r - band, r)}" fill="var(--muted)" opacity=".18"/>',
    ]
    colours = {"am": "var(--r-amber)", "md": "var(--accent)", "pm": "var(--r-green)"}
    bounds = {k: (rise if a is None else a, sset if b is None else b) for k, (a, b) in SESSIONS.items()}
    for slot, (h0, h1) in bounds.items():
        short, name = SLOT_NAMES[slot]
        body.append(f'<path d="{arc(h0, h1, r - band, r)}" fill="{colours[slot]}" opacity=".85"/>')
        # legend under the clock: one column per session, in the day's order
        lx = w * (0.5 + list(bounds).index(slot)) / len(bounds)
        when = f"{'sunrise' if h0 == rise else hour_label(int(h0))}–{'sunset' if h1 == sset else hour_label(int(h1))}"
        body += [
            f'<rect x="{lx - 34:.1f}" y="{h - 40}" width="10" height="10" rx="2" fill="{colours[slot]}"/>',
            f'<text x="{lx - 20:.1f}" y="{h - 31}" class="hs-label">{name.capitalize()}</text>',
            f'<text x="{lx - 34:.1f}" y="{h - 14}" class="hs-small">{when}</text>',
        ]
    for hr in range(24):  # ticks every hour, numbers every three
        x0, y0 = at(hr, r + 4)
        x1, y1 = at(hr, r + (10 if hr % 3 == 0 else 7))
        body.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="var(--muted)"/>')
        if hr % 3 == 0:
            tx, ty = at(hr, r + 22)
            label = "midnight" if hr == 0 else hour_label(hr)
            body.append(f'<text x="{tx:.1f}" y="{ty + 4:.1f}" text-anchor="middle" class="hs-small">{label}</text>')
    for hr in (rise, sset):  # the session ends at sunrise and sunset, which move through the year
        x0, y0 = at(hr, r - band - 2)
        x1, y1 = at(hr, r + 2)
        body.append(
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="var(--text)" '
            'stroke-width="1.5" stroke-dasharray="3 2"/>'
        )
    body.append(f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" class="hs-label">every day</text>')
    svg(
        "sessions",
        w,
        h,
        "Three sessions a day",
        "A 24-hour clock with noon at the top. Every day is cut into three sessions: morning from sunrise to 11am, "
        "midday from 11am to 2pm, and evening from 2pm to sunset. The night, from sunset to sunrise, isn't scored.",
        body,
    )


def warmth_fig():
    """A day going to 30 that turns with a southerly at 4pm: the temperature, and the warmth the score counts."""
    from beach_bot.forecast import Context

    temps = {
        5: 18,
        6: 18,
        7: 19,
        8: 21,
        9: 23,
        10: 25,
        11: 27,
        12: 28,
        13: 30,
        14: 30,
        15: 29,
        16: 24,
        17: 22,
        18: 21,
        19: 20,
        20: 19,
    }
    hours = {f"2026-01-10T{k:02d}:00": {"temperature_2m": v} for k, v in temps.items()}
    ctx = Context(hours)
    felt = {k: ctx.warmth(f"2026-01-10T{k:02d}:00") for k in temps}
    w, h, left, right, top, bottom = WIDTH, 210, 34, 14, 26, 30
    xy = axis_chart(w, h, left, right, top, bottom, 5, 20, 16, 32)
    body = []
    for i, (x0, x1, label) in enumerate(((5, 11, "morning"), (11, 14, "midday"), (14, 20, "evening"))):
        (a, _), (b, _) = xy(x0, 0), xy(x1, 0)
        body.append(  # alternate shades so the three sessions read apart
            f'<rect x="{a:.1f}" y="{top}" width="{b - a:.1f}" height="{h - top - bottom}" '
            f'fill="var(--accent)" opacity="{".14" if i % 2 else ".06"}"/>'
        )
        body.append(f'<text x="{(a + b) / 2:.1f}" y="{top - 8}" text-anchor="middle" class="hs-small">{label}</text>')
    for v in (16, 20, 24, 28, 32):
        _, y = xy(5, v)
        body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="var(--line)"/>')
        body.append(f'<text x="{left - 5}" y="{y + 4:.1f}" text-anchor="end" class="hs-small">{v}°</text>')
    for hr in (6, 9, 12, 15, 18):
        x, _ = xy(hr, 16)
        body.append(
            f'<text x="{x:.1f}" y="{h - bottom + 16}" text-anchor="middle" class="hs-small">{hour_label(hr)}</text>'
        )
    real = [xy(k, v) for k, v in temps.items()]
    counted = [xy(k, v) for k, v in felt.items()]
    body += [
        f'<path d="{path(real, close=False)}" fill="none" stroke="var(--muted)" stroke-width="2" '
        'stroke-dasharray="5 3"/>',
        f'<path d="{path(counted, close=False)}" fill="none" stroke="var(--r-amber)" stroke-width="2.5"/>',
    ]
    x7, y7 = xy(7, felt[7])
    _, r7 = xy(7, temps[7])
    x17, y17 = xy(17, temps[17])
    body += [
        f'<circle cx="{x7:.1f}" cy="{y7:.1f}" r="3.5" fill="var(--r-amber)"/>',
        f'<text x="{x7 - 6:.1f}" y="{y7 - 9:.1f}" class="hs-label">7am counts as {felt[7]:.0f}°</text>',
        f'<text x="{x7 + 2:.1f}" y="{r7 + 16:.1f}" class="hs-small">it’s {temps[7]}°</text>',
        f'<text x="{x17 - 6:.1f}" y="{y17 + 22:.1f}" text-anchor="end" class="hs-small">'
        "southerly: counts as it is</text>",
        f'<path d="M{left},{h - 6}h16" stroke="var(--muted)" stroke-width="2" stroke-dasharray="5 3"/>',
        f'<text x="{left + 20}" y="{h - 2}" class="hs-small">temperature</text>',
        f'<path d="M{left + 110},{h - 6}h16" stroke="var(--r-amber)" stroke-width="2.5"/>',
        f'<text x="{left + 130}" y="{h - 2}" class="hs-small">warmth the score counts</text>',
    ]
    svg(
        "warmth",
        w,
        h + 4,
        "Warmth counts where the day is heading",
        f"Line chart of a day going to 30 degrees with a southerly change at 4pm. At 7am it's {temps[7]} degrees, but "
        f"the score counts {felt[7]:.0f}, three under the warmth still to come. Through the afternoon it counts the "
        "warmth, three under the peak, until the change drops it four degrees or more; after that it counts the "
        "real temperature.",
        body,
    )


def sky_fig():
    """What the sky and the water temperature do to the score (points out of 100), as in scoring.weather()."""
    rows = (
        ("Storms about", None),
        ("Raining, or 60%+ chance", -20),
        ("40–60% chance of rain", -8),
        ("Heavy cloud (85%+)", -5),
        ("Air 26° or warmer", 15),
        ("Air under 17°", -15),
        ("Water over 22°", 5),
        ("Water under 20°", 0),
    )
    row, left, right, top = 22, 158, 24, 10
    w, h = WIDTH, top + row * len(rows) + 8
    mid = left + (w - left - right) / 2
    per = (w - left - right) / 2 / 32
    body = [
        f'<line x1="{mid:.1f}" y1="{top - 4}" x2="{mid:.1f}" y2="{h - 4}" stroke="var(--line)" stroke-width="1.5"/>'
    ]
    for i, (label, pts) in enumerate(rows):
        y = top + i * row
        body.append(f'<text x="{left - 8}" y="{y + 12}" text-anchor="end" class="hs-small">{label}</text>')
        if pts is None:
            body.append(
                f'<rect x="{left}" y="{y + 2}" width="{w - left - right}" height="14" rx="3" '
                'fill="var(--r-red)" opacity=".18"/>'
            )
            body.append(
                f'<text x="{mid:.1f}" y="{y + 13}" text-anchor="middle" class="hs-label" '
                'fill="var(--r-red)">ruled out</text>'
            )
        elif pts == 0:
            body.append(f'<text x="{mid + 6:.1f}" y="{y + 13}" class="hs-small">noted, no penalty</text>')
        else:
            c = "r-green" if pts > 0 else "r-red"
            x = mid if pts > 0 else mid + pts * per
            body.append(
                f'<rect x="{x:.1f}" y="{y + 3}" width="{abs(pts) * per:.1f}" height="12" rx="2" '
                f'fill="var(--{c})" opacity=".8"/>'
            )
            tx = mid + pts * per + (5 if pts > 0 else -5)
            body.append(
                f'<text x="{tx:.1f}" y="{y + 13}" text-anchor="{"start" if pts > 0 else "end"}" '
                f'class="hs-label">{pts:+d}</text>'
            )
    svg(
        "sky",
        w,
        h,
        "What the weather does to a score",
        "Bar chart of points out of 100. Storms rule a session out. Rain falling or a 60% chance costs 20, a 40 to "
        "60% chance costs 8, heavy cloud costs 5. Air of 26 degrees or more adds 15 and under 17 takes 15. Water "
        "over 22 degrees adds 5; water under 20 is only noted.",
        body,
    )


def pools_fig():
    """A day's tide: when a big swell washes over the pool walls, and the tides some pools are best at."""
    w, h, left, right, top, bottom = WIDTH, 190, 14, 14, 24, 30
    xy = axis_chart(w, h, left, right, top, bottom, 5, 21, -1.25, 1.25)
    high = 9.0
    tide = [xy(t / 4, math.cos(2 * math.pi * (t / 4 - high) / 12.4)) for t in range(20, 85)]
    body = []
    for hi in (high, high + 12.4):
        if hi - 2.5 < 21:
            (a, _), (b, _) = xy(max(hi - 2.5, 5), 0), xy(min(hi + 2.5, 21), 0)
            body.append(
                f'<rect x="{a:.1f}" y="{top}" width="{b - a:.1f}" height="{h - top - bottom}" '
                'fill="var(--r-amber)" opacity=".15"/>'
            )
    lo = high + 6.2
    (a, _), (b, _) = xy(lo - 3, 0), xy(lo + 3, 0)
    body.append(
        f'<rect x="{a:.1f}" y="{top}" width="{b - a:.1f}" height="{h - top - bottom}" '
        'fill="var(--r-green)" opacity=".12"/>'
    )
    body.append(f'<path d="{path(tide, close=False)}" fill="none" stroke="var(--accent)" stroke-width="2.5"/>')
    hx, hy = xy(high, 1)
    lx, ly = xy(lo, -1)
    body += [
        f'<text x="{hx:.1f}" y="{top - 8}" text-anchor="middle" class="hs-small">'
        "high tide: big swell washes over</text>",
        f'<text x="{lx:.1f}" y="{ly - 10:.1f}" text-anchor="middle" class="hs-small">'
        "low tide: Wylie’s, McIver’s</text>",
        f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="3.5" fill="var(--accent)"/>',
        f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.5" fill="var(--accent)"/>',
    ]
    for hr in (6, 9, 12, 15, 18, 21):
        x, _ = xy(hr, 0)
        body.append(
            f'<text x="{x:.1f}" y="{h - bottom + 16}" text-anchor="middle" class="hs-small">{hour_label(hr)}</text>'
        )
    svg(
        "pools",
        w,
        h,
        "Ocean pools and the tide",
        "A day's tide curve. Around high tide, two and a half hours either side, a big swell washes over the pool "
        "walls. Around low tide is when the low-tide pools, Wylie's Baths and McIver's, are at their best.",
        body,
    )


def bluebottle_fig():
    """Maroubra: the winds that blow bluebottles in, every 10 degrees."""
    m = Map(-33.9580, 151.2400, -33.9380, 151.2720)
    lat, lon = -33.9475, 151.2572
    fx, fy = m.px(lat, lon)
    lines = []
    for d in range(0, 360, 10):
        ne, south = 20 <= d <= 70, 135 <= d <= 200
        c, op = ("r-red", ".9") if ne or south else ("muted", ".35")
        x0, y0 = toward(fx, fy, d, 140)
        x1, y1 = toward(fx, fy, d, 22)
        lines.append(
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="var(--{c})" '
            f'stroke-width="2" opacity="{op}"/>'
        )
    labels = []
    for d, words in ((45, "north-easterlies"), (168, "southerlies")):
        x, y = toward(fx, fy, d, 150)
        x, y = min(max(x, 60), WIDTH - 60), min(max(y + 4, 14), m.height - 8)
        labels.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" class="hs-label" fill="var(--r-red)">{words}</text>'
        )
    body = [
        f'<rect width="{WIDTH}" height="{m.height}" fill="var(--hs-sea)"/>',
        *m.land(),
        *lines,
        *labels,
        *pin(m, lat, lon, "Maroubra", anchor="end", dx=-10, dy=-8),
        *m.scale_bar(500),
    ]
    svg(
        "bluebottles",
        WIDTH,
        m.height,
        "Winds that bring bluebottles",
        "Maroubra with lines for every wind direction. North-easterlies and southerlies are highlighted: a day of "
        "either at 20 km/h or more, from November to March, can blow bluebottles onto the eastern beaches, Maroubra "
        "most of all.",
        body,
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:  # just the named figures
        for name in sys.argv[1:]:
            globals()[f"{name.replace('-', '_')}_fig"]()
        sys.exit()
    sessions_fig()
    window_fig()
    window_wide_fig()
    wrap_fig()
    share_fig()
    period_fig()
    chop_fig()
    wind_fig()
    wind_water_fig()
    water_fig()
    rain_fig()
    warmth_fig()
    sky_fig()
    pools_fig()
    bluebottle_fig()
