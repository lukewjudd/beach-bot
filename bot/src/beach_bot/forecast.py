"""Fetching forecasts (Open-Meteo, Beachwatch), what is measured on the day (Randwick's lifeguards, Northern
Beaches Council's closures, the wave buoys), and look-backs over the hourly series."""

import html
import io
import json
import math
import re
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from statistics import mean, quantiles

import requests

from .beaches import EASTERN
from .config import (
    BOM_OBS_URL,
    BUOY_LAYER,
    BUOY_WFS,
    COOL_CHANGE,
    COUNCIL_STATUS_PAGES,
    FORECAST_DAYS,
    LIFEGUARD_FEED,
    RAIN_MODELS,
    TZ,
    WARMTH_AHEAD_TO,
    WARMTH_DISCOUNT,
    WARMTH_LAND_MIN_SEA,
)


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
    if "temperature_2m" in land["hourly"]:
        # The land cell on its own is the day's headline high (it sits by Observatory Hill in the east): what
        # Context.warmth reads for where the day's heading. On sea-breeze days the blend runs 4-5° under it.
        out["hourly"]["temperature_2m_land"] = land["hourly"]["temperature_2m"]
    return out


def load_data(region=EASTERN):
    wx = fetch_weather(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": region.forecast_point[0],
            "longitude": region.forecast_point[1],
            "hourly": "temperature_2m,precipitation,precipitation_probability,wind_speed_10m,"
            "wind_direction_10m,wind_gusts_10m,cloud_cover,uv_index,weather_code,cape",
            "daily": "sunrise,sunset",
            "timezone": "Australia/Sydney",
            "past_days": 7,  # a week back: spearfishing reads a week of rain and three days of swell
            "forecast_days": FORECAST_DAYS,
        },
    )
    sea = fetch_json(
        "https://marine-api.open-meteo.com/v1/marine",
        {
            "latitude": region.marine_point[0],
            "longitude": region.marine_point[1],
            "cell_selection": "sea",
            "hourly": "wave_height,swell_wave_height,swell_wave_direction,swell_wave_period,"
            "secondary_swell_wave_height,secondary_swell_wave_direction,secondary_swell_wave_period,"
            "wind_wave_height,wind_wave_direction,wind_wave_period,wave_period,"
            "sea_surface_temperature,sea_level_height_msl,ocean_current_velocity",
            "timezone": "Australia/Sydney",
            "past_days": 7,  # a week back: spearfishing reads a week of rain and three days of swell
            "forecast_days": FORECAST_DAYS,
        },
    )
    try:
        bw = fetch_json("https://api.beachwatch.nsw.gov.au/public/sites/geojson", {})
        beachwatch = fresh_forecasts(bw["features"], datetime.now(TZ).date())
    except Exception as e:  # undocumented API: fall back to rain rules
        print(f"Beachwatch unavailable ({e}); using rain thresholds", file=sys.stderr)
        beachwatch = {}
    beachwatch = Reports(
        beachwatch,
        lifeguard_reports(datetime.now(TZ).date()),
        council_statuses() if region.council_status else {},
        buoy_readings(region.buoys, datetime.now(TZ)),
    )

    hours = {}
    for i, t in enumerate(wx["hourly"]["time"]):
        hours[t] = {k: v[i] for k, v in wx["hourly"].items() if k != "time"}
    for i, t in enumerate(sea["hourly"]["time"]):
        if t in hours:
            hours[t].update({k: v[i] for k, v in sea["hourly"].items() if k != "time"})
    past_rain(hours, datetime.now(TZ), region.forecast_point)
    gauge_rain(hours, region.rain_gauges)
    measured_water(hours, region, beachwatch.lifeguards, datetime.now(TZ).date())
    sun = {
        d: (datetime.fromisoformat(r), datetime.fromisoformat(s))
        for d, r, s in zip(wx["daily"]["time"], wx["daily"]["sunrise"], wx["daily"]["sunset"], strict=True)
    }
    return hours, sun, beachwatch


