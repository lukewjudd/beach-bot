"""Beach bot: picks the best Sydney eastern suburbs beach for each morning/evening
session over the next couple of days and keeps a shared Google Calendar in sync.

Rules come from beach-knowledge.md (rule ids like R-W1 refer to that file).

Usage:
  python beach_bot.py            # dry run: print the scored sessions
  python beach_bot.py --sync     # also write/update/delete Google Calendar events

--sync needs env vars:
  GOOGLE_SERVICE_ACCOUNT_JSON  service account key (the JSON text)
  BEACH_CALENDAR_ID            id of the shared "Beach" calendar
"""

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from statistics import mean
from zoneinfo import ZoneInfo

import requests

TZ = ZoneInfo("Australia/Sydney")

# ---------------------------------------------------------------- tunables
DAYS_AHEAD = 2            # today + this many days
EVENT_THRESHOLD = 80      # session score needed to post an event (8/10)
FIRE_THRESHOLD = 90       # adds a 🔥 to the title (9/10+)
SURF_THRESHOLD = EVENT_THRESHOLD
CLOVELLY_TOLERANCE = 5    # R-TB1: Clovelly wins if within this many points
WINDOW_HOURS = 2          # sessions are judged on their best stretch this long, not the whole slot
FAVOURITE = "Clovelly"

WEEKDAY_SESSIONS = {"am": (None, 9), "pm": (17, None)}    # None = sunrise/sunset
WEEKEND_SESSIONS = {"am": (None, 11), "pm": (14, None)}

FORECAST_POINT = (-33.914, 151.267)  # Clovelly; weather is a blend of the land and sea cells either side
MARINE_POINT = (-33.92, 151.33)      # one offshore point; beaches differ via k below

# ---------------------------------------------------------------- beaches


@dataclass
class Beach:
    name: str
    facing: int                      # bearing the beach faces (looking out to sea)
    k: dict                          # swell exposure by sector (R-S, §4.2)
    rain_occ: float                  # mm in 24h: "occasionally" fails (§3.1)
    rain_often: float                # mm in 24h: "often" fails
    hazard: int                      # Beachsafe 1-10
    beachwatch: str                  # site name in the Beachwatch feed
    swim_limit: float = 1.2          # Hb above this = no swim
    poor_grade: bool = False         # R-R3: 3-day rain rule
    snorkel: bool = False
    patrolled_all_daylight: bool = False
    notes: list = field(default_factory=list)


BEACHES = [
    Beach("Bondi (north end)", 150, {"NE": .3, "E": .5, "SE": .8, "S": .9}, 5, 20, 7, "Bondi Beach"),
    Beach("Tamarama", 100, {"NE": .8, "E": 1.0, "SE": .9, "S": .6}, 1, 5, 8, "Tamarama Beach", swim_limit=0.9),
    Beach("Bronte", 90, {"NE": .8, "E": 1.0, "SE": .9, "S": .6}, 1, 10, 7, "Bronte Beach"),
    Beach("Clovelly", 120, {"NE": .15, "E": .25, "SE": .35, "S": .25}, 10, 20, 2, "Clovelly Beach",
          snorkel=True, patrolled_all_daylight=True),
    Beach("Gordons Bay", 90, {"NE": .4, "E": .5, "SE": .35, "S": .2}, 1, 10, 2, "Gordons Bay (East)",
          swim_limit=0.6, snorkel=True),
    Beach("Coogee", 100, {"NE": .6, "E": .6, "SE": .35, "S": .25}, 1, 10, 4, "Coogee Beach", poor_grade=True),
    Beach("Maroubra", 90, {"NE": .9, "E": 1.0, "SE": .9, "S": .6}, 5, 20, 6, "Maroubra Beach"),
    Beach("Malabar", 110, {"NE": .25, "E": .45, "SE": .5, "S": .3}, 1, 5, 3, "Malabar Beach"),
    Beach("Little Bay", 45, {"NE": .35, "E": .4, "SE": .35, "S": .2}, 1, 10, 2, "Little Bay Beach", snorkel=True),
]


