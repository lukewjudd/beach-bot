"""Command line: `beach-bot` (dry run), `beach-bot --sync` (calendar + bucket)."""

import argparse
import json
import os
from datetime import datetime, timedelta

from .beaches import EASTERN, REGIONS
from .calendar import event_body, sync
from .config import DAYS_AHEAD, TZ
from .export import export_scores, keep_this_week, load_previous, upload_scores
from .forecast import Context, load_data
from .sessions import build_sessions, score_session


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", action="store_true", help="write to Google Calendar and upload to the bucket")
    ap.add_argument("--all", action="store_true", help="print the full report for every session")
    ap.add_argument("--json", metavar="DIR", help="also write each region's scores-<region>.json here")
    ap.add_argument("--region", help="just this region (eastern, northern)")
    args = ap.parse_args()

    now = datetime.now(TZ)
    for region in REGIONS:
        if args.region and region.id != args.region:
            continue
        print(f"== {region.name}")
        run_region(region, now, args)


def run_region(region, now, args):
    hours, sun, beachwatch = load_data(region)
    ctx = Context(hours)
    # The site shows this week and next, Monday to Sunday; only sessions the swell forecast reaches get scored
    # (missing swell would read as dead calm)
    next_sunday = now.date() + timedelta(days=13 - now.weekday())
    days = [now.date() + timedelta(days=o) for o in range((next_sunday - now.date()).days + 1)]
    days = [d for d in days if d.isoformat() in sun]
    sessions = [
        s
        for s in build_sessions(hours, sun, now, days, region)
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

    # Each region has its own calendar; one without an id set yet just isn't posted
    cal = os.environ.get(region.calendar_env)
    posted = sync(soon, hours, ctx, beachwatch, now, cal) if args.sync and cal else None
    if args.sync and not cal:
        print(f"no {region.calendar_env} set: {region.name} isn't posted to a calendar")
    data = export_scores(sessions, hours, ctx, beachwatch, now, posted, sun, region)

    name = f"scores-{region.id}.json"
    path = os.path.join(args.json, name) if args.json else None
    bucket = os.environ.get("BEACH_BUCKET") if args.sync else None
    if bucket:
        previous = load_previous(bucket, name)
    elif path and os.path.exists(path):  # local runs carry forward from the last local file
        with open(path) as f:
            previous = json.load(f)
    else:
        previous = None
    data = keep_this_week(data, previous, now)
    if path:
        with open(path, "w") as f:
            json.dump(data, f, indent=1)
    if bucket:
        upload_scores(data, bucket, name)
        if region is EASTERN:  # the site's old address, for anyone with it open or bookmarked
            upload_scores(data, bucket, "scores.json")


if __name__ == "__main__":
    main()