def measured_water(hours, region, lifeguards, today):
    """Today's water temperature from the region's lifeguard reports (R-LG2), in place of the marine model's.
    The model's is a cell offshore and misses the cold a southerly or upwelling pushes onto the beaches (Coogee
    17C on 12 Nov 2026 with the model at 20C). Readings vary beach to beach (17 to 20 that morning, 2km apart),
    so the middle one stands for the region. Only today's hours: the reports say nothing about tomorrow. The
    model's own reading is kept as sea_surface_temperature_model, for the trend and to compare against."""
    temps = sorted(
        rep["water_c"]
        for b in region.beaches
        if b.lifeguard and (rep := lifeguards.get(b.lifeguard)) and 10 <= (rep.get("water_c") or 0) <= 30
    )
    if not temps:
        return None
    n = len(temps)
    water = temps[n // 2] if n % 2 else (temps[n // 2 - 1] + temps[n // 2]) / 2
    for t, h in hours.items():
        h["sea_surface_temperature_model"] = h.get("sea_surface_temperature")
        if t[:10] == today.isoformat():
            h["sea_surface_temperature"] = water
            h["water_measured"] = True
    return water


class Reports(dict):
    """Today's reports and measurements. The dict itself is Beachwatch's pollution forecasts by site name (as it
    always was, so a plain dict still works); .lifeguards is the lifeguards' morning reports by their feed title
    (Beach.lifeguard); .council is the council's status for each beach and rockpool (council_statuses); .buoys is
    the last day of wave buoy readings (buoy_readings)."""

    def __init__(self, beachwatch=None, lifeguards=None, council=None, buoys=None):
        super().__init__(beachwatch or {})
        self.lifeguards = lifeguards or {}
        self.council = council or {"beaches": {}, "pools": {}}
        self.buoys = buoys or []


BROWSER_UA = "Mozilla/5.0 (compatible; beach-bot)"


def council_name(name):
    """Northern Beaches Council's names against ours: "Manly Beach" and "Manly", "Fairy Bower Rockpool" and "Fairy
    Bower", "Paradise Beach" and "Paradise Beach Baths"."""
    n = re.sub(r"\s+", " ", name.strip().lower())
    return re.sub(r" (beach|rockpool|rock pool|baths)$", "", n)


def council_statuses():
    """Northern Beaches Council's status for each beach and rockpool right now (R-LG3), as
    {"beaches": {name: {"status", "message"}}, "pools": {...}} with council_name() keys, or empty if the site's
    down. The listings are 20 to a page."""
    out = {"beaches": {}, "pools": {}}
    for url, kind in zip(COUNCIL_STATUS_PAGES, ("beaches", "pools"), strict=True):
        for page in range(5):
            try:
                r = requests.get(url, params={"page": page}, headers={"User-Agent": BROWSER_UA}, timeout=30)
                r.raise_for_status()
            except Exception as e:
                print(f"council statuses unavailable ({e})", file=sys.stderr)
                break
            rows = parse_council(r.text)
            if not rows or rows.keys() <= out[kind].keys():
                break
            out[kind].update(rows)
    return out


def parse_council(text):
    """{council_name: {"status": "open" | "check at location" | "closed" | ..., "message": str | None}}"""
    rows = {}
    for art in re.findall(r"<article\b.*?</article>", text, re.S):
        name = re.search(r'node__title">.*?<span>([^<]+)</span>', art, re.S)
        status = re.search(r"status-wrapper status-([\w-]+)", art)
        if not name or not status:
            continue
        msg = re.search(r"ras-message'>.*?Message</span>\s*<span>(.*?)</span>", art, re.S)
        rows[council_name(html.unescape(name[1]))] = {
            "status": status[1].replace("-", " "),
            "message": html.unescape(re.sub(r"<[^>]+>", "", msg[1])).strip() if msg else None,
        }
    return rows


def buoy_readings(sites, now):
    """The last day's readings from the region's wave buoys (R-LG4), oldest first: [{"buoy", "time" (local, to
    the minute), "hs" (m), "period" (peak, s), "deg" (peak direction, from)}], or [] if the feed's down. MHL's
    buoys give Hs from zero crossings (WHTH), the IMOS ones spectral Hs (WSSH): near enough the same thing."""
    if not sites:
        return []
    feats = _buoy_features(now.strftime("%Y-%m-%dT%H"))
    return parse_buoys(feats, sites) if feats is not None else []


_BUOYS = {}


def _buoy_features(hour):
    """Every Sydney buoy's last day, fetched once per run (both regions read it) and tried three times: the server
    is slow at times."""
    if hour in _BUOYS:
        return _BUOYS[hour]
    since = (datetime.fromisoformat(hour + ":00").replace(tzinfo=TZ) - timedelta(hours=24)).astimezone(UTC)
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": BUOY_LAYER,
        "outputFormat": "application/json",
        "propertyName": "site_name,TIME,WSSH,WHTH,WPPE,WPDI",
        # Sydney's stretch of coast, by place: a filter on the station names trips the server's firewall
        "CQL_FILTER": f"TIME > '{since:%Y-%m-%dT%H:%M:%SZ}' AND "
        "LATITUDE > -34.2 AND LATITUDE < -33.4 AND LONGITUDE > 151",
    }
    err = None
    for _ in range(3):
        try:
            # It turns away python-requests' own user agent
            r = requests.get(BUOY_WFS, params=params, headers={"User-Agent": "beach-bot"}, timeout=90)
            r.raise_for_status()
            _BUOYS[hour] = r.json()["features"]
            return _BUOYS[hour]
        except Exception as e:
            err = e
    print(f"wave buoys unavailable ({err})", file=sys.stderr)
    return None