@dataclass
class SurfSpot:
    name: str
    facing: int
    swell_dirs: tuple                # (from_deg, to_deg) the spot works in
    min_hs: float
    max_hs: float = 2.5
    bonus_dirs: tuple = None         # swell direction range that gets a small bonus


SURF_SPOTS = [
    SurfSpot("Bondi (south end)", 140, (135, 200), 0.6, bonus_dirs=(157, 200)),   # R-SU1
    SurfSpot("Maroubra", 90, (30, 150), 0.5, bonus_dirs=(67, 112)),               # R-SU2
    SurfSpot("Bronte", 90, (67, 157), 0.8),                                        # R-SU3
    SurfSpot("Coogee", 100, (67, 112), 1.5, max_hs=3.0),                           # R-SU4
]

# Map positions for the website (swim areas from beach-knowledge.md §1; surf markers sit just offshore)
COORDS = {
    "Bondi (north end)": (-33.8905, 151.2805),
    "Tamarama": (-33.9007, 151.2709),
    "Bronte": (-33.9031, 151.2688),
    "Clovelly": (-33.9138, 151.2666),
    "Gordons Bay": (-33.9158, 151.2648),
    "Coogee": (-33.9208, 151.2582),
    "Maroubra": (-33.9475, 151.2572),
    "Malabar": (-33.9644, 151.2523),
    "Little Bay": (-33.9799, 151.2514),
}
SURF_COORDS = {
    "Bondi (south end)": (-33.8935, 151.2790),
    "Maroubra": (-33.9470, 151.2615),
    "Bronte": (-33.9040, 151.2725),
    "Coogee": (-33.9210, 151.2625),
}

# ---------------------------------------------------------------- helpers


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


# ---------------------------------------------------------------- data


def fetch_json(url, params):
    r = requests.get(url, params=params, timeout=180)   # multi-year backtest requests are slow
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
        if k == "wind_direction_10m":
            ws_l, ws_s = land["hourly"]["wind_speed_10m"], sea["hourly"]["wind_speed_10m"]
            vals = []
            for a, b, sa, sb in zip(lv, sv, ws_l, ws_s):
                if None in (a, b, sa, sb):
                    vals.append(a if a is not None else b)
                    continue
                x = sa * math.sin(math.radians(a)) + sb * math.sin(math.radians(b))
                y = sa * math.cos(math.radians(a)) + sb * math.cos(math.radians(b))
                vals.append(round(math.degrees(math.atan2(x, y)) % 360))
            out["hourly"][k] = vals
        else:
            out["hourly"][k] = [a if b is None else b if a is None else (a + b) / 2 for a, b in zip(lv, sv)]
    return out


def load_data():
    wx = fetch_weather("https://api.open-meteo.com/v1/forecast", {
        "latitude": FORECAST_POINT[0], "longitude": FORECAST_POINT[1],
        "hourly": "temperature_2m,precipitation,precipitation_probability,wind_speed_10m,"
                  "wind_direction_10m,wind_gusts_10m,cloud_cover,uv_index",
        "daily": "sunrise,sunset",
        "timezone": "Australia/Sydney", "past_days": 4, "forecast_days": DAYS_AHEAD + 1,
    })
    sea = fetch_json("https://marine-api.open-meteo.com/v1/marine", {
        "latitude": MARINE_POINT[0], "longitude": MARINE_POINT[1], "cell_selection": "sea",
        "hourly": "wave_height,swell_wave_height,swell_wave_direction,swell_wave_period,"
                  "sea_surface_temperature,sea_level_height_msl",
        "timezone": "Australia/Sydney", "past_days": 4, "forecast_days": DAYS_AHEAD + 1,
    })
    try:
        bw = fetch_json("https://api.beachwatch.nsw.gov.au/public/sites/geojson", {})
        beachwatch = {f["properties"]["siteName"]: f["properties"].get("pollutionForecast")
                      for f in bw["features"]}
    except Exception as e:  # undocumented API: fall back to rain rules
        print(f"Beachwatch unavailable ({e}); using rain thresholds", file=sys.stderr)
        beachwatch = {}

    hours = {}
    for i, t in enumerate(wx["hourly"]["time"]):
        hours[t] = {k: v[i] for k, v in wx["hourly"].items() if k != "time"}
    for i, t in enumerate(sea["hourly"]["time"]):
        if t in hours:
            hours[t].update({k: v[i] for k, v in sea["hourly"].items() if k != "time"})
    sun = {d: (datetime.fromisoformat(r), datetime.fromisoformat(s))
           for d, r, s in zip(wx["daily"]["time"], wx["daily"]["sunrise"], wx["daily"]["sunset"])}
    return hours, sun, beachwatch


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


