"""Morning, midday and evening sessions: best windows, picks and the out-of-10 report."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from statistics import mean

from .beaches import EASTERN, Beach, Pool, Region, SurfSpot
from .config import (
    CALENDAR_THRESHOLD,
    DAYS_AHEAD,
    EVENT_THRESHOLD,
    FAVOURITE_TOLERANCE,
    SESSIONS,
    SURF_THRESHOLD,
    TZ,
    WINDOW_HOURS,
)
from .geo import compass, wind_words
from .scoring import (
    POOL_TOPS,
    SWIM_TOPS,
    pool_parts,
    score_pool_hour,
    score_surf_hour,
    score_swim_hour,
    surf_parts,
    swim_parts,
)


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
    hourly: dict = field(default_factory=dict)  # (kind, name) -> [(score or None, notes)] for every hour
    ruled_out: dict = field(default_factory=dict)  # spot name -> why it's a no-go all session
    region: Region = EASTERN

    @property
    def key(self):
        return f"{self.region.key}{self.day:%Y%m%d}{self.slot}"  # valid Google event id (base32hex)

    @property
    def best_swim(self):
        """The best ocean beach. Harbour beaches are scored and shown, but never lead a session or decide
        whether it's worth going (so they never post to the calendar)."""
        return next((x for x in self.swim if not x[1].harbour), None)

    @property
    def best_surf(self):
        """The best surf break when it's pumping (8/10+), else None. Surf never leads or scores a session."""
        return self.surf[0] if self.surf and self.surf[0][0] >= SURF_THRESHOLD else None

    @property
    def surf_for_calendar(self):
        """Pumping surf, for the day's surf event (its own event, so a surf 8 is never read as a swim 8)."""
        return self.in_calendar and self.best_surf is not None

    @property
    def best_pool(self):
        return self.pools[0] if self.pools else None

    @property
    def best(self):
        """The session's score: the best ocean beach or pool. Surf is on another scale and doesn't count."""
        return max([x[0] for x in (self.best_swim, self.best_pool) if x] or [0])

    @property
    def is_good(self):
        return self.best >= EVENT_THRESHOLD

    @property
    def for_calendar(self):
        """Good enough for its own event (9/10): a higher bar than worth it on the site."""
        return self.in_calendar and self.best >= CALENDAR_THRESHOLD

    @property
    def in_calendar(self):
        """Weekday middays are on the site but never posted: most people can't get to the beach at lunch on a
        workday, and an event there is noise in their calendar."""
        return not (self.slot == "md" and self.day.weekday() < 5)


def build_sessions(hours, sun, now, days=None, region=EASTERN):
    sessions = []
    days = days or [now.date() + timedelta(days=o) for o in range(DAYS_AHEAD + 1)]
    for d in days:
        rise, sset = sun[d.isoformat()]
        for slot, (h_from, h_to) in SESSIONS.items():
            start = rise if h_from is None else datetime.combine(d, datetime.min.time()).replace(hour=h_from)
            end = sset if h_to is None else datetime.combine(d, datetime.min.time()).replace(hour=h_to)
            # An hour counts if most of it is inside the session (no 5am "window" before a 5:54 sunrise)
            first = start.hour + (1 if start.minute >= 30 else 0)
            last = end.hour + (1 if end.minute >= 30 else 0)
            keys = [f"{d.isoformat()}T{hr:02d}:00" for hr in range(first, last)]
            keys = [k for k in keys if k in hours]
            if keys:
                sessions.append(Session(d, slot, start.replace(tzinfo=TZ), end.replace(tzinfo=TZ), keys, region=region))
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
    region = sess.region
    for b in region.beaches:
        results = [score_swim_hour(b, t, hours[t], ctx, beachwatch, today) for t in sess.hours]
        sess.hourly[spot_key(b)] = results
        best = best_window(sess, [r[0] for r in results])
        if not best:
            sess.ruled_out[b.name] = main_reason(results)
            continue
        sc, i = best
        notes = sorted({x for _, ns in results[i : i + n] for x in ns})
        sess.swim.append((round(sc), b, notes))
        sess.windows[b.name] = (sess.hours[i], sess.hours[i + n - 1])
    sess.swim.sort(key=lambda x: -x[0])
    top = sess.best_swim
    if top and top[1].name != region.favourite:  # R-TB1
        fav = next((x for x in sess.swim if x[1].name == region.favourite), None)
        if fav and fav[0] >= top[0] - FAVOURITE_TOLERANCE:
            sess.swim.remove(fav)
            sess.swim.insert(0, fav)

    for p in region.pools:
        results = [score_pool_hour(p, t, hours[t], ctx, beachwatch, today) for t in sess.hours]
        sess.hourly[spot_key(p)] = results
        best = best_window(sess, [r[0] for r in results])
        if not best:
            sess.ruled_out[p.name] = main_reason(results)
            continue
        sc, i = best
        notes = sorted({x for _, ns in results[i : i + n] for x in ns})
        sess.pools.append((round(sc), p, notes))
        sess.windows[p.name] = (sess.hours[i], sess.hours[i + n - 1])
    sess.pools.sort(key=lambda x: -x[0])

    for sp in region.surf:
        results = [score_surf_hour(sp, t, hours[t], ctx, beachwatch, today) for t in sess.hours]
        sess.hourly[spot_key(sp)] = results
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


def spot_key(spot):
    """Surf breaks share names with their beaches, so spots are told apart by kind and name."""
    return type(spot).__name__, spot.name


