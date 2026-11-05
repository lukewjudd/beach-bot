"""Measure each spot's swell window from the OpenStreetMap coastline.

From a point just seaward of each beach (or at each surf break) a ray is cast every 2 degrees, and we record how
far it travels before it hits land, up to 30 km. Bearings that reach the cap are open ocean; ones stopped by a
nearby headland are the shadow. The result goes to src/beach_bot/swell_windows.json, which the bot reads.

  uv run --group build python scripts/build_swell_windows.py           # fetch the coastline and build
  uv run --group build python scripts/build_swell_windows.py --cached  # reuse coastline.json from the last run

Coastline data © OpenStreetMap contributors (ODbL).
"""

import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from shapely import LineString, STRtree

from beach_bot.beaches import REGIONS, SurfSpot

HERE = Path(__file__).parent
CACHE = HERE / "coastline.json"  # gitignored
OUT = HERE.parent / "src" / "beach_bot" / "swell_windows.json"
BBOX = (-34.35, 150.95, -33.30, 151.60)  # south, west, north, east: Royal NP to the Central Coast
STEP = 2  # degrees between rays
CAP_KM = 30
SEAWARD_M = 40  # beach rays start this far past the shoreline, walking out from the sand the way the beach faces
BREAK_M = 100  # surf breaks are measured from this far off the shore

LAT0 = -33.85
M_PER_DEG_LAT = 111_320
M_PER_DEG_LON = 111_320 * math.cos(math.radians(LAT0))


def xy(lat, lon):
    return (lon * M_PER_DEG_LON, lat * M_PER_DEG_LAT)


def fetch_coastline():
    s, w, n, e = BBOX
    q = f'[out:json][timeout:180];way["natural"="coastline"]({s},{w},{n},{e});out geom;'
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter",
        data=urllib.parse.urlencode({"data": q}).encode(),
        headers={"User-Agent": "beach-bot swell windows"},
    )
    with urllib.request.urlopen(req, timeout=200) as r:
        ways = [[(p["lat"], p["lon"]) for p in el["geometry"]] for el in json.load(r)["elements"]]
    CACHE.write_text(json.dumps(ways))
    return ways


def distances(tree, lines, lat, lon):
    """Distance to land (km, capped) on each bearing from the point."""
    x0, y0 = xy(lat, lon)
    out = []
    for b in range(0, 360, STEP):
        dx, dy = math.sin(math.radians(b)), math.cos(math.radians(b))
        ray = LineString([(x0 + dx * 5, y0 + dy * 5), (x0 + dx * CAP_KM * 1000, y0 + dy * CAP_KM * 1000)])
        best = CAP_KM
        for i in tree.query(ray, predicate="intersects"):
            hit = ray.intersection(lines[i])
            for p in getattr(hit, "geoms", [hit]):
                for cx, cy in p.coords:
                    best = min(best, math.hypot(cx - x0, cy - y0) / 1000)
        out.append(round(best, 2))
    return out


def in_water(tree, lines, x, y):
    """An even number of coastline crossings on the way out to the open sea = on the water. Checked on two
    slanted bearings, so a stretch of coast running dead east-west can't fool the count."""
    for b in (77, 113):
        dx, dy = math.sin(math.radians(b)), math.cos(math.radians(b))
        ray = LineString([(x, y), (x + dx * 60_000, y + dy * 60_000)])
        n = 0
        for i in tree.query(ray, predicate="intersects"):
            hit = ray.intersection(lines[i])
            n += len(getattr(hit, "geoms", [hit]))
        if n % 2:
            return False
    return True


def origin(tree, lines, region, spot):
    """Beach pins are on the sand: walk out the way the beach faces (or nearly) until we're on the water, then a
    little further. Surf pins sit out to sea (some ~800 m, so they don't cover the swim markers), but the waves
    break near the sand: walk back in toward the shore and measure from BREAK_M off it."""
    lat, lon = region.pin(spot)
    x0, y0 = xy(lat, lon)
    if isinstance(spot, SurfSpot):
        dx, dy = -math.sin(math.radians(spot.facing)), -math.cos(math.radians(spot.facing))
        d = 0
        while d < 2000 and in_water(tree, lines, x0 + dx * (d + 10), y0 + dy * (d + 10)):
            d += 10
        d = max(0, d - BREAK_M)
        return lat + d * dy / M_PER_DEG_LAT, lon + d * dx / M_PER_DEG_LON
    for turn in (0, 15, -15, 30, -30, 45, -45):
        dx, dy = math.sin(math.radians(spot.facing + turn)), math.cos(math.radians(spot.facing + turn))
        for d in range(0, 1500, 5):
            if all(in_water(tree, lines, x0 + dx * e, y0 + dy * e) for e in range(d, d + SEAWARD_M + 1, 5)):
                d += SEAWARD_M
                return lat + d * dy / M_PER_DEG_LAT, lon + d * dx / M_PER_DEG_LON
    raise ValueError(f"no water off {spot.name}")


def main():
    ways = json.loads(CACHE.read_text()) if "--cached" in sys.argv else fetch_coastline()
    lines = [LineString([xy(a, b) for a, b in w]) for w in ways if len(w) > 1]
    tree = STRtree(lines)
    print(f"{len(lines)} coastline ways")
    result = {"step": STEP, "cap_km": CAP_KM, "spots": {}}
    for region in REGIONS:
        for spot in [*region.beaches, *region.surf]:
            if getattr(spot, "harbour", False):  # no ocean coastline inside the harbour: hand-set k stays
                continue
            key = f"{spot.name} surf" if isinstance(spot, SurfSpot) else spot.name
            lat, lon = origin(tree, lines, region, spot)
            d = distances(tree, lines, lat, lon)
            result["spots"][key] = {"from": [round(lat, 5), round(lon, 5)], "km": d}
            open_ = [b * STEP for b, km in enumerate(d) if km >= CAP_KM]
            print(f"{key:<30} open {len(open_) * STEP:>3} deg  {arcs(open_)}")
    OUT.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(f"wrote {OUT}")


def arcs(bearings):
    """'40-190, 300-310' from a list of open bearings."""
    if not bearings:
        return "closed"
    runs, start, prev = [], bearings[0], bearings[0]
    for b in bearings[1:]:
        if b != prev + STEP:
            runs.append((start, prev))
            start = b
        prev = b
    runs.append((start, prev))
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == 360 - STEP:
        runs = [(runs[-1][0], runs[0][1]), *runs[1:-1]]
    return ", ".join(f"{a}-{b}" for a, b in runs)


if __name__ == "__main__":
    main()