# ---------------------------------------------------------------- scoring


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


# ---------------------------------------------------------------- sessions


@dataclass
class Session:
    day: date
    slot: str
    start: datetime
    end: datetime
    hours: list
    swim: list = field(default_factory=list)    # [(score, beach, notes)] best first
    surf: list = field(default_factory=list)    # [(score, spot)] best first
    windows: dict = field(default_factory=dict)  # spot name -> (first hour, last hour) of its best window

    @property
    def key(self):
        return f"beach{self.day:%Y%m%d}{self.slot}"   # valid Google event id (base32hex)

    @property
    def best_swim(self):
        return self.swim[0] if self.swim else None

    @property
    def best_surf(self):
        return self.surf[0] if self.surf and self.surf[0][0] >= SURF_THRESHOLD else None

    @property
    def is_good(self):
        return (self.best_swim and self.best_swim[0] >= EVENT_THRESHOLD) or self.best_surf is not None


def build_sessions(hours, sun, now, days=None):
    sessions = []
    days = days or [now.date() + timedelta(days=o) for o in range(DAYS_AHEAD + 1)]
    for d in days:
        rise, sset = sun[d.isoformat()]
        slots = WEEKEND_SESSIONS if d.weekday() >= 5 else WEEKDAY_SESSIONS
        for slot, (h_from, h_to) in slots.items():
            start = rise if h_from is None else datetime.combine(d, datetime.min.time()).replace(hour=h_from)
            end = sset if h_to is None else datetime.combine(d, datetime.min.time()).replace(hour=h_to)
            # An hour counts if most of it is inside the session (no 5am "window" before a 5:54 sunrise)
            first = start.hour + (1 if start.minute >= 30 else 0)
            last = end.hour + (1 if end.minute >= 30 else 0)
            keys = [f"{d.isoformat()}T{hr:02d}:00" for hr in range(first, last)]
            keys = [k for k in keys if k in hours]
            if keys:
                sessions.append(Session(d, slot, start.replace(tzinfo=TZ), end.replace(tzinfo=TZ), keys))
    return sessions


def best_window(sess, scores):
    """Best run of WINDOW_HOURS consecutive scored hours: (score, first index) or None.
    You only spend an hour or two at the beach, so a chilly 6am shouldn't sink a great 8am."""
    n = min(WINDOW_HOURS, len(scores))
    best = None
    for i in range(len(scores) - n + 1):
        win = scores[i:i + n]
        if None in win:
            continue
        sc = 0.6 * mean(win) + 0.4 * min(win)
        if best is None or sc > best[0]:
            best = (sc, i)
    return best


