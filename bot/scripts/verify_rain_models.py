"""How well each weather model forecasts Sydney's rain 1 and 2 days ahead, and the bot's eight-model vote (R-RF1).

Forecasts as they stood a day or two before, from Open-Meteo's previous-runs archive, against Sydney Airport's
daily gauge (BOM station 066037, via NOAA's GHCN-Daily copy: BOM's own site turns away scripts). Scored on the
bot's own question, 10mm and 20mm in a 9am-to-9am day. Results: research/rain-forecast-verification.md.

  uv run python scripts/verify_rain_models.py [start end]
"""

import csv
import io
import sys
from collections import defaultdict

import requests

from beach_bot.config import FORECAST_RAIN_MODELS
from beach_bot.forecast import consensus_rain, rain_day

POINT = (-33.95, 151.17)  # Sydney Airport
GAUGE = "ASN00066037"


def gauge(start, end):
    r = requests.get(
        "https://www.ncei.noaa.gov/access/services/data/v1",
        params={
            "dataset": "daily-summaries",
            "stations": GAUGE,
            "startDate": start,
            "endDate": end,
            "dataTypes": "PRCP",
            "format": "csv",
            "units": "metric",
        },
        timeout=180,
    )
    r.raise_for_status()
    return {row["DATE"]: float(row["PRCP"]) for row in csv.DictReader(io.StringIO(r.text)) if row["PRCP"]}


def forecasts(model, start, end):
    r = requests.get(
        "https://previous-runs-api.open-meteo.com/v1/forecast",
        params={
            "latitude": POINT[0],
            "longitude": POINT[1],
            "models": model,
            "timezone": "Australia/Sydney",
            "hourly": "precipitation_previous_day1,precipitation_previous_day2",
            "start_date": start,
            "end_date": end,
        },
        timeout=300,
    )
    r.raise_for_status()
    h = r.json()["hourly"]
    return {
        lead: {t: v for t, v in zip(h["time"], h[f"precipitation_previous_day{lead}"], strict=True) if v is not None}
        for lead in (1, 2)
    }


def daily(hourly):
    out = defaultdict(float)
    for t, v in hourly.items():
        out[rain_day(t)] += v
    return out


def score(name, f, obs, days, thr):
    hit = sum(f[d] >= thr and obs[d] >= thr for d in days)
    miss = sum(f[d] < thr <= obs[d] for d in days)
    false = sum(f[d] >= thr > obs[d] for d in days)
    print(
        f"  {thr:>2}mm  {name:<24} caught {hit / max(1, hit + miss):4.0%}"
        f"  false alarms {false / max(1, hit + false):4.0%}  score {hit / max(1, hit + miss + false):.2f}"
    )


def main():
    start, end = sys.argv[1:3] if len(sys.argv) > 2 else ("2024-08-10", "2026-10-29")
    obs = gauge(start, end)
    runs = {m: forecasts(m, start, end) for m in ("best_match", *FORECAST_RAIN_MODELS)}
    for lead in (1, 2):
        each = {m: daily(runs[m][lead]) for m in runs}
        vote = daily(consensus_rain({m: runs[m][lead] for m in FORECAST_RAIN_MODELS}))
        days = sorted(d for d in obs if d in vote and d in each["best_match"])
        print(f"{lead} day ahead: {len(days)} days, {sum(obs[d] >= 10 for d in days)} with 10mm+ at the gauge")
        for thr in (10, 20):
            for m, f in each.items():
                score(m, f, obs, [d for d in days if d in f], thr)
            score("eight-model vote", vote, obs, days, thr)


if __name__ == "__main__":
    main()
