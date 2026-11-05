"""The beaches, pools and surf spots of each region, with the local knowledge from beach-knowledge.md
(eastern suburbs) and northern-beaches-knowledge.md."""

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
    harbour: bool = False  # inside the harbour (or Pittwater): no ocean swell, often netted
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
    # Harbour beaches (research/eastern-additions.md §1): next to no ocean swell (k near 0), wind chop only.
    # Rain is the risk: Beachwatch and Woollahra say stay out 3 days after rain (R-H1, via poor_grade).
    # Hazard: Beachsafe doesn't rate them; 1-2 is a guess.
    # Netted Oct-Apr; only picks up swell in very big NE/E swells
    Beach(
        "Shark Beach",
        340,
        {"NE": 0.15, "E": 0.1, "SE": 0.05, "S": 0.0},
        5,
        20,
        1,
        "Nielsen Park",
        swim_limit=0.5,
        poor_grade=True,
        snorkel=True,
        harbour=True,
    ),
    # Not netted (boat exclusion zone); lifeguards weekends late Oct to Anzac Day and over the summer holidays
    Beach(
        "Camp Cove",
        310,
        {"NE": 0.08, "E": 0.05, "SE": 0.02, "S": 0.0},
        5,
        10,
        2,
        "Camp Cove",
        swim_limit=0.5,
        poor_grade=True,
        snorkel=True,
        harbour=True,
    ),
    # Netted inlet; the net comes out each winter
    Beach(
        "Parsley Bay",
        335,
        {"NE": 0.05, "E": 0.03, "SE": 0.0, "S": 0.0},
        1,
        5,
        1,
        "Parsley Bay",
        poor_grade=True,
        snorkel=True,
        harbour=True,
    ),
    # Netted all year, next to the ferry wharf; westerlies are onshore
    Beach(
        "Watsons Bay",
        275,
        {"NE": 0.03, "E": 0.02, "SE": 0.0, "S": 0.0},
        1,
        10,
        1,
        "Watsons Bay",
        poor_grade=True,
        harbour=True,
    ),
    # Netted enclosure in Double Bay; graded Good this year after two Poor years
    Beach(
        "Murray Rose Pool",
        330,
        {"NE": 0.0, "E": 0.0, "SE": 0.0, "S": 0.0},
        1,
        5,
        1,
        "Murray Rose Pool",
        poor_grade=True,
        harbour=True,
    ),
    # Milk Beach (no Beachwatch site) and Rose Bay (graded Poor every year, not netted) are left out
]


@dataclass
class SurfSpot:
    name: str
    facing: int
    k: dict  # how much of the open-ocean swell reaches the break, by swell sector (§1a)
    max_hs: float = 2.5  # above this (at the break) it closes out
    bonus_dirs: tuple = None  # swell direction range that gets a small bonus
    beach: Beach | None = None  # the beach it breaks off: shares its water (and Beachwatch site)


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
    # Harbour: inside the OSM beach polygons (eastern-additions.md §6)
    "Shark Beach": (-33.8502, 151.2675),
    "Camp Cove": (-33.8398, 151.2789),  # the sand is a crescent; nearest point on it to the centre
    "Parsley Bay": (-33.8515, 151.2775),
    "Watsons Bay": (-33.8443, 151.2816),
    "Murray Rose Pool": (-33.8719, 151.2474),
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
    facing_override: int | None = None  # where it faces, when that differs from its beach
    women_only: bool = False  # women and children only (McIver's)

    @property
    def facing(self):
        """For on/offshore wind: you're sitting on the deck in the same breeze as the beach next door."""
        return self.facing_override if self.facing_override is not None else self.beach.facing


_BEACH = {b.name: b for b in BEACHES}

