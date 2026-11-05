"""How much of the offshore swell reaches each spot, by direction and period.

For every wave train (main swell, second swell, wind chop):

1. Refraction. As the swell reaches shallower water it bends toward the shore, and long-period swell bends
   further because it feels the bottom sooner. Oblique swell spreads its energy along more of the coast, which
   shrinks it (Snell's law against the general line of the Sydney coast, averaged over the swell's spread).
   Nearer in it bends to the beach itself: we turn it with Snell's law to 12 m, about where it rounds the
   headlands, against the way the beach faces.
2. The spot's swell window. swell_windows.json says which bearings are open ocean from each spot, measured
   from the OpenStreetMap coastline (scripts/build_swell_windows.py). The edge of a window isn't a hard cut:
   swell spreads into a headland's shadow, giving about 0.71 of the height right on the edge and fading behind
   it (Kraus 1984's fit to Goda's diffraction diagrams). Clean groundswell spreads less than messy wind chop.
3. The last bend into the beach: swell that still arrives at an angle to the beach loses some height.
4. Breaker height grows with period: T^0.4 at swimming beaches (Komar & Gaughan 1972), T^0.7 at surf breaks
   (fitted), scaled so a 9 s swell (10 s for surf) straight onto an open beach keeps its height, which is
   what the size bands were set against.
5. Local knowledge. Each spot's hand-set exposure (NE/E/SE/S, from beach-knowledge.md) is the prior: the result
   is the geometric mean of the geometry and the prior at 10 s, with the geometry's period response on top.
   Observations (and the NSW Nearshore Wave Tool, when we have it) will replace the prior.

Harbour beaches have no ocean coastline to measure, so they keep their hand-set exposure.
See reports/Sydney beach swell transformation.md for the sources.
"""

import json
import math
from functools import cache
from itertools import pairwise
from pathlib import Path

G = 9.81
COAST_NORMAL = 100  # the Sydney coast faces about ESE overall (eastern suburbs ~90, northern beaches ~110)
HEADLAND_DEPTH = 12  # m: where swell rounds the headlands
BREAK_DEPTH = 2  # m: roughly where it breaks on the beach
REF_PERIOD = 10  # s: the period the hand-set exposures were thought of at
PRIOR_WEIGHT = 0.5  # how much the hand-set exposure counts against the geometry (in log terms)

WINDOWS = json.loads((Path(__file__).parent / "swell_windows.json").read_text())


def wrap(deg):
    """Angle in -180..180."""
    return (deg + 180) % 360 - 180


@cache
def celerity_ratio(period, depth):
    """Wave speed at `depth` over its deep-water speed (linear dispersion)."""
    w = 2 * math.pi / period
    k = w * w / G  # deep-water wavenumber as a first guess
    for _ in range(40):
        k = w * w / (G * math.tanh(k * depth))
    return math.tanh(k * depth)


def refract(direction, normal, period, ratio_from, ratio_to):
    """Snell's law: (new direction, height factor from the energy spreading out). Swell running side-on to the
    shore still bends in a little; from further behind than that (more than 120 degrees off) it can't."""
    a0 = wrap(direction - normal)
    fade = 1.0 if abs(a0) < 89 else max(0.0, (120 - abs(a0)) / 31)
    a = math.copysign(min(abs(a0), 89), a0)
    a1 = math.degrees(math.asin(math.sin(math.radians(a)) * ratio_to / ratio_from))
    k = math.sqrt(math.cos(math.radians(a)) / math.cos(math.radians(a1)))
    return direction - (a - a1) * fade, k


def spreading(period):
    """Goda's directional spreading s_max: wind sea spreads wide, groundswell hardly at all."""
    return 10 if period < 8 else 25 if period < 12 else 60


def edge_factor(inside_deg, period):
    """Kraus (1984): height factor at `inside_deg` from the window edge (negative = into the shadow)."""
    s = spreading(period)
    w = -0.000130 * s * s + 0.270 * s + 5.31
    return math.sqrt(0.5 * (math.tanh(s * math.radians(inside_deg) / w) + 1))


