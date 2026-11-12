"""Hour-by-hour scores for shore spearfishing (research/spearfishing-conditions.md §5). Rule ids (R-SP1 etc.)
refer to the spearfishing section of beach-knowledge.md.

Six parts, each 0-1 and weighted (the site's bars are each part out of 10):
- Visibility, predicted in metres: the reef's usual clarity, less what the last few days' swell has stirred up
  (and hasn't settled), less a week of rain runoff, by season. Fitted to 612 dated Reef Life Survey readings.
- Surge: how far the water moves back and forth on the bottom where you're diving. Long-period swell surges much
  harder than its height suggests: 1m at 12s moves the water about 1m at 8m deep; 1.2m at 7s about 0.6m.
- Wind (surface chop, and drift with any current), tide, light and water temperature.

Visibility and surge set the ceiling, the way wave size does for surf: a glassy, sunny day in 2m of vis is still a
poor dive. Hard no-gos: storms, waves breaking over the entry, a lagoon flushing after heavy rain, and the harbour
after rain.
"""

import math
from datetime import datetime

from . import swell
from .config import TZ
from .geo import in_range, sun_elevation, wind_kind
from .scoring import storm, wave_trains
from .spearspots import SpearSpot

WEIGHTS = {"Visibility": 40, "Surge": 25, "Wind": 15, "Tide": 10, "Light": 5, "Water temp": 5}

# ---------------------------------------------------------------- visibility model (R-SP1)
# vis = base[water] x exp(-SWELL_A x swell memory) x exp(-RAIN_B x rain index) x season. Fitted by
# scripts/fit_spear_vis.py to the Reef Life Survey's dated visibility readings round Sydney: 331 site-days on 204
# dates, 2009-2025. On years it hadn't seen it ranks vis with Spearman 0.41, mostly from the open coast being
# clearer than the bays and the harbour. The surveys only run on calm days (4 of the 331 had much swell behind
# them), so they can't say what a big swell costs: SWELL_A comes from the pilot instead (open coast, median 10m
# after a small three days, 6m after 3m offshore: 2.4m at 10s on an open reef is a memory of ~58).
VIS_BASE = {"open": 8.1, "bay": 6.2, "harbour": 5.7}  # m, a calm, dry day
SWELL_A = 0.009  # per m2.s of swell memory (fitted: 0.005, from calm days only)
RAIN_B = 0.0044  # per mm of the rain index
OUTLET_RAIN = 1.75  # runoff hits spots by a lagoon, estuary or drain (and the bays and harbour) this much harder
WINTER, SUMMER = 1.15, 0.93  # Jun-Sep, Dec-Feb (fitted); clearest in winter, as the dive shops say
MEMORY_HALF_LIFE = 24  # h: stirred-up sand settles about this fast
API_DECAY = 0.6  # each day of rain counts this much less than the day after it

ENTRY_LIMIT = {"platform": 1.0, "cove": 1.5}  # m breaking at the entry: past this, getting in or out isn't safe
GROUNDSWELL = 12  # s: long-period swell surges harder at the entry; the limit drops a fifth

LAT, LON = -33.87, 151.25  # for the sun: a few km either way makes no difference


def spot_trains(h: dict, sp: SpearSpot):
    """[(height at the reef, period)] for each wave train: its offshore height times the share that reaches the
    reef from that direction at that period (swell.py), before any breaking."""
    key = swell.key(sp)
    return [(ht * swell.exposure(sp, key, d, per), per) for ht, d, per in wave_trains(h)]


def swell_here(h: dict, sp: SpearSpot):
    """Significant height at the reef, the trains added as energy."""
    return sum(ht * ht for ht, _ in spot_trains(h, sp)) ** 0.5


def entry_waves(h: dict, sp: SpearSpot):
    """Breaking height at the entry (the swimming-beach breaker formula)."""
    return sum(swell.breaker(ht, per) ** 2 for ht, per in spot_trains(h, sp)) ** 0.5


def wavenumber(period, depth):
    w = 2 * math.pi / max(period, 2)
    k = w * w / 9.81
    for _ in range(30):
        k = w * w / (9.81 * math.tanh(k * depth))
    return k


def surge(h: dict, sp: SpearSpot):
    """How far the water swings back and forth on the bottom at the dive depth (m, either way of centre): linear
    wave theory's orbital excursion, Hs / (2 sinh(kh)), each train added as energy. The depth is the survey's
    median reef depth round the pin (spear_reefs.json), else the hand-set one."""
    d = sp.dive_depth
    return sum((ht / (2 * math.sinh(wavenumber(per or 8, d) * d))) ** 2 for ht, per in spot_trains(h, sp)) ** 0.5


