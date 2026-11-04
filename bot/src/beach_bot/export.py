"""scores.json for the map site, and uploading it to the public bucket."""

import json
from datetime import timedelta

from .beaches import BEACH_FOR_SURF, BEACHES, COORDS, POOL_COORDS, POOLS, SURF_COORDS, SURF_SPOTS
from .config import CLOVELLY_TOLERANCE, DAYS_AHEAD, EVENT_THRESHOLD, FAVOURITE, FIRE_THRESHOLD
from .sessions import coast_report, conditions, headline, hour_label, lead_kind, out_of_10, report, window_hours


def slug(name, kind):
    return kind + "-" + "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-").replace("--", "-")


def area(beach):
    """The place a spot belongs to, so the site can group a beach with its surf break and pools ("Coogee")."""
    return beach.name.split(" (")[0]


def export_scores(sessions, hours, ctx, beachwatch, now, posted=None):
    """Everything the map site needs, as one JSON-able dict. `posted` is the session keys with a live calendar
    event (from sync), so the site says "worth it" exactly when the calendar has it; without a sync, 8/10+."""
    spots = [
        {
            "id": slug(b.name, "swim"),
            "name": b.name,
            "kind": "swim",
            "snorkel": b.snorkel,
            "area": area(b),
            "lat": COORDS[b.name][0],
            "lon": COORDS[b.name][1],
        }
        for b in BEACHES
    ]
    spots += [
        {
            "id": slug(sp.name, "surf"),
            "name": sp.name,
            "kind": "surf",
            "area": area(BEACH_FOR_SURF[sp.name]),
            "lat": SURF_COORDS[sp.name][0],
            "lon": SURF_COORDS[sp.name][1],
        }
        for sp in SURF_SPOTS
    ]
    spots += [
        {
            "id": slug(p.name, "pool"),
            "name": p.name,
            "kind": "pool",
            "area": area(p.beach),
            "lat": POOL_COORDS[p.name][0],
            "lon": POOL_COORDS[p.name][1],
        }
        for p in POOLS
    ]

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

        scores = [
            {"id": slug(b.name, "swim"), "score": sc, "rating": out_of_10(sc), "window": window(b.name), "notes": notes}
            for sc, b, notes in sess.swim
        ]
        scores += [
            {
                "id": slug(sp.name, "surf"),
                "score": sc,
                "rating": out_of_10(sc),
                "window": window(sp.name),
                "notes": notes,
            }
            for sc, sp, notes in sess.surf
        ]
        scores += [
            {"id": slug(p.name, "pool"), "score": sc, "rating": out_of_10(sc), "window": window(p.name), "notes": notes}
            for sc, p, notes in sess.pools
        ]
        out_sessions.append(
            {
                "key": sess.key,
                "date": sess.day.isoformat(),
                "label": f"{sess.start:%a} {'AM' if sess.slot == 'am' else 'PM'}",
                "start": sess.start.isoformat(),
                "end": sess.end.isoformat(),
                "started": sess.start <= now,
                "posted": sess.key in posted if posted is not None else bool(sess.is_good),
                # Past a couple of days the forecast is a guide, not a plan (and the calendar doesn't post it)
                "confidence": "high" if sess.day <= now.date() + timedelta(days=DAYS_AHEAD) else "low",
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
                "reports": {
                    slug(sp.name, kind): report(sess, hours, ctx, beachwatch, now.date(), sp)
                    for kind, group in (("swim", BEACHES), ("pool", POOLS), ("surf", SURF_SPOTS))
                    for sp in group
                },
                "ruled_out": {
                    slug(name, "pool" if any(p.name == name for p in POOLS) else "swim"): why
                    for name, why in sess.ruled_out.items()
                },
                "scores": scores,
            }
        )
    return {
        "generated_at": now.isoformat(timespec="minutes"),
        "thresholds": {"post": EVENT_THRESHOLD, "fire": FIRE_THRESHOLD},
        # The favourite wins close calls (R-TB1); the site ranks its list the same way as the headline
        "favourite": {"id": slug(FAVOURITE, "swim"), "tolerance": CLOVELLY_TOLERANCE},
        "spots": spots,
        "sessions": out_sessions,
    }


def upload_scores(data, bucket):
    from google.cloud import storage

    blob = storage.Client().bucket(bucket).blob("scores.json")
    blob.cache_control = "public, max-age=300"
    blob.upload_from_string(json.dumps(data), content_type="application/json")
    print(f"uploaded gs://{bucket}/scores.json")