def score_session(sess, hours, ctx, beachwatch, today):
    n = min(WINDOW_HOURS, len(sess.hours))
    for b in BEACHES:
        results = [score_swim_hour(b, t, hours[t], ctx, beachwatch, today) for t in sess.hours]
        best = best_window(sess, [r[0] for r in results])
        if not best:
            continue
        sc, i = best
        notes = sorted({x for _, ns in results[i:i + n] for x in ns})
        sess.swim.append((round(sc), b, notes))
        sess.windows[b.name] = (sess.hours[i], sess.hours[i + n - 1])
    sess.swim.sort(key=lambda x: -x[0])
    if sess.swim and sess.swim[0][1].name != FAVOURITE:               # R-TB1
        fav = next((x for x in sess.swim if x[1].name == FAVOURITE), None)
        if fav and fav[0] >= sess.swim[0][0] - CLOVELLY_TOLERANCE:
            sess.swim.remove(fav)
            sess.swim.insert(0, fav)

    for sp in SURF_SPOTS:
        best = best_window(sess, [score_surf_hour(sp, hours[t]) for t in sess.hours])
        if best:
            sc, i = best
            sess.surf.append((round(sc), sp))
            sess.windows[sp.name] = (sess.hours[i], sess.hours[i + n - 1])
    sess.surf.sort(key=lambda x: -x[0])


def window_hours(sess, name):
    """Hour keys of a spot's best window (falls back to the whole session)."""
    if name not in sess.windows:
        return sess.hours
    first, last = sess.windows[name]
    return sess.hours[sess.hours.index(first):sess.hours.index(last) + 1]


def headline(sess):
    """The spot the event leads with: surf if it beats a postable swim, else the swim pick."""
    swim, surf = sess.best_swim, sess.best_surf
    if surf and (not swim or swim[0] < EVENT_THRESHOLD or surf[0] > swim[0]):
        return surf[1].name
    return swim[1].name if swim else None


