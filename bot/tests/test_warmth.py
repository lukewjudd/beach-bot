"""Warmth is scored on where the day's heading: a cool early morning on a hot day counts as a warm-day swim,
and a hot afternoon doesn't carry into an evening after a southerly change."""

from datetime import date

from conftest import make_forecast

from beach_bot.forecast import Context

WED = date(2026, 11, 4)


def day_of(temps):
    """A forecast whose temperatures on WED follow `temps` (hour -> degrees), 20 degrees otherwise."""

    def tweak(t, h):
        h["temperature_2m"] = temps.get(int(t[11:13]), 20.0) if t.startswith(WED.isoformat()) else 20.0
        return h

    return Context(make_forecast(WED, tweak)[0])


def test_a_cool_morning_on_a_hot_day_gets_the_days_warmth_less_three_degrees():
    ctx = day_of({6: 21, 7: 22, 8: 24, 9: 26, 10: 28, 11: 29, 12: 30, 13: 31})
    assert ctx.warmth(f"{WED}T06:00") == 28  # heading for 31 by 1pm, less 3


def test_a_morning_never_scores_cooler_than_it_is():
    ctx = day_of({7: 25, 13: 24})  # a day that cools off: the morning keeps its own 25
    assert ctx.warmth(f"{WED}T07:00") == 25


def test_a_southerly_change_ends_the_afternoons_warmth():
    hot = {12: 32, 13: 34, 14: 35, 15: 35, 16: 34, 17: 33, 18: 32}
    assert day_of(hot).warmth(f"{WED}T17:00") == 33  # still hot: its own 33 (the afternoon's 35 less 3 is 32)
    change = {**hot, 16: 26, 17: 23, 18: 22}  # the change came through at 4pm
    assert day_of(change).warmth(f"{WED}T17:00") == 23  # scored on the evening it actually is


def land_and_blend(land, blend):
    """A forecast whose WED blend follows `blend` and land cell follows `land` (hour -> degrees)."""

    def tweak(t, h):
        on = t.startswith(WED.isoformat())
        h["temperature_2m"] = blend.get(int(t[11:13]), 20.0) if on else 20.0
        h["temperature_2m_land"] = land.get(int(t[11:13]), 20.0) if on else 20.0
        return h

    return Context(make_forecast(WED, tweak)[0])


def test_a_sea_breeze_day_is_judged_on_the_land_high():
    # 7 Nov 2026: the land cell (by Observatory Hill) went to 28 while the land/sea blend only reached 24
    ctx = land_and_blend({7: 19, 10: 25, 13: 28}, {7: 17, 10: 22, 13: 24})
    assert ctx.warmth(f"{WED}T07:00") == 25  # heading for 28, less 3 (the blend alone gave 21)


def test_the_gap_between_land_and_blend_is_not_a_southerly_change():
    hot = {12: 30, 13: 31, 14: 31, 15: 30, 16: 29}
    ctx = land_and_blend(hot, {k: v - 5 for k, v in hot.items()})  # blend 5 under all afternoon
    assert ctx.warmth(f"{WED}T16:00") == 28  # the afternoon's 31 less 3, not the blend's 24


def test_cold_water_keeps_the_morning_on_the_blend():
    # A hot spring westerly heats the land, but an 18° sea is still an 18° swim: no land-high credit
    def tweak(t, h):
        on = t.startswith(WED.isoformat())
        h["temperature_2m"] = {7: 17, 13: 23}.get(int(t[11:13]), 20.0) if on else 20.0
        h["temperature_2m_land"] = {7: 19, 13: 29}.get(int(t[11:13]), 20.0) if on else 20.0
        h["sea_surface_temperature"] = 18.0
        return h

    ctx = Context(make_forecast(WED, tweak)[0])
    assert ctx.warmth(f"{WED}T07:00") == 20  # the blend's 23 less 3, not the land's 29 less 3
