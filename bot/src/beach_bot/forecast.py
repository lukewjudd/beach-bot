"""Fetching forecasts (Open-Meteo, Beachwatch) and look-backs over the hourly series."""

import math
import re
import sys
from datetime import datetime
from statistics import mean, quantiles

import requests

from .config import DAYS_AHEAD, FORECAST_POINT, MARINE_POINT, RAIN_MODELS, TZ


def fetch_json(url, params):
    r = requests.get(url, params=params, timeout=180)  # multi-year backtest requests are slow
    r.raise_for_status()
    return r.json()


def fetch_weather(url, params):
    """There's no model grid cell on the coast itself: the nearest land cell is ~7km inland
    (too hot, too calm) and the coastal cell is over the water (too cool, too windy). The beach
    sits between them, so average the two. Wind direction is averaged as a vector."""
    land = fetch_json(url, {**params, "cell_selection": "land"})
    sea = fetch_json(url, {**params, "cell_selection": "sea"})
    out = {**land, "hourly": {"time": land["hourly"]["time"]}}
    for k, lv in land["hourly"].items():
        if k == "time":
            continue
        sv = sea["hourly"][k]
        if k == "weather_code":  # codes aren't quantities: keep the worse of the two (95+ = thunderstorm)
            out["hourly"][k] = [max(a or 0, b or 0) for a, b in zip(lv, sv, strict=True)]
            continue
        if k == "wind_direction_10m":
            ws_l, ws_s = land["hourly"]["wind_speed_10m"], sea["hourly"]["wind_speed_10m"]
            vals = []
            for a, b, sa, sb in zip(lv, sv, ws_l, ws_s, strict=True):
                if None in (a, b, sa, sb):
                    vals.append(a if a is not None else b)
                    continue
                x = sa * math.sin(math.radians(a)) + sb * math.sin(math.radians(b))
                y = sa * math.cos(math.radians(a)) + sb * math.cos(math.radians(b))
                vals.append(round(math.degrees(math.atan2(x, y)) % 360))
            out["hourly"][k] = vals
        else:
            out["hourly"][k] = [
                a if b is None else b if a is None else (a + b) / 2 for a, b in zip(lv, sv, strict=True)
            ]
    return out


def load_data():
    wx = fetch_weather(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": FORECAST_POINT[0],
            "longitude": FORECAST_POINT[1],
            "hourly": "temperature_2m,precipitation,precipitation_probability,wind_speed_10m,"
            "wind_direction_10m,wind_gusts_10m,cloud_cover,uv_index,weather_code,cape",
            "daily": "sunrise,sunset",
            "timezone": "Australia/Sydney",
            "past_days": 4,
            "forecast_days": DAYS_AHEAD + 1,
        },
    )
    sea = fetch_json(
        "https://marine-api.open-meteo.com/v1/marine",
        {
            "latitude": MARINE_POINT[0],
            "longitude": MARINE_POINT[1],
            "cell_selection": "sea",
            "hourly": "wave_height,swell_wave_height,swell_wave_direction,swell_wave_period,"
            "sea_surface_temperature,sea_level_height_msl",
            "timezone": "Australia/Sydney",
            "past_days": 4,
            "forecast_days": DAYS_AHEAD + 1,
        },
    )
    try:
        bw = fetch_json("https://api.beachwatch.nsw.gov.au/public/sites/geojson", {})
        beachwatch = fresh_forecasts(bw["features"], datetime.now(TZ).date())
    except Exception as e:  # undocumented API: fall back to rain rules
        print(f"Beachwatch unavailable ({e}); using rain thresholds", file=sys.stderr)
        beachwatch = {}

    hours = {}
    for i, t in enumerate(wx["hourly"]["time"]):
        hours[t] = {k: v[i] for k, v in wx["hourly"].items() if k != "time"}
    for i, t in enumerate(sea["hourly"]["time"]):
        if t in hours:
            hours[t].update({k: v[i] for k, v in sea["hourly"].items() if k != "time"})
    past_rain(hours, datetime.now(TZ))
    sun = {
        d: (datetime.fromisoformat(r), datetime.fromisoformat(s))
        for d, r, s in zip(wx["daily"]["time"], wx["daily"]["sunrise"], wx["daily"]["sunset"], strict=True)
    }
    return hours, sun, beachwatch