@cache
def _edges(key):
    """Signed degrees from the window edge, for each whole bearing: positive inside the window."""
    spot = WINDOWS["spots"][key]
    step, cap = WINDOWS["step"], WINDOWS["cap_km"]
    open_ = [km >= cap for km in spot["km"]]
    n = len(open_)
    out = []
    for deg in range(360):
        i = round(deg / step) % n
        here = open_[i]
        d = next((j for j in range(1, n // 2 + 1) if open_[(i + j) % n] != here or open_[(i - j) % n] != here), n)
        out.append((d - 0.5) * step * (1 if here else -1))
    return out


def window_factor(key, direction, period):
    if not any(km >= WINDOWS["cap_km"] for km in WINDOWS["spots"][key]["km"]):
        return edge_factor(-40, period)  # no open ocean at all (Shelly Beach): only what leaks round
    return edge_factor(_edges(key)[round(direction) % 360], period)


def coast_factor(direction, facing, period, mid):
    """Oblique swell spreads along more of the coast and arrives smaller. The seabed contours swing from the
    general line of the coast out on the shelf to the beach's own line near shore; we take them halfway. Averaged
    over the swell's natural spread (about +-20 degrees), since a forecast direction is only the middle of it."""
    normal = facing + wrap(COAST_NORMAL - facing) / 2
    energy = 0.0
    for off in (-20, -10, 0, 10, 20):
        _, k = refract(direction + off, normal, period, 1.0, mid)
        energy += 0 if abs(wrap(direction + off - normal)) >= 89 else k * k
    return math.sqrt(energy / 5)


def geometry(key, facing, direction, period):
    """Share of one wave train's height that reaches the spot, before the breaker-height scaling."""
    period = min(max(period or REF_PERIOD, 3), 20)
    mid, shallow = celerity_ratio(period, HEADLAND_DEPTH), celerity_ratio(period, BREAK_DEPTH)
    k_coast = coast_factor(direction, facing, period, mid)
    # nearer in, the swell bends to the local seabed, which runs with the beach and its headlands
    bent, _ = refract(direction, facing, period, 1.0, mid)
    k_window = window_factor(key, bent, period)
    a = max(min(wrap(bent - facing), 80), -80)  # swell that got in round a headland turns to face the beach
    _, k_beach = refract(facing + a, facing, period, mid, shallow)
    return k_coast * k_window * k_beach


# ---------------------------------------------------------------- the hand-set prior
_SECTOR_DEG = (("NE", 45), ("E", 90), ("SE", 135), ("S", 180))


def prior(k, deg):
    """The hand-set exposure (beach-knowledge.md), blended by angle between NE/E/SE/S."""
    floor = min(0.1, *k.values())
    pts = [(0, floor), *((d, k[s]) for s, d in _SECTOR_DEG), (225, floor)]
    deg %= 360
    for (a0, v0), (a1, v1) in pairwise(pts):
        if a0 <= deg <= a1:
            return v0 + (v1 - v0) * (deg - a0) / (a1 - a0)
    return floor


@cache
def _correction(key, facing, k_items):
    """Local-knowledge multiplier at each anchor direction: (prior / geometry) ** PRIOR_WEIGHT at 10 s, kept
    within 0.5-2 so a near-zero geometry can't blow it up."""
    k = dict(k_items)
    return tuple(
        (d, min(max((max(k[s], 0.02) / max(geometry(key, facing, d, REF_PERIOD), 0.02)) ** PRIOR_WEIGHT, 0.5), 2))
        for s, d in _SECTOR_DEG
    )


def correction(key, facing, k, deg):
    pts = _correction(key, facing, tuple(sorted(k.items())))
    deg = min(max(deg % 360, 45), 180)
    for (a0, v0), (a1, v1) in pairwise(pts):
        if a0 <= deg <= a1:
            return v0 + (v1 - v0) * (deg - a0) / (a1 - a0)
    return pts[-1][1]


def key(spot):
    """swell_windows.json key: surf breaks share names with beaches."""
    return f"{spot.name} surf" if hasattr(spot, "max_hs") else spot.name


def exposure(spot, key, direction, period):
    """Share of a wave train's height that reaches the spot (0 to about 1)."""
    if key not in WINDOWS["spots"]:  # harbour beaches
        return prior(spot.k, direction)
    return min(1.0, geometry(key, spot.facing, direction, period) * correction(key, spot.facing, spot.k, direction))


def breaker(height, period, exponent=0.4, ref=9):
    """Longer-period swell breaks bigger: height x (period / ref) ** exponent. Komar & Gaughan's breaker formula
    gives 0.4 for swimming beaches. Surf breaks use 0.7, fitted to the old size-by-period table and webcam checks
    (0.86m at 7s was knee-high at Bondi). Komar & Gaughan's H^0.8 term is left out: it swelled small days, and
    the webcam didn't agree."""
    return max(height, 0) * (min(max(period or ref, 2), 20) / ref) ** exponent
