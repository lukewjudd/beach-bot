"""scores.json for the map site, and uploading it to the public bucket."""

import json
from datetime import timedelta

from . import swell
from .beaches import EASTERN, Pool, SurfSpot
from .config import (
    DAYS_AHEAD,
    EVENT_THRESHOLD,
    FAVOURITE_TOLERANCE,
    FIRE_THRESHOLD,
    LIFEGUARD_LOG_DAYS,
    SLOT_NAMES,
    SURF_THRESHOLD,
)
from .geo import compass, in_range, wind_kind
from .scoring import at_beach, at_break, surf_period
from .sessions import (
    coast_report,
    conditions,
    headline,
    hour_label,
    later_warning,
    lead_kind,
    out_of_10,
    report,
    spot_key,
    window_hours,
)


def slug(name, kind):
    return kind + "-" + "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-").replace("--", "-")


def kind_of(spot):
    """What the site calls a spot: a swimming beach, a harbour beach, a pool or a surf break."""
    if isinstance(spot, Pool):
        return "pool"
    if isinstance(spot, SurfSpot):
        return "surf"
    return "harbour" if spot.harbour else "swim"


def spot_id(spot):
    return slug(spot.name, kind_of(spot))


def area(beach):
    """The place a spot belongs to, so the site can group a beach with its surf break and pools ("Coogee")."""
    return beach.name.split(" (")[0]


def clock(t):
    return t.strftime("%-I:%M%p").lower()  # 5:41am


