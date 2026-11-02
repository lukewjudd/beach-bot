"""Google Calendar events: one per good session, kept in sync with the forecast."""

import json
import os
from datetime import datetime

from .config import EVENT_THRESHOLD, FIRE_THRESHOLD, TZ
from .geo import wind_kind
from .sessions import conditions, headline, hour_label, out_of_10, report, top_spots, window_hours


def event_body(sess, hours, ctx, beachwatch, today):
    lead = headline(sess)
    keys = window_hours(sess, lead)
    c = conditions(sess, hours, keys)
    swim, surf = sess.best_swim, sess.best_surf
    best = max(swim[0] if swim else 0, surf[0] if surf else 0)
    fire = "🔥 " if best >= FIRE_THRESHOLD else ""
    parts = []
    if swim and swim[0] >= EVENT_THRESHOLD:
        parts.append(f"🏖️ {swim[1].name}")
    if surf:
        parts.append(f"🏄 {surf[1].name} {c['hs']:.1f}m")
    if not parts and swim:  # only seen in --all previews
        parts.append(f"🏖️ {swim[1].name}")
    b = swim[1] if swim else None
    kind = {"cross": "cross-shore"}.get(k := wind_kind(c["wind_deg"], b.facing), k) if b else ""
    wind_line = f"{c['wind_dir']} {c['wind']:.0f} km/h gust {c['gust']:.0f}"
    title = f"{fire}{out_of_10(best)}/10 {' · '.join(parts)} · 💨 {wind_line} · {c['air']:.0f}°"
    if c["sea"]:
        title += f"/{c['sea']:.0f}° water"

    lines = [
        f"💨 Wind: {c['wind_desc']} {c['wind_dir']} {c['wind']:.0f} km/h, gusts {c['gust']:.0f}"
        + (f" ({kind} at {b.name})" if b else ""),
        f"⏰ Best window: {hour_label(keys[0], 0)}–{hour_label(keys[-1], 1)} at {lead}",
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
        f"Updated {datetime.now(TZ):%a %-d %b %-I:%M%p}. The event is removed if conditions drop.",
    ]
    return title, "\n".join(lines)


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


def sync(sessions, hours, ctx, beachwatch, now):
    from googleapiclient.errors import HttpError

    svc = calendar_service()
    cal = os.environ["BEACH_CALENDAR_ID"]
    # Fails loudly if the calendar isn't shared with the bot (a missing event alone looks like a 404)
    svc.events().list(calendarId=cal, maxResults=1).execute()
    print(f"calendar ok, {sum(s.is_good for s in sessions)} good session(s)")
    for sess in sessions:
        if sess.start <= now:
            continue  # never touch a session that has started
        try:
            existing = svc.events().get(calendarId=cal, eventId=sess.key).execute()
        except HttpError as e:
            if e.resp.status != 404:
                raise
            existing = None
        live = existing and existing.get("status") != "cancelled"

        if not sess.is_good:
            if live:
                svc.events().delete(calendarId=cal, eventId=sess.key).execute()
                print(f"deleted  {sess.key}")
            continue

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
        if existing:  # includes previously deleted ones; ids can't be re-inserted
            svc.events().update(calendarId=cal, eventId=sess.key, body=body).execute()
            print(f"{'updated ' if live else 'restored'} {sess.key}  {title}")
        else:
            svc.events().insert(calendarId=cal, body=body).execute()
            print(f"created  {sess.key}  {title}")