# Surf spots share the water (and Beachwatch site) of the beach they break off
BEACH_FOR_SURF = {
    "Bondi (south end)": _BEACH["Bondi (north end)"],
    "Maroubra": _BEACH["Maroubra"],
    "Bronte": _BEACH["Bronte"],
    "Coogee": _BEACH["Coogee"],
}
for _sp in SURF_SPOTS:
    _sp.beach = BEACH_FOR_SURF[_sp.name]

POOLS = [
    # R-P7: Thursdays. Sits at Bondi's south end facing east, not the south-east of the north end
    Pool("Bondi Icebergs", _BEACH["Bondi (north end)"], 1.0, cleaning_day=3, facing_override=90),
    Pool("Bronte Baths", _BEACH["Bronte"], 0.8, cleaning_day=2, cleaning_before_low=True),  # R-P7: Wednesdays
    Pool("Giles Baths", _BEACH["Coogee"], 0.8, best_tide="mid"),  # R-P5
    Pool("Wylie's Baths", _BEACH["Coogee"], 0.6, best_tide="low", opens=7),  # R-P1, R-P8
    Pool("Ross Jones Pool", _BEACH["Coogee"], 0.9, cleaning_day=0),  # R-P7: Mondays
    Pool("Mahon Pool", _BEACH["Maroubra"], 1.0, best_tide="mid_high"),  # R-P3
    # Women and children only; cleaned Tuesdays; 7am-7pm Oct-Mar, 7am-4pm in winter (from 1 Apr; the bot's
    # winter hours start 13 Apr, so the first fortnight of April shows it open an hour late)
    Pool(
        "McIver's Ladies Baths",
        _BEACH["Coogee"],
        0.7,
        best_tide="low",
        cleaning_day=1,
        opens=7,
        closes_winter=16,
        women_only=True,
    ),
    # Rings of rocks on the sand at South Maroubra: swim near high tide, empty at very low tide
    Pool("South Maroubra Rockpool", _BEACH["Maroubra"], 0.8, best_tide="mid_high", facing_override=70),
]
# Ivor Rowe (a small wading pool), Wally Weekes (empties at low tide) and North Bondi's kids' pool are left out

POOL_COORDS = {
    "Bondi Icebergs": (-33.8953, 151.2744),
    "Bronte Baths": (-33.9052, 151.2693),
    "Giles Baths": (-33.9202, 151.2606),
    "Wylie's Baths": (-33.9256, 151.2594),
    "Ross Jones Pool": (-33.9228, 151.2578),
    "Mahon Pool": (-33.9430, 151.2639),
    "McIver's Ladies Baths": (-33.9242, 151.2587),
    "South Maroubra Rockpool": (-33.9536, 151.2583),
}


@dataclass(frozen=True, eq=False)  # fixed once defined; compared by identity
class Region:
    """One stretch of coast: its spots, where its forecasts come from, its favourite and its calendar."""

    id: str  # "eastern"
    name: str  # "Eastern suburbs"
    key: str  # session and calendar event id prefix: Google wants base32hex, so letters a-v only
    beaches: list
    pools: list
    surf: list
    coords: dict  # map pins, by spot name ("<name> surf" for surf breaks, which share names with beaches)
    forecast_point: tuple  # weather (a blend of the land and sea cells either side)
    marine_point: tuple  # swell, sea temperature and tides; beaches differ via k
    favourite: str  # wins close calls (R-TB1)
    calendar_env: str  # env var holding the region's Google Calendar id
    tiles: str  # map/<tiles>.pmtiles
    bounds: tuple  # ((south, west), (north, east)) the map can pan within; inside the tiles' bbox
    rain_gauges: tuple = ("94768", "94767")  # BOM stations: Observatory Hill, Sydney Airport

    def pin(self, spot):
        return self.coords[f"{spot.name} surf" if isinstance(spot, SurfSpot) else spot.name]