def export_scores(sessions, hours, ctx, beachwatch, now, posted=None, sun=None, region=EASTERN):
    """Everything the map site needs for one region, as one JSON-able dict. `posted` is the session keys with a
    live calendar event (from sync), so the site says "worth it" exactly when the calendar has it; without a
    sync, 8/10+. `sun` is load_data()'s sunrise and sunset by date."""
    all_spots = [*region.beaches, *region.surf, *region.pools]
    by_name = {}  # (name, kind) -> spot: a beach and its surf break can share a name ("Maroubra")
    spots = []
    for sp in all_spots:
        by_name[sp.name, kind_of(sp)] = sp
        water = sp.beach if isinstance(sp, Pool | SurfSpot) else sp
        spots.append(
            {
                "id": spot_id(sp),
                "name": sp.name,
                "kind": kind_of(sp),
                "snorkel": getattr(sp, "snorkel", False),
                "women_only": getattr(sp, "women_only", False),
                "level": getattr(sp, "level", None),
                "area": area(water),
                "lat": region.pin(sp)[0],
                "lon": region.pin(sp)[1],
            }
        )

    out_sessions = []
    for sess in sessions:
        lead = headline(sess)
        keys = window_hours(sess, lead) if lead else sess.hours
        c = conditions(sess, hours, keys)
        best = sess.best
        kind = lead_kind(sess)

        def window(name, sess=sess):
            w = sess.windows.get(name)
            return [hour_label(w[0], 0), hour_label(w[1], 1)] if w else None

        def entry(sc, spot, notes, sess=sess):
            """A spot's call, plus every hour of the session for the site's hour-by-hour strip: the score (None
            when ruled out) and, for hours ruled out or stormy, why."""
            results = sess.hourly.get(spot_key(spot), [])
            why = {str(k): ns[0] for k, (s, ns) in enumerate(results) if ns and (s is None or "storms" in ns[0])}
            out = {"id": spot_id(spot), "score": sc, "rating": out_of_10(sc), "window": window(spot.name)}
            out["notes"] = notes
            out["hourly"] = [None if s is None else round(s) for s, _ in results]
            if why:
                out["why"] = why
            if later := later_warning(sess, spot):
                out["later"] = later
            if here := conditions_here(sess, spot, hours):
                out["here"] = here
            return out

        scores = [entry(sc, b, notes) for sc, b, notes in sess.swim]
        scores += [entry(sc, sp, notes) for sc, sp, notes in sess.surf]
        scores += [entry(sc, p, notes) for sc, p, notes in sess.pools]
        out_sessions.append(
            {
                "key": sess.key,
                "hours": [hour_label(t, 0) for t in sess.hours],  # each hour's start, for the strip
                "date": sess.day.isoformat(),
                "label": f"{sess.start:%a} {SLOT_NAMES[sess.slot][0]}",
                "start": sess.start.isoformat(),
                "end": sess.end.isoformat(),
                "started": sess.start <= now,
                # Worth it on the site at 8/10; the calendar holds out for 9 (in_event says if it has one)
                "posted": bool(sess.is_good),
                "in_event": sess.key in posted if posted is not None else bool(sess.for_calendar),
                # Past a couple of days the forecast is a guide, not a plan (and the calendar doesn't post it)
                "confidence": "high" if sess.day <= now.date() + timedelta(days=DAYS_AHEAD) else "low",
                "sun": (
                    {"rise": clock(sun[sess.day.isoformat()][0]), "set": clock(sun[sess.day.isoformat()][1])}
                    if sun and sess.day.isoformat() in sun
                    else None
                ),
                "tides": [{"kind": kind, "time": hour_label(t, 0)} for kind, t in ctx.tide_times(sess.day.isoformat())],
                "fire": best >= FIRE_THRESHOLD,
                # Surf's own call, for the site's surf mode: the best break on the surf scale, and whether it's in
                # the day's surf event (pumping, 8/10+ on that scale)
                "surf": surf_call(sess, posted, window),
                "lead": {
                    "id": slug(lead, kind) if lead else None,
                    "kind": kind,
                    "name": lead,
                    "score": best,
                    "rating": out_of_10(best),
                    "window": window(lead) if lead else None,
                },
                "conditions": {
                    "wind_kmh": round(c["wind"]),
                    "wind_dir": c["wind_dir"],
                    "wind_deg": round(c["wind_deg"]),  # direction it blows FROM, for the map's wind animation
                    "gust_kmh": round(c["gust"]),
                    "wind_desc": c["wind_desc"],
                    "swell_m": round(c["hs"], 1),
                    "swell_dir": c["swell_dir"],
                    "swell_deg": c["swell_deg"],  # where it comes FROM, for the map's swell layer
                    "period_s": round(c["period"]),
                    "air_c": round(c["air"]),
                    "water_c": round(c["sea"]) if c["sea"] else None,
                    "rain_pct": round(c["rain_prob"]),
                    "uv": round(c["uv"]),
                    "trains": swell_trains(hours, keys),
                },
                "report": report(sess, hours, ctx, beachwatch, now.date()),
                "coast": coast_report(sess, hours, ctx, beachwatch, now.date()),
                # Conditions at each spot, so the site can show the one you've picked
                "reports": {spot_id(sp): report(sess, hours, ctx, beachwatch, now.date(), sp) for sp in all_spots},
                # Only beaches and pools get ruled out (surf always scores), and their names are unique
                "ruled_out": {
                    spot_id(by_name.get((name, "pool")) or next(b for b in region.beaches if b.name == name)): why
                    for name, why in sess.ruled_out.items()
                },
                "scores": scores,
            }
        )
    fav = next(b for b in region.beaches if b.name == region.favourite)
    return {
        "region": {
            "id": region.id,
            "name": region.name,
            "key": region.key,
            "tiles": region.tiles,
            "bounds": [list(region.bounds[0]), list(region.bounds[1])],
        },
        "generated_at": now.isoformat(timespec="minutes"),
        "thresholds": {"post": EVENT_THRESHOLD, "fire": FIRE_THRESHOLD, "surf": SURF_THRESHOLD},
        # The favourite wins close calls (R-TB1); the site ranks its list the same way as the headline
        "favourite": {"id": spot_id(fav), "tolerance": FAVOURITE_TOLERANCE},
        "spots": spots,
        "sessions": out_sessions,
        "lifeguards": lifeguards(region, hours, beachwatch),
        "swell_hours": swell_hours(hours, sessions, region),
    }


