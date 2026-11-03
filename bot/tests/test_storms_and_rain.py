"""The night of 3 Nov 2026: thunderstorms, ~22mm of rain, and a 4am run that still said 6/10."""

from datetime import date

from conftest import make_forecast, score

from beach_bot.forecast import fresh_forecasts, hourly_rain
from beach_bot.sessions import report

WED = date(2026, 11, 4)


def storm_from(start):
    def tweak(t, h):
        if t >= start:
            h.update(weather_code=95, precipitation=3.0, precipitation_probability=90, cape=1500)
        return h

    return tweak


def test_thunderstorms_rule_out_swimming_and_pools_and_floor_the_surf():
    sessions, _ = score(*make_forecast(WED, storm_from("2026-11-04T14:00")), WED)
    pm = sessions["pm"]

    assert pm.swim == [] and pm.pools == []
    assert pm.ruled_out["Clovelly"] == "storms ⚡"
    assert all(sc == 10 for sc, _, _ in pm.surf)


def test_storm_energy_with_rain_likely_counts_as_a_storm_without_the_weather_code():
    def tweak(t, h):
        if t >= "2026-11-04T14:00":
            h.update(cape=1200, precipitation_probability=80)
        return h

    sessions, _ = score(*make_forecast(WED, tweak), WED)
    assert sessions["pm"].swim == []


def test_overnight_rain_drags_surf_spots_down_too():
    def wet(t, h):
        if "2026-11-03T18:00" <= t < "2026-11-04T02:00":
            h["precipitation"] = 3.0  # 24mm overnight
        return h

    dry, _ = score(*make_forecast(WED), WED)
    rained, _ = score(*make_forecast(WED, wet), WED)

    def maroubra(s):
        return next(sc for sc, sp, _ in s["am"].surf if sp.name == "Maroubra")

    assert maroubra(rained) < maroubra(dry)


def test_yesterdays_beachwatch_forecast_is_ignored():
    features = [
        {
            "properties": {
                "siteName": "Clovelly Beach",
                "pollutionForecast": "Unlikely",
                "pollutionForecastTimeStamp": "2026-11-02T19:00:00.2333333+00:00",
            }
        },  # 6am Tue
        {
            "properties": {
                "siteName": "Coogee Beach",
                "pollutionForecast": "Likely",
                "pollutionForecastTimeStamp": "2026-11-03T19:00:00.2333333+00:00",
            }
        },  # 6am Wed
    ]
    assert fresh_forecasts(features, WED) == {"Coogee Beach": "Likely"}


def test_bom_rain_since_9am_becomes_hourly_rain():
    obs = [
        {"aifstime_local": "20261103183000", "rain_trace": "0.4"},
        {"aifstime_local": "20261103190000", "rain_trace": "12.6"},
        {"aifstime_local": "20261103193000", "rain_trace": "13.4"},
        {"aifstime_local": "20261104083000", "rain_trace": "22.4"},
        {"aifstime_local": "20261104090000", "rain_trace": "-"},
        {"aifstime_local": "20261104093000", "rain_trace": "0.2"},  # the count resets at 9am
    ]
    rain = hourly_rain(obs)

    assert round(rain["2026-11-03T19:00"], 1) == 12.2
    assert round(rain["2026-11-03T20:00"], 1) == 0.8
    assert round(rain["2026-11-04T10:00"], 1) == 0.2


def test_swimming_spots_show_calm_water_and_surf_spots_show_surf_quality():
    sessions, ctx = score(*make_forecast(WED), WED)
    am = sessions["am"]
    hours = make_forecast(WED)[0]
    maroubra_beach = next(b for _, b, _ in am.swim if b.name == "Maroubra")
    maroubra_surf = next(sp for _, sp, _ in am.surf if sp.name == "Maroubra")

    beach = report(am, hours, ctx, {}, WED, maroubra_beach)
    surf = report(am, hours, ctx, {}, WED, maroubra_surf)

    assert "Calm water" in beach and "Surf quality" not in beach
    assert "Surf quality" in surf and "Calm water" not in surf