EASTERN = Region(
    id="eastern",
    name="Eastern suburbs",
    key="beach",
    beaches=BEACHES,
    pools=POOLS,
    surf=SURF_SPOTS,
    coords={**COORDS, **POOL_COORDS, **{f"{name} surf": pin for name, pin in SURF_COORDS.items()}},
    forecast_point=(-33.914, 151.267),  # Clovelly
    marine_point=(-33.92, 151.33),
    favourite="Clovelly",
    calendar_env="BEACH_CALENDAR_ID",
    tiles="eastern-suburbs",
    bounds=((-34.05, 151.05), (-33.80, 151.40)),  # = the eastern-suburbs.pmtiles bbox
)


# ---------------------------------------------------------------- Northern beaches (northern-beaches-knowledge.md)
NORTHERN_BEACHES = [
    # §2. Ocean beaches, south to north
    Beach("Manly", 75, {"NE": 0.7, "E": 0.8, "SE": 0.6, "S": 0.4}, 1, 10, 6, "South Steyne Beach"),
    Beach(
        "Shelly Beach",
        290,
        {"NE": 0.3, "E": 0.3, "SE": 0.15, "S": 0.1},
        1,
        10,
        2,
        "Shelly Beach (Manly)",
        swim_limit=0.6,
        snorkel=True,
    ),  # faces W into Cabbage Tree Bay; R-NS1, R-NS2
    Beach("Queenscliff", 105, {"NE": 0.7, "E": 0.9, "SE": 0.8, "S": 0.7}, 1, 10, 6, "Queenscliff Beach"),  # R-NL1
    Beach("Freshwater", 130, {"NE": 0.6, "E": 0.9, "SE": 0.9, "S": 0.8}, 1, 20, 7, "Freshwater Beach"),
    Beach("South Curl Curl", 115, {"NE": 0.7, "E": 1.0, "SE": 1.0, "S": 0.9}, 5, 20, 7, "South Curl Curl Beach"),
    Beach(
        "North Curl Curl", 130, {"NE": 0.5, "E": 0.9, "SE": 1.0, "S": 0.9}, 10, 20, 6, "North Curl Curl Beach"
    ),  # R-NL1
    Beach("Dee Why", 125, {"NE": 0.6, "E": 0.9, "SE": 0.8, "S": 0.7}, 10, 20, 6, "Dee Why Beach"),
    Beach(
        "Long Reef", 155, {"NE": 0.3, "E": 0.7, "SE": 1.0, "S": 0.9}, 5, 20, 6, "Long Reef Beach"
    ),  # NE wind offshore; R-NL1
    Beach(
        "Collaroy", 75, {"NE": 0.8, "E": 0.7, "SE": 0.4, "S": 0.25}, 1, 5, 5, "Collaroy Beach"
    ),  # sheltered from southerlies
    Beach(
        "North Narrabeen",
        110,
        {"NE": 0.9, "E": 1.0, "SE": 0.9, "S": 0.7},
        1,
        20,
        7,
        "North Narrabeen Beach",
        swim_limit=1.0,
    ),  # R-NS3, R-NL1
    Beach("Warriewood", 80, {"NE": 0.9, "E": 0.9, "SE": 0.6, "S": 0.4}, 5, 20, 6, "Warriewood Beach"),
    Beach("Mona Vale", 115, {"NE": 0.8, "E": 1.0, "SE": 0.9, "S": 0.7}, 1, 20, 7, "Mona Vale Beach"),
    Beach("Bungan", 115, {"NE": 0.7, "E": 1.0, "SE": 0.9, "S": 0.8}, 1, 20, 7, "Bungan Beach"),  # R-NPT3
    Beach("Newport", 95, {"NE": 0.7, "E": 0.6, "SE": 0.45, "S": 0.3}, 1, 20, 6, "Newport Beach"),  # Newport Reef lee
    Beach("Bilgola", 125, {"NE": 0.6, "E": 0.9, "SE": 0.7, "S": 0.7}, 10, 20, 6, "Bilgola Beach"),
    Beach("Avalon", 125, {"NE": 0.7, "E": 1.0, "SE": 1.0, "S": 0.9}, 20, 30, 7, "Avalon Beach"),  # "often" [HEURISTIC]
    Beach(
        "Whale Beach", 95, {"NE": 0.9, "E": 1.0, "SE": 0.9, "S": 0.7}, 10, 20, 7, "Whale Beach"
    ),  # "often" [HEURISTIC]
    Beach("Palm Beach", 75, {"NE": 0.8, "E": 0.8, "SE": 0.5, "S": 0.35}, 10, 20, 6, "Palm Beach"),  # south end
    # §3. Harbour and Pittwater: estuarine, so the 3-day rain rule (R-NL2)
    Beach(
        "Manly Cove",
        195,
        {"NE": 0.0, "E": 0.1, "SE": 0.1, "S": 0.05},
        1,
        20,
        1,
        "Manly Cove",
        poor_grade=True,
        harbour=True,
    ),
    Beach(
        "Little Manly Cove",
        190,
        {"NE": 0.0, "E": 0.1, "SE": 0.1, "S": 0.05},
        5,
        20,
        1,
        "Little Manly Cove",
        poor_grade=True,
        harbour=True,
    ),
    Beach(
        "Fairlight",
        190,
        {"NE": 0.05, "E": 0.15, "SE": 0.15, "S": 0.1},
        5,
        20,
        1,
        "Fairlight Beach",
        poor_grade=True,
        harbour=True,
    ),  # "receives low swell through the heads"
    Beach(
        "Forty Baskets",
        60,
        {"NE": 0.0, "E": 0.1, "SE": 0.1, "S": 0.05},
        5,
        20,
        1,
        "Forty Baskets Pool",
        poor_grade=True,
        harbour=True,
    ),
    Beach(
        "Paradise Beach Baths",
        275,
        {"NE": 0.0, "E": 0.0, "SE": 0.0, "S": 0.0},
        1,
        10,
        1,
        "Paradise Beach Baths",
        poor_grade=True,
        harbour=True,
    ),
]
_NB = {b.name: b for b in NORTHERN_BEACHES}

