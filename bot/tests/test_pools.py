import math
from datetime import date, datetime

from conftest import make_forecast, score

WED = date(2026, 11, 4)
MON = date(2026, 11, 2)


def with_tide(high_at_hour, then=lambda t, h: h):
    """Semi-diurnal tide (12.4h cycle) with a high at `high_at_hour` on the scored day."""

    def tweak(t, h):
        hours_from_high = (datetime.fromisoformat(t) - datetime.fromisoformat(t[:10] + "T00:00")).total_seconds() / 3600
        h["sea_level_height_msl"] = 0.6 * math.cos(2 * math.pi * (hours_from_high - high_at_hour) / 12.42)
        return then(t, h)

    return tweak


def pool(session, name):
    return next((x for x in session.pools if x[1].name == name), None)


def test_pools_score_on_a_calm_day():
    hours, sun = make_forecast(WED, with_tide(high_at_hour=12))
    sessions, _ = score(hours, sun, WED)

    assert pool(sessions["am"], "Giles Baths")[0] >= 80


def test_big_swell_at_high_tide_washes_over_the_walls():
    def big(t, h):
        h["wave_height"] = 2.8
        return h

    hours, sun = make_forecast(WED, with_tide(high_at_hour=7, then=big))
    sessions, _ = score(hours, sun, WED)

    assert pool(sessions["am"], "Mahon Pool") is None
    assert pool(sessions["am"], "Bondi Icebergs") is None


def test_wylies_is_shut_before_7am():
    hours, sun = make_forecast(WED, with_tide(high_at_hour=12))
    sessions, _ = score(hours, sun, WED)

    first, _ = sessions["am"].windows["Wylie's Baths"]
    assert first[11:13] >= "07"


def test_cleaning_days_close_pools():
    hours, sun = make_forecast(MON, with_tide(high_at_hour=12))
    sessions, _ = score(hours, sun, MON)

    assert pool(sessions["am"], "Ross Jones Pool") is None  # drained on Mondays
    assert pool(sessions["am"], "Giles Baths") is not None


def test_a_pool_can_make_a_session_worth_it_when_the_beaches_are_blown_out():
    def onshore_gale(t, h):
        h.update(wind_speed_10m=18.0, wind_direction_10m=90, wind_gusts_10m=30.0, wave_height=1.3)
        return h

    hours, sun = make_forecast(WED, with_tide(high_at_hour=14, then=onshore_gale))
    sessions, _ = score(hours, sun, WED)

    am = sessions["am"]
    assert am.best_swim[0] < am.best_pool[0]
    assert am.is_good == (am.best >= 80)
