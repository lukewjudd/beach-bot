from datetime import date

from conftest import make_forecast, score

from beach_bot.beaches import EASTERN
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

    assert len(sessions["am"].surf) == len(EASTERN.surf)
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


def maroubra_12_apr(t, h):
    """Maroubra, Sun 12 Apr 2026: 4-6 ft and clean (a drone clip at 8am), the forecast as the archive has it. A
    1.4m east swell whose swell period reads 8 s while the whole sea's is 11 s, and a 21 km/h westerly gusting 49."""
    h.update(wave_height=1.4, swell_wave_direction=90, swell_wave_period=8.0, wave_period=11.0)
    h.update(wind_speed_10m=21.0, wind_direction_10m=270, wind_gusts_10m=49.0)
    return h


def test_a_classic_maroubra_morning_scores_like_one():
    sessions, _ = score(*make_forecast(WED, maroubra_12_apr), WED)

    assert out_of_10(surf(sessions["am"], "Maroubra")[0]) >= 8


def test_surf_reads_the_longer_of_the_swell_and_whole_sea_periods():
    short, _ = score(*make_forecast(WED, swell(1.4, 90, 8, wind=6)), WED)

    def longer(t, h):
        h = swell(1.4, 90, 8, wind=6)(t, h)
        h["wave_period"] = 11.0
        return h

    long_, _ = score(*make_forecast(WED, longer), WED)
    assert surf(long_["am"], "Maroubra")[0] > surf(short["am"], "Maroubra")[0]


def test_a_strong_offshore_suits_solid_swell_better_than_small():
    from beach_bot.beaches import EASTERN
    from beach_bot.scoring import offshore_points

    maroubra = next(sp for sp in EASTERN.surf if sp.name == "Maroubra")
    h = {"wind_speed_10m": 25.0, "wind_direction_10m": 270, "wind_gusts_10m": 40.0}
    assert offshore_points(h, maroubra, 1.6) > offshore_points(h, maroubra, 0.6)
    assert offshore_points({**h, "wind_speed_10m": 12.0, "wind_gusts_10m": 18.0}, maroubra, 1.5) == 30
    assert offshore_points({**h, "wind_speed_10m": 50.0, "wind_gusts_10m": 75.0}, maroubra, 2.0) <= 2


def test_reefs_need_their_own_swell_and_never_make_the_call():
    # 2.2m ENE groundswell, light westerly: Clovelly Bombie fires, but the session's surf call is a break for everyone
    sessions, _ = score(*make_forecast(WED, swell(2.2, 70, 12, wind=6, wind_dir=260)), WED)
    am = sessions["am"]
    assert out_of_10(surf(am, "Clovelly Bombie")[0]) >= 7
    assert not am.surf[0][1].advanced

    # The same size from the south: the bombie isn't breaking on it, while Malabar likes it
    sessions, _ = score(*make_forecast(WED, swell(2.2, 170, 12, wind=6, wind_dir=320)), WED)
    assert "wrong swell direction" in surf(sessions["am"], "Clovelly Bombie")[2]
    assert out_of_10(surf(sessions["am"], "Clovelly Bombie")[0]) <= 2


def test_a_reef_on_a_small_day_isnt_breaking():
    sessions, _ = score(*make_forecast(WED, swell(0.8, 90, 11, wind=6, wind_dir=260)), WED)
    sc, _, notes = surf(sessions["am"], "Clovelly Bombie")
    assert out_of_10(sc) <= 2 and "not breaking" in notes


def test_maroubras_north_corner_is_the_pick_in_a_nor_easter():
    # 1.4m SE at 10s with a 20 km/h north-easter: the open beach is chopped up, the corner under Mistral Point less so
    sessions, _ = score(*make_forecast(WED, swell(1.4, 140, 10, wind=20, wind_dir=30)), WED)
    corner = surf(sessions["am"], "Maroubra (north end)")
    assert corner[0] > surf(sessions["am"], "Maroubra")[0]
    assert "sheltered from the wind" in corner[2]


def test_collaroys_corner_is_the_northern_hideout_in_a_southerly():
    # 2.8m E groundswell with a 25 km/h southerly: the open beaches are blown out, Collaroy's corner is sheltered
    from beach_bot.beaches import NORTHERN

    sessions, _ = score(*make_forecast(WED, swell(2.8, 100, 12, wind=25, wind_dir=190)), WED, region=NORTHERN)
    corner = surf(sessions["am"], "Collaroy")
    assert "sheltered from the wind" in corner[2]
    assert corner[0] > surf(sessions["am"], "Long Reef")[0]
    assert corner[0] > surf(sessions["am"], "South Narrabeen")[0]
