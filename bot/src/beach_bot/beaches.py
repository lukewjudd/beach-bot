"""The beaches and surf spots, with the local knowledge from beach-knowledge.md."""

from dataclasses import dataclass, field

@dataclass
class Beach:
    name: str
    facing: int                      # bearing the beach faces (looking out to sea)
    k: dict                          # swell exposure by sector (R-S, §4.2)
    rain_occ: float                  # mm in 24h: "occasionally" fails (§3.1)
    rain_often: float                # mm in 24h: "often" fails
    hazard: int                      # Beachsafe 1-10
    beachwatch: str                  # site name in the Beachwatch feed
    swim_limit: float = 1.2          # Hb above this = no swim
    poor_grade: bool = False         # R-R3: 3-day rain rule
    snorkel: bool = False
    patrolled_all_daylight: bool = False
    notes: list = field(default_factory=list)


BEACHES = [
    Beach("Bondi (north end)", 150, {"NE": .3, "E": .5, "SE": .8, "S": .9}, 5, 20, 7, "Bondi Beach"),
    Beach("Tamarama", 100, {"NE": .8, "E": 1.0, "SE": .9, "S": .6}, 1, 5, 8, "Tamarama Beach", swim_limit=0.9),
    Beach("Bronte", 90, {"NE": .8, "E": 1.0, "SE": .9, "S": .6}, 1, 10, 7, "Bronte Beach"),
    Beach("Clovelly", 120, {"NE": .15, "E": .25, "SE": .35, "S": .25}, 10, 20, 2, "Clovelly Beach",
          snorkel=True, patrolled_all_daylight=True),
    Beach("Gordons Bay", 90, {"NE": .4, "E": .5, "SE": .35, "S": .2}, 1, 10, 2, "Gordons Bay (East)",
          swim_limit=0.6, snorkel=True),
    Beach("Coogee", 100, {"NE": .6, "E": .6, "SE": .35, "S": .25}, 1, 10, 4, "Coogee Beach", poor_grade=True),
    Beach("Maroubra", 90, {"NE": .9, "E": 1.0, "SE": .9, "S": .6}, 5, 20, 6, "Maroubra Beach"),
    Beach("Malabar", 110, {"NE": .25, "E": .45, "SE": .5, "S": .3}, 1, 5, 3, "Malabar Beach"),
    Beach("Little Bay", 45, {"NE": .35, "E": .4, "SE": .35, "S": .2}, 1, 10, 2, "Little Bay Beach", snorkel=True),
]


@dataclass
class SurfSpot:
    name: str
    facing: int
    swell_dirs: tuple                # (from_deg, to_deg) the spot works in
    min_hs: float
    max_hs: float = 2.5
    bonus_dirs: tuple = None         # swell direction range that gets a small bonus


SURF_SPOTS = [
    SurfSpot("Bondi (south end)", 140, (135, 200), 0.6, bonus_dirs=(157, 200)),   # R-SU1
    SurfSpot("Maroubra", 90, (30, 150), 0.5, bonus_dirs=(67, 112)),               # R-SU2
    SurfSpot("Bronte", 90, (67, 157), 0.8),                                        # R-SU3
    SurfSpot("Coogee", 100, (67, 112), 1.5, max_hs=3.0),                           # R-SU4
]

# Map positions for the website (swim areas from beach-knowledge.md §1; surf markers sit just offshore)
COORDS = {
    "Bondi (north end)": (-33.8905, 151.2805),
    "Tamarama": (-33.9007, 151.2709),
    "Bronte": (-33.9031, 151.2688),
    "Clovelly": (-33.9138, 151.2666),
    "Gordons Bay": (-33.9158, 151.2648),
    "Coogee": (-33.9208, 151.2582),
    "Maroubra": (-33.9475, 151.2572),
    "Malabar": (-33.9644, 151.2523),
    "Little Bay": (-33.9799, 151.2514),
}
SURF_COORDS = {   # pushed further out to sea than the swim markers so the two don't overlap
    "Bondi (south end)": (-33.8945, 151.2830),
    "Maroubra": (-33.9480, 151.2665),
    "Bronte": (-33.9045, 151.2770),
    "Coogee": (-33.9215, 151.2670),
}
