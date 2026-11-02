"""Command line: `beach-bot` (dry run), `beach-bot --sync` (calendar + bucket)."""

import argparse
import json
import os
from datetime import datetime

from .calendar import event_body, sync
from .config import TZ
from .export import export_scores, upload_scores
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
    sessions = build_sessions(hours, sun, now)
    for sess in sessions:
        score_session(sess, hours, ctx, beachwatch, now.date())

    for sess in sessions:
        flag = "✅" if sess.is_good else "  "
        swim = sess.best_swim
        surf = sess.surf[0] if sess.surf else None
        print(f"{flag} {sess.start:%a %d %b} {sess.slot}  "
              f"swim: {swim[1].name if swim else '-'} {swim[0] if swim else ''}  "
              f"surf: {surf[1].name + ' ' + str(surf[0]) if surf else '-'}")
        if sess.is_good or args.all:
            title, desc = event_body(sess, hours, ctx, beachwatch, now.date())
            print(f"     → {title}")
            print("       " + desc.replace("\n", "\n       "))

    data = export_scores(sessions, hours, ctx, beachwatch, now)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(data, f, indent=1)
    if args.sync:
        sync(sessions, hours, ctx, beachwatch, now)
        if os.environ.get("BEACH_BUCKET"):
            upload_scores(data, os.environ["BEACH_BUCKET"])


if __name__ == "__main__":
    main()
