from datetime import date

from conftest import make_forecast, score

from beach_bot.calendar import event_body
from beach_bot.export import export_scores
from beach_bot.forecast import Context
from beach_bot.sessions import build_sessions, out_of_10, score_session

WED = date(2026, 11, 4)


def test_calm_warm_morning_is_worth_it_at_clovelly():
    hours, sun = make_forecast(WED)
    sessions, ctx = score(hours, sun, WED)

    am = sessions["am"]
    assert am.is_good
    assert am.best_swim[1].name == "Clovelly"
    title, _ = event_body(am, hours, ctx, {}, WED)
    assert f"{out_of_10(am.best_swim[0])}/10 🏖️ Clovelly" in title


def test_a_chilly_first_hour_doesnt_sink_a_good_morning():
    def cold_dawn(t, h):
        if t.startswith(WED.isoformat()) and t[11:13] == "06":
            h["temperature_2m"] = 15.0  # weekday mornings are only 6-9am, so one cold hour is enough to test
        return h

    hours, sun = make_forecast(WED, cold_dawn)
    sessions, _ = score(hours, sun, WED)

    assert sessions["am"].is_good
    assert sessions["am"].windows["Clovelly"][0][11:13] == "07"


def test_heavy_rain_the_day_before_rules_out_clovelly():
    def downpour(t, h):
        if t.startswith("2026-11-03") and 6 <= int(t[11:13]) < 12:
            h["precipitation"] = 5.0  # 30mm over the morning, past Clovelly's 20mm limit
        return h

    hours, sun = make_forecast(WED, downpour)
    sessions, _ = score(hours, sun, WED)

    assert "Clovelly" not in [b.name for _, b, _ in sessions["am"].swim]


def test_a_gusty_onshore_wind_is_not_worth_it():
    def blowing(t, h):
        h.update(wind_speed_10m=35.0, wind_direction_10m=45, wind_gusts_10m=55.0)
        return h

    hours, sun = make_forecast(WED, blowing)
    sessions, _ = score(hours, sun, WED)

    assert not sessions["am"].is_good
    assert not sessions["pm"].is_good


def test_cool_water_is_noted_but_not_penalised():
    def water(temp):
        def tweak(t, h):
            h["sea_surface_temperature"] = temp
            return h

        return tweak

    warmish, _ = score(*make_forecast(WED, water(21.0)), WED)
    cool, _ = score(*make_forecast(WED, water(18.5)), WED)

    assert cool["am"].best_swim[0] == warmish["am"].best_swim[0]
    assert "fresh water" in cool["am"].best_swim[2]


def test_the_site_and_calendar_agree_on_what_is_worth_it(real_forecast):
    hours, sun, beachwatch, now = real_forecast
    ctx = Context(hours)
    sessions = build_sessions(hours, sun, now)
    for s in sessions:
        score_session(s, hours, ctx, beachwatch, now.date())

    data = export_scores(sessions, hours, ctx, beachwatch, now)

    for sess, exported in zip(sessions, data["sessions"], strict=True):
        assert exported["posted"] == bool(sess.is_good)
        assert exported["posted"] == (exported["lead"]["rating"] >= 8)


def test_monday_2_nov_was_not_worth_it(real_forecast):
    hours, sun, beachwatch, now = real_forecast
    ctx = Context(hours)
    sessions = build_sessions(hours, sun, now)
    for s in sessions:
        score_session(s, hours, ctx, beachwatch, now.date())
    monday = {s.slot: s for s in sessions if s.day == now.date()}

    # Glassy but only 16-19°: Clovelly's the pick, but it's a 6
    assert monday["am"].best_swim[1].name == "Clovelly"
    assert out_of_10(monday["am"].best_swim[0]) == 6
    assert not monday["am"].is_good
    # NE sea breeze gusting past 40 km/h under full cloud
    assert not monday["pm"].is_good
