"""The beaches and surf spots, with the local knowledge from beach-knowledge.md."""

from dataclasses import dataclass, field


@dataclass
class Beach:
    name: str
    facing: int  # bearing the beach faces (looking out to sea)
    k: dict  # swell exposure by sector (R-S, §4.2)
    rain_occ: float  # mm in 24h: "occasionally" fails (§3.1)
    rain_often: float  # mm in 24h: "often" fails
    hazard: int  # Beachsafe 1-10
    beachwatch: str  # site name in the Beachwatch feed
    swim_limit: float = 1.2  # Hb above this = no swim
    poor_grade: bool = False  # R-R3: 3-day rain rule
    snorkel: bool = False
    patrolled_all_daylight: bool = False
    notes: list = field(default_factory=list)


BEACHES = [
    Beach("Bondi (north end)", 150, {"NE": 0.3, "E": 0.5, "SE": 0.8, "S": 0.9}, 5, 20, 7, "Bondi Beach"),
    Beach("Tamarama", 100, {"NE": 0.8, "E": 1.0, "SE": 0.9, "S": 0.6}, 1, 5, 8, "Tamarama Beach", swim_limit=0.9),
    Beach("Bronte", 90, {"NE": 0.8, "E": 1.0, "SE": 0.9, "S": 0.6}, 1, 10, 7, "Bronte Beach"),
    Beach(
        "Clovelly",
        120,
        {"NE": 0.15, "E": 0.25, "SE": 0.35, "S": 0.25},
        10,
        20,
        2,
        "Clovelly Beach",
        snorkel=True,
        patrolled_all_daylight=True,
    ),
    Beach(
        "Gordons Bay",
        90,
        {"NE": 0.4, "E": 0.5, "SE": 0.35, "S": 0.2},
        1,
        10,
        2,
        "Gordons Bay (East)",
        swim_limit=0.6,
        snorkel=True,
    ),
    Beach("Coogee", 100, {"NE": 0.6, "E": 0.6, "SE": 0.35, "S": 0.25}, 1, 10, 4, "Coogee Beach", poor_grade=True),
    Beach("Maroubra", 90, {"NE": 0.9, "E": 1.0, "SE": 0.9, "S": 0.6}, 5, 20, 6, "Maroubra Beach"),
    Beach("Malabar", 110, {"NE": 0.25, "E": 0.45, "SE": 0.5, "S": 0.3}, 1, 5, 3, "Malabar Beach"),
    Beach("Little Bay", 45, {"NE": 0.35, "E": 0.4, "SE": 0.35, "S": 0.2}, 1, 10, 2, "Little Bay Beach", snorkel=True),
]


@dataclass
class SurfSpot:
    name: str
    facing: int
    k: dict  # how much of the open-ocean swell reaches the break, by swell sector (§1a)
    max_hs: float = 2.5  # above this (at the break) it closes out
    bonus_dirs: tuple = None  # swell direction range that gets a small bonus


SURF_SPOTS = [
    # R-SU1: a south swell magnet; Ben Buckler shadows the NE
    SurfSpot("Bondi (south end)", 140, {"NE": 0.3, "E": 0.6, "SE": 0.9, "S": 1.0}, bonus_dirs=(157, 200)),
    # R-SU2: most consistent in E swell; S swell mostly misses it
    SurfSpot("Maroubra", 90, {"NE": 0.9, "E": 1.0, "SE": 0.9, "S": 0.6}, bonus_dirs=(67, 112)),
    # R-SU3: E-SE reef and beachie, still works a bit in S
    SurfSpot("Bronte", 90, {"NE": 0.8, "E": 1.0, "SE": 0.9, "S": 0.6}),
    # R-SU4: Wedding Cake Island blocks SE/S; needs a solid E swell
    SurfSpot("Coogee", 100, {"NE": 0.5, "E": 0.7, "SE": 0.3, "S": 0.2}, max_hs=3.0),
]

# Map positions for the website (swim areas from beach-knowledge.md §1; surf markers sit just offshore)
COORDS = {
    "Bondi (north end)": (-33.8905, 151.2805),
    "Tamarama": (-33.9007, 151.2709),
    "Bronte": (-33.9031, 151.2688),
    "Clovelly": (-33.9138, 151.2666),
    "Gordons Bay": (-33.9149, 151.2613),  # the sand at the back of the bay (OSM beach polygon)
    "Coogee": (-33.9208, 151.2582),
    "Maroubra": (-33.9475, 151.2572),
    "Malabar": (-33.9644, 151.2523),
    "Little Bay": (-33.9799, 151.2514),
}
SURF_COORDS = {  # pushed further out to sea than the swim markers so the two don't overlap
    "Bondi (south end)": (-33.8932, 151.2772),  # off the Icebergs end, not Ben Buckler (that's the north)
    "Maroubra": (-33.9480, 151.2665),
    "Bronte": (-33.9045, 151.2770),
    "Coogee": (-33.9215, 151.2670),
}


@dataclass
class Pool:
    """An ocean pool (beach-knowledge.md §2). Water quality follows the beach next to it (R-R5)."""

    name: str
    beach: Beach  # the beach whose water fills it
    exposure: float  # how readily big swell washes over the walls (1 = fully exposed)
    best_tide: str | None = None  # "low", "mid" or "mid_high"
    cleaning_day: int | None = None  # weekday (Mon=0) it's drained for cleaning, for a few hours
    cleaning_before_low: bool = False  # only closed in the ~4h before low tide (Bronte Baths)
    opens: int | None = None  # opening hour, for pools with gates
    closes_summer: int = 19  # 1 Oct - 12 Apr
    closes_winter: int = 17


_BEACH = {b.name: b for b in BEACHES}

# Surf spots share the water (and Beachwatch site) of the beach they break off
BEACH_FOR_SURF = {
    "Bondi (south end)": _BEACH["Bondi (north end)"],
    "Maroubra": _BEACH["Maroubra"],
    "Bronte": _BEACH["Bronte"],
    "Coogee": _BEACH["Coogee"],
}

POOLS = [
    Pool("Bondi Icebergs", _BEACH["Bondi (north end)"], 1.0, cleaning_day=3),  # R-P7: Thursdays
    Pool("Bronte Baths", _BEACH["Bronte"], 0.8, cleaning_day=2, cleaning_before_low=True),  # R-P7: Wednesdays
    Pool("Giles Baths", _BEACH["Coogee"], 0.8, best_tide="mid"),  # R-P5
    Pool("Wylie's Baths", _BEACH["Coogee"], 0.6, best_tide="low", opens=7),  # R-P1, R-P8
    Pool("Ross Jones Pool", _BEACH["Coogee"], 0.9, cleaning_day=0),  # R-P7: Mondays
    Pool("Mahon Pool", _BEACH["Maroubra"], 1.0, best_tide="mid_high"),  # R-P3
]
# McIver's (women and children only), Ivor Rowe and South Maroubra rockpool (small wading pools) are left out

POOL_COORDS = {
    "Bondi Icebergs": (-33.8953, 151.2744),
    "Bronte Baths": (-33.9052, 151.2693),
    "Giles Baths": (-33.9202, 151.2606),
    "Wylie's Baths": (-33.9256, 151.2594),
    "Ross Jones Pool": (-33.9228, 151.2578),
    "Mahon Pool": (-33.9430, 151.2639),
}
