from datetime import date, datetime

from conftest import make_forecast, score

from beach_bot.beaches import BEACHES
from beach_bot.calendar import event_body, fingerprint
from beach_bot.config import TZ
from beach_bot.export import export_scores
from beach_bot.forecast import Context
from beach_bot.sessions import build_sessions, out_of_10, report, score_session

WED = date(2026, 11, 4)


def test_calm_warm_morning_is_worth_it_at_clovelly():
    hours, sun = make_forecast(WED)
    sessions, ctx = score(hours, sun, WED)

    am = sessions["am"]
    assert am.is_good
    assert am.best_swim[1].name == "Clovelly"
    title, _ = event_body(am, hours, ctx, {}, WED)
    assert f"{out_of_10(am.best_swim[0])}/10 Clovelly" in title


def test_a_chilly_first_hour_doesnt_sink_a_good_morning():
    def cold_dawn(t, h):
        if t.startswith(WED.isoformat()) and t[11:13] == "06":
            h["temperature_2m"] = 15.0
            h["cloud_cover"] = 95  # and grey: still the worst hour, even with the day's warmth credited
        return h

    hours, sun = make_forecast(WED, cold_dawn)
    sessions, _ = score(hours, sun, WED)

    assert sessions["am"].is_good
    assert sessions["am"].windows["Clovelly"][0][11:13] == "07"


def test_heavy_rain_the_day_before_rules_out_clovelly():
    def downpour(t, h):
        if t.startswith("2026-11-03") and 6 <= int(t[11:13]):
            h["precipitation"] = 5.0  # 90mm from 6am on: every morning hour is past Clovelly's 20mm limit
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
    assert "cold water" in cool["am"].best_swim[2]


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


def test_conditions_are_per_spot_where_they_should_be():
    # A NE breeze and a 1m E swell: onshore and rough at Maroubra, sheltered inside Clovelly
    def ne_breeze(t, h):
        h.update(wind_speed_10m=22.0, wind_direction_10m=45, wind_gusts_10m=30.0, wave_height=1.0)
        h["swell_wave_direction"] = 90
        return h

    hours, sun = make_forecast(WED, ne_breeze)
    sessions, ctx = score(hours, sun, WED)
    am = sessions["am"]
    beach = {b.name: b for _, b, _ in am.swim}
    clovelly = report(am, hours, ctx, {}, WED, beach["Clovelly"])
    maroubra = report(am, hours, ctx, {}, WED, beach["Maroubra"])

    assert clovelly["Calm water"] > maroubra["Calm water"]
    assert clovelly["Wind"] > maroubra["Wind"]  # cross-shore at Clovelly, onshore at Maroubra
    assert "Water temp" not in clovelly  # one sea temperature for the coast: a summary stat, not a spot row


def test_beachwatch_wins_over_the_rain_rules_for_water_quality():
    def a_little_rain(t, h):
        if t.startswith("2026-11-02"):
            h["precipitation"] = 0.3  # ~7mm two days before: Coogee's Poor-grade rule would mark it down
        return h

    hours, sun = make_forecast(WED, a_little_rain)
    sessions, ctx = score(hours, sun, WED)
    am = sessions["am"]
    coogee = next(b for b in BEACHES if b.name == "Coogee")  # ruled out for swimming by the rain, still reported

    assert report(am, hours, ctx, {}, WED, coogee)["Water quality"] < 10  # no Beachwatch forecast
    assert report(am, hours, ctx, {"Coogee Beach": "Unlikely"}, WED, coogee)["Water quality"] == 10


def test_started_sessions_keep_their_last_call_until_the_week_is_out():
    from datetime import datetime

    from beach_bot.config import TZ
    from beach_bot.export import keep_this_week

    now = datetime(2026, 11, 4, 18, 0, tzinfo=TZ)  # Wednesday evening
    fresh = {
        "sessions": [
            {
                "key": "beach20261104pm",
                "date": "2026-11-04",
                "start": "2026-11-04T17:00:00+11:00",
                "lead": {"rating": 9},
            }
        ]
    }
    previous = {
        "sessions": [
            {
                "key": "beach20261026am",
                "date": "2026-10-26",
                "start": "2026-10-26T05:50:00+11:00",
                "lead": {"rating": 5},
            },
            {
                "key": "beach20261102am",
                "date": "2026-11-02",
                "start": "2026-11-02T05:52:00+11:00",
                "lead": {"rating": 4},
            },
            {
                "key": "beach20261104pm",
                "date": "2026-11-04",
                "start": "2026-11-04T17:00:00+11:00",
                "lead": {"rating": 3},
            },
        ]
    }
    keys = {s["key"]: s for s in keep_this_week(fresh, previous, now)["sessions"]}

    assert "beach20261026am" not in keys  # last week: gone
    assert keys["beach20261102am"]["frozen"]  # Monday this week: kept
    assert keys["beach20261104pm"]["lead"]["rating"] == 3  # started an hour ago: the call it had, not a rescore


