"""How much swell reaches a spot: the swell window from the coastline, refraction and wrap by period, the
breaker height, and each wave train weighed on its own."""

from beach_bot import swell
from beach_bot.beaches import EASTERN, NORTHERN, Beach
from beach_bot.scoring import at_beach

BEACH = {b.name: b for r in (EASTERN, NORTHERN) for b in r.beaches}


def exp(name, direction, period=10):
    b = BEACH[name]
    return swell.exposure(b, swell.key(b), direction, period)


def test_exposure_is_smooth_between_directions():
    # 112 and 113 degrees used to fall in different buckets (E 1.0 vs SE 0.9)
    assert abs(exp("Bronte", 112) - exp("Bronte", 113)) < 0.02


def test_harbour_beaches_take_no_swell_from_offshore_directions():
    assert exp("Murray Rose Pool", 270) == 0


def test_a_textbook_swell_on_an_open_beach_breaks_at_its_own_height():
    # the size bands were set against offshore height: 1.5m at 9s straight in should still read 1.5m
    assert abs(swell.breaker(1.5, 9) - 1.5) < 1e-9


def test_longer_period_breaks_bigger_without_a_step():
    sizes = [swell.breaker(1.0, t) for t in (8, 10, 11, 12, 14, 16)]
    assert sizes == sorted(sizes)
    assert 1.1 < swell.breaker(1.5, 12) / 1.5 < 1.15  # Komar & Gaughan: about 1.12x at 12s
    assert swell.breaker(1.0, 7, exponent=0.7, ref=10) < 0.8  # surf: 7s swell is the old table's 0.75x
    assert swell.breaker(1.0, 12) / swell.breaker(1.0, 11) < 1.05  # no jump at 12s any more


def test_ben_buckler_shades_north_bondi_from_the_north_east():
    assert exp("Bondi (north end)", 45) < 0.1
    assert exp("Bondi (north end)", 160) > 0.5


def test_long_period_swell_wraps_into_a_sheltered_corner():
    # Collaroy is tucked behind Long Reef from the south: SSE groundswell bends round more than short swell does
    assert exp("Collaroy", 157, 14) > exp("Collaroy", 157, 8) + 0.1


def test_a_south_swell_misses_a_beach_that_faces_north_east():
    # 1.2m of south groundswell plus a little east chop: Little Bay stays calm, Bronte doesn't
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
    assert at_beach(h, BEACH["Little Bay"]) < 0.4
    assert at_beach(h, BEACH["Bronte"]) > 0.6


def test_a_beach_open_everywhere_gets_the_whole_sea():
    everywhere = Beach("Nowhere", 90, {"NE": 1.0, "E": 1.0, "SE": 1.0, "S": 1.0}, 1, 1, 1, "")
    h = {"wave_height": 1.5, "swell_wave_height": 1.5, "swell_wave_direction": 90, "swell_wave_period": 9}
    assert abs(at_beach(h, everywhere) - 1.5) < 0.01
