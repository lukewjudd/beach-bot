"""Google Calendar events: one per day with a good session, bundling every good session that day, kept in sync
with the forecast."""

import hashlib
import json
import os
import re
from datetime import datetime, timedelta

from .config import FIRE_THRESHOLD, KEEP_THRESHOLD, SITE_URL, SLOT_NAMES, TZ
from .export import clock
from .geo import wind_kind
from .sessions import conditions, headline, lead_kind, out_of_10, report, top_spots, window_hours


def day_key(sess):
    """The day's event id: the session key without its slot (still base32hex, so a valid Google event id)."""
    return f"{sess.region.key}{sess.day:%Y%m%d}"


def session_lines(sess, hours, ctx, beachwatch, today):
    """One session's part of the description: its call, wind, top 3 spots, ratings, swell and temperatures."""
    lead = headline(sess)
    keys = window_hours(sess, lead)
    c = conditions(sess, hours, keys)
    swim = sess.best_swim
    kind = lead_kind(sess)
    where = (lead + (" surf" if kind == "surf" else "")) if lead else "the coast"
    b = swim[1] if swim and kind == "swim" else None  # wind direction only means something at a beach
    rel = {"cross": "cross-shore"}.get(k := wind_kind(c["wind_deg"], b.facing), k) if b else ""
    lines = [
        f"{SLOT_NAMES[sess.slot][1].capitalize()} {clock(sess.start)}–{clock(sess.end)}: "
        f"{out_of_10(sess.best)}/10 {where}",
        f"Wind: {c['wind_desc']} {c['wind_dir']} {c['wind']:.0f} km/h, gusts {c['gust']:.0f}"
        + (f" ({rel} at {b.name})" if b else ""),
        "Top 3 spots:",
    ]
    for i, (sc, name, activity, notes) in enumerate(top_spots(sess), 1):
        lines.append(f"  {i}. {name}: {out_of_10(sc)}/10 {activity}" + (f" ({', '.join(notes)})" if notes else ""))
    lines.append("Conditions:")
    for k, v in report(sess, hours, ctx, beachwatch, today).items():
        lines.append(f"  {k:<14}{v:>2}/10")
    lines += [
        f"Swell: {c['hs']:.1f}m {c['swell_dir']} @ {c['period']:.0f}s (open ocean)",
        f"Air max {c['air']:.0f}°"
        + (f" · water {c['sea']:.0f}°" if c["sea"] else "")
        + f" · rain chance {c['rain_prob']:.0f}% · UV {c['uv']:.0f}",
    ]
    return lines


def day_body(sessions, hours, ctx, beachwatch, today):
    """Title and description for one day's event, from its good sessions (in time order). The title is the
    day's best call and which sessions it covers: "9/10 Clovelly · Sat morning & evening"."""
    sessions = sorted(sessions, key=lambda s: s.start)
    top = max(sessions, key=lambda s: s.best)
    lead, kind = headline(top), lead_kind(top)
    # Surf spots share names with beaches, so they say "surf"; pool names already say Pool or Baths
    where = (lead + (" surf" if kind == "surf" else "")) if lead else "the coast"
    names = [SLOT_NAMES[s.slot][1] for s in sessions]
    when = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " & " + names[-1]
    fire = "🔥 " if top.best >= FIRE_THRESHOLD else ""
    title = f"{fire}{out_of_10(top.best)}/10 {where} · {top.day:%a} {when}"
    lines = []
    for s in sessions:
        lines += [*session_lines(s, hours, ctx, beachwatch, today), ""]
    lines += [
        f"Last changed {datetime.now(TZ):%a %-d %b %-I:%M%p}. A session comes off if it drops below 7/10, "
        "and the event once none are left.",
        f"Map and every spot's score: {SITE_URL}?s={top.key}",  # opens the site on the day's best session
    ]
    return title, "\n".join(lines)


def event_body(sess, hours, ctx, beachwatch, today):
    """A single session as its own day event (what the dry run prints)."""
    return day_body([sess], hours, ctx, beachwatch, today)


def fingerprint(body):
    """What an event update is worth sending for: the title (score, spot, session), the times, the place and
    the top 3 spots with their scores. Everything else (a spot's notes like "cold water", the best window, the
    condition ratings, the wind) wobbles from run to run, and an update makes Google email an "event updated"."""
    top3 = [re.sub(r"\s*\(.*\)$", "", x).strip() for x in body["description"].splitlines() if re.match(r"\s+\d\. ", x)]
    parts = [body["summary"], body["start"]["dateTime"], body["end"]["dateTime"], body.get("location") or "", *top3]
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