def swell_hours(hours, sessions, region=EASTERN):
    """Every hour of the forecast's days, for surf mode's swell chart: each wave train offshore as [height m,
    direction it comes from, period s] (null when there isn't one), the tide (sea level, m) and the height at each
    surf break. Hour i is `start` plus i hours. The main swell's period is the longer of its own and the whole
    sea's (R-SU6)."""
    days = sorted({s.day.isoformat() for s in sessions})
    keys = sorted(t for t in hours if days and days[0] <= t[:10] <= days[-1])
    if not keys:
        return None
    out = {"start": keys[0], "swell": [], "swell2": [], "chop": [], "tide": []}
    # The wave height at each surf break, hour by hour, as the surf score sees it: the chart draws the open
    # break's line over the offshore swell, so you can see what its shelter does to it
    out["breaks"] = {spot_id(sp): [round(at_break(hours[t], sp), 1) for t in keys] for sp in region.surf}
    for t in keys:
        h = hours[t]
        for kind, p in (("swell", "swell_wave"), ("swell2", "secondary_swell_wave"), ("chop", "wind_wave")):
            ht, deg = h.get(f"{p}_height"), h.get(f"{p}_direction")
            per = surf_period(h) if kind == "swell" else h.get(f"{p}_period") or 0
            ok = ht is not None and deg is not None and ht >= 0.05
            out[kind].append([round(ht, 2), round(deg), round(per, 1)] if ok else None)
        tide = h.get("sea_level_height_msl")
        out["tide"].append(None if tide is None else round(tide, 2))
    return out