def parse_buoys(features, sites):
    out = []
    for f in features:
        p = f["properties"]
        if p.get("site_name") not in sites:
            continue
        hs = p.get("WSSH") if p.get("WSSH") is not None else p.get("WHTH")
        if hs is None or not p.get("TIME"):
            continue
        t = datetime.fromisoformat(p["TIME"].replace("Z", "+00:00")).astimezone(TZ)
        out.append(
            {
                "buoy": p["site_name"],
                "time": t.isoformat(timespec="minutes"),
                "hs": round(hs, 2),
                "period": round(p["WPPE"], 1) if p.get("WPPE") is not None else None,
                "deg": round(p["WPDI"]) if p.get("WPDI") is not None else None,
            }
        )
    return sorted(out, key=lambda r: r["time"])


def lifeguard_reports(today):
    """Randwick Council's lifeguard reports (Clovelly, Coogee, Maroubra, Little Bay), or {} if the feed's down.
    It's the council's RSS feed for exactly this; the reports page itself sits behind a bot check, so only the
    feed is read."""
    try:
        r = requests.get(LIFEGUARD_FEED, timeout=30)
        r.raise_for_status()
        return parse_lifeguards(r.text, today)
    except Exception as e:
        print(f"lifeguard reports unavailable ({e})", file=sys.stderr)
        return {}


def parse_lifeguards(xml_text, today):
    """Today's report per beach, by feed title. A beach's item stays in the feed until its next report, so one
    from an earlier day is dropped rather than read as today's. Each report's description is labelled fields
    (<p><strong>Rips:</strong> Dangerous</p>); the free-text Description is kept as it's written."""
    out = {}
    for item in ET.fromstring(xml_text).iter("item"):
        title = (item.findtext("title") or "").strip()
        try:
            when = parsedate_to_datetime(item.findtext("pubDate") or "").astimezone(TZ)
        except (TypeError, ValueError):
            continue
        if not title or when.date() != today:
            continue
        fields = {
            k.strip().lower(): html.unescape(re.sub(r"<[^>]+>", "", v)).strip()
            for k, v in re.findall(
                r"<strong>\s*([^<:]+):\s*</strong>(.*?)</p>", item.findtext("description") or "", re.S
            )
        }
        out[title] = {
            "time": when.isoformat(timespec="minutes"),
            "summary": fields.get("summary"),
            "status": fields.get("beach status"),
            "closed": (fields.get("beach status") or "").lower().startswith("closed"),
            "water_c": _number(fields.get("water temp")),
            "waves": fields.get("wave height"),
            "waves_m": _number(fields.get("wave height"), largest=True),
            "rips": fields.get("rips"),
            "bluebottles": fields.get("bluebottles"),
            "stingers": _stingers(fields.get("bluebottles")),
            "description": fields.get("description"),
        }
    return out


def _number(text, largest=False):
    """18 from "18 C"; 2 from "+2m"; with largest, 1 from "0.5-1m"."""
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text or "")]
    return (max(nums) if largest else nums[0]) if nums else None


def _stingers(text):
    """ "none" when the lifeguards say there aren't any, "seen" when they've seen some, None when it's not said
    or it's worded in a way that isn't clear either way."""
    t = (text or "").lower()
    if not t:
        return None
    if re.search(r"\b(none|nil|no)\b", t):
        return "none"
    if re.search(r"sighted|present|some|few|many|lots|numerous|heavy|light|moderate|scattered|\d", t):
        return "seen"
    return None


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


