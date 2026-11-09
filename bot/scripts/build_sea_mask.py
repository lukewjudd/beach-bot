"""The open ocean on each region's map, for the site's swell layer: the map's box cut up by the OpenStreetMap
coastline, keeping the piece out to sea. Lines across the heads of Sydney Harbour, Botany Bay and Broken Bay cut
those off, so the swell only shows on the open coast.

  uv run --group build python scripts/build_sea_mask.py   # needs coastline.json from build_swell_windows.py

Writes web/src/sea.json: {region id: [[lat, lon], ...]}, simplified to about 40 m. Coastline © OpenStreetMap
contributors.
"""

import json
from pathlib import Path

from shapely import LineString, Point, box, polygonize, unary_union

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "web" / "src" / "sea.json"

# Each region's map bounds (web/src/regions.ts) and a point well out to sea
REGIONS = {
    "eastern": ((-34.05, 151.05, -33.8, 151.4), (-33.93, 151.35)),
    "northern": ((-33.87, 151.05, -33.53, 151.45), (-33.70, 151.42)),
}
# Across the heads, (lat, lon) to (lat, lon), drawn a little past the rocks so the cut is clean
HEADS = [
    ((-33.8185, 151.2995), (-33.8375, 151.2855)),  # Sydney Harbour: North Head to South Head
    ((-33.9990, 151.2500), (-34.0110, 151.2290)),  # Botany Bay: Cape Banks to Cape Solander
    ((-33.5860, 151.3330), (-33.5320, 151.3590)),  # Broken Bay: Barrenjoey to Box Head
]


def main():
    ways = [
        LineString([(lon, lat) for lat, lon in w])
        for w in json.loads((HERE / "coastline.json").read_text())
        if len(w) > 1
    ]
    cuts = [LineString([(a[1], a[0]), (b[1], b[0])]) for a, b in HEADS]
    out = {}
    for rid, ((s, w, n, e), (olat, olon)) in REGIONS.items():
        frame = box(w, s, e, n)
        lines = [g for g in (x.intersection(frame) for x in [*ways, *cuts]) if not g.is_empty]
        pieces = polygonize(list(unary_union([frame.boundary, *lines]).geoms)).geoms
        sea = next(p for p in pieces if p.contains(Point(olon, olat)))
        sea = sea.simplify(0.0004)
        out[rid] = [[round(lat, 5), round(lon, 5)] for lon, lat in sea.exterior.coords]
        print(f"{rid}: {len(out[rid])} points, {sea.area / frame.area:.0%} of the map is open ocean")
    OUT.write_text(json.dumps(out, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
