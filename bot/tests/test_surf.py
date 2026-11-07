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
    assert out_of_10(surf(sessions["am"], "Coogee")[0]) <= 3  # Wedding Cake Island blocks most of it: tiny
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


def test_surf_never_leads_or_scores_a_session():
    # Pumping: 1.6m east groundswell, light offshore. Great surf, too rough for most beaches
    sessions, _ = score(*make_forecast(WED, swell(1.6, 100, 12, wind=6, wind_dir=270)), WED)
    am = sessions["am"]

    from beach_bot.sessions import headline, lead_kind

    assert out_of_10(am.surf[0][0]) >= 8 and am.surf_for_calendar
    assert lead_kind(am) != "surf"
    assert headline(am) in {x[1].name for x in (am.best_swim, am.best_pool) if x}
    assert am.best == max(x[0] for x in (am.best_swim, am.best_pool) if x)  # surf isn't in the session's score


def test_surf_bars_shrink_with_the_waves_like_the_score():
    from beach_bot.forecast import Context
    from beach_bot.sessions import report

    # 7 Nov 2026 at Bondi (south end): half a metre at 6-7s with a NE breeze across it, a 2/10
    hours, sun = make_forecast(WED, swell(0.6, 160, 6, wind=15, wind_dir=45))
    sessions, _ = score(hours, sun, WED)
    sc, spot, _ = surf(sessions["pm"], "Bondi (south end)")
    bars = report(sessions["pm"], hours, Context(hours), {}, WED, spot)
    assert out_of_10(sc) <= 3
    assert all(bars[k] <= 5 for k in ("Wave size", "Wave quality", "Wind", "Weather")), bars

    hours, sun = make_forecast(WED, swell(1.6, 100, 12, wind=6, wind_dir=270))  # pumping
    sessions, _ = score(hours, sun, WED)
    sc, spot, _ = surf(sessions["am"], "Bondi (south end)")
    bars = report(sessions["am"], hours, Context(hours), {}, WED, spot)
    assert out_of_10(sc) >= 8 and min(bars.values()) >= 7, bars
