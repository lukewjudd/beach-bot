"""Morning/evening sessions: best windows, picks and the out-of-10 report."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from statistics import mean

from .beaches import BEACH_FOR_SURF, BEACHES, POOLS, SURF_SPOTS, Pool
from .config import (
    CLOVELLY_TOLERANCE,
    DAYS_AHEAD,
    EVENT_THRESHOLD,
    FAVOURITE,
    SURF_THRESHOLD,
    TZ,
    WEEKDAY_SESSIONS,
    WEEKEND_SESSIONS,
    WINDOW_HOURS,
)
from .geo import compass, swell_sector, wind_kind, wind_words
from .scoring import score_pool_hour, score_surf_hour, score_swim_hour


@dataclass
class Session:
    day: date
    slot: str
    start: datetime
    end: datetime
    hours: list
    swim: list = field(default_factory=list)  # [(score, beach, notes)] best first
    surf: list = field(default_factory=list)  # [(score, spot, notes)] best first, every spot
    pools: list = field(default_factory=list)  # [(score, pool, notes)] best first
    windows: dict = field(default_factory=dict)  # spot name -> (first hour, last hour) of its best window
    ruled_out: dict = field(default_factory=dict)  # spot name -> why it's a no-go all session

    @property
    def key(self):
        return f"beach{self.day:%Y%m%d}{self.slot}"  # valid Google event id (base32hex)

    @property
    def best_swim(self):
        return self.swim[0] if self.swim else None

    @property
    def best_surf(self):
        return self.surf[0] if self.surf and self.surf[0][0] >= SURF_THRESHOLD else None

    @property
    def best_pool(self):
        return self.pools[0] if self.pools else None

    @property
    def best(self):
        """Top score across beaches, pools and surf: what decides worth it on the site and the calendar."""
        return max([x[0] for x in (self.best_swim, self.best_pool, self.surf[0] if self.surf else None) if x] or [0])

    @property
    def is_good(self):
        return self.best >= EVENT_THRESHOLD


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
        win = scores[i : i + n]
        if None in win:
            continue
        sc = 0.6 * mean(win) + 0.4 * min(win)
        if best is None or sc > best[0]:
            best = (sc, i)
    return best


def main_reason(results):
    """The most common reason across the hours that were a no-go."""
    reasons = [ns[0] for sc, ns in results if sc is None and ns]
    return max(set(reasons), key=reasons.count) if reasons else "not swimmable"


def score_session(sess, hours, ctx, beachwatch, today):
    n = min(WINDOW_HOURS, len(sess.hours))
    for b in BEACHES:
        results = [score_swim_hour(b, t, hours[t], ctx, beachwatch, today) for t in sess.hours]
        best = best_window(sess, [r[0] for r in results])
        if not best:
            sess.ruled_out[b.name] = main_reason(results)
            continue
        sc, i = best
        notes = sorted({x for _, ns in results[i : i + n] for x in ns})
        sess.swim.append((round(sc), b, notes))
        sess.windows[b.name] = (sess.hours[i], sess.hours[i + n - 1])
    sess.swim.sort(key=lambda x: -x[0])
    if sess.swim and sess.swim[0][1].name != FAVOURITE:  # R-TB1
        fav = next((x for x in sess.swim if x[1].name == FAVOURITE), None)
        if fav and fav[0] >= sess.swim[0][0] - CLOVELLY_TOLERANCE:
            sess.swim.remove(fav)
            sess.swim.insert(0, fav)

    for p in POOLS:
        results = [score_pool_hour(p, t, hours[t], ctx, beachwatch, today) for t in sess.hours]
        best = best_window(sess, [r[0] for r in results])
        if not best:
            sess.ruled_out[p.name] = main_reason(results)
            continue
        sc, i = best
        notes = sorted({x for _, ns in results[i : i + n] for x in ns})
        sess.pools.append((round(sc), p, notes))
        sess.windows[p.name] = (sess.hours[i], sess.hours[i + n - 1])
    sess.pools.sort(key=lambda x: -x[0])

    for sp in SURF_SPOTS:
        results = [score_surf_hour(sp, hours[t]) for t in sess.hours]
        sc, i = best_window(sess, [r[0] for r in results])  # never None: surf always scores
        notes = sorted({x for _, ns in results[i : i + n] for x in ns})
        sess.surf.append((round(sc), sp, notes))
        sess.windows[sp.name] = (sess.hours[i], sess.hours[i + n - 1])
    sess.surf.sort(key=lambda x: -x[0])


def window_hours(sess, name):
    """Hour keys of a spot's best window (falls back to the whole session)."""
    if name not in sess.windows:
        return sess.hours
    first, last = sess.windows[name]
    return sess.hours[sess.hours.index(first) : sess.hours.index(last) + 1]


def headline(sess):
    """The spot the event leads with. A beach wins close calls with a pool (Clovelly first, R-TB1),
    and surf leads when it beats a postable swim."""
    swim, pool, surf = sess.best_swim, sess.best_pool, sess.best_surf
    lead = swim
    if pool and (not swim or pool[0] > swim[0] + CLOVELLY_TOLERANCE):
        lead = pool
    if surf and (not lead or lead[0] < EVENT_THRESHOLD or surf[0] > lead[0]):
        return surf[1].name
    return lead[1].name if lead else None


