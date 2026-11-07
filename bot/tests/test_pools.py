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


def test_a_cleaning_day_is_a_warning_when_the_window_isnt_known():
    monday, _ = score(*make_forecast(MON, with_tide(high_at_hour=12)), MON)
    tuesday, _ = score(*make_forecast(date(2026, 11, 3), with_tide(high_at_hour=12)), date(2026, 11, 3))

    ross_jones = pool(monday["am"], "Ross Jones Pool")  # cleaned for a few hours on Mondays
    assert ross_jones[0] < pool(tuesday["am"], "Ross Jones Pool")[0]
    assert "may be shut for cleaning (Mondays)" in ross_jones[2]


def test_ruled_out_spots_say_why():
    def huge(t, h):
        h["wave_height"] = 3.5
        return h

    sessions, _ = score(*make_forecast(WED, with_tide(high_at_hour=7, then=huge)), WED)

    assert sessions["am"].ruled_out["Mahon Pool"] == "waves over the walls"


def test_a_pool_can_make_a_session_worth_it_when_the_beaches_are_blown_out():
    def onshore_gale(t, h):
        h.update(wind_speed_10m=18.0, wind_direction_10m=90, wind_gusts_10m=30.0, wave_height=1.3)
        return h

    hours, sun = make_forecast(WED, with_tide(high_at_hour=14, then=onshore_gale))
    sessions, _ = score(hours, sun, WED)

    am = sessions["am"]
    best_ocean = max(sc for sc, b, _ in am.swim if not b.harbour)
    assert best_ocean < am.best_pool[0]
    assert am.is_good == (am.best >= 80)


def test_harbour_beaches_stay_swimmable_when_the_ocean_is_too_big():
    def big_swell(t, h):
        h.update(wave_height=2.8, swell_wave_direction=135, swell_wave_period=11, wind_direction_10m=200)
        return h

    sessions, _ = score(*make_forecast(WED, big_swell), WED)
    am = sessions["am"]
    swimmable = {b.name for _, b, _ in am.swim}

    assert "Bronte" not in swimmable  # ~2.5m+ at an exposed beach
    assert {"Shark Beach", "Parsley Bay", "Murray Rose Pool"} <= swimmable


def test_pools_feel_the_same_breeze_as_their_beach():
    def breeze(direction):
        def tweak(t, h):
            h.update(wind_speed_10m=18, wind_direction_10m=direction, wind_gusts_10m=26)
            return h

        return tweak

    onshore, ctx = score(*make_forecast(WED, breeze(60)), WED)  # NE sea breeze: onshore at Coogee
    offshore, _ = score(*make_forecast(WED, breeze(270)), WED)  # westerly: offshore

    assert pool(onshore["pm"], "Ross Jones Pool")[0] < pool(offshore["pm"], "Ross Jones Pool")[0]

    # The Wind bar is the pool's own wind points, so it shows the sea breeze too
    from beach_bot.beaches import POOLS
    from beach_bot.forecast import Context
    from beach_bot.sessions import report

    rj = next(p for p in POOLS if p.name == "Ross Jones Pool")
    on_h, off_h = make_forecast(WED, breeze(60))[0], make_forecast(WED, breeze(270))[0]
    on_bar = report(onshore["pm"], on_h, ctx, {}, WED, rj)["Wind"]
    off_bar = report(offshore["pm"], off_h, Context(off_h), {}, WED, rj)["Wind"]
    assert on_bar < off_bar


def test_pools_are_rated_on_calm_and_tide():
    from beach_bot.beaches import POOLS
    from beach_bot.sessions import report

    hours, sun = make_forecast(WED, with_tide(18))  # high tide mid-evening
    sessions, ctx = score(hours, sun, WED)
    mahon = next(p for p in POOLS if p.name == "Mahon Pool")  # likes mid to high tide
    rows = report(sessions["pm"], hours, ctx, {}, WED, mahon)

    assert {"Calm in the pool", "Tide"} <= rows.keys()
    assert rows["Tide"] >= 8