def test_harbour_beaches_never_lead_or_make_a_session_worth_it():
    # A big swell rules the ocean beaches out; the harbour stays calm but must not post on its own
    def big_swell(t, h):
        h.update(wave_height=5.0, swell_wave_direction=135, swell_wave_period=12, wind_direction_10m=200)
        return h

    sessions, _ = score(*make_forecast(WED, big_swell), WED)
    am = sessions["am"]

    assert any(b.harbour for _, b, _ in am.swim)  # still scored, for the site
    assert am.best_swim is None or not am.best_swim[1].harbour
    harbour_best = max(sc for sc, b, _ in am.swim if b.harbour)
    assert am.best < harbour_best  # a calm harbour doesn't make the session worth it


def test_the_event_title_is_just_the_call():
    hours, sun = make_forecast(WED)
    sessions, ctx = score(hours, sun, WED)
    title, _ = event_body(sessions["am"], hours, ctx, {}, WED)
    assert title.endswith("Clovelly · Wed morning")
    assert "km/h" not in title and "°" not in title  # wind and temperatures live in the description


def test_events_are_only_rewritten_when_the_call_changes():
    hours, sun = make_forecast(WED)
    sessions, ctx = score(hours, sun, WED)
    title, desc = event_body(sessions["am"], hours, ctx, {}, WED)
    body = {
        "summary": title,
        "description": desc,
        "start": {"dateTime": "2026-11-04T06:00:00+11:00"},
        "end": {"dateTime": "2026-11-04T10:00:00+11:00"},
        "location": "Clovelly, NSW",
    }
    later = {**body, "description": desc.replace("Last changed", "Last changed (an hour on)")}
    wobble = {**body, "description": desc.replace("Weather", "Weather (a point either way)")}
    # 6 Nov: the sea warmed to 20 overnight and "cold water" dropped off the top 3 spots' notes
    notes = {**body, "description": desc.replace("(good snorkelling)", "(cold water, good snorkelling)")}
    new_lead = {**body, "summary": title.replace("Clovelly", "Bronte")}
    assert fingerprint(later) == fingerprint(body) == fingerprint(wobble) == fingerprint(notes)
    assert fingerprint(new_lead) != fingerprint(body)


def test_every_day_is_three_sessions_end_to_end():
    for day in (WED, date(2026, 11, 7)):  # a weekday and a Saturday: the same split
        hours, sun = make_forecast(day)
        sessions, ctx = score(hours, sun, day)

        assert list(sessions) == ["am", "md", "pm"]
        assert sessions["am"].hours[-1][11:13] == "10"  # to 11am
        assert [t[11:13] for t in sessions["md"].hours] == ["11", "12", "13"]  # 11am to 2pm, no gap either side
        assert sessions["pm"].hours[0][11:13] == "14"
        assert sessions["md"].key.endswith("md")  # base32hex, so it can be a Google event id
        title, _ = event_body(sessions["md"], hours, ctx, {}, day)
        assert title.endswith(f"· {day:%a} midday")


def test_weekday_middays_are_on_the_site_but_not_the_calendar():
    sat = date(2026, 11, 7)
    weekday, _ = score(*make_forecast(WED), WED)
    weekend, _ = score(*make_forecast(sat), sat)
    assert not weekday["md"].in_calendar
    assert weekday["am"].in_calendar and weekday["pm"].in_calendar
    assert all(s.in_calendar for s in weekend.values())

    hours, sun = make_forecast(WED)
    ctx = Context(hours)
    now = datetime(2026, 11, 4, 3, tzinfo=TZ)
    sessions = build_sessions(hours, sun, now, days=[WED])
    for s in sessions:
        score_session(s, hours, ctx, {}, WED)
    md = next(s for s in sessions if s.slot == "md")
    assert md.is_good
    data = export_scores(sessions, hours, ctx, {}, now, posted=set())  # the calendar posted nothing
    assert next(x for x in data["sessions"] if x["key"] == md.key)["posted"]  # still worth it on the site
