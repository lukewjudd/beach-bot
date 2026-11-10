"""Find each spearfishing spot's reef from the NSW seabed survey, and write src/beach_bot/spear_reefs.json.

For each spot, a grid of points around its shore entry (`SpearSpot.entry_at`) is sampled for depth and slope
from NSW Marine LiDAR 2018 (5 m grid), and sorted into reef or sand by the NSW Marine Habitats map. Then:
- the pin goes on the nearest reef to the entry at diving depth (3-15 m), so it marks where you'd actually dive,
  not a mark out to sea;
- around the pin (150 m): the depth range (10th to 90th percentile), the median reef depth (what surge is worked
  out at), how much of the bottom is reef, and how steep it is (share of cells over 10 degrees).

The LiDAR's only public service answers one point at a time, so the samples are cached in reef_samples.json
(gitignored) and only new spots are fetched. Run the swell windows build after this one: they're measured at the
pin.

  uv run --group build python scripts/build_spear_reefs.py

Bathymetry © State of New South Wales (DCCEEW), NSW Marine LiDAR Topo-Bathy 2018, CC BY 4.0. Habitats © State of
New South Wales (DPIRD), NSW Marine Habitats, CC BY 4.0.
"""

import json
import math
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from shapely import Point
from shapely.geometry import shape

from beach_bot.beaches import REGIONS

HERE = Path(__file__).parent
CACHE = HERE / "reef_samples.json"  # gitignored
OUT = HERE.parent / "src" / "beach_bot" / "spear_reefs.json"
LIDAR = (
    "https://mapprod2.environment.nsw.gov.au/arcgis/rest/services/Coastal_Marine/"
    "NSW_Marine_Lidar_Bathymetry_Data_2018/MapServer/identify"
)
HABITAT = "https://spatial.industry.nsw.gov.au/arcgis/rest/services/PUBLIC/NSW_Marine_Habitats/MapServer/0/query"
SEARCH_M = 400  # how far from the entry to look for reef
STEP_M = 30
AROUND_M = 150  # the spot's own patch, round the pin
DIVE = (3, 15)  # m: shore spearfishing depths
MOVE_M = 300  # the pin moves at most this far from the entry

M_LAT = 111_320


def get(url, params):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers={"User-Agent": "beach-bot"})
    for _ in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # the service drops the odd request under load
            err = e
    raise err


def sample(lat, lon):
    """(depth m, positive down, or None on land/no data; slope degrees) at one point."""
    d = 0.0005
    out = get(
        LIDAR,
        {
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "sr": 4326,
            "layers": "all:1,2",
            "tolerance": 0,
            "mapExtent": f"{lon - d},{lat - d},{lon + d},{lat + d}",
            "imageDisplay": "200,200,96",
            "returnGeometry": "false",
            "f": "json",
        },
    )
    vals = {r["layerId"]: r["attributes"].get("Pixel Value") for r in out.get("results", [])}

    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):  # "NoData"
            return None

    z, slope = num(vals.get(2)), num(vals.get(1))
    return (None if z is None or z >= 0 else round(-z, 2)), (None if slope is None else round(slope, 1))


def habitats(lat, lon, radius):
    dlat, dlon = radius / M_LAT, radius / (M_LAT * math.cos(math.radians(lat)))
    gj = get(
        HABITAT,
        {
            "geometry": f"{lon - dlon},{lat - dlat},{lon + dlon},{lat + dlat}",
            "geometryType": "esriGeometryEnvelope",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "Habitat",
            "outSR": 4326,
            "f": "geojson",
        },
    )
    return [(shape(f["geometry"]), (f["properties"].get("Habitat") or "").lower()) for f in gj["features"]]


def grid(lat, lon, radius, step):
    m_lon = M_LAT * math.cos(math.radians(lat))
    n = int(radius // step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            if math.hypot(i, j) * step <= radius:
                yield round(lat + i * step / M_LAT, 6), round(lon + j * step / m_lon, 6)


def metres(a, b):
    return math.hypot((a[0] - b[0]) * M_LAT, (a[1] - b[1]) * M_LAT * math.cos(math.radians(a[0])))


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, round(q * (len(xs) - 1))))]


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    out = {}
    for region in REGIONS:
        for sp in region.spear:
            lat0, lon0 = sp.entry_at
            key = f"{lat0},{lon0}"
            if key not in cache:
                pts = list(grid(lat0, lon0, SEARCH_M, STEP_M))
                with ThreadPoolExecutor(6) as ex:
                    vals = list(ex.map(lambda p: sample(*p), pts))
                hab = habitats(lat0, lon0, SEARCH_M + 50)
                kinds = []
                for (la, lo), _ in zip(pts, vals, strict=True):
                    pt = Point(lo, la)
                    kinds.append(next((k for g, k in hab if g.contains(pt)), None))
                cache[key] = [[la, lo, z, s, k] for (la, lo), (z, s), k in zip(pts, vals, kinds, strict=True)]
                CACHE.write_text(json.dumps(cache))
            cells = [c for c in cache[key] if c[2] is not None]
            # Within MOVE_M of the entry: further than that it's somewhere else (Camp Cove's nearest deep reef is
            # across at Green Point)
            close = [c for c in cells if metres((c[0], c[1]), (lat0, lon0)) <= MOVE_M]
            reef = [c for c in close if c[4] == "reef"]
            diveable = [c for c in reef if DIVE[0] <= c[2] <= DIVE[1]]
            pick = min(diveable or reef or close, key=lambda c: metres((c[0], c[1]), (lat0, lon0)), default=None)
            if not pick:
                print(f"{sp.name:<22} no LiDAR here: keeps its hand-set pin and depth")
                continue
            pin = (pick[0], pick[1])
            near = [c for c in cells if metres((c[0], c[1]), pin) <= AROUND_M]
            near_reef = [c for c in near if c[4] == "reef"] or near
            depths = [c[2] for c in near]
            mapped = [c for c in near if c[4]]
            slopes = [c[3] for c in near if c[3] is not None]
            rec = {
                "pin": [round(pin[0], 5), round(pin[1], 5)],
                "depth_m": round(min(max(pct([c[2] for c in near_reef], 0.5), 2), 20), 1),
                "range_m": [round(pct(depths, 0.1)), round(pct(depths, 0.9))],
                # None where the habitat map has nothing (inside the harbour): unknown, not sand
                "reef": round(sum(c[4] == "reef" for c in mapped) / len(mapped), 2) if mapped else None,
                "steep": round(sum(s > 10 for s in slopes) / len(slopes), 2) if slopes else None,
                "from_entry_m": round(metres(pin, (lat0, lon0))),
            }
            out[sp.name] = rec
            flag = "" if diveable else ("  (no reef at 3-15 m: nearest reef)" if reef else "  (no reef mapped)")
            print(
                f"{sp.name:<22} pin {rec['from_entry_m']:>4} m out, {rec['range_m'][0]}-{rec['range_m'][1]} m deep,"
                f" dive {rec['depth_m']} m, reef {rec['reef']}, steep {rec['steep']}{flag}"
            )
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