def sync(sessions, hours, ctx, beachwatch, now, cal, svc=None):
    """One event per day, covering that day's sessions at 8/10+ (weekday middays never go in). A session already
    in the event stays until it drops below 7/10 (KEEP_THRESHOLD), so one hovering around 8 doesn't come and go
    every hour; the event goes once no sessions are left. Once the event has started it's left alone.
    Returns the keys of the sessions that are in a live event."""
    from googleapiclient.errors import HttpError

    svc = svc or calendar_service()
    days = sorted({s.day for s in sessions})
    if not days:
        return set()
    # Everything on those days in one call, deleted ones too: an id that was ever used can't be inserted again
    t0 = datetime.combine(days[0], datetime.min.time(), TZ)
    t1 = datetime.combine(days[-1] + timedelta(days=1), datetime.min.time(), TZ)
    existing, token = {}, None
    while True:  # also fails loudly if the calendar isn't shared with the bot
        page = (
            svc.events()
            .list(
                calendarId=cal,
                timeMin=t0.isoformat(),
                timeMax=t1.isoformat(),
                showDeleted=True,
                singleEvents=True,
                maxResults=250,
                pageToken=token,
            )
            .execute()
        )
        existing.update({e["id"]: e for e in page.get("items", [])})
        token = page.get("nextPageToken")
        if not token:
            break
    is_live = lambda e: bool(e) and e.get("status") != "cancelled"  # noqa: E731
    print(f"calendar ok, {sum(s.is_good and s.in_calendar for s in sessions)} good session(s)")

    posted = set()
    for day in days:
        todays = sorted((s for s in sessions if s.day == day), key=lambda s: s.start)
        # Events from before days were bundled (one per session): cleared once, unless already under way
        for s in todays:
            if is_live(existing.get(s.key)):
                if s.start <= now:
                    posted.add(s.key)
                else:
                    svc.events().delete(calendarId=cal, eventId=s.key).execute()
                    print(f"deleted  {s.key} (now part of the day's event)")

        key = day_key(todays[0])
        ev = existing.get(key)
        live = is_live(ev)
        had = set(ev.get("extendedProperties", {}).get("private", {}).get("sessions", "").split()) if live else set()
        if live and datetime.fromisoformat(ev["start"]["dateTime"]) <= now:  # under way: leave it be
            posted |= {s.key for s in todays if s.slot in had}
            continue

        keep = [
            s
            for s in todays
            if s.in_calendar and s.start > now and (s.is_good or (s.slot in had and s.best >= KEEP_THRESHOLD))
        ]
        if not keep:
            if live:
                svc.events().delete(calendarId=cal, eventId=key).execute()
                print(f"deleted  {key}")
            continue
        posted |= {s.key for s in keep}

        title, desc = day_body(keep, hours, ctx, beachwatch, now.date())
        top = max(keep, key=lambda s: s.best)
        body = {
            "id": key,
            "summary": title,
            "description": desc,
            "status": "confirmed",
            "location": top.best_swim[1].name + ", NSW" if top.best_swim else None,
            "start": {"dateTime": keep[0].start.isoformat(), "timeZone": "Australia/Sydney"},
            "end": {"dateTime": keep[-1].end.isoformat(), "timeZone": "Australia/Sydney"},
            "transparency": "transparent",  # don't show as busy
        }
        fp = fingerprint(body)
        body["extendedProperties"] = {"private": {"beachbot2": fp, "sessions": " ".join(s.slot for s in keep)}}
        if live and ev.get("extendedProperties", {}).get("private", {}).get("beachbot2") == fp:
            continue  # nothing worth an update
        if ev:  # includes previously deleted ones; ids can't be re-inserted
            svc.events().update(calendarId=cal, eventId=key, body=body).execute()
            print(f"{'updated ' if live else 'restored'} {key}  {title}")
            continue
        try:
            svc.events().insert(calendarId=cal, body=body).execute()
            print(f"created  {key}  {title}")
        except HttpError as e:
            if e.resp.status != 409:  # deleted long ago and missing from the listing: it still owns the id
                raise
            svc.events().update(calendarId=cal, eventId=key, body=body).execute()
            print(f"restored {key}  {title}")
    return posted
