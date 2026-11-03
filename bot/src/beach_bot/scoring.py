"""Hour-by-hour scores for swimming and surfing. Rule ids (R-W1 etc.) refer to beach-knowledge.md."""

from datetime import date

from .beaches import BEACH_FOR_SURF, Beach, Pool, SurfSpot
from .config import STORM_CAPE, STORM_CODE, STORM_RAIN_PROB
from .forecast import Context
from .geo import in_range, swell_sector, wind_kind


def storm(h: dict):
    """Thunderstorm risk this hour: get out of the water."""
    if (h.get("weather_code") or 0) >= STORM_CODE:
        return True
    return (h.get("cape") or 0) >= STORM_CAPE and (h.get("precipitation_probability") or 0) >= STORM_RAIN_PROB


def score_swim_hour(b: Beach, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """Returns (score, notes). score None = no-go."""
    if storm(h):
        return None, ["storms ⚡"]
    notes = []
    s = 45
    hs = h.get("wave_height") or 0
    sdir = h.get("swell_wave_direction") or 0
    period = h.get("swell_wave_period") or 0
    wind = h["wind_speed_10m"]
    wdir = h["wind_direction_10m"]
    hour = int(t[11:13])
    month = int(t[5:7])

    # Swell at the beach (§4.2, R-S7)
    sector = swell_sector(sdir)
    hb = hs * (b.k[sector] if sector else 0.1) * (1.3 if period >= 12 else 1)
    if b.name == "Clovelly" and hs > 2.5 and sector in ("E", "SE"):  # R-S3
        return None, ["too much swell in the inlet"]
    if b.name == "Gordons Bay" and hs > 1.2 and sector in ("NE", "E", "SE"):  # R-S5
        return None, ["waves in the bay"]
    if hb > b.swim_limit:
        return None, [f"~{hb:.1f}m at the beach"]
    if hb < 0.5:
        s += 15
    elif hb > 0.8:
        s -= 20
    if b.snorkel and hs < 1.0:
        s += 5
        notes.append("good snorkelling")

    # Wind (§4.1)
    kind = wind_kind(wdir, b.facing)
    if kind == "offshore" and wind <= 25:
        s += 10
    elif kind == "onshore" and wind >= 28:
        s -= 35
    elif kind == "onshore" and wind >= 15:
        s -= 15
    elif kind == "cross" and wind >= 20:
        s -= 8
    if wind >= 40 and b.hazard >= 6:
        s -= 25
    if wind < 8:
        s += 5
    elif wind >= 20:
        s -= 5  # blowy on the sand even where the water is sheltered
    gust = h.get("wind_gusts_10m") or 0
    s -= 15 if gust >= 45 else 8 if gust >= 35 else 0
    if 0 <= wdir <= 70 and b.name == "Bondi (north end)":  # R-W6
        s += 10
    if 160 <= wdir <= 200 and b.name == "Bondi (north end)":  # R-W7
        s -= 15
    if (h.get("wind_gusts_10m") or 0) >= 54 and 160 <= wdir <= 250:  # R-W5
        s -= 20 if b.name in ("Clovelly", "Bronte") else 40
        notes.append("southerly change")

    q = water_quality(b, t, ctx, beachwatch, today, notes)
    if q is None:
        return None, notes
    s += q
    if b.snorkel and ctx.rain(t, 0, 48) >= 10 and not beachwatch_says(b, t, beachwatch, today):  # R-R4
        s -= 10
    s += weather(h, t, ctx, notes)

    # Bluebottles (R-B1)
    if month in (11, 12, 1, 2, 3):
        w24, dirs = ctx.mean_wind(t, 24)
        ne = sum(20 <= d <= 70 for d in dirs) > len(dirs) / 2 if dirs else False
        south = sum(135 <= d <= 200 for d in dirs) > len(dirs) / 2 if dirs else False
        if (ne or south) and w24 >= 20:
            pen = {"Maroubra": 20, "Coogee": 10, "Bronte": 10, "Tamarama": 10, "Clovelly": 3 if ne else 8}.get(
                b.name, 5
            )
            s -= pen * (2 if w24 >= 30 else 1)
            if pen >= 8:
                notes.append("bluebottles possible")

    # Patrols (R-PT1): no flags early/late, so exposed beaches lose points
    last_patrol = 19 if month in (10, 11, 12, 1, 2, 3) else 17
    if b.hazard >= 6 and (hour < 7 or hour >= last_patrol):
        s -= 15

    return max(0, min(100, s)), notes


def beachwatch_says(b: Beach, t: str, beachwatch: dict, today: date):
    """Beachwatch's pollution forecast for this beach, which only covers today."""
    bw = beachwatch.get(b.beachwatch) if t[:10] == today.isoformat() else None
    return bw if bw in ("Unlikely", "Possible", "Likely") else None


def water_quality(b: Beach, t: str, ctx: Context, beachwatch: dict, today: date, notes: list):
    """Points for water quality (§4.4), or None when it's a no-go. Beachwatch first, then the rain rules."""
    bw = beachwatch_says(b, t, beachwatch, today)
    if bw == "Likely":
        notes.append("pollution likely (Beachwatch)")
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
    """Points for air temperature, rain, cloud and water temperature (§4.5)."""
    s = 0
    temp = h["temperature_2m"]
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
            notes.append("fresh water")
    if ctx.ne_days(t) >= 3:
        notes.append("cold upwelling likely")
    return s


def score_pool_hour(p: Pool, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """Returns (score, notes) for an ocean pool (beach-knowledge.md §2, rules R-P*). None = closed or unsafe.
    Pools stay flat when the beaches are rough; what matters is swell over the walls near high tide."""
    if storm(h):
        return None, ["storms ⚡"]
    notes = []
    s = 45
    hs = h.get("wave_height") or 0
    wind = h["wind_speed_10m"]
    hour = int(t[11:13])
    day = date.fromisoformat(t[:10])
    tide = ctx.tide(t)  # (hours to nearest high, hours to nearest low), or None without tide data

    # Cleaning days (R-P7) and opening hours (R-P8). Only Bronte's cleaning window is known (the ~4h before low
    # tide); for the others it's a few hours sometime that day, so it's a warning rather than a closure.
    if p.cleaning_day == day.weekday():
        if p.cleaning_before_low:
            if tide and 0 <= tide[1] <= 4:
                return None, ["closed for cleaning before low tide"]
        else:
            s -= 15
            notes.append(f"may be shut for cleaning ({day:%A}s)")
    if p.opens is not None:
        summer = (day.month, day.day) >= (10, 1) or (day.month, day.day) <= (4, 12)
        if hour < p.opens or hour >= (p.closes_summer if summer else p.closes_winter):
            return None, [f"closed until {p.opens}am" if hour < p.opens else "closed for the day"]

    # Swell over the walls (R-P3)
    near_high = tide is not None and abs(tide[0]) <= 2.5
    surge = hs * p.exposure
    if surge >= 2.5 and (near_high or tide is None):
        return None, ["waves over the walls"]
    if surge >= 3.2:
        return None, ["waves over the walls"]
    if surge >= 1.5 and near_high:
        s -= 20
        notes.append("washy at high tide")
    elif surge >= 2.0:
        s -= 10
    if surge < 1.0:
        s += 15
    elif surge < 1.5:
        s += 8

    # Tide preferences (R-P1, R-P3, R-P5)
    if tide is not None:
        to_high, to_low = abs(tide[0]), abs(tide[1])
        if p.best_tide == "low" and to_low <= 3:
            s += 10
            notes.append("low tide")
        elif p.best_tide == "mid" and min(to_high, to_low) >= 1.5 and hs < 1.0:
            s += 10
            notes.append("mid tide")
        elif p.best_tide == "mid_high" and to_high <= 3 and hs < 1.2:
            s += 5
            notes.append("wave pool fun")

    # Wind: pools sit low behind rocks, so direction matters less than strength
    if wind < 8:
        s += 5
    elif wind >= 28:
        s -= 15
    elif wind >= 20:
        s -= 5
    gust = h.get("wind_gusts_10m") or 0
    s -= 10 if gust >= 45 else 5 if gust >= 35 else 0

    q = water_quality(p.beach, t, ctx, beachwatch, today, notes)  # R-R5: pools share the beach's water
    if q is None:
        return None, notes
    s += q
    s += weather(h, t, ctx, notes)
    return max(0, min(100, s)), notes


def score_surf_hour(sp: SurfSpot, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """Returns (score, notes) for surfing. Every spot always gets a score: flat or blown out is just low.
    Size at the break sets the ceiling (no waves = 1/10 however nice the wind); the gap between waves
    and the wind decide how much of that ceiling you get. Storms and dirty water drop it to the floor."""
    if storm(h):
        return 10, ["storms ⚡"]
    notes = []
    q_water = water_quality(BEACH_FOR_SURF[sp.name], t, ctx, beachwatch, today, notes)
    if q_water is None:
        return 10, notes
    hs = h.get("wave_height") or 0
    sdir = h.get("swell_wave_direction") or 0
    period = h.get("swell_wave_period") or 0
    wind = h["wind_speed_10m"]
    sector = swell_sector(sdir)
    # Short-period swell arrives smaller and weaker than its offshore height suggests
    reach = 0.6 if period < 6 else 0.75 if period < 8 else 0.9 if period < 10 else 1.0 if period < 12 else 1.2
    size = hs * (sp.k[sector] if sector else 0.1) * reach

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
    q = 0 if period < 6 else 5 if period < 8 else 10 if period < 10 else 15 if period < 12 else 22
    q += 3 if period >= 14 else 0
    if period < 6:
        notes.append("short, choppy swell")
    kind = wind_kind(h["wind_direction_10m"], sp.facing)
    if wind < 8:
        q += 28
    elif kind == "offshore":
        q += 30 if wind <= 12 else 22 if wind <= 20 else 12
    elif kind == "cross":
        q += 15 if wind < 12 else 8 if wind < 20 else 3
        notes.append("cross-shore wind")
    else:
        q += 6 if wind < 12 else 1 if wind < 20 else 0
        notes.append("onshore wind")
    if (h.get("wind_gusts_10m") or 0) >= 40:
        q -= 5
    if sp.bonus_dirs and in_range(sdir, *sp.bonus_dirs):
        q += 5
    temp = h["temperature_2m"]
    q += 5 if temp >= 24 else 0 if temp >= 16 else -5
    if (h.get("precipitation_probability") or 0) >= 60:
        q -= 5

    s = 5 + size_pts + max(0, q) * factor + q_water
    return max(10, min(100, round(s))), notes  # 1/10 is the floor
