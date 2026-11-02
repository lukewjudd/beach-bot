from datetime import date

from conftest import make_forecast, score

from beach_bot.sessions import out_of_10

WED = date(2026, 11, 4)


def surf(session, name):
    return next(x for x in session.surf if x[1].name == name)


def swell(height, direction, period, wind=5.0, wind_dir=270):
    def tweak(t, h):
        h.update(wave_height=height, swell_wave_direction=direction, swell_wave_period=period)
        h.update(wind_speed_10m=wind, wind_direction_10m=wind_dir, wind_gusts_10m=wind * 1.6)
        return h

    return tweak


def test_every_surf_spot_always_gets_a_score():
    sessions, _ = score(*make_forecast(WED, swell(0.2, 90, 5)), WED)

    assert len(sessions["am"].surf) == 4
    assert all(out_of_10(sc) == 1 for sc, _, _ in sessions["am"].surf)  # flat everywhere


def test_a_clean_south_groundswell_lights_up_bondi_but_not_coogee():
    sessions, _ = score(*make_forecast(WED, swell(1.4, 180, 11, wind=8, wind_dir=315)), WED)

    assert out_of_10(surf(sessions["am"], "Bondi (south end)")[0]) >= 8
    assert out_of_10(surf(sessions["am"], "Coogee")[0]) <= 2  # Wedding Cake Island blocks southerlies
    assert sessions["am"].is_good


def test_small_windy_south_swell_is_a_few_points_not_one():
    # Mon 2 Nov 2026 at 2pm: knee-high and textured on the Bondi webcam
    sessions, _ = score(*make_forecast(WED, swell(0.86, 158, 7, wind=21, wind_dir=55)), WED)

    bondi = surf(sessions["am"], "Bondi (south end)")
    assert 2 <= out_of_10(bondi[0]) <= 4
    assert "small" in bondi[2]


def test_onshore_wind_ruins_good_swell():
    clean, _ = score(*make_forecast(WED, swell(1.3, 90, 10, wind=8, wind_dir=270)), WED)
    onshore, _ = score(*make_forecast(WED, swell(1.3, 90, 10, wind=25, wind_dir=90)), WED)

    assert surf(onshore["am"], "Maroubra")[0] < surf(clean["am"], "Maroubra")[0] - 25
    assert "onshore wind" in surf(onshore["am"], "Maroubra")[2]