def later_warning(sess, spot):
    """What rules out the rest of a session after a spot's best stretch, e.g. "⚡ storms from 4pm", or None.
    The score is the best two hours, so without this a lovely 2pm hides a stormy 5pm."""
    results = sess.hourly.get(spot_key(spot))
    if not results or spot.name not in sess.windows:
        return None
    end = sess.hours.index(sess.windows[spot.name][1])
    for t, (sc, notes) in zip(sess.hours[end + 1 :], results[end + 1 :], strict=True):
        why = notes[0] if notes else ""
        if sc is None or "storms" in why:  # surf scores storms as 1/10 rather than ruling them out
            when = hour_label(t, 0)
            if "storms" in why:
                return f"⚡ storms from {when}"
            if why == "closed for the day":
                return f"closes at {when}"
            return f"{why} from {when}"
    return None


def headline(sess):
    """The spot the session leads with: a beach or a pool, never surf. A beach wins close calls with a pool
    (Clovelly first, R-TB1)."""
    swim, pool = sess.best_swim, sess.best_pool
    lead = swim
    # The beach wins a close call, unless the pool is what makes the session worth it: then it's the headline
    # (no "Clovelly 8/10" when Clovelly is a 7 and the 8 is Wylie's)
    if pool and (not swim or pool[0] > swim[0] + FAVOURITE_TOLERANCE or swim[0] < EVENT_THRESHOLD <= pool[0]):
        lead = pool
    return lead[1].name if lead else None


def lead_kind(sess):
    """'swim', 'harbour' or 'pool' for the headline spot."""
    name = headline(sess)
    if sess.best_pool and sess.best_pool[1].name == name and not (sess.best_swim and sess.best_swim[1].name == name):
        return "pool"
    return "harbour" if sess.best_swim and sess.best_swim[1].harbour else "swim"


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


# Each bar is one part of the score, out of 10: 10 is the most that part can add, and every step down is 5 points
# the score didn't get. So a spot with every bar at 10 scores about 95-100, and two bars at 8 cost it 20 points.
# Water quality can only take points away, so it's 10 until it does. Surf quality points are scaled by the wave
# size (no waves, no surf), so there a bar shows the part's own points before that.
BAR_STEP = 5
BAR_TOPS = {  # the score's own tops (scoring.SWIM_TOPS, POOL_TOPS), in the order the bars show
    Beach: {k: SWIM_TOPS[k] for k in ("Wind", "Calm water", "Weather", "Water quality")},
    Pool: {k: POOL_TOPS[k] for k in ("Wind", "Calm in the pool", "Tide", "Weather", "Water quality")},
    SurfSpot: {"Wind": 30, "Wave size": 35, "Wave quality": 30, "Weather": 5, "Water quality": 0},
}


def bar(points, top):
    """A part's points as an out-of-10 bar; None (the part that rules a spot out) is 1."""
    return 1 if points is None else max(1, min(10, round(10 - (top - points) / BAR_STEP)))


def report(sess, hours, ctx, beachwatch, today, spot=None):
    """Out-of-10 bars per part of the score at one spot (a Beach, Pool or SurfSpot) over its best window: the
    score's own points for that part, averaged over the window (see BAR_TOPS). No water temperature bar: it's one
    sea temperature for the whole coast, a stat in the summary, and its points sit in Weather. Without a spot it's
    the top swim pick, which is what the calendar event shows."""
    spot = spot or (sess.best_swim[1] if sess.best_swim else sess.region.beaches[0])
    keys = window_hours(sess, spot.name)
    if isinstance(spot, SurfSpot):
        parts = [surf_parts(spot, t, hours[t], ctx, beachwatch, today)[0] for t in keys]
    elif isinstance(spot, Pool):
        parts = [pool_parts(spot, t, hours[t], ctx, beachwatch, today)[0] for t in keys]
    else:
        parts = [swim_parts(spot, t, hours[t], ctx, beachwatch, today)[0] for t in keys]
    tops = dict(BAR_TOPS[type(spot)])
    if isinstance(spot, Pool):  # only pools with a best tide get a tide bar, out of what that tide's worth
        if spot.best_tide is None:
            del tops["Tide"]
        elif spot.best_tide == "mid_high":
            tops["Tide"] = 5
    out = {}
    for k, top in tops.items():
        vals = [p[k] for p in parts]
        out[k] = bar(None if None in vals else mean(vals), top)
    return out


def coast_report(sess, hours, ctx, beachwatch, today):
    """The typical beach this session: the median of each row across every beach. Shown on the site when
    nothing's worth going to, so it doesn't single out a spot."""
    # Ocean beaches only: the always-calm harbour would make the coast look calmer than it is
    reports = [report(sess, hours, ctx, beachwatch, today, b) for b in sess.region.beaches if not b.harbour]
    return {k: sorted(r[k] for r in reports)[len(reports) // 2] for k in reports[0]}


def top_spots(sess, n=3):
    """Best beach, pool and surf options merged into one ranked list."""
    picks = [
        (sc, b.name, ("harbour swim" if b.harbour else "swim") + (" / snorkel" if b.snorkel else ""), notes)
        for sc, b, notes in sess.swim
        if not b.harbour  # the event is about the ocean; harbour beaches are on the site
    ]
    picks += [(sc, p.name, "pool", notes) for sc, p, notes in sess.pools]
    picks += [(sc, sp.name, "surf", notes) for sc, sp, notes in sess.surf]
    fav = sess.region.favourite
    picks.sort(key=lambda x: -(x[0] + (FAVOURITE_TOLERANCE + 0.5 if x[1] == fav else 0)))  # R-TB1
    seen, out = set(), []
    for p in picks:
        if p[1] not in seen:
            seen.add(p[1])
            out.append(p)
    return out[:n]
