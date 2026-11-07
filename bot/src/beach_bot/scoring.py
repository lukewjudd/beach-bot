"""Hour-by-hour scores for swimming and surfing. Rule ids (R-W1 etc.) refer to beach-knowledge.md."""

from datetime import date

from . import swell
from .beaches import Beach, Pool, SurfSpot
from .config import STORM_CAPE, STORM_CODE, STORM_RAIN_PROB
from .forecast import Context
from .geo import in_range, swell_sector, wind_kind

# ---------------------------------------------------------------- swell reaching a spot
# The sea is split into wave trains (the main swell, a second swell from another direction, and the local wind
# chop). Each goes through swell.py on its own (how much reaches the spot from that direction at that period,
# then how big it breaks), and the trains add as energy. A spot open from every direction gets the whole sea,
# and one that only faces east shrugs off a south swell even when an east wind chop is running alongside it.


def wave_trains(h: dict):
    """[(height, direction, period)] for the main swell, the second swell and the wind chop. Falls back to the
    combined height on the main swell's direction when the forecast doesn't split them."""
    trains = [
        (h.get(f"{p}_height"), h.get(f"{p}_direction"), h.get(f"{p}_period") or 0)
        for p in ("swell_wave", "secondary_swell_wave", "wind_wave")
    ]
    trains = [(ht, d, per) for ht, d, per in trains if ht and d is not None]
    if not trains or h.get("secondary_swell_wave_height") is None and h.get("wind_wave_height") is None:
        return [(h.get("wave_height") or 0, h.get("swell_wave_direction") or 0, h.get("swell_wave_period") or 0)]
    return trains


def at_beach(h: dict, spot):
    """Breaking wave height at a swimming beach."""
    key = swell.key(spot)
    return sum(swell.breaker(ht * swell.exposure(spot, key, d, per), per) ** 2 for ht, d, per in wave_trains(h)) ** 0.5


def at_break(h: dict, spot):
    """Wave size at a surf break: the whole sea on the main swell's direction and period. Unlike the beaches it
    isn't split into trains: the size bands were set against the combined height, and splitting them out
    dropped classic days (1.8m SSE at 11s, offshore wind) out of the sweet spot."""
    per = h.get("swell_wave_period") or 0
    k = swell.exposure(spot, swell.key(spot), h.get("swell_wave_direction") or 0, per)
    return swell.breaker((h.get("wave_height") or 0) * k, per, exponent=0.7, ref=10)


def storm(h: dict):
    """Thunderstorm risk this hour: get out of the water."""
    if (h.get("weather_code") or 0) >= STORM_CODE:
        return True
    return (h.get("cape") or 0) >= STORM_CAPE and (h.get("precipitation_probability") or 0) >= STORM_RAIN_PROB


SWIM_BASE = 45  # where every swim hour starts; the parts' best add up to 100 (15 + 15 + 20 + 5 extras)

# Wind points at a swimming beach, by strength then direction (§4.1): (under km/h, offshore, cross, onshore).
# Under 8 km/h it's glassy whichever way it blows. Past that, offshore keeps the water smooth while cross-shore
# and onshore chop it up, more the stronger it gets; and past 20 km/h it's blowy on the sand whatever the water.
WIND_POINTS = [
    (8, 15, 15, 15),
    (15, 12, 8, 3),
    (20, 10, 0, -15),
    (25, 5, -13, -20),
    (28, -5, -13, -20),
    (float("inf"), -5, -13, -40),
]


def wind_points(wind, kind):
    row = next(r for r in WIND_POINTS if wind < r[0])
    return row[{"offshore": 1, "cross": 2, "onshore": 3}[kind]]


