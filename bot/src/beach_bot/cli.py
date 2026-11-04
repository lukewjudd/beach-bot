"""Command line: `beach-bot` (dry run), `beach-bot --sync` (calendar + bucket)."""

import argparse
import json
import os
from datetime import datetime, timedelta

from .calendar import event_body, sync
from .config import DAYS_AHEAD, TZ
from .export import export_scores, keep_this_week, load_previous, upload_scores
from .forecast import Context, load_data
from .sessions import build_sessions, score_session


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", action="store_true", help="write to Google Calendar")
    ap.add_argument("--all", action="store_true", help="print the full report for every session")
    ap.add_argument("--json", metavar="PATH", help="also write the website's scores.json here")
    args = ap.parse_args()

    now = datetime.now(TZ)
    hours, sun, beachwatch = load_data()
    ctx = Context(hours)
    # The site shows this week and next, Monday to Sunday; only sessions the swell forecast reaches get scored
    # (missing swell would read as dead calm)
    next_sunday = now.date() + timedelta(days=13 - now.weekday())
    days = [now.date() + timedelta(days=o) for o in range((next_sunday - now.date()).days + 1)]
    days = [d for d in days if d.isoformat() in sun]
    sessions = [
        s
        for s in build_sessions(hours, sun, now, days)
        if all(hours[t].get("wave_height") is not None for t in s.hours)
    ]
    for sess in sessions:
        score_session(sess, hours, ctx, beachwatch, now.date())
    # The calendar only gets the next couple of days: further out the forecast isn't good enough to plan on
    soon = [s for s in sessions if s.day <= now.date() + timedelta(days=DAYS_AHEAD)]

    for sess in soon:
        flag = "✅" if sess.is_good else "  "
        swim = sess.best_swim
        surf = sess.surf[0] if sess.surf else None
        print(
            f"{flag} {sess.start:%a %d %b} {sess.slot}  "
            f"swim: {swim[1].name if swim else '-'} {swim[0] if swim else ''}  "
            f"surf: {surf[1].name + ' ' + str(surf[0]) if surf else '-'}"
        )
        if sess.is_good or args.all:
            title, desc = event_body(sess, hours, ctx, beachwatch, now.date())
            print(f"     → {title}")
            print("       " + desc.replace("\n", "\n       "))

    posted = sync(soon, hours, ctx, beachwatch, now) if args.sync else None
    data = export_scores(sessions, hours, ctx, beachwatch, now, posted, sun)
    bucket = os.environ.get("BEACH_BUCKET") if args.sync else None
    if bucket:
        previous = load_previous(bucket)
    elif args.json and os.path.exists(args.json):  # local runs carry forward from the last local file
        with open(args.json) as f:
            previous = json.load(f)
    else:
        previous = None
    data = keep_this_week(data, previous, now)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(data, f, indent=1)
    if bucket:
        upload_scores(data, bucket)


if __name__ == "__main__":
    main()