NORTHERN_SURF = [
    SurfSpot("Manly", 75, {"NE": 0.8, "E": 0.9, "SE": 0.7, "S": 0.5}, bonus_dirs=(22, 67)),  # offshore WSW
    SurfSpot("Freshwater", 130, {"NE": 0.7, "E": 0.9, "SE": 0.9, "S": 0.7}),  # offshore NW
    SurfSpot("Curl Curl", 115, {"NE": 0.6, "E": 0.9, "SE": 1.0, "S": 0.9}, bonus_dirs=(112, 157)),  # R-NSU4
    # R-NSU2: only above 1.5m (needs a min_hs); faces NE along the point so S-WSW is offshore
    SurfSpot("Dee Why Point", 40, {"NE": 0.2, "E": 0.5, "SE": 0.9, "S": 1.0}, max_hs=4.0, bonus_dirs=(147, 192)),
    SurfSpot("Long Reef", 115, {"NE": 0.3, "E": 0.8, "SE": 1.0, "S": 0.9}, bonus_dirs=(112, 157)),  # offshore W-WNW
    SurfSpot("North Narrabeen", 115, {"NE": 1.0, "E": 1.0, "SE": 0.8, "S": 0.6}, max_hs=3.0, bonus_dirs=(22, 67)),
    SurfSpot("Warriewood", 60, {"NE": 0.8, "E": 1.0, "SE": 0.8, "S": 0.5}, bonus_dirs=(101, 124)),  # SSW offshore
    SurfSpot("Newport", 95, {"NE": 0.8, "E": 0.8, "SE": 0.6, "S": 0.4}, max_hs=2.0),  # The Peak, small-moderate
    SurfSpot("Avalon", 115, {"NE": 0.8, "E": 1.0, "SE": 1.0, "S": 0.9}, max_hs=3.0),  # offshore W
    SurfSpot("Palm Beach", 90, {"NE": 0.8, "E": 1.0, "SE": 1.0, "S": 0.8}, bonus_dirs=(112, 157)),  # offshore W
]

