"""scores.json for the map site, and uploading it to the public bucket."""

import json
from datetime import timedelta

from .beaches import EASTERN, Pool, SurfSpot
from .config import DAYS_AHEAD, EVENT_THRESHOLD, FAVOURITE_TOLERANCE, FIRE_THRESHOLD, SLOT_NAMES
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
                    "period_s": round(c["period"]),
                    "air_c": round(c["air"]),
                    "water_c": round(c["sea"]) if c["sea"] else None,
                    "rain_pct": round(c["rain_prob"]),
                    "uv": round(c["uv"]),
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
        "thresholds": {"post": EVENT_THRESHOLD, "fire": FIRE_THRESHOLD},
        # The favourite wins close calls (R-TB1); the site ranks its list the same way as the headline
        "favourite": {"id": spot_id(fav), "tolerance": FAVOURITE_TOLERANCE},
        "spots": spots,
        "sessions": out_sessions,
    }


def keep_this_week(data, previous, now):
    """Sessions that have started keep the last call made before they started, until the week (Mon-Sun) is out,
    so the site can show how each one was called. The bot keeps no history of its own: `previous` is the last
    scores.json, which already holds those frozen calls."""
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
