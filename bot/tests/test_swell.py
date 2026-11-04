"""How much swell reaches a spot: smooth across directions, and each wave train weighed on its own."""

from beach_bot.beaches import EASTERN
from beach_bot.scoring import at_beach, exposure

BEACH = {b.name: b for b in EASTERN.beaches}


def test_exposure_is_smooth_between_directions():
    k = BEACH["Bronte"].k  # NE 0.8, E 1.0, SE 0.9, S 0.6
    assert exposure(k, 90) == k["E"] and exposure(k, 180) == k["S"]
    # 112 and 113 degrees used to fall in different buckets (E 1.0 vs SE 0.9)
    assert abs(exposure(k, 112) - exposure(k, 113)) < 0.01


def test_harbour_beaches_take_no_swell_from_offshore_directions():
    assert exposure(BEACH["Murray Rose Pool"].k, 270) == 0


def test_a_beach_open_everywhere_gets_the_whole_sea():
    everywhere = {"NE": 1.0, "E": 1.0, "SE": 1.0, "S": 1.0}
    h = {
        "wave_height": 1.0,
        "swell_wave_height": 0.8,
        "swell_wave_direction": 160,
        "swell_wave_period": 9,
        "secondary_swell_wave_height": 0.5,
        "secondary_swell_wave_direction": 90,
        "secondary_swell_wave_period": 8,
        "wind_wave_height": 0.33,
        "wind_wave_direction": 45,
        "wind_wave_period": 3,
    }
    assert abs(at_beach(h, everywhere) - 1.0) < 0.02  # 0.8, 0.5 and 0.33 add up (as energy) to the 1.0m sea


def test_a_south_swell_misses_a_beach_that_faces_north_east():
    # 1.2m of south groundswell plus a little east chop: Little Bay (S 0.2) stays calm, Bronte (S 0.6) doesn't
    h = {
        "wave_height": 1.25,
        "swell_wave_height": 1.2,
        "swell_wave_direction": 180,
        "swell_wave_period": 10,
        "secondary_swell_wave_height": 0.0,
        "secondary_swell_wave_direction": 90,
        "secondary_swell_wave_period": 6,
        "wind_wave_height": 0.35,
        "wind_wave_direction": 90,
        "wind_wave_period": 3,
    }
    assert at_beach(h, BEACH["Little Bay"].k) < 0.35
    assert at_beach(h, BEACH["Bronte"].k) > 0.7