NORTHERN_BEACH_FOR_SURF = {
    "Manly": _NB["Manly"],
    "Freshwater": _NB["Freshwater"],
    "Curl Curl": _NB["North Curl Curl"],
    "Dee Why Point": _NB["Dee Why"],
    "Long Reef": _NB["Long Reef"],
    "North Narrabeen": _NB["North Narrabeen"],
    "Warriewood": _NB["Warriewood"],
    "Newport": _NB["Newport"],
    "Avalon": _NB["Avalon"],
    "Palm Beach": _NB["Palm Beach"],
}
for _sp in NORTHERN_SURF:
    _sp.beach = NORTHERN_BEACH_FOR_SURF[_sp.name]

# cleaning_day = the weekday the pool RE-OPENS (it's shut from the previous evening, often until 5pm): R-NP1
NORTHERN_POOLS = [
    Pool("Fairy Bower", _NB["Shelly Beach"], 0.7, cleaning_day=2, facing_override=10),  # Wednesdays, daytime (R-NP2)
    Pool("Queenscliff Rockpool", _NB["Queenscliff"], 0.9, cleaning_day=2),  # Tue night -> Wed
    Pool("Freshwater Rockpool", _NB["Freshwater"], 0.9, cleaning_day=3),  # Wed night -> Thu
    Pool("North Curl Curl Rockpool", _NB["North Curl Curl"], 1.0, best_tide="low"),  # never cleaned; R-NP3
    Pool("South Curl Curl Rockpool", _NB["South Curl Curl"], 0.9, cleaning_day=0),  # Sun night -> Mon
    Pool("Dee Why Rockpool", _NB["Dee Why"], 0.8, cleaning_day=4),  # Thu night -> Fri
    Pool("Collaroy Rockpool", _NB["Collaroy"], 0.7, cleaning_day=1),  # Mon night -> Tue
    Pool("North Narrabeen Rockpool", _NB["North Narrabeen"], 0.8, cleaning_day=1),  # Mon night -> Tue
    Pool("Mona Vale Rockpool", _NB["Mona Vale"], 0.9, cleaning_day=3),  # Wed night -> Thu
    Pool("Newport Rockpool", _NB["Newport"], 0.6, cleaning_day=3),  # Wed night -> Thu
    Pool("Bilgola Rockpool", _NB["Bilgola"], 0.8, cleaning_day=2),  # Tue night -> Wed
    Pool("Avalon Rockpool", _NB["Avalon"], 0.9, cleaning_day=4),  # Thu night -> Fri
    Pool("Whale Beach Rockpool", _NB["Whale Beach"], 0.8, cleaning_day=4),  # Thu night -> Fri
    Pool("Palm Beach Rockpool", _NB["Palm Beach"], 0.7, cleaning_day=0),  # Sun night -> Mon
    Pool("Fairlight Rockpool", _NB["Fairlight"], 0.2, cleaning_day=3),  # Thursdays, daytime (R-NP2)
]

