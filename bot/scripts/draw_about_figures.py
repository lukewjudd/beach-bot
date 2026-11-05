"""Draw the figures for the site's About dialog, which walk through how swell and wind are worked out, from the
bot's own data. Colours are the site's CSS variables, so they follow light and dark mode when inlined.

  uv run --group build python scripts/draw_about_figures.py   # needs coastline.json from build_swell_windows.py

Writes web/src/about/*.svg:
  window.svg  North Bondi: rays cast from the beach, open ocean vs the headland's shadow
  window-wide.svg  the same, zoomed out to Maroubra: where the southern rays land
  wrap.svg    Collaroy: how far round Long Reef an 8 s and a 14 s swell reach
  share.svg   North Bondi: how much of a NE, E, SE and S swell gets in
  period.svg  Breaking height of a 1.5 m swell by period, at a beach and at a surf break
  wind.svg    Coogee: which winds are offshore, cross-shore and onshore

Coastline © OpenStreetMap contributors.
"""

import json
import math
from pathlib import Path

from shapely import LineString, MultiLineString, box, polygonize, unary_union

from beach_bot import swell
from beach_bot.beaches import EASTERN, NORTHERN
from beach_bot.geo import wind_kind

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "web" / "src" / "about"
BEACH = {b.name: b for r in (EASTERN, NORTHERN) for b in r.beaches}
WAYS = json.loads((HERE / "coastline.json").read_text())
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
        ways = [LineString([(lon, lat) for lat, lon in w]) for w in WAYS if len(w) > 1]
        coast = [c for c in (w.intersection(frame) for w in ways) if not c.is_empty]
        lines = MultiLineString([list(w.coords) for w in ways])
        out = []
        for f in polygonize(list(unary_union([frame.boundary, *coast]).geoms)).geoms:
            p = f.representative_point()
            hit = LineString([(p.x, p.y), (p.x + 1.0, p.y + 0.07)]).intersection(lines)
            if (0 if hit.is_empty else len(getattr(hit, "geoms", [hit]))) % 2:
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


def wind_fig():
    """Coogee: the wind compass on the map, coloured by how each direction crosses the beach."""
    m = Map(-33.9290, 151.2470, -33.9130, 151.2740)
    b = BEACH["Coogee"]
    lat, lon = -33.9208, 151.2582
    cx, cy, rr = 60, 56, 36
    body = [
        f'<rect width="{WIDTH}" height="{m.height}" fill="var(--hs-sea)"/>',
        *m.land(),
        *pin(m, lat, lon, "Coogee", anchor="end", dx=-10, dy=-8),
    ]
    for a in range(0, 360, 10):
        colour = {"offshore": "r-green", "cross": "r-amber", "onshore": "r-red"}[wind_kind(a + 5, b.facing)]
        body.append(f'<path d="{wedge(cx, cy, a, a + 10, rr)}" fill="var(--{colour})" opacity=".8"/>')
    body += [
        f'<circle cx="{cx}" cy="{cy}" r="{rr * 0.5:.0f}" fill="var(--surface)"/>',
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" class="hs-small">wind</text>',
        f'<text x="{cx}" y="{cy - rr - 5}" text-anchor="middle" class="hs-small">N</text>',
    ]
    for i, (colour, words) in enumerate((("r-green", "offshore"), ("r-amber", "cross-shore"), ("r-red", "onshore"))):
        y = cy + rr + 18 + i * 16
        body.append(f'<rect x="{cx - rr}" y="{y - 9}" width="10" height="10" rx="2" fill="var(--{colour})"/>')
        body.append(f'<text x="{cx - rr + 15}" y="{y}" class="hs-small">{words}</text>')
    fx, fy = m.px(lat, lon)
    tx, ty = toward(fx, fy, b.facing, 60)
    body += [
        arrow_defs("hs-wind", ("muted",)),
        f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="var(--muted)" stroke-width="2" '
        'marker-end="url(#hs-wind-muted)"/>',
        f'<text x="{tx:.1f}" y="{ty + 16:.1f}" text-anchor="middle" class="hs-small">faces {b.facing}°</text>',
        *m.scale_bar(500),
    ]
    svg(
        "wind",
        WIDTH,
        m.height,
        "Which winds are offshore at Coogee",
        f"Coogee faces {b.facing} degrees, a little south of east. A compass shows winds from the south-west round to "
        "the north-west are offshore, blowing from the land out over the water; winds from the north-east round to "
        "the south-east are onshore; the rest are cross-shore.",
        body,
    )


if __name__ == "__main__":
    window_fig()
    window_wide_fig()
    wrap_fig()
    share_fig()
    period_fig()
    wind_fig()
