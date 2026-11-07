"""Google Calendar events: one per good session, kept in sync with the forecast."""

import hashlib
import json
import os
import re
from datetime import datetime

from .config import FIRE_THRESHOLD, KEEP_THRESHOLD, SITE_URL, SLOT_NAMES, TZ
from .geo import wind_kind
from .sessions import conditions, headline, lead_kind, out_of_10, report, top_spots, window_hours


def event_body(sess, hours, ctx, beachwatch, today):
    lead = headline(sess)
    keys = window_hours(sess, lead)
    c = conditions(sess, hours, keys)
    swim = sess.best_swim
    best = sess.best
    fire = "🔥 " if best >= FIRE_THRESHOLD else ""
    kind = lead_kind(sess)
    # Just the call: the score, where and when. The detail is in the description.
    # Surf spots share names with beaches, so they say "surf"; pool names already say Pool or Baths
    where = (lead + (" surf" if kind == "surf" else "")) if lead else "the coast"
    title = f"{fire}{out_of_10(best)}/10 {where} · {sess.day:%a} {SLOT_NAMES[sess.slot][1]}"
    b = swim[1] if swim and kind == "swim" else None  # wind direction only means something at a beach
    rel = {"cross": "cross-shore"}.get(k := wind_kind(c["wind_deg"], b.facing), k) if b else ""

    lines = [
        f"Wind: {c['wind_desc']} {c['wind_dir']} {c['wind']:.0f} km/h, gusts {c['gust']:.0f}"
        + (f" ({rel} at {b.name})" if b else ""),
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
        f"Air max {c['air']:.0f}°"
        + (f" · water {c['sea']:.0f}°" if c["sea"] else "")
        + f" · rain chance {c['rain_prob']:.0f}% · UV {c['uv']:.0f}",
        "",
        f"Last changed {datetime.now(TZ):%a %-d %b %-I:%M%p}. The event is removed if it drops below 7/10.",
        f"Map and every spot's score: {SITE_URL}?s={sess.key}",  # opens the site on this session
    ]
    return title, "\n".join(lines)


def fingerprint(body):
    """What an event update is worth sending for: the title (score, spot, session), the times, the place and
    the top 3 spots with their scores. Everything else (a spot's notes like "cold water", the best window, the
    condition ratings, the wind) wobbles from run to run, and an update makes Google email an "event updated"."""
    top3 = [re.sub(r"\s*\(.*\)$", "", x).strip() for x in body["description"].splitlines() if re.match(r"\s+\d\. ", x)]
    parts = [body["summary"], body["start"]["dateTime"], body["end"]["dateTime"], body.get("location") or "", *top3]
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()[:16]


def _fingerprint_v1(body):
    """The first version (5 Nov 2026), which also counted spot notes and the best window. Only used so events it
    stamped aren't rewritten just because the fingerprint changed; safe to drop once they've passed."""
    desc = body["description"].splitlines()
    keep = [x for x in desc if x.startswith(("Best window", "Overall")) or re.match(r"\s+\d\. ", x)]
    parts = [body["summary"], body["start"]["dateTime"], body["end"]["dateTime"], body.get("location") or "", *keep]
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()[:16]


def calendar_service():
    import google.auth
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/calendar.events"]
    if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):  # key file, e.g. for local testing
        info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    else:  # on Cloud Run: the job's own service account, no key needed
        creds, _ = google.auth.default(scopes=scopes)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def sync(sessions, hours, ctx, beachwatch, now, cal):
    """Posts sessions at 8/10+ and removes them once they drop below 7/10 (KEEP_THRESHOLD), so a session
    hovering around 8 doesn't add and remove itself every hour. Returns the keys that have a live event."""
    from googleapiclient.errors import HttpError

    svc = calendar_service()
    # Fails loudly if the calendar isn't shared with the bot (a missing event alone looks like a 404)
    svc.events().list(calendarId=cal, maxResults=1).execute()
    print(f"calendar ok, {sum(s.is_good for s in sessions)} good session(s)")
    posted = set()
    for sess in sessions:
        try:
            existing = svc.events().get(calendarId=cal, eventId=sess.key).execute()
        except HttpError as e:
            if e.resp.status != 404:
                raise
            existing = None
        live = existing and existing.get("status") != "cancelled"
        if sess.start <= now:  # never touch a session that has started
            if live:
                posted.add(sess.key)
            continue

        if not (sess.is_good or (live and sess.best >= KEEP_THRESHOLD)):
            if live:
                svc.events().delete(calendarId=cal, eventId=sess.key).execute()
                print(f"deleted  {sess.key}")
            continue
        posted.add(sess.key)

        title, desc = event_body(sess, hours, ctx, beachwatch, now.date())
        body = {
            "id": sess.key,
            "summary": title,
            "description": desc,
            "status": "confirmed",
            "location": sess.best_swim[1].name + ", NSW" if sess.best_swim else None,
            "start": {"dateTime": sess.start.isoformat(), "timeZone": "Australia/Sydney"},
            "end": {"dateTime": sess.end.isoformat(), "timeZone": "Australia/Sydney"},
            "transparency": "transparent",  # don't show as busy
        }
        fp = fingerprint(body)
        body["extendedProperties"] = {"private": {"beachbot2": fp}}
        stamp = existing.get("extendedProperties", {}).get("private", {}) if existing else {}
        if live and (stamp.get("beachbot2") == fp or stamp.get("beachbot") == _fingerprint_v1(body)):
            continue  # nothing worth an update
        if existing:  # includes previously deleted ones; ids can't be re-inserted
            svc.events().update(calendarId=cal, eventId=sess.key, body=body).execute()
            print(f"{'updated ' if live else 'restored'} {sess.key}  {title}")
        else:
            svc.events().insert(calendarId=cal, body=body).execute()
            print(f"created  {sess.key}  {title}")
    return posted
