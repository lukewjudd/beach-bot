"""Compass and wind-direction helpers."""


def angle_diff(a, b):
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def in_range(deg, lo, hi):
    return lo <= deg <= hi if lo <= hi else deg >= lo or deg <= hi


def swell_sector(deg):
    if 22.5 <= deg < 67.5:
        return "NE"
    if 67.5 <= deg < 112.5:
        return "E"
    if 112.5 <= deg < 157.5:
        return "SE"
    if 157.5 <= deg < 202.5:
        return "S"
    return None


def compass(deg):
    pts = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return pts[round(deg / 22.5) % 16]


def wind_kind(wind_dir, facing):
    rel = angle_diff(wind_dir, facing)
    if rel <= 45:
        return "onshore"
    if rel >= 135:
        return "offshore"
    return "cross"


def wind_words(kmh):
    if kmh < 8:
        return "glassy"
    if kmh < 15:
        return "light"
    if kmh < 25:
        return "moderate"
    return "windy"


def sun_elevation(lat, lon, when):
    """The sun's height above the horizon in degrees at `when` (an aware datetime), from the NOAA approximation:
    good to a fraction of a degree, which is plenty for telling dawn light from midday."""
    import math
    from datetime import UTC

    t = when.astimezone(UTC)
    day = t.timetuple().tm_yday
    hour = t.hour + t.minute / 60
    g = 2 * math.pi / 365 * (day - 1 + (hour - 12) / 24)
    decl = (
        0.006918
        - 0.399912 * math.cos(g)
        + 0.070257 * math.sin(g)
        - 0.006758 * math.cos(2 * g)
        + 0.000907 * math.sin(2 * g)
        - 0.002697 * math.cos(3 * g)
        + 0.00148 * math.sin(3 * g)
    )
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(g)
        - 0.032077 * math.sin(g)
        - 0.014615 * math.cos(2 * g)
        - 0.040849 * math.sin(2 * g)
    )
    solar_min = hour * 60 + eqtime + 4 * lon
    ha = math.radians(solar_min / 4 - 180)
    la = math.radians(lat)
    cos_z = math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)
    return 90 - math.degrees(math.acos(max(-1, min(1, cos_z))))