def energy(h: dict, sp: SpearSpot):
    """Swell energy at the reef that stirs the bottom: height squared times period, summed over the trains."""
    return sum(ht * ht * (per or 8) for ht, per in spot_trains(h, sp))


class SpearContext:
    """Look-backs for spearfishing on top of forecast.Context: the reef's swell over the last few days and a
    week of rain, cached per spot and hour (every hour of a session looks back over the same days)."""

    def __init__(self, ctx):
        self.ctx = ctx
        self._energy = {}

    def energy_at(self, sp, i):
        key = (id(sp), i)
        if key not in self._energy:
            h = self.ctx.hours[self.ctx.times[i]]
            self._energy[key] = energy(h, sp) if h.get("wave_height") is not None else None
        return self._energy[key]

    def memory(self, sp, t, hours=72):
        """Swell memory: the most swell energy over the last `hours`, each hour fading with a 24h half-life (the
        sand it stirred up settling out). Also the undecayed peak, for the murky-below-the-surface flag."""
        i = self.ctx.index[t]
        best = peak = 0.0
        for j in range(0, min(hours, i) + 1):
            e = self.energy_at(sp, i - j)
            if e is None:
                continue
            best = max(best, e * 0.5 ** (j / MEMORY_HALF_LIFE))
            peak = max(peak, e)
        return best, peak

    def rain_index(self, t):
        """A week's rain, each day back counting 0.6 of the one after it (mm)."""
        return sum(self.ctx.rain(t, d * 24, (d + 1) * 24) * API_DECAY**d for d in range(7))

    def sst_drop(self, t, hours=72):
        """How much the sea's cooled over the last 3 days (positive = colder now), or 0 without the data. The
        model's reading at both ends, so today's lifeguard reading isn't compared with the model's."""
        i = self.ctx.index[t]

        def sst(h):
            return h.get("sea_surface_temperature_model", h.get("sea_surface_temperature"))

        now = sst(self.ctx.hours[t])
        then = sst(self.ctx.hours[self.ctx.times[max(0, i - hours)]])
        return 0.0 if now is None or then is None else then - now


def predicted_vis(sp: SpearSpot, t: str, sctx: SpearContext):
    """Visibility in metres (R-SP1)."""
    mem, _ = sctx.memory(sp, t)
    api = sctx.rain_index(t)
    b = RAIN_B * (OUTLET_RAIN if sp.outlet or sp.water != "open" else 1)
    month = int(t[5:7])
    season = WINTER if month in (6, 7, 8, 9) else SUMMER if month in (12, 1, 2) else 1
    vis = VIS_BASE[sp.water] * math.exp(-SWELL_A * mem) * math.exp(-b * api) * season
    # A big flood keeps the bays, the harbour and anywhere by an outlet murky for a week or more (R-SP3)
    if (sp.outlet or sp.water != "open") and sctx.ctx.rain(t, 0, 168) >= 100:
        vis = min(vis, 3)
    return vis


def _ramp(x, pts):
    """Piecewise-linear through [(x, y), ...], flat past either end."""
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:], strict=False):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def vis_part(vis):
    """0-1 for the predicted vis. 5-10m is a normal Sydney day and 15m+ a great one (the dive shops), so it takes
    about 12m for an 8/10 bar, and a normal 8m day is a 6."""
    return _ramp(vis, [(3, 0), (5, 0.3), (8, 0.6), (12, 0.85), (15, 1)])


def surge_part(a):
    return _ramp(a, [(0.4, 1), (0.8, 0.6), (1.2, 0.3), (1.8, 0)])


def tide_state(ctx, t):
    """('rising' or 'falling', hours to the nearest high), or None without tide data."""
    tide = ctx.tide(t)
    if tide is None:
        return None
    to_high, to_low = tide
    nxt_high = to_high if to_high > 0 else math.inf
    nxt_low = to_low if to_low > 0 else math.inf
    return ("rising" if nxt_high < nxt_low else "falling"), abs(to_high)


