"""Spearfishing (beach-knowledge.md §4.9): the real pipeline on made-up forecasts."""

from datetime import date, datetime

from conftest import make_forecast, score

from beach_bot.beaches import EASTERN, NORTHERN
from beach_bot.config import TZ
from beach_bot.export import export_scores
from beach_bot.sessions import out_of_10

WED = date(2026, 11, 4)
JUL = date(2026, 7, 15)


def spear(session, name):
    return next((x for x in session.spear if x[1].name == name), None)


def sea(height, direction=110, period=8, rain=lambda t: 0.0, wind=5.0):
    def tweak(t, h):
        h.update(wave_height=height, swell_wave_height=height, swell_wave_direction=direction)
        h.update(swell_wave_period=period, precipitation=rain(t), wind_speed_10m=wind, wind_gusts_10m=wind * 1.5)
        return h

    return tweak


def test_a_flat_dry_week_is_a_good_dive_and_a_big_swell_rules_out_the_platforms():
    flat, _ = score(*make_forecast(WED, sea(0.3), lookback_days=7), WED)
    big, _ = score(*make_forecast(WED, sea(2.5, period=12), lookback_days=7), WED)

    assert out_of_10(spear(flat["am"], "Mahon Pool")[0]) >= 6
    assert spear(big["am"], "Mahon Pool") is None
    assert big["am"].spear_ruled_out["Mahon Pool"].endswith("waves at the entry")
    # The bay side of Kurnell is out of the east swell, so it's still diveable
    assert spear(big["am"], "Kurnell (bay side)") is not None


def test_a_swell_that_has_dropped_leaves_the_water_murky_down_deep():
    # Three days of 2.5m east swell, gone by the morning of the dive
    def dropped(t):
        return 2.5 if t < "2026-11-04T00:00" else 0.3

    sessions, _ = score(*make_forecast(WED, lambda t, h: sea(dropped(t))(t, h), lookback_days=7), WED)
    calm, _ = score(*make_forecast(WED, sea(0.3), lookback_days=7), WED)

    _, _, notes = spear(sessions["am"], "Mahon Pool")
    assert "may be murky down deep: sand still settling" in notes
    assert spear(sessions["am"], "Mahon Pool")[0] < spear(calm["am"], "Mahon Pool")[0]


def test_heavy_rain_closes_the_lagoon_mouth_and_the_harbour_but_not_the_open_coast():
    def rain(t):
        return 5.0 if "2026-11-03T00:00" <= t < "2026-11-03T08:00" else 0.0  # 40mm the day before

    north, _ = score(*make_forecast(WED, sea(0.3, rain=rain), lookback_days=7), WED, region=NORTHERN)
    east, _ = score(*make_forecast(WED, sea(0.3, rain=rain), lookback_days=7), WED)

    assert north["am"].spear_ruled_out["Narrabeen Head"] == "lagoon flushing after rain"
    assert east["am"].spear_ruled_out["Camp Cove"] == "harbour runoff after rain"
    assert spear(north["am"], "Long Reef") is not None
    assert "bull sharks more likely after rain" in spear(east["am"], "La Perouse")[2]


def test_winter_water_is_clearer():
    summer, _ = score(*make_forecast(WED, sea(0.3), lookback_days=7), WED)
    winter, _ = score(*make_forecast(JUL, sea(0.3), lookback_days=7), JUL)

    assert spear(winter["md"], "Mahon Pool")[0] > spear(summer["md"], "Mahon Pool")[0]


def test_the_spear_call_skips_spots_for_the_experienced_and_the_site_gets_their_conditions():
    hours, sun = make_forecast(WED, sea(0.3), lookback_days=7)
    sessions, ctx = score(hours, sun, WED)
    now = datetime(2026, 11, 4, 3, tzinfo=TZ)
    data = export_scores(list(sessions.values()), hours, ctx, {}, now, sun=sun, region=EASTERN)
    am = next(s for s in data["sessions"] if s["key"].endswith("am"))
    spots = {s["id"]: s for s in data["spots"]}

    call = am["spear"]
    assert spots[call["id"]]["kind"] == "spear"
    assert spots[call["id"]]["level"] == "all" and spots[call["id"]]["checked"]
    here = next(x for x in am["scores"] if x["id"] == call["id"])["here"]
    assert here["vis_m"] >= 5 and here["surge_m"] < 0.4
    assert set(am["reports"][call["id"]]) == {"Visibility", "Surge", "Wind", "Tide", "Light", "Water temp"}


def test_every_spot_sits_on_the_seabed_survey_with_its_own_swell_window():
    from beach_bot import swell

    for region in (EASTERN, NORTHERN):
        (s, w), (n, e) = region.bounds
        for sp in region.spear:
            lat, lon = region.pin(sp)
            assert s < lat < n and w < lon < e, sp.name
            assert sp.reef, f"{sp.name} has no survey record: run scripts/build_spear_reefs.py"
            assert 2 <= sp.dive_depth <= 20, sp.name
            if sp.water != "harbour":
                assert swell.key(sp) in swell.WINDOWS["spots"], f"{sp.name}: run scripts/build_swell_windows.py"
