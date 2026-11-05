"""Draw the "how swell and wind work" example for the site's About dialog: North Bondi's coastline, its swell
window, what share of a few swells gets in (from swell.py), and which winds are offshore. Colours are the
site's CSS variables, so it follows light and dark mode when inlined.

  uv run --group build python scripts/draw_bondi_example.py   # needs coastline.json from build_swell_windows.py

Writes web/src/how-swell.svg. Coastline © OpenStreetMap contributors.
"""

import json
import math
from pathlib import Path

from shapely import LineString, MultiLineString, box, polygonize, unary_union

from beach_bot import swell
from beach_bot.beaches import EASTERN
from beach_bot.geo import wind_kind

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "web" / "src" / "how-swell.svg"
NAME = "Bondi (north end)"
S, W, N, E = -33.9010, 151.2690, -33.8810, 151.2980  # lat/lon box around Bondi
WIDTH = 400
LAT0 = (S + N) / 2
KX = math.cos(math.radians(LAT0))
SCALE = WIDTH / ((E - W) * KX)
HEIGHT = round((N - S) * SCALE)


def px(lat, lon):
    return ((lon - W) * KX * SCALE, (N - lat) * SCALE)


def land_paths():
    """Land polygons inside the box: the box cut up by the coastline, keeping the pieces on the land side."""
    ways = json.loads((HERE / "coastline.json").read_text())
    frame = box(W, S, E, N)
    coast = [LineString([(lon, lat) for lat, lon in w]).intersection(frame) for w in ways if len(w) > 1]
    coast = [c for c in coast if not c.is_empty]
    faces = polygonize(list(unary_union([frame.boundary, *coast]).geoms)).geoms
    lines = MultiLineString([list(LineString([(lon, lat) for lat, lon in w]).coords) for w in ways if len(w) > 1])
    out = []
    for f in faces:
        p = f.representative_point()
        ray = LineString([(p.x, p.y), (p.x + 1.0, p.y + 0.07)])  # out to sea, east-ish
        hit = ray.intersection(lines)
        crossings = 0 if hit.is_empty else len(getattr(hit, "geoms", [hit]))
        if crossings % 2:  # odd: on land
            pts = [px(lat, lon) for lon, lat in f.exterior.coords]
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return out


def wedge(cx, cy, a0, a1, r):
    pts = [(cx, cy)]
    for a in range(a0, a1 + 1, 2):
        pts.append((cx + r * math.sin(math.radians(a)), cy - r * math.cos(math.radians(a))))
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


def main():
    beach = next(b for b in EASTERN.beaches if b.name == NAME)
    spot = swell.WINDOWS["spots"][NAME]
    ox, oy = px(*spot["from"])
    open_ = [i * swell.WINDOWS["step"] for i, km in enumerate(spot["km"]) if km >= swell.WINDOWS["cap_km"]]
    a0, a1 = min(open_), max(open_)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-labelledby="hs-t hs-d" class="how-swell">',
        '<title id="hs-t">How swell and wind reach North Bondi</title>',
        f'<desc id="hs-d">Map of Bondi Beach. Ben Buckler, the headland at the north end, blocks swell from the '
        f"north-east and east, so only swell from {a0} to {a1} degrees (south-south-east round to south) has an open "
        f"run to the north end. Arrows show the share of a 10 second swell that reaches it from each direction. "
        f"A compass shows north-west winds blow offshore and south-east winds onshore.</desc>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="var(--hs-sea)"/>',
        f'<path d="{wedge(ox, oy, a0, a1, 600)}" fill="var(--accent)" opacity=".18"/>',
    ]
    parts += [f'<path d="{d}" fill="var(--hs-land)" stroke="var(--line)" stroke-width="1"/>' for d in land_paths()]
    for a in (a0, a1):
        x, y = ox + 600 * math.sin(math.radians(a)), oy - 600 * math.cos(math.radians(a))
        parts.append(
            f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--accent)" '
            'stroke-width="1.2" stroke-dasharray="4 3"/>'
        )

    # swells: an arrow in from each direction, labelled with the share that reaches the north end at 10 s
    for deg, label, r in ((45, "NE", 120), (90, "E", 118), (135, "SE", 135), (170, "S", 135)):
        share = swell.exposure(beach, NAME, deg, 10)
        sx, sy = ox + r * math.sin(math.radians(deg)), oy - r * math.cos(math.radians(deg))
        ex, ey = ox + 22 * math.sin(math.radians(deg)), oy - 22 * math.cos(math.radians(deg))
        colour = "var(--r-green)" if share >= 0.6 else "var(--r-amber)" if share >= 0.25 else "var(--r-red)"
        dash = "" if share >= 0.25 else ' stroke-dasharray="5 4"'
        parts.append(
            f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{colour}" stroke-width="3" '
            f'marker-end="url(#hs-arrow-{colour[6:-1]})"{dash}/>'
        )
        east = math.sin(math.radians(deg)) > 0.3  # labels on the east side start at the arrow's tail
        gap = 8 if east else 16
        tx, ty = ox + (r + gap) * math.sin(math.radians(deg)), oy - (r + gap) * math.cos(math.radians(deg)) + 5
        tx, ty = min(max(tx, 30), WIDTH - 60), min(max(ty, 14), HEIGHT - 8)
        parts.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{"start" if east else "middle"}" class="hs-label">'
            f'{label} <tspan class="hs-num">{round(share * 100)}%</tspan></text>'
        )
    parts.insert(
        5,
        "<defs>"
        + "".join(
            f'<marker id="hs-arrow-{c}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" '
            f'orient="auto-start-reverse"><path d="M0,0L10,5L0,10Z" fill="var(--{c})"/></marker>'
            for c in ("r-green", "r-amber", "r-red")
        )
        + "</defs>",
    )
    parts.append(
        f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="5" fill="var(--text)" stroke="var(--surface)" stroke-width="2"/>'
    )
    parts.append(f'<text x="{ox - 10:.1f}" y="{oy - 9:.1f}" text-anchor="end" class="hs-place">North Bondi</text>')
    bx, by = px(-33.8893, 151.2852)
    parts.append(f'<text x="{bx:.1f}" y="{by:.1f}" text-anchor="middle" class="hs-place hs-italic">Ben Buckler</text>')

    # wind compass, on the land in the top-left corner: green offshore, amber cross-shore, red onshore
    cx, cy, rr = 52, 58, 34
    for a in range(0, 360, 10):
        kind = wind_kind(a + 5, beach.facing)
        colour = {"offshore": "r-green", "cross": "r-amber", "onshore": "r-red"}[kind]
        parts.append(f'<path d="{wedge(cx, cy, a, a + 10, rr)}" fill="var(--{colour})" opacity=".75"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{rr * 0.5:.0f}" fill="var(--surface)"/>')
    parts.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" class="hs-small">wind</text>')
    parts.append(f'<text x="{cx}" y="{cy - rr - 5}" text-anchor="middle" class="hs-small">N</text>')
    for i, (colour, words) in enumerate((("r-green", "offshore"), ("r-amber", "cross-shore"), ("r-red", "onshore"))):
        y = cy + rr + 16 + i * 16
        parts.append(f'<rect x="{cx - rr}" y="{y - 9}" width="10" height="10" rx="2" fill="var(--{colour})"/>')
        parts.append(f'<text x="{cx - rr + 15}" y="{y}" class="hs-small">{words}</text>')
    parts.append("</svg>")
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
