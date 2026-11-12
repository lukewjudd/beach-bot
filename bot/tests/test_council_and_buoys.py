"""Northern Beaches Council's closures (R-LG3) and the wave buoys (R-LG4)."""

from datetime import date, datetime

from conftest import make_forecast, score

from beach_bot.beaches import NORTHERN
from beach_bot.config import TZ
from beach_bot.export import buoy_log, export_scores
from beach_bot.forecast import Reports, parse_buoys, parse_council

THU = date(2026, 11, 12)


def item(name, status, message=None):
    """One listing as the council's page has it (trimmed)."""
    msg = (
        f"<div class='ras-message'><span class=\"element-invisible\">Message</span><span>{message}</span></div>"
        if message
        else ""
    )
    return f"""<article class="node-1 node-ra teaser clearfix"><h2 class="node__title"><a href="/x"><span>{name}</span>
      </a></h2><div class='status-wrapper status-{status}'><div class='current-status'>
      <span class="element-invisible">Status</span><div>{status}</div></div>{msg}</div></article>"""


BEACHES = item("Dee Why Beach", "closed", "Dangerous surf") + item("Bungan Beach", "check-at-location", "Not patrolled")
POOLS = item("Fairy Bower Rockpool", "closed", "Closed for cleaning") + item("Freshwater Rockpool", "open")


def test_reading_the_council_listing():
    rows = parse_council(BEACHES)
    assert rows["dee why"] == {"status": "closed", "message": "Dangerous surf"}
    assert rows["bungan"]["status"] == "check at location"


def test_a_closed_beach_or_rockpool_is_out_today_and_check_at_location_is_not():
    council = {"beaches": parse_council(BEACHES), "pools": parse_council(POOLS)}
    reports = Reports({}, {}, council)
    sessions, _ = score(*make_forecast(THU), THU, reports, region=NORTHERN)

    for s in sessions.values():
        assert s.ruled_out["Dee Why"] == "closed by council"
        assert "Bungan" not in s.ruled_out
        pools = {p.name for _, p, _ in s.pools}
        assert "Fairy Bower" not in pools and "Freshwater Rockpool" in pools


FEATURES = [
    {"properties": {"site_name": "Sydney", "TIME": "2026-11-12T00:00:00Z", "WHTH": 1.17, "WPPE": 14.8, "WPDI": 156}},
    {"properties": {"site_name": "Collaroy Narrabeen", "TIME": "2026-11-12T00:40:00Z", "WSSH": 0.713, "WPPE": 14.6}},
    {"properties": {"site_name": "Port Kembla", "TIME": "2026-11-12T00:00:00Z", "WHTH": 1.5}},
]


def test_buoy_readings_and_the_site_gets_the_regions_own_first():
    readings = parse_buoys(FEATURES, ("Collaroy Narrabeen", "Sydney"))
    assert [r["buoy"] for r in readings] == ["Sydney", "Collaroy Narrabeen"]  # oldest first; Port Kembla isn't ours
    assert readings[0] == {"buoy": "Sydney", "time": "2026-11-12T11:00+11:00", "hs": 1.17, "period": 14.8, "deg": 156}

    hours, sun = make_forecast(THU)
    sessions, ctx = score(hours, sun, THU, region=NORTHERN)
    data = export_scores(
        list(sessions.values()),
        hours,
        ctx,
        Reports({}, {}, None, readings),
        datetime(2026, 11, 12, 12, tzinfo=TZ),
        sun=sun,
        region=NORTHERN,
    )
    assert [b["name"] for b in data["buoys"]] == ["Narrabeen buoy", "Sydney buoy"]
    assert data["buoys"][1]["dir"] == "SSE" and data["buoys"][1]["modelled_m"] is not None


def test_the_buoy_log_keeps_one_reading_every_three_hours_for_a_month():
    def row(time, hs):
        return {"time": time, "buoy": "Sydney", "hs": hs}

    previous = {"buoy_log": [row("2026-10-01T09:00", 1.0), row("2026-11-12T09:00", 1.1)]}
    data = {"buoy_log": [row("2026-11-12T10:00", 1.2), row("2026-11-12T12:00", 1.3)]}
    log = buoy_log(data, previous, datetime(2026, 11, 12, 13, tzinfo=TZ))

    assert [(r["time"], r["hs"]) for r in log] == [("2026-11-12T09:00", 1.1), ("2026-11-12T12:00", 1.3)]