def swim_parts(b: Beach, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """The points for each part of a swim hour: (parts, notes, nogo). parts holds Calm water, Wind, Weather and
    Water quality (what the site's bars show) and Extras (snorkelling, bluebottles); a part that rules the hour
    out is None, and nogo says why."""
    notes, nogo = [], None
    if storm(h):
        nogo = "storms ⚡"
    hs = h.get("wave_height") or 0
    sdir = h.get("swell_wave_direction") or 0
    wind = h["wind_speed_10m"]
    wdir = h["wind_direction_10m"]
    month = int(t[5:7])

    # Swell at the beach (§4.2, R-S7)
    sector = swell_sector(sdir)
    hb = at_beach(h, b)
    calm = 15 if hb < 0.5 else -20 if hb > 0.8 else 0
    if b.name == "Clovelly" and hs > 2.5 and sector in ("E", "SE"):  # R-S3
        calm, nogo = None, nogo or "too much swell in the inlet"
    elif b.name == "Gordons Bay" and hs > 1.2 and sector in ("NE", "E", "SE"):  # R-S5
        calm, nogo = None, nogo or "waves in the bay"
    elif hb > b.swim_limit:
        calm, nogo = None, nogo or f"~{hb:.1f}m at the beach"

    # Wind (§4.1)
    kind = wind_kind(wdir, b.facing)
    w = wind_points(wind, kind)
    if wind >= 40 and b.hazard >= 6:
        w -= 25
    gust = h.get("wind_gusts_10m") or 0
    w -= 15 if gust >= 45 else 8 if gust >= 35 else 0
    if 0 <= wdir <= 70 and b.name == "Bondi (north end)":  # R-W6
        w += 10
    if 160 <= wdir <= 200 and b.name == "Bondi (north end)":  # R-W7
        w -= 15
    if gust >= 54 and 160 <= wdir <= 250:  # R-W5
        w -= 20 if b.name in ("Clovelly", "Bronte") else 40
        notes.append("southerly change")

    q_notes = []
    q = water_quality(b, t, ctx, beachwatch, today, q_notes)
    if q is None:
        nogo = nogo or q_notes[-1]
    notes += q_notes

    # Snorkelling (R-S4, R-R4): small swell, and clear water. Rain and runoff cloud it for a couple of days.
    extras = 0
    if b.snorkel:
        murky = ctx.rain(t, 0, 48) >= 10 or beachwatch_says(b, t, beachwatch, today) == "Possible"
        if murky:
            notes.append("murky for snorkelling")
            if not beachwatch_says(b, t, beachwatch, today):
                extras -= 10
        elif hs < 1.0 and not (kind == "onshore" and wind >= 15):
            extras += 5
            notes.append("good snorkelling")
    wx = None if storm(h) else weather(h, t, ctx, notes)

    # Bluebottles (R-B1)
    if month in (11, 12, 1, 2, 3) and not b.harbour:  # they don't make it into the harbour
        w24, dirs = ctx.mean_wind(t, 24)
        ne = sum(20 <= d <= 70 for d in dirs) > len(dirs) / 2 if dirs else False
        south = sum(135 <= d <= 200 for d in dirs) > len(dirs) / 2 if dirs else False
        if (ne or south) and w24 >= 20:
            pen = {"Maroubra": 20, "Coogee": 10, "Bronte": 10, "Tamarama": 10, "Clovelly": 3 if ne else 8}.get(
                b.name, 5
            )
            extras -= pen * (2 if w24 >= 30 else 1)
            if pen >= 8:
                notes.append("bluebottles possible")

    parts = {"Calm water": calm, "Wind": w, "Weather": wx, "Water quality": q, "Extras": extras}
    return parts, notes, nogo


def score_swim_hour(b: Beach, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """Returns (score, notes). score None = no-go."""
    parts, notes, nogo = swim_parts(b, t, h, ctx, beachwatch, today)
    if nogo:
        return None, [nogo]  # just the reason it's a no-go
    return max(0, min(100, SWIM_BASE + sum(parts.values()))), notes


def beachwatch_says(b: Beach, t: str, beachwatch: dict, today: date):
    """Beachwatch's pollution forecast for this beach, which only covers today."""
    bw = beachwatch.get(b.beachwatch) if t[:10] == today.isoformat() else None
    return bw if bw in ("Unlikely", "Possible", "Likely") else None


def water_quality(b: Beach, t: str, ctx: Context, beachwatch: dict, today: date, notes: list):
    """Points for water quality (§4.4), or None when it's a no-go. Beachwatch first, then the rain rules."""
    bw = beachwatch_says(b, t, beachwatch, today)
    if bw == "Likely":
        notes.append("pollution likely")  # Beachwatch is credited on the site's data sources page
        return None
    if bw == "Possible":
        notes.append("pollution possible")
        return -30
    if bw == "Unlikely":
        return 0
    s = 0
    r24, r48, r72 = ctx.rain(t, 0, 24), ctx.rain(t, 24, 48), ctx.rain(t, 0, 72)
    if r24 >= b.rain_often:
        notes.append(f"{r24:.0f}mm rain in last 24h")
        return None
    if r24 >= b.rain_occ:
        s -= 25
        notes.append("recent rain")
    if r48 >= b.rain_often:
        s -= 15
    if b.poor_grade and r72 >= 5:
        notes.append("rain in last 3 days")
        return None
    if b.poor_grade and r72 >= 1:
        s -= 20
    return s


def weather(h: dict, t: str, ctx: Context, notes: list):
    """Points for air temperature (where the day's heading: Context.warmth), rain, cloud and water temperature
    (§4.5)."""
    s = 0
    temp = ctx.warmth(t)
    s += 15 if temp >= 26 else 10 if temp >= 23 else 5 if temp >= 21 else 0 if temp >= 19 else -8 if temp >= 17 else -15
    if (h.get("precipitation") or 0) >= 0.5 or (h.get("precipitation_probability") or 0) >= 60:
        s -= 20
        notes.append("rain about")
    elif (h.get("precipitation_probability") or 0) >= 40:
        s -= 8
    if (h.get("cloud_cover") or 0) >= 85:
        s -= 5
    # Warm water earns a bonus; cool water is only a note, never a penalty
    sst = h.get("sea_surface_temperature")
    if sst is not None:
        if sst > 22:
            s += 5
        elif sst < 20:
            notes.append("cold water")
    if ctx.ne_days(t) >= 3:
        notes.append("cold upwelling likely")
    return s


POOL_BASE = 45


def pool_parts(p: Pool, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """The points for each part of an hour at an ocean pool (beach-knowledge.md §2, rules R-P*): (parts, notes,
    nogo). parts holds Calm in the pool, Tide, Wind, Weather and Water quality (the site's bars) and Extras (a
    cleaning day). Pools stay flat when the beaches are rough; what matters is swell over the walls near high tide."""
    notes, nogo = [], None
    if storm(h):
        nogo = "storms ⚡"
    hs = h.get("wave_height") or 0
    wind = h["wind_speed_10m"]
    hour = int(t[11:13])
    day = date.fromisoformat(t[:10])
    tide = ctx.tide(t)  # (hours to nearest high, hours to nearest low), or None without tide data

    # Cleaning days (R-P7) and opening hours (R-P8). Only Bronte's cleaning window is known (the ~4h before low
    # tide); for the others it's a few hours sometime that day, so it's a warning rather than a closure.
    extras = 0
    if p.cleaning_day == day.weekday():
        if p.cleaning_before_low:
            if tide and 0 <= tide[1] <= 4:
                nogo = nogo or "closed for cleaning before low tide"
        else:
            extras -= 15
            notes.append(f"may be shut for cleaning ({day:%A}s)")
    if p.opens is not None:
        summer = (day.month, day.day) >= (10, 1) or (day.month, day.day) <= (4, 12)
        if hour < p.opens or hour >= (p.closes_summer if summer else p.closes_winter):
            nogo = nogo or (f"closed until {p.opens}am" if hour < p.opens else "closed for the day")

    # Swell over the walls (R-P3)
    near_high = tide is not None and abs(tide[0]) <= 2.5
    surge = hs * p.exposure
    calm = 0
    if surge >= 3.2 or (surge >= 2.5 and (near_high or tide is None)):
        calm, nogo = None, nogo or "waves over the walls"
    elif surge >= 1.5 and near_high:
        calm = -20
        notes.append("washy at high tide")
    elif surge >= 2.0:
        calm = -10
    elif surge < 1.0:
        calm = 15
    elif surge < 1.5:
        calm = 8

    # Tide preferences (R-P1, R-P3, R-P5)
    tide_pts = 0
    if tide is not None:
        to_high, to_low = abs(tide[0]), abs(tide[1])
        if p.best_tide == "low" and to_low <= 3:
            tide_pts = 10
            notes.append("low tide")
        elif p.best_tide == "mid" and min(to_high, to_low) >= 1.5 and hs < 1.0:
            tide_pts = 10
            notes.append("mid tide")
        elif p.best_tide == "mid_high" and to_high <= 3 and hs < 1.2:
            tide_pts = 5
            notes.append("wave pool fun")

    # Wind: the walls keep the chop out, so direction counts for about half what it does at the beach,
    # but you're still on the deck in the same breeze
    kind = wind_kind(h["wind_direction_10m"], p.facing)
    w = 0
    if kind == "offshore" and wind <= 25:
        w += 5
    elif kind == "onshore" and wind >= 28:
        w -= 15
    elif kind == "onshore" and wind >= 15:
        w -= 8
    if wind < 8:
        w += 5
    elif wind >= 28:
        w -= 15
    elif wind >= 20:
        w -= 5
    gust = h.get("wind_gusts_10m") or 0
    w -= 10 if gust >= 45 else 5 if gust >= 35 else 0

    q_notes = []
    q = water_quality(p.beach, t, ctx, beachwatch, today, q_notes)  # R-R5: pools share the beach's water
    if q is None:
        nogo = nogo or q_notes[-1]
    notes += q_notes
    wx = None if storm(h) else weather(h, t, ctx, notes)
    parts = {"Calm in the pool": calm, "Tide": tide_pts, "Wind": w, "Weather": wx, "Water quality": q, "Extras": extras}
    return parts, notes, nogo


def score_pool_hour(p: Pool, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """Returns (score, notes) for an ocean pool. None = closed or unsafe."""
    parts, notes, nogo = pool_parts(p, t, h, ctx, beachwatch, today)
    if nogo:
        return None, [nogo]
    return max(0, min(100, POOL_BASE + sum(parts.values()))), notes


def surf_parts(sp: SurfSpot, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """The points for each part of a surf hour: (parts, factor, notes, nogo). parts holds Wave size, Wave quality
    (the gap between waves), Wind, Weather and Water quality. Size sets the ceiling: the quality points (period,
    wind and weather) only count for `factor` of themselves, so no waves is 1/10 however nice the wind."""
    notes = []
    nogo = "storms ⚡" if storm(h) else None
    q_notes = []
    q_water = water_quality(sp.beach, t, ctx, beachwatch, today, q_notes)
    if q_water is None:
        nogo = nogo or q_notes[-1]
    notes += q_notes
    sdir = h.get("swell_wave_direction") or 0
    period = h.get("swell_wave_period") or 0
    wind = h["wind_speed_10m"]
    size = at_break(h, sp)

    # Size at the break (§1a): ~1-1.8m is the sweet spot for these beachies and reefs
    if size < 0.3:
        size_pts, factor = 0, 0.1
        notes.append("flat")
    elif size < 0.5:
        size_pts, factor = 8, 0.35
        notes.append("tiny")
    elif size < 0.8:
        size_pts, factor = 18, 0.6
        notes.append("small")
    elif size < 1.0:
        size_pts, factor = 18, 0.8
    elif size < 1.4:
        size_pts, factor = 25, 0.95
    elif size <= 2.0:
        size_pts, factor = 35, 1.0
    elif size <= sp.max_hs:
        size_pts, factor = 30, 0.95
    else:
        size_pts, factor = 8, 0.4
        notes.append("closing out")

    # Quality: gap between waves (short wind chop is mushy, groundswell is clean) and wind
    per = 0 if period < 6 else 5 if period < 8 else 10 if period < 10 else 15 if period < 12 else 22
    per += 3 if period >= 14 else 0
    if sp.bonus_dirs and in_range(sdir, *sp.bonus_dirs):
        per += 5
    if period < 6:
        notes.append("short, choppy swell")
    kind = wind_kind(h["wind_direction_10m"], sp.facing)
    if wind < 8:
        w = 28
    elif kind == "offshore":
        w = 30 if wind <= 12 else 22 if wind <= 20 else 12
    elif kind == "cross":
        w = 15 if wind < 12 else 8 if wind < 20 else 3
        notes.append("cross-shore wind")
    else:
        w = 6 if wind < 12 else 1 if wind < 20 else 0
        notes.append("onshore wind")
    if (h.get("wind_gusts_10m") or 0) >= 40:
        w -= 5
    temp = ctx.warmth(t)
    wx = 5 if temp >= 24 else 0 if temp >= 16 else -5
    if (h.get("precipitation_probability") or 0) >= 60:
        wx -= 5
    parts = {"Wave size": size_pts, "Wave quality": per, "Wind": w, "Weather": wx, "Water quality": q_water}
    return parts, factor, notes, nogo


def score_surf_hour(sp: SurfSpot, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """Returns (score, notes) for surfing. Every spot always gets a score: flat or blown out is just low, and
    storms and dirty water drop it to the floor."""
    parts, factor, notes, nogo = surf_parts(sp, t, h, ctx, beachwatch, today)
    if nogo:
        return 10, [nogo]
    quality = parts["Wave quality"] + parts["Wind"] + parts["Weather"]
    s = 5 + parts["Wave size"] + max(0, quality) * factor + parts["Water quality"]
    return max(10, min(100, round(s))), notes  # 1/10 is the floor