def lead_kind(sess):
    """'swim', 'pool' or 'surf' for the headline spot."""
    name = headline(sess)
    if sess.best_surf and sess.best_surf[1].name == name:
        return "surf"
    if sess.best_pool and sess.best_pool[1].name == name and not (sess.best_swim and sess.best_swim[1].name == name):
        return "pool"
    return "swim"


def conditions(sess, hours, keys=None):
    hs = [hours[t] for t in (keys or sess.hours)]
    wind = mean(h["wind_speed_10m"] for h in hs)
    wdir = hs[len(hs) // 2]["wind_direction_10m"]
    return {
        "air": max(h["temperature_2m"] for h in hs),
        "sea": next((h["sea_surface_temperature"] for h in hs if h.get("sea_surface_temperature")), None),
        "wind": wind,
        "wind_deg": wdir,
        "wind_dir": compass(wdir),
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
    return max(1, min(10, int(score // 10)))  # 80-89 -> 8, so 8/10 always means it cleared the bar


def report(sess, hours, ctx, beachwatch, today, spot=None):
    """Out-of-10 ratings per condition at one spot (a Beach, Pool or SurfSpot) during its best window.
    Without a spot it's the top swim pick, which is what the calendar event shows.
    Wind, weather and water temp come from area-wide forecasts; how the wind and swell hit the spot,
    and its water quality, are the spot's own."""
    spot = spot or (sess.best_swim[1] if sess.best_swim else BEACHES[3])
    keys = window_hours(sess, spot.name)
    c = conditions(sess, hours, keys)
    hs_list = [hours[t] for t in keys]
    facing = None if isinstance(spot, Pool) else spot.facing  # pools sit behind rocks: no on/offshore
    water_beach = spot.beach if isinstance(spot, Pool) else BEACH_FOR_SURF.get(spot.name, spot)

    wind = c["wind"]
    w = 10 if wind < 8 else 8 if wind < 15 else 6 if wind < 20 else 4 if wind < 28 else 2
    if facing is not None:
        kinds = [wind_kind(h["wind_direction_10m"], facing) for h in hs_list]
        if kinds.count("onshore") > len(kinds) / 2 and wind >= 12:
            w -= 2
        elif kinds.count("offshore") > len(kinds) / 2:
            w += 1
    w -= 3 if c["gust"] >= 45 else 2 if c["gust"] >= 35 else 0

    if isinstance(spot, Pool):  # calm inside unless swell is coming over the walls
        surge = c["hs"] * spot.exposure
        calm = 10 if surge < 0.8 else 8 if surge < 1.2 else 6 if surge < 1.5 else 4 if surge < 2.0 else 2
    else:
        sector = swell_sector(hs_list[0].get("swell_wave_direction") or 0)
        hb = c["hs"] * (spot.k[sector] if sector else 0.1) * (1.3 if c["period"] >= 12 else 1)
        calm = 10 if hb < 0.3 else 8 if hb < 0.5 else 6 if hb < 0.8 else 4 if hb < 1.2 else 2
    own_surf = next((sc for sc, sp, _ in sess.surf if sp.name == spot.name), None)
    surf = out_of_10(own_surf if own_surf is not None else sess.surf[0][0]) if sess.surf else 1

    sea = c["sea"] or 20
    water = (
        10
        if sea >= 22
        else 9
        if sea >= 21
        else 8
        if sea >= 20
        else 7
        if sea >= 19
        else 6
        if sea >= 18
        else 5
        if sea >= 17
        else 3
    )
    if ctx.ne_days(sess.hours[0]) >= 3:
        water -= 1

    air = c["air"]
    weather = 10 if air >= 26 else 8 if air >= 23 else 6 if air >= 21 else 4 if air >= 19 else 2
    weather -= 3 if c["rain_prob"] >= 60 else 1 if c["rain_prob"] >= 40 else 0

    b = water_beach
    bw = beachwatch.get(b.beachwatch) if sess.day == today else None
    rain24 = ctx.rain(sess.hours[0], 0, 24)
    quality = {"Likely": 2, "Possible": 5, "Unlikely": 10}.get(
        bw, 10 if rain24 < b.rain_occ else 6 if rain24 < b.rain_often else 3
    )
    # R-R3: Poor-graded sites take up to 3 days to clear after rain. Only when Beachwatch has no forecast
    # (it covers today only); its own forecast always wins.
    if bw is None and b.poor_grade and quality == 10 and ctx.rain(sess.hours[0], 0, 72) >= 1:
        quality = 6

    clamp = lambda x: max(1, min(10, x))  # noqa: E731
    return {
        "Wind": clamp(w),
        "Calm water": clamp(calm),
        "Surf": clamp(surf),
        "Water temp": clamp(water),
        "Weather": clamp(weather),
        "Water quality": clamp(quality),
    }


def top_spots(sess, n=3):
    """Best beach, pool and surf options merged into one ranked list."""
    picks = [(sc, b.name, "swim" + (" / snorkel" if b.snorkel else ""), notes) for sc, b, notes in sess.swim]
    picks += [(sc, p.name, "pool", notes) for sc, p, notes in sess.pools]
    picks += [(sc, sp.name, "surf", notes) for sc, sp, notes in sess.surf]
    picks.sort(key=lambda x: -(x[0] + (CLOVELLY_TOLERANCE + 0.5 if x[1] == FAVOURITE else 0)))  # R-TB1
    seen, out = set(), []
    for p in picks:
        if p[1] not in seen:
            seen.add(p[1])
            out.append(p)
    return out[:n]
