"""Clovelly's seabed at 1 m, from the NSW Marine LiDAR 2018 point cloud, for the site's underwater map.

The point cloud (four 1 km .laz tiles, SydEstB2018-C3-AHD_33962xx and 34062xx) is ordered free from ELVIS
(elevation.fsdf.org.au): it isn't committed. Put the tiles in scripts/clovelly_lidar/ (gitignored), then:

  uv run --group build python scripts/build_clovelly_depth.py

Writes web/src/clovelly-depth.json: a grid of 1 m cells over the inlet, each with its height above AHD (the seabed,
or the rock where it's above water) and whether the survey called it reef or sand. Depth at any tide is then the
sea level (on AHD) less the cell's height, which the site works out as you drag the tide.

Classes kept (Report of Survey, table 3.10): 2 ground (rock above the water), 15 shoals, 16 seabed sand, 17
seabed reef. Each cell takes the median height of its points. Single empty cells between readings (the laser
missed under white water) are filled from their neighbours; bigger gaps stay empty.

Bathymetry © State of New South Wales (DCCEEW), NSW Marine LiDAR Topo-Bathy 2018, CC BY 4.0.
"""

import base64
import glob
import json
from pathlib import Path

import laspy
import numpy as np
from pyproj import Transformer

HERE = Path(__file__).parent
TILES = HERE / "clovelly_lidar"
OUT = HERE.parent.parent / "web" / "src" / "clovelly-depth.json"
# The inlet from the beach to just past its mouth (MGA zone 56, metres): picked off a 1 m render of the area
BOX = (339707, 6245847, 340087, 6246107)  # west, south, east, north
CELL = 1.0
KEEP = (2, 15, 16, 17)
NONE = -32768  # no reading


def main():
    w0, s0, e0, n0 = BOX
    W, H = int((e0 - w0) / CELL), int((n0 - s0) / CELL)
    xs, ys, zs, cs = [], [], [], []
    for f in sorted(glob.glob(str(TILES / "*.laz"))):
        las = laspy.read(f)
        x, y, z, c = (np.asarray(v) for v in (las.x, las.y, las.z, las.classification))
        m = (x >= w0) & (x < e0) & (y > s0) & (y <= n0) & np.isin(c, KEEP)
        xs.append(x[m]), ys.append(y[m]), zs.append(z[m]), cs.append(c[m])
    if not xs:
        raise SystemExit(f"no .laz tiles in {TILES}: order them from ELVIS (see the docstring)")
    x, y, z, c = (np.concatenate(v) for v in (xs, ys, zs, cs))
    col = np.clip(((x - w0) / CELL).astype(int), 0, W - 1)
    row = np.clip(((n0 - y) / CELL).astype(int), 0, H - 1)  # row 0 is the north edge
    idx = row * W + col

    # Median height per cell
    order = np.lexsort((z, idx))
    idx, z, c = idx[order], z[order], c[order]
    cells, start, count = np.unique(idx, return_index=True, return_counts=True)
    height = np.full(W * H, np.nan)
    height[cells] = z[start + count // 2]
    # Reef or sand: the majority of the cell's seabed points (rock above the water counts as reef)
    reef = np.zeros(W * H)
    sand = np.zeros(W * H)
    np.add.at(reef, idx, (c == 17) | (c == 2))
    np.add.at(sand, idx, (c == 16) | (c == 15))
    height = height.reshape(H, W)

    # Fill lone empty cells from their neighbours (median of those with a reading, needing at least 5 of 8)
    pad = np.pad(height, 1, constant_values=np.nan)
    neigh = np.stack(
        [pad[1 + dy : 1 + dy + H, 1 + dx : 1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
    )
    filled = np.isnan(height) & (np.sum(~np.isnan(neigh), axis=0) >= 5)
    height[filled] = np.nanmedian(neigh[:, filled], axis=0)

    kind = np.where(reef >= sand, 2, 1).reshape(H, W)  # 1 sand, 2 reef
    kind[np.isnan(height)] = 0
    cm = np.where(np.isnan(height), NONE, np.round(height * 100)).astype("<i2")

    to_ll = Transformer.from_crs(7856, 4326, always_xy=True)
    corners = [to_ll.transform(px, py) for px, py in ((w0, n0), (e0, n0), (e0, s0), (w0, s0))]  # NW NE SE SW
    data = {
        "source": "NSW Marine LiDAR Topo-Bathy 2018 (DCCEEW), CC BY 4.0; captured 17-19 Aug 2018",
        "crs": "EPSG:7856",
        "box": list(BOX),
        "cell": CELL,
        "w": W,
        "h": H,
        "corners": [[round(lat, 6), round(lon, 6)] for lon, lat in corners],
        # Height above AHD in cm, row by row from the north-west corner; -32768 = no reading
        "z": base64.b64encode(cm.tobytes()).decode(),
        # 0 no reading, 1 sand, 2 reef or rock
        "kind": base64.b64encode(kind.astype(np.uint8).tobytes()).decode(),
    }
    OUT.write_text(json.dumps(data, separators=(",", ":")) + "\n")
    have = int((cm != NONE).sum())
    lo, hi = np.nanmin(height), np.nanmax(height)
    print(f"{W}x{H} cells, {have} with a reading ({filled.sum()} filled), heights {lo:.1f} to {hi:.1f} m AHD")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