def conditions(sess, hours, keys=None):
    hs = [hours[t] for t in (keys or sess.hours)]
    wind = mean(h["wind_speed_10m"] for h in hs)
    wdir = hs[len(hs) // 2]["wind_direction_10m"]
    return {
        "air": max(h["temperature_2m"] for h in hs),
        "sea": next((h["sea_surface_temperature"] for h in hs if h.get("sea_surface_temperature")), None),
        "wind": wind, "wind_deg": wdir, "wind_dir": compass(wdir),
        "wind_desc": wind_words(max(wind, max(h["wind_gusts_10m"] for h in hs) * 0.6)),
        "gust": max(h["wind_gusts_10m"] for h in hs),
        "hs": mean(h.get("wave_height") or 0 for h in hs),
        "period": mean(h.get("swell_wave_period") or 0 for h in hs),
        "swell_dir": compass(hs[len(hs) // 2].get("swell_wave_direction") or 0),
        "rain_prob": max(h.get("precipitation_probability") or 0 for h in hs),
        "uv": max(h.get("uv_index") or 0 for h in hs),
    }


def hour_label(key, add):
    hr = int(key[11:13]) + add
    return f"{(hr - 1) % 12 + 1}{'am' if hr < 12 else 'pm'}"


def out_of_10(score):
    return max(1, min(10, int(score // 10)))   # 80-89 -> 8, so 8/10 always means it cleared the bar


def report(sess, hours, ctx, beachwatch, today):
    """Out-of-10 ratings per condition, judged at the top swim pick during its best window."""
    b = sess.best_swim[1] if sess.best_swim else BEACHES[3]
    keys = window_hours(sess, b.name)
    c = conditions(sess, hours, keys)
    hs_list = [hours[t] for t in keys]

    wind = c["wind"]
    w = 10 if wind < 8 else 8 if wind < 15 else 6 if wind < 20 else 4 if wind < 28 else 2
    kinds = [wind_kind(h["wind_direction_10m"], b.facing) for h in hs_list]
    if kinds.count("onshore") > len(kinds) / 2 and wind >= 12:
        w -= 2
    elif kinds.count("offshore") > len(kinds) / 2:
        w += 1
    w -= 3 if c["gust"] >= 45 else 2 if c["gust"] >= 35 else 0

    sector = swell_sector(hs_list[0].get("swell_wave_direction") or 0)
    hb = c["hs"] * (b.k[sector] if sector else 0.1) * (1.3 if c["period"] >= 12 else 1)
    calm = 10 if hb < 0.3 else 8 if hb < 0.5 else 6 if hb < 0.8 else 4 if hb < 1.2 else 2
    surf = out_of_10(sess.surf[0][0]) if sess.surf else 1

    sea = c["sea"] or 20
    water = 10 if sea >= 22 else 9 if sea >= 21 else 8 if sea >= 20 else 7 if sea >= 19 else 6 if sea >= 18 else 5 if sea >= 17 else 3
    if ctx.ne_days(sess.hours[0]) >= 3:
        water -= 1

    air = c["air"]
    weather = 10 if air >= 26 else 8 if air >= 23 else 6 if air >= 21 else 4 if air >= 19 else 2
    weather -= 3 if c["rain_prob"] >= 60 else 1 if c["rain_prob"] >= 40 else 0

    bw = beachwatch.get(b.beachwatch) if sess.day == today else None
    rain24 = ctx.rain(sess.hours[0], 0, 24)
    quality = {"Likely": 2, "Possible": 5, "Unlikely": 10}.get(
        bw, 10 if rain24 < b.rain_occ else 6 if rain24 < b.rain_often else 3)

    clamp = lambda x: max(1, min(10, x))   # noqa: E731
    return {"Wind": clamp(w), "Calm water": clamp(calm), "Surf": clamp(surf), "Water temp": clamp(water),
            "Weather": clamp(weather), "Water quality": clamp(quality)}


def top_spots(sess, n=3):
    """Best swim and surf options merged into one ranked list."""
    picks = [(sc, b.name, "swim" + (" / snorkel" if b.snorkel else ""), notes) for sc, b, notes in sess.swim]
    picks += [(sc, sp.name, "surf", []) for sc, sp in sess.surf]
    picks.sort(key=lambda x: -(x[0] + (CLOVELLY_TOLERANCE + 0.5 if x[1] == FAVOURITE else 0)))   # R-TB1
    seen, out = set(), []
    for p in picks:
        if p[1] not in seen:
            seen.add(p[1])
            out.append(p)
    return out[:n]


def event_body(sess, hours, ctx, beachwatch, today):
    lead = headline(sess)
    keys = window_hours(sess, lead)
    c = conditions(sess, hours, keys)
    swim, surf = sess.best_swim, sess.best_surf
    best = max(swim[0] if swim else 0, surf[0] if surf else 0)
    fire = "🔥 " if best >= FIRE_THRESHOLD else ""
    parts = []
    if swim and swim[0] >= EVENT_THRESHOLD:
        parts.append(f"🏖️ {swim[1].name}")
    if surf:
        parts.append(f"🏄 {surf[1].name} {c['hs']:.1f}m")
    if not parts and swim:   # only seen in --all previews
        parts.append(f"🏖️ {swim[1].name}")
    b = swim[1] if swim else None
    kind = {"cross": "cross-shore"}.get(k := wind_kind(c["wind_deg"], b.facing), k) if b else ""
    wind_line = f"{c['wind_dir']} {c['wind']:.0f} km/h gust {c['gust']:.0f}"
    title = f"{fire}{out_of_10(best)}/10 {' · '.join(parts)} · 💨 {wind_line} · {c['air']:.0f}°"
    if c["sea"]:
        title += f"/{c['sea']:.0f}° water"

    lines = [
        f"💨 Wind: {c['wind_desc']} {c['wind_dir']} {c['wind']:.0f} km/h, gusts {c['gust']:.0f}"
        + (f" ({kind} at {b.name})" if b else ""),
        f"⏰ Best window: {hour_label(keys[0], 0)}–{hour_label(keys[-1], 1)} at {lead}",
        f"Overall: {out_of_10(best)}/10",
        "",
    ]
    lines.append("Top 3 spots:")
    for i, (sc, name, activity, notes) in enumerate(top_spots(sess), 1):
        lines.append(f"  {i}. {name}: {out_of_10(sc)}/10 {activity}" + (f" ({', '.join(notes)})" if notes else ""))
    lines += ["", "Conditions:"]
    for k, v in report(sess, hours, ctx, beachwatch, today).items():
        lines.append(f"  {k:<14}{v:>2}/10")
    lines += [
        "",
        f"Swell: {c['hs']:.1f}m {c['swell_dir']} @ {c['period']:.0f}s (open ocean)",
        f"Air max {c['air']:.0f}°" + (f" · water {c['sea']:.0f}°" if c["sea"] else "")
        + f" · rain chance {c['rain_prob']:.0f}% · UV {c['uv']:.0f}",
        "",
        f"Updated {datetime.now(TZ):%a %-d %b %-I:%M%p}. The event is removed if conditions drop.",
    ]
    return title, "\n".join(lines)


# ---------------------------------------------------------------- website data


def slug(name, kind):
    return kind + "-" + "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-").replace("--", "-")


def export_scores(sessions, hours, ctx, beachwatch, now):
    """Everything the map site needs, as one JSON-able dict."""
    spots = [{"id": slug(b.name, "swim"), "name": b.name, "kind": "swim", "snorkel": b.snorkel,
              "lat": COORDS[b.name][0], "lon": COORDS[b.name][1]} for b in BEACHES]
    spots += [{"id": slug(sp.name, "surf"), "name": sp.name, "kind": "surf",
               "lat": SURF_COORDS[sp.name][0], "lon": SURF_COORDS[sp.name][1]} for sp in SURF_SPOTS]

    out_sessions = []
    for sess in sessions:
        lead = headline(sess)
        keys = window_hours(sess, lead) if lead else sess.hours
        c = conditions(sess, hours, keys)
        swim, surf = sess.best_swim, sess.surf[0] if sess.surf else None
        best = max(swim[0] if swim else 0, surf[0] if surf else 0)

        def window(name):
            w = sess.windows.get(name)
            return [hour_label(w[0], 0), hour_label(w[1], 1)] if w else None

        scores = [{"id": slug(b.name, "swim"), "score": sc, "rating": out_of_10(sc),
                   "window": window(b.name), "notes": notes} for sc, b, notes in sess.swim]
        scores += [{"id": slug(sp.name, "surf"), "score": sc, "rating": out_of_10(sc),
                    "window": window(sp.name), "notes": []} for sc, sp in sess.surf]
        out_sessions.append({
            "key": sess.key,
            "date": sess.day.isoformat(),
            "label": f"{sess.start:%a} {'AM' if sess.slot == 'am' else 'PM'}",
            "start": sess.start.isoformat(), "end": sess.end.isoformat(),
            "started": sess.start <= now,
            "posted": bool(sess.is_good),
            "fire": best >= FIRE_THRESHOLD,
            "lead": {"name": lead, "score": best, "rating": out_of_10(best), "window": window(lead) if lead else None},
            "conditions": {
                "wind_kmh": round(c["wind"]), "wind_dir": c["wind_dir"], "gust_kmh": round(c["gust"]),
                "wind_desc": c["wind_desc"], "swell_m": round(c["hs"], 1), "swell_dir": c["swell_dir"],
                "period_s": round(c["period"]), "air_c": round(c["air"]),
                "water_c": round(c["sea"]) if c["sea"] else None,
                "rain_pct": round(c["rain_prob"]), "uv": round(c["uv"]),
            },
            "report": report(sess, hours, ctx, beachwatch, now.date()),
            "scores": scores,
        })
    return {
        "generated_at": now.isoformat(timespec="minutes"),
        "thresholds": {"post": EVENT_THRESHOLD, "fire": FIRE_THRESHOLD},
        "spots": spots,
        "sessions": out_sessions,
    }


def upload_scores(data, bucket):
    from google.cloud import storage
    blob = storage.Client().bucket(bucket).blob("scores.json")
    blob.cache_control = "public, max-age=300"
    blob.upload_from_string(json.dumps(data), content_type="application/json")
    print(f"uploaded gs://{bucket}/scores.json")


# ---------------------------------------------------------------- calendar


def calendar_service():
    import google.auth
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    scopes = ["https://www.googleapis.com/auth/calendar.events"]
    if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):   # key file, e.g. for local testing
        info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    else:   # on Cloud Run: the job's own service account, no key needed
        creds, _ = google.auth.default(scopes=scopes)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def sync(sessions, hours, ctx, beachwatch, now):
    from googleapiclient.errors import HttpError
    svc = calendar_service()
    cal = os.environ["BEACH_CALENDAR_ID"]
    # Fails loudly if the calendar isn't shared with the bot (a missing event alone looks like a 404)
    svc.events().list(calendarId=cal, maxResults=1).execute()
    print(f"calendar ok, {sum(s.is_good for s in sessions)} good session(s)")
    for sess in sessions:
        if sess.start <= now:
            continue   # never touch a session that has started
        try:
            existing = svc.events().get(calendarId=cal, eventId=sess.key).execute()
        except HttpError as e:
            if e.resp.status != 404:
                raise
            existing = None
        live = existing and existing.get("status") != "cancelled"

        if not sess.is_good:
            if live:
                svc.events().delete(calendarId=cal, eventId=sess.key).execute()
                print(f"deleted  {sess.key}")
            continue

        title, desc = event_body(sess, hours, ctx, beachwatch, now.date())
        body = {
            "id": sess.key, "summary": title, "description": desc, "status": "confirmed",
            "location": sess.best_swim[1].name + ", NSW" if sess.best_swim else None,
            "start": {"dateTime": sess.start.isoformat(), "timeZone": "Australia/Sydney"},
            "end": {"dateTime": sess.end.isoformat(), "timeZone": "Australia/Sydney"},
            "transparency": "transparent",   # don't show as busy
        }
        if existing:   # includes previously deleted ones; ids can't be re-inserted
            svc.events().update(calendarId=cal, eventId=sess.key, body=body).execute()
            print(f"{'updated ' if live else 'restored'} {sess.key}  {title}")
        else:
            svc.events().insert(calendarId=cal, body=body).execute()
            print(f"created  {sess.key}  {title}")


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", action="store_true", help="write to Google Calendar")
    ap.add_argument("--all", action="store_true", help="print the full report for every session")
    ap.add_argument("--json", metavar="PATH", help="also write the website's scores.json here")
    args = ap.parse_args()

    now = datetime.now(TZ)
    hours, sun, beachwatch = load_data()
    ctx = Context(hours)
    sessions = build_sessions(hours, sun, now)
    for sess in sessions:
        score_session(sess, hours, ctx, beachwatch, now.date())

    for sess in sessions:
        flag = "✅" if sess.is_good else "  "
        swim = sess.best_swim
        surf = sess.surf[0] if sess.surf else None
        print(f"{flag} {sess.start:%a %d %b} {sess.slot}  "
              f"swim: {swim[1].name if swim else '-'} {swim[0] if swim else ''}  "
              f"surf: {surf[1].name + ' ' + str(surf[0]) if surf else '-'}")
        if sess.is_good or args.all:
            title, desc = event_body(sess, hours, ctx, beachwatch, now.date())
            print(f"     → {title}")
            print("       " + desc.replace("\n", "\n       "))

    data = export_scores(sessions, hours, ctx, beachwatch, now)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(data, f, indent=1)
    if args.sync:
        sync(sessions, hours, ctx, beachwatch, now)
        if os.environ.get("BEACH_BUCKET"):
            upload_scores(data, os.environ["BEACH_BUCKET"])


if __name__ == "__main__":
    main()
