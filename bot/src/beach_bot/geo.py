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
