"""Randwick's lifeguard reports (R-LG1): the feed as it stood on the morning of Mon 9 Nov 2026, with Coogee and
Maroubra closed in a 2m south swell and Clovelly's report still Sunday's."""

from datetime import date, datetime
from pathlib import Path

from conftest import make_forecast, score

from beach_bot import forecast
from beach_bot.config import TZ
from beach_bot.export import lifeguard_log
from beach_bot.forecast import Reports, parse_lifeguards

MON, TUE = date(2026, 11, 9), date(2026, 11, 10)
FEED = (Path(__file__).parent / "fixtures" / "lifeguards-2026-11-09.xml").read_text()


def test_reads_todays_reports_and_drops_a_stale_one():
    reps = parse_lifeguards(FEED, MON)

    assert set(reps) == {"Coogee Beach", "Maroubra Beach"}  # Clovelly's is from Sunday
    m = reps["Maroubra Beach"]
    assert m["closed"] and m["status"] == "Closed"
    assert m["waves"] == "+2m" and m["waves_m"] == 2.0
    assert m["water_c"] == 20.0 and m["rips"] == "Dangerous"
    assert m["stingers"] == "none"
    assert m["time"] == "2026-11-09T06:48+11:00"
    assert m["description"].startswith("Large south swell")


def test_closed_beaches_are_out_today_but_their_pools_are_not():
    reports = Reports({}, parse_lifeguards(FEED, MON))
    sessions, _ = score(*make_forecast(MON), MON, reports)

    for s in sessions.values():
        assert s.ruled_out["Coogee"] == "closed by lifeguards"
        assert s.ruled_out["Maroubra"] == "closed by lifeguards"
        assert "Clovelly" not in s.ruled_out
        assert {"Giles Baths", "Mahon Pool"} <= {p.name for _, p, _ in s.pools}


def test_a_closure_is_only_for_the_day_it_was_reported():
    hours, sun = make_forecast(TUE, lookback_days=5)
    reports = Reports({}, parse_lifeguards(FEED, MON))
    sessions, _ = score(hours, sun, TUE, reports, now=datetime(2026, 11, 9, 9, tzinfo=TZ))

    assert all("Coogee" not in s.ruled_out for s in sessions.values())


def ne_blow(t, h):
    h.update(wind_direction_10m=45, wind_speed_10m=24.0, wind_gusts_10m=30.0)
    return h


def maroubra(sessions):
    return next((sc, notes) for sc, b, notes in sessions["md"].swim if b.name == "Maroubra")


def open_with(bluebottles):
    rep = parse_lifeguards(FEED, MON)["Maroubra Beach"]
    rep.update(closed=False, status="Open", stingers=forecast._stingers(bluebottles), bluebottles=bluebottles)
    return Reports({}, {"Maroubra Beach": rep})


def test_none_sighted_clears_the_wind_based_bluebottle_guess():
    guess, _ = score(*make_forecast(MON, ne_blow), MON)
    told, _ = score(*make_forecast(MON, ne_blow), MON, open_with("None sighted"))

    assert "bluebottles possible" in maroubra(guess)[1]
    assert "bluebottles possible" not in maroubra(told)[1]
    assert maroubra(told)[0] > maroubra(guess)[0]


def test_bluebottles_sighted_count_whatever_the_wind():
    calm, _ = score(*make_forecast(MON), MON)
    seen, _ = score(*make_forecast(MON), MON, open_with("Some sighted"))

    assert "bluebottles reported" in maroubra(seen)[1]
    assert maroubra(seen)[0] < maroubra(calm)[0]


def test_reading_the_fields():
    assert forecast._stingers("None sighted") == "none"
    assert forecast._stingers("Some sighted") == "seen"
    assert forecast._stingers("") is None and forecast._stingers("Unknown") is None
    assert forecast._number("18 C") == 18.0
    assert forecast._number("0.5-1m", largest=True) == 1.0


def test_feed_down_means_no_reports(monkeypatch):
    def boom(*a, **k):
        raise ConnectionError("feed down")

    monkeypatch.setattr(forecast.requests, "get", boom)
    assert forecast.lifeguard_reports(MON) == {}


def test_the_log_keeps_each_morning_and_lets_old_ones_go():
    now = datetime(2026, 11, 9, 9, tzinfo=TZ)
    previous = {
        "lifeguard_log": [
            {"date": "2026-11-08", "id": "swim-clovelly", "reported_m": 2.0, "modelled_m": 0.8},
            {"date": "2026-01-01", "id": "swim-coogee", "reported_m": 1.0, "modelled_m": 1.0},
        ]
    }
    data = {
        "lifeguards": {
            "swim-coogee": {"time": "2026-11-09T08:35+11:00", "waves": "2m", "waves_m": 2.0, "modelled_m": 0.9}
        }
    }
    log = lifeguard_log(data, previous, now)

    assert [(r["date"], r["id"]) for r in log] == [("2026-11-08", "swim-clovelly"), ("2026-11-09", "swim-coogee")]
    assert log[1]["reported_m"] == 2.0 and log[1]["modelled_m"] == 0.9


def test_todays_water_is_the_lifeguards_middle_reading_and_later_days_keep_the_model():
    from beach_bot.beaches import EASTERN, NORTHERN
    from beach_bot.export import export_scores

    hours, sun = make_forecast(MON, lookback_days=3)
    reps = {name: {"water_c": c} for name, c in (("Coogee Beach", 17), ("Clovelly Beach", 19), ("Maroubra Beach", 20))}
    model = hours["2026-11-09T09:00"]["sea_surface_temperature"]

    assert forecast.measured_water(hours, EASTERN, reps, MON) == 19
    assert hours["2026-11-09T09:00"]["sea_surface_temperature"] == 19
    assert hours["2026-11-09T09:00"]["sea_surface_temperature_model"] == model
    assert hours["2026-11-08T09:00"]["sea_surface_temperature"] == model  # other days keep the model
    # Randwick's lifeguards don't speak for the northern beaches
    assert forecast.measured_water({}, NORTHERN, reps, MON) is None

    sessions, ctx = score(hours, sun, MON)
    data = export_scores(list(sessions.values()), hours, ctx, {}, datetime(2026, 11, 9, 5, tzinfo=TZ), sun=sun)
    today = [s["conditions"] for s in data["sessions"] if s["date"] == "2026-11-09"]
    assert today and all(c["water_c"] == 19 and c["water_measured"] for c in today)
