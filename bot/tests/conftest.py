"""Builds forecasts in the same shape load_data() returns, so tests run the real scoring end to end."""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from beach_bot.config import TZ
from beach_bot.forecast import Context
from beach_bot.sessions import build_sessions, score_session

# A calm, warm, clean-water hour: the kind of conditions that should be worth going for
NICE = {
    "temperature_2m": 26.0,
    "precipitation": 0.0,
    "precipitation_probability": 0,
    "wind_speed_10m": 5.0,
    "wind_direction_10m": 270,  # westerly: offshore on the east-facing beaches
    "wind_gusts_10m": 12.0,
    "cloud_cover": 5,
    "uv_index": 6,
    "wave_height": 0.6,
    "swell_wave_height": 0.5,
    "swell_wave_direction": 170,  # small southerly
    "swell_wave_period": 9.0,
    "sea_surface_temperature": 23.0,
    "sea_level_height_msl": 0.2,
}


def make_forecast(day: date, tweak=lambda t, h: h, lookback_days=4):
    """Hourly data from `lookback_days` before `day` to the end of `day`. `tweak(time_key, hour)` adjusts any hour."""
    hours = {}
    start = datetime.combine(day - timedelta(days=lookback_days), datetime.min.time())
    for i in range((lookback_days + 1) * 24):
        t = (start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00")
        hours[t] = tweak(t, dict(NICE))
    sun = {
        (day - timedelta(days=d)).isoformat(): (
            datetime.combine(day - timedelta(days=d), datetime.min.time()).replace(hour=5, minute=50),
            datetime.combine(day - timedelta(days=d), datetime.min.time()).replace(hour=19, minute=30),
        )
        for d in range(lookback_days + 1)
    }
    return hours, sun


def score(hours, sun, day, beachwatch=None, now=None, region=None):
    """Runs the real pipeline for one day and returns its sessions keyed by slot ('am', 'md', 'pm')."""
    now = now or datetime.combine(day, datetime.min.time()).replace(hour=3, tzinfo=TZ)
    ctx = Context(hours)
    sessions = build_sessions(hours, sun, now, days=[day], **({"region": region} if region else {}))
    for s in sessions:
        score_session(s, hours, ctx, {} if beachwatch is None else beachwatch, now.date())
    return {s.slot: s for s in sessions}, ctx


@pytest.fixture
def real_forecast():
    """The live forecast saved on Mon 2 Nov 2026: a glassy but cool morning, then a gusty NE sea breeze."""
    f = json.loads((Path(__file__).parent / "fixtures" / "forecast-2026-11-02.json").read_text())
    sun = {d: (datetime.fromisoformat(a), datetime.fromisoformat(b)) for d, (a, b) in f["sun"].items()}
    return f["hours"], sun, f["beachwatch"], datetime.fromisoformat(f["now"])