def swell_trains(hours, keys):
    """Every wave train in the sea at the middle of the session's best hours, for surf mode: the main swell, a
    second swell from another direction, and the local wind chop. Surfers read a day by these: a clean groundswell
    under some wind chop is a different day from chop alone. The main swell's period is the longer of its own and
    the whole sea's, as the surf score reads it (R-SU6: the swell partition reads short on groundswell days)."""
    if not keys:
        return []
    h = hours[keys[len(keys) // 2]]
    out = []
    for kind, p in (("swell", "swell_wave"), ("swell2", "secondary_swell_wave"), ("chop", "wind_wave")):
        ht, deg, per = h.get(f"{p}_height"), h.get(f"{p}_direction"), h.get(f"{p}_period") or 0
        if not ht or ht < 0.1 or deg is None:
            continue
        per = surf_period(h) if kind == "swell" else per
        out.append({"kind": kind, "m": round(ht, 1), "dir": compass(deg), "deg": round(deg), "s": round(per)})
    return out


def conditions_here(sess, spot, hours):
    """What the session is like at this spot rather than out at sea, over its best window: the waves at its sand
    or break (the swell chip is the offshore swell, the same for the whole coast) and which way the wind blows
    there. Pools are left without waves: what matters there is swell over the walls, which the score covers."""
    keys = [t for t in window_hours(sess, spot.name) if t in hours]
    if not keys:
        return None
    mid = hours[keys[len(keys) // 2]]
    wdir, kmh = mid["wind_direction_10m"], mid["wind_speed_10m"]
    out = {
        "wind_kmh": round(kmh),
        "wind_dir": compass(wdir),
        "wind_kind": "light" if round(kmh) < 8 else wind_kind(wdir, spot.facing),
    }
    sheltered = getattr(spot, "wind_shelter", None) and in_range(wdir, *spot.wind_shelter)
    sheltered = sheltered or (spot.name == "Bondi (north end)" and 0 <= wdir <= 70)  # R-W6: under Ben Buckler
    if sheltered and round(kmh) >= 8:
        out["wind_kind"] += ", sheltered"
    if isinstance(spot, SurfSpot):
        out["waves_m"] = round(sum(at_break(hours[t], spot) for t in keys) / len(keys), 1)
        # Each swell train as it arrives at this break (its exposure to that direction and period, then breaking
        # height), biggest first: a south groundswell can be the bigger wave at Bondi's south end while an east
        # wind swell is the bigger one offshore. The score itself reads the whole sea on the main swell's direction
        key = swell.key(spot)
        trains = []
        for t in swell_trains(hours, keys):
            k = swell.exposure(spot, key, t["deg"], t["s"])
            m = swell.breaker(t["m"] * k, t["s"], exponent=0.7, ref=10)
            if m >= 0.1:
                trains.append({**t, "m": round(m, 1)})
        out["trains"] = sorted(trains, key=lambda t: -t["m"])
    elif not isinstance(spot, Pool):
        out["waves_m"] = round(sum(at_beach(hours[t], spot) for t in keys) / len(keys), 1)
    return out


def surf_call(sess, posted, window):
    """The session's best surf break, or None where no break was scored."""
    if not sess.surf:
        return None
    sc, sp, _ = sess.surf[0]
    in_event = sess.key in getattr(posted, "surf", set()) if posted is not None else sess.surf_for_calendar
    return {
        "id": spot_id(sp),
        "name": sp.name,
        "score": sc,
        "rating": out_of_10(sc),
        "window": window(sp.name),
        "posted": sc >= SURF_THRESHOLD,
        "in_event": bool(in_event),
    }


def lifeguards(region, hours, beachwatch):
    """This morning's lifeguard reports by spot id (R-LG1), each with what the swell model had for that beach at
    that hour, so the two can be compared over time (see LIFEGUARD_LOG_DAYS)."""
    out = {}
    for b in region.beaches:
        rep = getattr(beachwatch, "lifeguards", {}).get(b.lifeguard) if b.lifeguard else None
        if not rep:
            continue
        h = hours.get(rep["time"][:13] + ":00")
        out[spot_id(b)] = {**rep, "modelled_m": round(at_beach(h, b), 1) if h else None}
    return out


def keep_this_week(data, previous, now):
    """Sessions that have started keep the last call made before they started, until the week (Mon-Sun) is out,
    so the site can show how each one was called. The bot keeps no history of its own: `previous` is the last
    scores.json, which already holds those frozen calls."""
    data["lifeguard_log"] = lifeguard_log(data, previous, now)
    if not previous:
        return data
    monday = (now.date() - timedelta(days=now.weekday())).isoformat()
    fresh = {s["key"]: s for s in data["sessions"]}
    for old in previous.get("sessions", []):
        if old["date"] < monday or old["start"] > now.isoformat():
            continue  # last week's, or hasn't started yet (the fresh call wins)
        # Started: freeze the call as it stood, whether this run recalculated it or the forecast has moved on
        fresh[old["key"]] = {**old, "started": True, "frozen": True}
    data["sessions"] = sorted(fresh.values(), key=lambda s: s["start"])
    return data


def lifeguard_log(data, previous, now):
    """Wave height the lifeguards reported next to the swell model's, one row per beach per morning, kept for
    LIFEGUARD_LOG_DAYS: the observations to tune each beach's exposure against. Carried in scores.json like the
    week's frozen calls, since the bot keeps no history of its own."""
    since = (now.date() - timedelta(days=LIFEGUARD_LOG_DAYS)).isoformat()
    rows = {(r["date"], r["id"]): r for r in (previous or {}).get("lifeguard_log", []) if r["date"] >= since}
    for sid, rep in data.get("lifeguards", {}).items():
        if rep.get("waves_m") is None and rep.get("modelled_m") is None:
            continue
        day = rep["time"][:10]
        rows[day, sid] = {
            "date": day,
            "id": sid,
            "time": rep["time"][11:16],
            "reported": rep.get("waves"),
            "reported_m": rep.get("waves_m"),
            "modelled_m": rep.get("modelled_m"),
        }
    return sorted(rows.values(), key=lambda r: (r["date"], r["id"]))


def load_previous(bucket, name):
    """The region's scores from the last run, or None (first run, or the bucket's unreachable)."""
    from google.cloud import storage

    try:
        return json.loads(storage.Client().bucket(bucket).blob(name).download_as_bytes())
    except Exception as e:
        print(f"no previous scores ({e}); past sessions start fresh")
        return None


def upload_scores(data, bucket, name):
    from google.cloud import storage

    blob = storage.Client().bucket(bucket).blob(name)
    blob.cache_control = "public, max-age=300"
    blob.upload_from_string(json.dumps(data), content_type="application/json")
    print(f"uploaded gs://{bucket}/{name}")
