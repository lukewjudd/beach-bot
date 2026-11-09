"""Replays beach_bot's scoring over past forecasts to see when the 8/10+ sessions would have been.

  beach-backtest                     # 2023-01-01 to yesterday
  beach-backtest 2024-10-01          # from a given date

Uses Open-Meteo's archived forecasts (what the bot would have seen at the time) and the same
offshore marine point. Beachwatch has no history, so water quality falls back to the rain rules.
Writes every session to backtest.csv.
"""

import csv
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from .beaches import EASTERN
from .forecast import Context, fetch_json, fetch_weather
from .sessions import build_sessions, conditions, headline, lead_kind, out_of_10, score_session

ICONS = {"swim": "🏖️", "pool": "🏊", "surf": "🏄"}  # terminal output only


def load_history(start, end):
    lead = (start - timedelta(days=4)).isoformat()  # look-back for rain and NE wind rules
    wx = fetch_weather(
        "https://historical-forecast-api.open-meteo.com/v1/forecast",
        {
            "latitude": EASTERN.forecast_point[0],
            "longitude": EASTERN.forecast_point[1],
            "hourly": "temperature_2m,precipitation,precipitation_probability,wind_speed_10m,"
            "wind_direction_10m,wind_gusts_10m,cloud_cover,uv_index,weather_code,cape",
            "daily": "sunrise,sunset",
            "timezone": "Australia/Sydney",
            "start_date": lead,
            "end_date": end.isoformat(),
        },
    )
    sea = fetch_json(
        "https://marine-api.open-meteo.com/v1/marine",
        {
            "latitude": EASTERN.marine_point[0],
            "longitude": EASTERN.marine_point[1],
            "cell_selection": "sea",
            "hourly": "wave_height,swell_wave_height,swell_wave_direction,swell_wave_period,"
            "secondary_swell_wave_height,secondary_swell_wave_direction,secondary_swell_wave_period,"
            "wind_wave_height,wind_wave_direction,wind_wave_period,wave_period,"
            "sea_surface_temperature,sea_level_height_msl",
            "timezone": "Australia/Sydney",
            "start_date": lead,
            "end_date": end.isoformat(),
        },
    )
    hours = {}
    for i, t in enumerate(wx["hourly"]["time"]):
        row = {k: v[i] for k, v in wx["hourly"].items() if k != "time"}
        if row["wind_speed_10m"] is not None and row["temperature_2m"] is not None:
            hours[t] = row
    for i, t in enumerate(sea["hourly"]["time"]):
        if t in hours:
            hours[t].update({k: v[i] for k, v in sea["hourly"].items() if k != "time"})
    sun = {
        d: (datetime.fromisoformat(r), datetime.fromisoformat(s))
        for d, r, s in zip(wx["daily"]["time"], wx["daily"]["sunrise"], wx["daily"]["sunset"], strict=True)
        if r and s
    }
    return hours, sun


def main():
    start = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date(2023, 1, 1)
    end = date.today() - timedelta(days=1)
    hours, sun = load_history(start, end)
    ctx = Context(hours)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    days = [d for d in days if d.isoformat() in sun]
    sessions = build_sessions(hours, sun, None, days=days)

    rows = []
    for s in sessions:
        score_session(s, hours, ctx, {}, date.min)  # no Beachwatch history
        swim, surf = s.best_swim, (s.surf[0] if s.surf else None)
        best = s.best
        c = conditions(s, hours)
        rows.append(
            {
                "date": s.day.isoformat(),
                "dow": f"{s.day:%a}",
                "slot": s.slot,
                "rating": out_of_10(best),
                "score": best,
                "posted": s.is_good,
                "kind": lead_kind(s),
                "spot": headline(s) or "",
                "swim": swim[1].name if swim else "",
                "swim_score": swim[0] if swim else "",
                "surf": surf[1].name if surf else "",
                "surf_score": surf[0] if surf else "",
                "air": round(c["air"]),
                "water": round(c["sea"]) if c["sea"] else "",
                "wind": f"{c['wind_dir']} {c['wind']:.0f}/{c['gust']:.0f}",
                "swell": f"{c['hs']:.1f}m {c['swell_dir']} {c['period']:.0f}s",
            }
        )
    with open("backtest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    posted = [r for r in rows if r["posted"]]
    print(
        f"{len(rows)} sessions from {start} to {end}; {len(posted)} would have posted "
        f"({len(posted) / len(rows):.1%}), {sum(r['rating'] >= 9 for r in posted)} with 🔥\n"
    )

    by_month = defaultdict(Counter)
    for r in posted:
        by_month[r["date"][:7]]["all"] += 1
        by_month[r["date"][:7]]["fire"] += r["rating"] >= 9
    print("Posted per month, averaged over years (🏖️ beach / 🏊 pool / 🏄 surf):")
    months = sorted({r["date"][:7] for r in rows})
    for m in sorted({m[5:] for m in months}):
        ms = [x for x in months if x[5:] == m]
        n = {k: sum(1 for r in posted if r["date"][5:7] == m and r["kind"] == k) / len(ms) for k in ICONS}
        bars = "".join(c * round(n[k]) for k, c in (("swim", "▓"), ("pool", "▒"), ("surf", "░")))
        counts = "  ".join(f"{ICONS[k]} {n[k]:4.1f}" for k in ICONS)
        print(f"  {datetime.strptime(m, '%m'):%b}  {counts}  {bars}")

    print("\nWinning spot on posted sessions:")
    for name, n in Counter(f"{ICONS[r['kind']]} {r['spot']}" for r in posted).most_common():
        print(f"  {n:4}  {name}")
    print(
        "\nSlots:",
        dict(Counter(f"{'weekend' if r['dow'] in ('Sat', 'Sun') else 'weekday'} {r['slot']}" for r in posted)),
    )

    for kind in ICONS:
        print(f"\nTop 12 {kind} sessions:")
        for r in sorted((r for r in rows if r["kind"] == kind), key=lambda r: -r["score"])[:12]:
            print(
                f"  {r['rating']}/10 {r['score']:>3}  {r['dow']} {r['date']} {r['slot']}  {r['spot']:<18} "
                f"air {r['air']}° water {r['water']}°  wind {r['wind']}  swell {r['swell']}"
            )


if __name__ == "__main__":
    main()
