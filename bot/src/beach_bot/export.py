"""scores.json for the map site, and uploading it to the public bucket."""

import json

from .beaches import BEACHES, COORDS, SURF_COORDS, SURF_SPOTS
from .config import EVENT_THRESHOLD, FIRE_THRESHOLD
from .sessions import conditions, headline, hour_label, out_of_10, report, window_hours


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
