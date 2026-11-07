"""The calendar gets one event per day, bundling that day's good sessions, against a stand-in for Google Calendar."""

from datetime import date, datetime

from conftest import make_forecast, score

from beach_bot.calendar import sync
from beach_bot.config import TZ

WED = date(2026, 11, 4)
SAT = date(2026, 11, 7)


class Call:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result


class FakeCalendar:
    """Just enough of the Calendar API: events kept by id, deleted ones kept as cancelled (as Google does)."""

    def __init__(self, events=()):
        self.store = {e["id"]: e for e in events}
        self.log = []

    def events(self):
        return self

    def list(self, **kw):
        return Call({"items": list(self.store.values())})

    def insert(self, calendarId, body):
        self.log.append(("insert", body["id"]))
        self.store[body["id"]] = body
        return Call(body)

    def update(self, calendarId, eventId, body):
        self.log.append(("update", eventId))
        self.store[eventId] = body
        return Call(body)

    def delete(self, calendarId, eventId):
        self.log.append(("delete", eventId))
        self.store[eventId] = {**self.store[eventId], "status": "cancelled"}
        return Call({})


def run(day, now, svc, tweak=lambda t, h: h):
    hours, sun = make_forecast(day, tweak)
    sessions, ctx = score(hours, sun, day, now=now)
    posted = sync(list(sessions.values()), hours, ctx, {}, now, "cal", svc=svc)
    return sessions, posted


def test_a_good_day_is_one_event_covering_its_sessions():
    svc = FakeCalendar()
    sessions, posted = run(SAT, datetime(2026, 11, 7, 4, tzinfo=TZ), svc)

    assert svc.log == [("insert", "beach20261107")]
    ev = svc.store["beach20261107"]
    assert ev["summary"].endswith("· Sat morning, midday & evening")
    assert ev["start"]["dateTime"] == sessions["am"].start.isoformat()
    assert ev["end"]["dateTime"] == sessions["pm"].end.isoformat()
    assert ev["description"].count("Top 3 spots:") == 3  # each session has its own part
    assert posted == {s.key for s in sessions.values()}


def test_a_weekday_midday_is_left_out_of_the_days_event():
    svc = FakeCalendar()
    sessions, posted = run(WED, datetime(2026, 11, 4, 4, tzinfo=TZ), svc)

    assert svc.store["beach20261104"]["summary"].endswith("· Wed morning & evening")
    assert sessions["md"].key not in posted


def test_a_run_with_nothing_new_sends_nothing():
    svc = FakeCalendar()
    now = datetime(2026, 11, 7, 4, tzinfo=TZ)
    run(SAT, now, svc)
    svc.log.clear()
    run(SAT, now, svc)
    assert svc.log == []


def test_old_per_session_events_are_cleared_once_days_are_bundled():
    old = {
        "id": "beach20261107pm",
        "status": "confirmed",
        "start": {"dateTime": "2026-11-07T14:00:00+11:00"},
        "end": {"dateTime": "2026-11-07T19:30:00+11:00"},
    }
    svc = FakeCalendar([old])
    run(SAT, datetime(2026, 11, 7, 4, tzinfo=TZ), svc)
    assert ("delete", "beach20261107pm") in svc.log
    assert svc.store["beach20261107"]["status"] == "confirmed"


def test_a_session_drops_off_below_7_and_the_event_goes_when_none_are_left():
    svc = FakeCalendar()
    now = datetime(2026, 11, 7, 4, tzinfo=TZ)
    run(SAT, now, svc)

    def stormy_afternoon(t, h):  # storms from 2pm: the evening falls away, the morning and midday stay
        if t.startswith("2026-11-07") and int(t[11:13]) >= 14:
            h.update(weather_code=95)
        return h

    run(SAT, now, svc, stormy_afternoon)
    assert svc.store["beach20261107"]["summary"].endswith("· Sat morning & midday")

    def washout(t, h):
        h.update(precipitation_probability=90, precipitation=2.0, cloud_cover=100, temperature_2m=15.0)
        return h

    run(SAT, now, svc, washout)
    assert svc.store["beach20261107"]["status"] == "cancelled"


def test_an_event_under_way_is_left_alone():
    svc = FakeCalendar()
    run(SAT, datetime(2026, 11, 7, 4, tzinfo=TZ), svc)
    svc.log.clear()

    def washout(t, h):
        h.update(precipitation_probability=90, precipitation=2.0, cloud_cover=100, temperature_2m=15.0)
        return h

    _, posted = run(SAT, datetime(2026, 11, 7, 8, tzinfo=TZ), svc, washout)  # the morning has started
    assert svc.log == []
    assert len(posted) == 3  # the site still shows what the event said
