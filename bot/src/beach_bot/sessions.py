"""Morning/evening sessions: best windows, picks and the out-of-10 report."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from statistics import mean

from .beaches import BEACHES, SURF_SPOTS
from .config import (CLOVELLY_TOLERANCE, DAYS_AHEAD, EVENT_THRESHOLD, FAVOURITE, SURF_THRESHOLD, TZ,
                     WEEKDAY_SESSIONS, WEEKEND_SESSIONS, WINDOW_HOURS)
from .geo import compass, swell_sector, wind_kind, wind_words
from .scoring import score_surf_hour, score_swim_hour


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
