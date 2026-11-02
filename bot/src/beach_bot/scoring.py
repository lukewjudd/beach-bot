"""Hour-by-hour scores for swimming and surfing. Rule ids (R-W1 etc.) refer to beach-knowledge.md."""

from datetime import date

from .beaches import Beach, SurfSpot
from .forecast import Context
from .geo import in_range, swell_sector, wind_kind


def score_swim_hour(b: Beach, t: str, h: dict, ctx: Context, beachwatch: dict, today: date):
    """Returns (score, notes). score None = no-go."""
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
    if b.name == "Clovelly" and hs > 2.5 and sector in ("E", "SE"):   # R-S3
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
        s -= 5   # blowy on the sand even where the water is sheltered
    gust = h.get("wind_gusts_10m") or 0
    s -= 15 if gust >= 45 else 8 if gust >= 35 else 0
    if 0 <= wdir <= 70 and b.name == "Bondi (north end)":                # R-W6
        s += 10
    if 160 <= wdir <= 200 and b.name == "Bondi (north end)":             # R-W7
        s -= 15
    if (h.get("wind_gusts_10m") or 0) >= 54 and 160 <= wdir <= 250:      # R-W5
        s -= 20 if b.name in ("Clovelly", "Bronte") else 40
        notes.append("southerly change")

    # Water quality (§4.4). Beachwatch only forecasts today.
    bw = beachwatch.get(b.beachwatch) if t[:10] == today.isoformat() else None
    if bw == "Likely":
        return None, ["pollution likely (Beachwatch)"]
    if bw == "Possible":
        s -= 30
        notes.append("pollution possible")
    if bw not in ("Unlikely", "Possible"):
        r24, r48, r72 = ctx.rain(t, 0, 24), ctx.rain(t, 24, 48), ctx.rain(t, 0, 72)
        if r24 >= b.rain_often:
            return None, [f"{r24:.0f}mm rain in last 24h"]
        if r24 >= b.rain_occ:
            s -= 25
            notes.append("recent rain")
        if r48 >= b.rain_often:
            s -= 15
        if b.poor_grade and r72 >= 5:
            return None, ["rain in last 3 days"]
        if b.poor_grade and r72 >= 1:
            s -= 20
        if b.snorkel and ctx.rain(t, 0, 48) >= 10:                        # R-R4
            s -= 10

    # Weather during the session
    temp = h["temperature_2m"]
    s += 15 if temp >= 26 else 10 if temp >= 23 else 5 if temp >= 21 else 0 if temp >= 19 else -8 if temp >= 17 else -15
    if (h.get("precipitation") or 0) >= 0.5 or (h.get("precipitation_probability") or 0) >= 60:
        s -= 20
        notes.append("rain about")
    elif (h.get("precipitation_probability") or 0) >= 40:
        s -= 8
    if (h.get("cloud_cover") or 0) >= 85:
        s -= 5

    # Water temperature and upwelling (§4.5)
    sst = h.get("sea_surface_temperature")
    # Warm water earns a bonus; cool water is only a note, never a penalty
    if sst is not None:
        if sst > 22:
            s += 5
        elif sst < 20:
            notes.append("fresh water")
    if ctx.ne_days(t) >= 3:
        notes.append("cold upwelling likely")

    # Bluebottles (R-B1)
    if month in (11, 12, 1, 2, 3):
        w24, dirs = ctx.mean_wind(t, 24)
        ne = sum(20 <= d <= 70 for d in dirs) > len(dirs) / 2 if dirs else False
        south = sum(135 <= d <= 200 for d in dirs) > len(dirs) / 2 if dirs else False
        if (ne or south) and w24 >= 20:
            pen = {"Maroubra": 20, "Coogee": 10, "Bronte": 10, "Tamarama": 10,
                   "Clovelly": 3 if ne else 8}.get(b.name, 5)
            s -= pen * (2 if w24 >= 30 else 1)
            if pen >= 8:
                notes.append("bluebottles possible")

    # Patrols (R-PT1): no flags early/late, so exposed beaches lose points
    last_patrol = 19 if month in (10, 11, 12, 1, 2, 3) else 17
    if b.hazard >= 6 and (hour < 7 or hour >= last_patrol):
        s -= 15

    return max(0, min(100, s)), notes


def score_surf_hour(sp: SurfSpot, h: dict):
    hs = h.get("wave_height") or 0
    sdir = h.get("swell_wave_direction") or 0
    period = h.get("swell_wave_period") or 0
    wind = h["wind_speed_10m"]
    if not (in_range(sdir, *sp.swell_dirs) and sp.min_hs <= hs <= sp.max_hs):
        return None
    kind = wind_kind(h["wind_direction_10m"], sp.facing)
    if kind == "onshore" and wind >= 12:
        return None
    if period < 6:
        return None   # short-period wind chop, not worth paddling out
    s = 40
    s += 15 if 1.0 <= hs <= 1.8 else 8 if 0.8 <= hs <= 2.2 else 0
    s += 15 if period >= 12 else 10 if period >= 10 else 0 if period >= 8 else -15
    if kind == "offshore" and wind <= 20 or wind < 8:
        s += 15
    elif kind == "cross" and wind >= 18:
        s -= 15
    gust = h.get("wind_gusts_10m") or 0
    s -= 10 if gust >= 40 else 0
    if sp.bonus_dirs and in_range(sdir, *sp.bonus_dirs):
        s += 5
    temp = h["temperature_2m"]
    s += 5 if temp >= 24 else 0 if temp >= 18 else -5 if temp >= 14 else -10
    if (h.get("precipitation_probability") or 0) >= 60:
        s -= 10
    return max(0, min(100, s))