def past_rain(hours, now, point):
    """Fallback for when the BOM gauges are down: a wetter read of past rain across several models. One model
    smears storms out: on the night of 3 Nov 2026 the default had 6mm where Sydney Airport measured 22mm, so the
    rain rules never kicked in. The 75th percentile of six models had 12.5mm there and barely moves on ordinary
    days. Leaning wet is the safe side for water quality, since it's the runoff that matters."""
    try:
        wx = fetch_weather(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": point[0],
                "longitude": point[1],
                "hourly": "precipitation",
                "models": ",".join(RAIN_MODELS),
                "timezone": "Australia/Sydney",
                "past_days": 7,  # a week back: spearfishing reads a week of rain and three days of swell
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


def gauge_rain(hours, stations):
    """Rain that's actually fallen, from BOM's rain gauges, over the top of the modelled rain. Storms are patchy
    (on 3 Nov 2026 Observatory Hill had 50mm and the airport 22mm), so it takes the wetter station: for water
    quality it's the runoff that matters. Comes from BOM's public FTP, which is how BOM shares data for automated
    use: one bundle with the last ~72h of half-hourly readings for every NSW station."""
    try:
        with urllib.request.urlopen(BOM_OBS_URL, timeout=60) as r:
            bundle = tarfile.open(fileobj=io.BytesIO(r.read()), mode="r:gz")
        gauges = []
        for station in stations:
            f = bundle.extractfile(f"IDN60910.{station}.json")
            gauges.append(hourly_rain(json.load(f)["observations"]["data"]))
    except Exception as e:  # keep the modelled rain
        print(f"BOM rain gauges unavailable ({e}); using modelled rain", file=sys.stderr)
        return
    gauges = [g for g in gauges if g]
    if not gauges:
        return
    first, last = max(min(g) for g in gauges), min(max(g) for g in gauges)  # hours every gauge covers
    for t, h in hours.items():
        if first <= t <= last:
            h["precipitation"] = max(g.get(t, 0) for g in gauges)


def hourly_rain(observations):
    """BOM's half-hourly "rain since 9am" readings -> mm per hour, keyed like Open-Meteo (the hour ending at t)."""
    obs = sorted(observations, key=lambda o: o["aifstime_local"])
    hourly, prev = {}, None
    for o in obs:
        try:
            total = float(o["rain_trace"])
        except (TypeError, ValueError):  # "-" when the gauge didn't report
            continue
        at = datetime.strptime(o["aifstime_local"], "%Y%m%d%H%M%S")
        if prev is not None:
            fell = total if total < prev else total - prev  # the count resets at 9am
            end = at if at.minute == 0 else at.replace(minute=0) + timedelta(hours=1)
            key = end.strftime("%Y-%m-%dT%H:%M")
            hourly[key] = hourly.get(key, 0) + fell
        prev = total
    return hourly


class Context:
    """Rolling look-backs over the hourly series (rain history, persistent winds)."""

    def __init__(self, hours):
        self.times = sorted(hours)
        self.hours = hours
        self.index = {t: i for i, t in enumerate(self.times)}

    def _window(self, t, h_from, h_to):
        i = self.index[t]
        return [self.hours[self.times[j]] for j in range(max(0, i - h_to), max(0, i - h_from))]

    def warmth(self, t):
        """Air temperature to score this hour's warmth on: where the day's heading (see WARMTH_DISCOUNT).
        The hour itself is the land/sea blend; where the day's heading is the land cell's headline high, since
        the sea cell drags the blend 4-5° under it on sea-breeze days (7 Nov 2026: land 28°, Observatory Hill
        29°, blend 24°). Falls back to the blend when there's no land series."""
        now = self.hours[t]["temperature_2m"]
        day, hr = t[:10], int(t[11:13])
        sst = self.hours[t].get("sea_surface_temperature")
        land = sst is None or sst >= WARMTH_LAND_MIN_SEA  # cold water: a hot day on land doesn't make the swim
        temps = {}
        for k in range(24):
            h = self.hours.get(f"{day}T{k:02d}:00") or {}
            v = h.get("temperature_2m_land") if land else None
            v = h.get("temperature_2m") if v is None else v
            if v is not None:
                temps[k] = v
        here = temps.get(hr, now)  # this hour on the same series, for spotting a change
        if hr < 12:  # morning: the warmth still to come, up to early afternoon
            ahead = max([now] + [v for k, v in temps.items() if hr <= k <= WARMTH_AHEAD_TO])
        else:  # afternoon and evening: the afternoon's warmth, unless a change has since come through
            peak = max([here] + [v for k, v in temps.items() if 12 <= k <= hr])
            ahead = now if peak - here >= COOL_CHANGE else peak
        return max(now, ahead - WARMTH_DISCOUNT)

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

    def tide_times(self, day):
        """High and low tides on a day: [("high", "2026-11-04T17:00"), ...] (to the hour)."""
        self.tide(self.times[len(self.times) // 2])  # builds self._tides
        return [(kind, self.times[i]) for i, kind in self._tides if self.times[i].startswith(day)]

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