NORTHERN_COORDS = {  # on the sand: OSM natural=beach polygon centres (§2, §3)
    "Manly": (-33.7981, 151.2893),
    "Shelly Beach": (-33.8006, 151.2980),
    "Queenscliff": (-33.7878, 151.2881),
    "Freshwater": (-33.7818, 151.2909),
    "South Curl Curl": (-33.7720, 151.2943),  # south part of the Curl Curl polygon
    "North Curl Curl": (-33.7680, 151.2979),  # north part of the Curl Curl polygon
    "Dee Why": (-33.7505, 151.2990),
    "Long Reef": (-33.7447, 151.3075),
    "Collaroy": (-33.7286, 151.3007),
    "North Narrabeen": (-33.7072, 151.3046),
    "Warriewood": (-33.6904, 151.3087),
    "Mona Vale": (-33.6826, 151.3122),
    "Bungan": (-33.6675, 151.3192),
    "Newport": (-33.6537, 151.3237),
    "Bilgola": (-33.6454, 151.3281),
    "Avalon": (-33.6351, 151.3329),
    "Whale Beach": (-33.6106, 151.3317),
    "Palm Beach": (-33.5978, 151.3251),  # centre of the patrolled southern 600m, not the whole 2.3km
    "Manly Cove": (-33.7989, 151.2827),
    "Little Manly Cove": (-33.8065, 151.2866),
    "Fairlight": (-33.7999, 151.2750),
    "Forty Baskets": (-33.8035, 151.2700),
    "Paradise Beach Baths": (-33.6243, 151.3168),
}
NORTHERN_POOL_COORDS = {  # OSM leisure=swimming_pool polygon centres (main pool where there's a toddler pool too)
    "Fairy Bower": (-33.8008, 151.2945),
    "Queenscliff Rockpool": (-33.7863, 151.2894),
    "Freshwater Rockpool": (-33.7816, 151.2948),
    "North Curl Curl Rockpool": (-33.7676, 151.3016),
    "South Curl Curl Rockpool": (-33.7745, 151.2934),
    "Dee Why Rockpool": (-33.7552, 151.2988),
    "Collaroy Rockpool": (-33.7335, 151.3044),
    "North Narrabeen Rockpool": (-33.7035, 151.3093),
    "Mona Vale Rockpool": (-33.6787, 151.3166),
    "Newport Rockpool": (-33.6585, 151.3246),
    "Bilgola Rockpool": (-33.6474, 151.3278),
    "Avalon Rockpool": (-33.6376, 151.3322),
    "Whale Beach Rockpool": (-33.6135, 151.3322),
    "Palm Beach Rockpool": (-33.5998, 151.3278),
    "Fairlight Rockpool": (-33.8002, 151.2755),
}
NORTHERN_SURF_COORDS = {  # just seaward of each break, checked to be on the water side of the OSM coastline
    "Manly": (-33.7925, 151.2905),
    "Freshwater": (-33.7830, 151.2925),
    "Curl Curl": (-33.7695, 151.3000),
    "Dee Why Point": (-33.7548, 151.3008),
    "Long Reef": (-33.7488, 151.3060),
    "North Narrabeen": (-33.7045, 151.3075),
    "Warriewood": (-33.6898, 151.3112),
    "Newport": (-33.6500, 151.3265),
    "Avalon": (-33.6366, 151.3350),
    "Palm Beach": (-33.5905, 151.3285),
}

NORTHERN = Region(
    id="northern",
    name="Northern beaches",
    key="north",  # base32hex: letters a-v only
    beaches=NORTHERN_BEACHES,
    pools=NORTHERN_POOLS,
    surf=NORTHERN_SURF,
    coords={
        **NORTHERN_COORDS,
        **NORTHERN_POOL_COORDS,
        **{f"{name} surf": pin for name, pin in NORTHERN_SURF_COORDS.items()},
    },
    forecast_point=(-33.752, 151.297),  # Dee Why: land cell by Narrabeen Lagoon, sea cell off Curl Curl
    marine_point=(-33.70, 151.37),  # MFWAM cell (-33.708, 151.375), ~6km off Narrabeen
    favourite="Shelly Beach",
    calendar_env="BEACH_CALENDAR_ID_NORTH",
    tiles="northern-beaches",
    bounds=((-33.87, 151.05), (-33.53, 151.45)),  # = the northern-beaches.pmtiles bbox
    rain_gauges=("94759", "94768"),  # Terrey Hills, Observatory Hill
)
REGIONS = [EASTERN, NORTHERN]
