"""Google Calendar events: one per day with a good session, bundling every good session that day, kept in sync
with the forecast."""

import hashlib
import json
import os
import re
from datetime import datetime, timedelta

from .config import FIRE_THRESHOLD, KEEP_THRESHOLD, SITE_URL, SLOT_NAMES, SURF_KEEP_THRESHOLD, TZ
from .export import clock
from .geo import wind_kind
from .sessions import conditions, headline, later_warning, lead_kind, out_of_10, report, top_spots, window_hours


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
    picks = {"swim": sess.swim, "pool": sess.pools, "surf": sess.surf}.get(kind, [])
    spot = next((x[1] for x in picks if x[1].name == lead), None)
    later = later_warning(sess, spot) if spot else None
    lines = [
        f"{SLOT_NAMES[sess.slot][1].capitalize()} {clock(sess.start)}–{clock(sess.end)}: "
        f"{out_of_10(sess.best)}/10 {where}" + (f" (then {later})" if later else ""),
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
        f"Last changed {datetime.now(TZ):%a %-d %b %-I:%M%p}. A session comes off if it drops below 8/10, "
        "and the event once none are left.",
        f"Map and every spot's score: {SITE_URL}?s={top.key}",  # opens the site on the day's best session
    ]
    location = top.best_swim[1].name + ", NSW" if top.best_swim else None
    return title, "\n".join(lines), location


def surf_day_body(sessions, hours, ctx, beachwatch, today):
    """Title and description for a day's surf event: "🏄 Surf 8/10 Maroubra · Sat morning". Always says surf,
    so it's never read as a swim score."""
    sessions = sorted(sessions, key=lambda s: s.start)
    top = max(sessions, key=lambda s: s.surf[0][0])
    sc, spot, _ = top.surf[0]
    names = [SLOT_NAMES[s.slot][1] for s in sessions]
    when = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " & " + names[-1]
    title = f"🏄 Surf {out_of_10(sc)}/10 {spot.name} · {top.day:%a} {when}"
    lines = ["Surf's pumping. This is the surf score, on its own scale: waves, wind and swell, not a swim.", ""]
    for s in sessions:
        keys = window_hours(s, s.surf[0][1].name)
        c = conditions(s, hours, keys)
        lines += [
            f"{SLOT_NAMES[s.slot][1].capitalize()} {clock(s.start)}–{clock(s.end)}: surf {out_of_10(s.surf[0][0])}/10 "
            f"{s.surf[0][1].name}",
            f"Swell: {c['hs']:.1f}m {c['swell_dir']} @ {c['period']:.0f}s (open ocean)",
            f"Wind: {c['wind_desc']} {c['wind_dir']} {c['wind']:.0f} km/h, gusts {c['gust']:.0f}",
            "Top 3 breaks:",
        ]
        for i, (bsc, b, notes) in enumerate(s.surf[:3], 1):
            lines.append(f"  {i}. {b.name}: {out_of_10(bsc)}/10 surf" + (f" ({', '.join(notes)})" if notes else ""))
        lines.append("")
    lines += [
        f"Last changed {datetime.now(TZ):%a %-d %b %-I:%M%p}. A session comes off if the surf drops below 7/10.",
        f"Map and every spot's score: {SITE_URL}?s={top.key}",
    ]
    return title, "\n".join(lines), spot.name + ", NSW"


def event_body(sess, hours, ctx, beachwatch, today):
    """A single session as its own day event (what the dry run prints): title and description."""
    return day_body([sess], hours, ctx, beachwatch, today)[:2]


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


class Posted(set):
    """Keys of the sessions in a live swim event (the set itself), and in a live surf event (.surf)."""

    def __init__(self, *a):
        super().__init__(*a)
        self.surf = set()


def sync(sessions, hours, ctx, beachwatch, now, cal, svc=None):
    """One swim event per day, covering that day's sessions at 9/10+ (weekday middays never go in), and a separate
    surf event on days the surf is pumping. A session already in an event stays until it drops a step below the
    bar, so one hovering around it doesn't come and go every hour; an event goes once no sessions are left, and
    once it has started it's left alone. Returns the keys of the sessions in a live swim event."""
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
    print(
        f"calendar ok, {sum(s.for_calendar for s in sessions)} swim session(s) at 9/10+, "
        f"{sum(s.surf_for_calendar for s in sessions)} surf session(s) pumping"
    )

    def put(key, todays, wanted, still_ok, body_fn):
        """Create, update or remove one day's event from the sessions it should cover. Returns their keys."""
        ev = existing.get(key)
        live = is_live(ev)
        had = set(ev.get("extendedProperties", {}).get("private", {}).get("sessions", "").split()) if live else set()
        if live and datetime.fromisoformat(ev["start"]["dateTime"]) <= now:  # under way: leave it be
            return {s.key for s in todays if s.slot in had}
        keep = [s for s in todays if s.in_calendar and s.start > now and (wanted(s) or (s.slot in had and still_ok(s)))]
        if not keep:
            if live:
                svc.events().delete(calendarId=cal, eventId=key).execute()
                print(f"deleted  {key}")
            return set()

        title, desc, location = body_fn(keep, hours, ctx, beachwatch, now.date())
        body = {
            "id": key,
            "summary": title,
            "description": desc,
            "status": "confirmed",
            "location": location,
            "start": {"dateTime": keep[0].start.isoformat(), "timeZone": "Australia/Sydney"},
            "end": {"dateTime": keep[-1].end.isoformat(), "timeZone": "Australia/Sydney"},
            "transparency": "transparent",  # don't show as busy
        }
        fp = fingerprint(body)
        body["extendedProperties"] = {"private": {"beachbot2": fp, "sessions": " ".join(s.slot for s in keep)}}
        keys = {s.key for s in keep}
        if live and ev.get("extendedProperties", {}).get("private", {}).get("beachbot2") == fp:
            return keys  # nothing worth an update
        if ev:  # includes previously deleted ones; ids can't be re-inserted
            svc.events().update(calendarId=cal, eventId=key, body=body).execute()
            print(f"{'updated ' if live else 'restored'} {key}  {title}")
            return keys
        try:
            svc.events().insert(calendarId=cal, body=body).execute()
            print(f"created  {key}  {title}")
        except HttpError as e:
            if e.resp.status != 409:  # deleted long ago and missing from the listing: it still owns the id
                raise
            svc.events().update(calendarId=cal, eventId=key, body=body).execute()
            print(f"restored {key}  {title}")
        return keys

    posted = Posted()
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

        # The day's swim event (9/10+, kept until it drops below 8), and, separately, a surf event when it's
        # pumping (8/10+ on the surf scale, kept until 7): two scales, so never in the same event
        posted |= put(
            day_key(todays[0]), todays, lambda s: s.for_calendar, lambda s: s.best >= KEEP_THRESHOLD, day_body
        )
        posted.surf |= put(
            day_key(todays[0]) + "su",
            todays,
            lambda s: s.surf_for_calendar,
            lambda s: bool(s.surf) and s.surf[0][0] >= SURF_KEEP_THRESHOLD,
            surf_day_body,
        )
    return posted