def fresh_forecasts(features, today):
    """Beachwatch pollution forecasts that were issued today. The feed updates around 6am, so an early run
    sees yesterday's call, which can say "Unlikely" from before a storm; that one is dropped (rain rules apply)."""
    out = {}
    for f in features:
        p = f["properties"]
        stamp = p.get("pollutionForecastTimeStamp")
        if not stamp:
            continue
        # .NET writes 7 decimal places, which fromisoformat won't take
        issued = datetime.fromisoformat(re.sub(r"\.\d+", "", stamp)).astimezone(TZ).date()
        if issued == today:
            out[p["siteName"]] = p.get("pollutionForecast")
    return out


def past_rain(hours, now):
    """Swap the past rain for a wetter read across several models. One model smears storms out: on the night
    of 3 Nov 2026 the default had 6mm where Sydney Airport measured 22mm, so the rain rules never kicked in.
    The 75th percentile of six models had 12.5mm there and barely moves on ordinary days. Leaning wet is
    the safe side for water quality, since it's the runoff that matters."""
    try:
        wx = fetch_weather(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": FORECAST_POINT[0],
                "longitude": FORECAST_POINT[1],
                "hourly": "precipitation",
                "models": ",".join(RAIN_MODELS),
                "timezone": "Australia/Sydney",
                "past_days": 4,
                "forecast_days": 1,
            },
        )
    except Exception as e:  # keep the single model's rain
        print(f"multi-model rain unavailable ({e}); using the default model", file=sys.stderr)
        return
    h = wx["hourly"]
    cutoff = now.strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(h["time"]):
        if t in hours and t <= cutoff:
            vals = [h[f"precipitation_{m}"][i] or 0 for m in RAIN_MODELS]
            hours[t]["precipitation"] = quantiles(vals, n=4, method="inclusive")[2]


class Context:
    """Rolling look-backs over the hourly series (rain history, persistent winds)."""

    def __init__(self, hours):
        self.times = sorted(hours)
        self.hours = hours
        self.index = {t: i for i, t in enumerate(self.times)}

    def _window(self, t, h_from, h_to):
        i = self.index[t]
        return [self.hours[self.times[j]] for j in range(max(0, i - h_to), max(0, i - h_from))]

    def rain(self, t, h_from, h_to):
        return sum((h.get("precipitation") or 0) for h in self._window(t, h_from, h_to))

    def mean_wind(self, t, hours_back):
        w = self._window(t, 0, hours_back)
        speeds = [h["wind_speed_10m"] for h in w]
        dirs = [h["wind_direction_10m"] for h in w]
        return (mean(speeds) if speeds else 0), dirs

    def ne_days(self, t):
        """Days out of the last 4 with mean NE wind >= 15 km/h (R-T1)."""
        count = 0
        for d in range(4):
            w = self._window(t, d * 24, (d + 1) * 24)
            if not w:
                continue
            ne = [h for h in w if 20 <= h["wind_direction_10m"] <= 70]
            if len(ne) >= len(w) / 2 and mean(h["wind_speed_10m"] for h in w) >= 15:
                count += 1
        return count

    def tide(self, t):
        """(hours to the nearest high tide, hours to the nearest low tide) from `sea_level_height_msl`.
        Positive = still to come. None when there's no tide data around this hour."""
        if not hasattr(self, "_tides"):
            levels = [self.hours[k].get("sea_level_height_msl") for k in self.times]
            self._tides = []
            for i in range(2, len(levels) - 2):
                win = levels[i - 2 : i + 3]
                if None in win:
                    continue
                if levels[i] == max(win) and levels[i] > levels[i + 1]:
                    self._tides.append((i, "high"))
                elif levels[i] == min(win) and levels[i] < levels[i + 1]:
                    self._tides.append((i, "low"))
        i = self.index[t]
        nearest = {}
        for j, kind in self._tides:
            if abs(j - i) <= 8 and (kind not in nearest or abs(j - i) < abs(nearest[kind])):
                nearest[kind] = j - i
        if "high" not in nearest or "low" not in nearest:
            return None
        return nearest["high"], nearest["low"]