def spear_parts(sp: SpearSpot, t: str, h: dict, sctx: SpearContext):
    """(parts as 0-1, notes, nogo) for one hour at a spearfishing spot."""
    ctx = sctx.ctx
    notes, nogo = [], None
    if storm(h):
        nogo = "storms ⚡"
    r72 = ctx.rain(t, 0, 72)

    # Getting in and out (R-SP2): the swell breaking over the entry
    hb = entry_waves(h, sp)
    period = max((per for ht, per in spot_trains(h, sp) if ht >= 0.2), default=0)
    limit = ENTRY_LIMIT[sp.entry] * (0.8 if period >= GROUNDSWELL else 1)
    if hb > limit:
        nogo = nogo or f"~{hb:.1f}m waves at the entry"
    # Runoff (R-SP3): a lagoon that's flushing after heavy rain, and the harbour after rain (as for swimming)
    if sp.outlet == "lagoon" and r72 >= 30:
        nogo = nogo or "lagoon flushing after rain"
    if sp.water == "harbour" and r72 >= 20:
        nogo = nogo or "harbour runoff after rain"

    vis = predicted_vis(sp, t, sctx)
    a = surge(h, sp)

    # Wind: chop on the surface, and drift on the float line
    wind, wdir = h["wind_speed_10m"], h["wind_direction_10m"]
    if sp.wind_shelter and in_range(wdir, *sp.wind_shelter):
        wind *= 0.5
        notes.append("sheltered from the wind")
    kind = wind_kind(wdir, sp.facing)
    w = 1 if wind < 10 else 0.7 if wind < 18 else 0.4 if wind < 25 else 0.1
    if kind == "onshore" and wind >= 10:
        w *= 0.7
        notes.append("onshore chop")
    elif kind == "offshore" and wind >= 30:
        w *= 0.6
        notes.append("strong offshore: watch the drift")
    if (h.get("wind_gusts_10m") or 0) >= 45:
        w *= 0.7
    current = h.get("ocean_current_velocity")  # km/h, the model's surface current offshore
    if current is not None and current >= 2:  # ~0.55 m/s: hard work on a float line
        w *= 0.7
        notes.append("current running")

    # Tide (R-SP4): bays and the harbour want the clean water coming in; rock exits want water over the rocks
    tide_pts = 0.7
    state = tide_state(ctx, t)
    if state:
        direction, to_high = state
        if sp.best_tide == "incoming":
            if direction == "rising" or to_high <= 1:
                tide_pts = 1
                notes.append("incoming tide")
            else:
                tide_pts = 0.2 if r72 >= 20 else 0.6
                notes.append("outgoing tide")
        elif sp.best_tide == "high":
            tide_pts = 1 if to_high <= 2 else 0.4 if to_high >= 4.5 else 0.7
            if to_high <= 2:
                notes.append("high tide")
        else:
            tide_pts = 1 if to_high <= 1.5 else 0.7

    # Light: spotting fish (and seeing the bottom) needs the sun up and not too much cloud
    when = datetime.fromisoformat(t).replace(tzinfo=TZ)
    sun = sun_elevation(LAT, LON, when.replace(minute=30))
    cloud = h.get("cloud_cover") or 0
    light = 0.3 if sun < 0 else 0.5 if sun < 10 or cloud >= 85 else 1 if sun >= 30 and cloud < 50 else 0.75

    sst = h.get("sea_surface_temperature")
    temp = 0.7 if sst is None else _ramp(sst, [(15, 0.2), (16, 0.4), (18, 0.65), (20, 0.85), (22, 1)])

    # Clear on top, murky by a few metres down (R-SP5): leftover stirred-up sand, cold water pushing in along the
    # bottom, or old runoff. Can't be seen from the surface, or by a satellite, so it's a flag rather than a score
    mem, _ = sctx.memory(sp, t)
    # The swell memory (fading as the sand settles) still well above what today's swell stirs up, after a solid swell
    if mem >= 2.5 * max(energy(h, sp), 1) and mem >= 8:  # 8: ~0.9m at 10s on the reef, a day on
        notes.append("may be murky down deep: sand still settling")
    elif ctx.ne_days(t) >= 2 and sctx.sst_drop(t) >= 1.5:
        notes.append("may be murky down deep: cold upwelling")
    elif sp.outlet and ctx.rain(t, 24, 144) >= 20:
        notes.append("may be murky down deep: old runoff")
    if ctx.rain(t, 0, 48) >= 20 and (sp.outlet in ("lagoon", "estuary") or sp.water != "open"):
        notes.append("bull sharks more likely after rain")  # NSW SharkSmart: murky water by river mouths

    parts = {
        "Visibility": vis_part(vis),
        "Surge": surge_part(a),
        "Wind": w,
        "Tide": tide_pts,
        "Light": light,
        "Water temp": temp,
    }
    return parts, notes, nogo


def score_spear_hour(sp: SpearSpot, t: str, h: dict, sctx: SpearContext):
    """Returns (score, notes). score None = no-go."""
    parts, notes, nogo = spear_parts(sp, t, h, sctx)
    if nogo:
        return None, [nogo]
    raw = sum(WEIGHTS[k] * v for k, v in parts.items())
    ceiling = min(1, 0.4 + 0.8 * min(parts["Visibility"], parts["Surge"]))  # 0.75 or better on both: no cap
    return max(0, min(100, round(raw * ceiling))), notes
