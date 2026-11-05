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
