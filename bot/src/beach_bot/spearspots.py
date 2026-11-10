"""Shore spearfishing spots in each region (research/spearfishing-spots.md). Only spots it's legal to spear from
shore: closed waters (Clovelly and Gordons Bay, Cabbage Tree Bay, North Harbour, Narrabeen Lake, Port Hacking,
the ocean beaches away from their ends) aren't listed at all, and nor are the spots to stay away from (the
Diamond Bay and Turimetta outfalls, Magic Point's grey nurse sharks, Bare Island while it's shut)."""

import json
from dataclasses import dataclass
from pathlib import Path

# Each spot's reef from the NSW seabed survey (scripts/build_spear_reefs.py): its pin, depth range, how much of the
# bottom is reef. A spot that isn't in it keeps its hand-set pin and depth
REEFS = (
    json.loads((Path(__file__).parent / "spear_reefs.json").read_text())
    if (Path(__file__).parent / "spear_reefs.json").exists()
    else {}
)


@dataclass(frozen=True, eq=False)  # fixed once defined; compared by identity
class SpearSpot:
    name: str
    facing: int  # bearing the reef faces, looking out to sea
    k: dict  # how much of the open-ocean swell reaches the reef, by swell sector (the swell model's prior)
    depth: float  # m: where most of the diving is, for surge on the bottom (the survey's reef depth wins)
    entry_at: tuple = None  # (lat, lon) where you get in: the survey looks for reef from here
    entry: str = "platform"  # "platform" (rock entry, swell washes over it) or "cove" (a sheltered way in)
    water: str = "open"  # "open" coast, a "bay" (Botany Bay, Broken Bay) or the "harbour": sets its usual vis
    outlet: str | None = None  # runoff nearby: "lagoon" (shut after heavy rain), "estuary" or "drain"
    best_tide: str | None = None  # "high" (the exit needs water over the rocks) or "incoming" (clean water in)
    wind_shelter: tuple = None  # (from, to): wind from here is blocked and blows at about half strength
    level: str = "all"  # "all" or "advanced" (long swims, jump entries, exposed points)
    checked: bool = True  # False: from guides only, nothing dated to check it against
    entry_note: str | None = None  # how to get in, for the card

    @property
    def advanced(self):
        return self.level == "advanced" or not self.checked

    @property
    def reef(self):
        """The survey's record for this spot (pin, depth_m, range_m, reef share, steep share), or {}."""
        return REEFS.get(self.name, {})

    @property
    def dive_depth(self):
        return self.reef.get("depth_m", self.depth)


SPEAR_SPOTS = [
    SpearSpot(
        "North Bondi",
        150,
        {"NE": 0.2, "E": 0.6, "SE": 0.9, "S": 0.9},
        10,
        entry_at=(-33.8912, 151.2822),
        entry="cove",
        entry_note="In at the boat ramp, not the beach",
    ),
    SpearSpot(
        "Mackenzies Bay",
        70,
        {"NE": 0.7, "E": 0.8, "SE": 0.5, "S": 0.3},
        6,
        entry_at=(-33.8990, 151.2762),
        entry_note="Off Flat Rock, on the Mackenzies Point platform",
    ),
    SpearSpot(
        "Wedding Cake Island",
        100,
        {"NE": 0.8, "E": 1.0, "SE": 1.0, "S": 0.8},
        10,
        entry_at=(-33.9259, 151.2654),
        level="advanced",
        entry_note="About a 600m swim from Trenerry Reserve",
    ),
    SpearSpot(
        "Lurline Bay", 80, {"NE": 0.7, "E": 0.9, "SE": 0.6, "S": 0.3}, 8, entry_at=(-33.9375, 151.2618), checked=False
    ),
    SpearSpot(
        "Mahon Pool",
        90,
        {"NE": 0.8, "E": 1.0, "SE": 0.8, "S": 0.5},
        10,
        entry_at=(-33.9430, 151.2639),
        best_tide="high",
        entry_note="Off the platform north of the pool; the exit is a slot in the rock",
    ),
    SpearSpot(
        "South Maroubra",
        60,
        {"NE": 0.7, "E": 0.7, "SE": 0.35, "S": 0.2},
        8,
        entry_at=(-33.9535, 151.2598),
        entry="cove",
        entry_note="In at the inlet in the platform, not off the beach",
    ),
    SpearSpot(
        "Long Bay",
        100,
        {"NE": 0.3, "E": 0.5, "SE": 0.5, "S": 0.3},
        6,
        entry_at=(-33.9685, 151.2546),
        entry="cove",
        outlet="drain",
        best_tide="high",
        entry_note="In by the ocean pool on the south side",
    ),
    SpearSpot(
        "Little Bay",
        80,
        {"NE": 0.4, "E": 0.5, "SE": 0.4, "S": 0.2},
        8,
        entry_at=(-33.9790, 151.2545),
        entry="cove",
        best_tide="high",
        entry_note="Stay east of the marked line; not in or out off the beach",
    ),
    SpearSpot(
        "Cape Banks",
        150,
        {"NE": 0.1, "E": 0.5, "SE": 0.9, "S": 1.0},
        12,
        entry_at=(-34.0005, 151.2495),
        level="advanced",
        entry_note="Exposed, with current at the heads",
    ),
    SpearSpot(
        "Henry Head",
        180,
        {"NE": 0.05, "E": 0.3, "SE": 0.6, "S": 0.6},
        10,
        entry_at=(-33.9983, 151.2383),
        water="bay",
        outlet="estuary",
        best_tide="incoming",
        level="advanced",
        entry_note="A long walk in, and the shipping channel's just off the head",
    ),
    SpearSpot(
        "La Perouse",
        200,
        {"NE": 0.05, "E": 0.2, "SE": 0.4, "S": 0.4},
        8,
        entry_at=(-33.9901, 151.2304),
        entry="cove",
        water="bay",
        outlet="estuary",
        best_tide="incoming",
        entry_note="Astrolabe Cove or Larpa Point (Bare Island is shut until about late 2027)",
    ),
    SpearSpot(
        "Kurnell (bay side)",
        20,
        {"NE": 0.3, "E": 0.2, "SE": 0.05, "S": 0.05},
        8,
        entry_at=(-34.0020, 151.2248),
        entry="cove",
        water="bay",
        outlet="estuary",
        best_tide="incoming",
        entry_note="In at The Steps; the park gates set the hours",
    ),
    SpearSpot(
        "The Leap and Yena",
        120,
        {"NE": 0.4, "E": 0.8, "SE": 1.0, "S": 0.8},
        15,
        entry_at=(-34.0046, 151.2294),
        level="advanced",
        best_tide="high",
        entry_note="A jump off the shelf; the only exit is back at The Steps",
    ),
    SpearSpot(
        "Boat Harbour",
        170,
        {"NE": 0.1, "E": 0.4, "SE": 0.7, "S": 0.8},
        5,
        entry_at=(-34.0400, 151.1990),
        entry="cove",
        checked=False,
        entry_note="Merries Reef; 4WD access only",
    ),
    SpearSpot(
        "Camp Cove",
        300,
        {"NE": 0.08, "E": 0.05, "SE": 0.02, "S": 0.0},
        6,
        entry_at=(-33.8389, 151.2787),
        entry="cove",
        water="harbour",
        outlet="estuary",
        best_tide="incoming",
    ),
]

# Hand-set pins, for any spot the survey hasn't placed: McFadyen's published marks, else just off the rocks (OSM)
SPEAR_COORDS = {sp.name: sp.entry_at for sp in SPEAR_SPOTS}

NORTHERN_SPEAR = [
    SpearSpot(
        "Freshwater Head",
        60,
        {"NE": 0.7, "E": 0.8, "SE": 0.4, "S": 0.3},
        5,
        entry_at=(-33.7815, 151.2948),
        outlet="drain",
        best_tide="high",
        entry_note="Off the Freshwater side; Manly Lagoon runs out on the Queenscliff side",
    ),
    SpearSpot(
        "Dee Why Head",
        110,
        {"NE": 0.6, "E": 0.9, "SE": 0.8, "S": 0.6},
        6,
        entry_at=(-33.7685, 151.3015),
        outlet="drain",
        best_tide="high",
        checked=False,
        entry_note="The reef at North Curl Curl's north end; Curl Curl Lagoon runs out at the south end",
    ),
    SpearSpot(
        "Long Reef",
        20,
        {"NE": 0.5, "E": 0.4, "SE": 0.2, "S": 0.1},
        6,
        entry_at=(-33.7395, 151.3100),
        entry="cove",
        best_tide="high",
        wind_shelter=(135, 200),
        entry_note="In off Fishermans Beach",
    ),
    SpearSpot(
        "Narrabeen Head",
        80,
        {"NE": 0.8, "E": 0.9, "SE": 0.6, "S": 0.4},
        8,
        entry_at=(-33.7038, 151.3100),
        outlet="lagoon",
        best_tide="high",
    ),
    SpearSpot(
        "Mona Vale Headland",
        90,
        {"NE": 0.8, "E": 1.0, "SE": 0.8, "S": 0.6},
        8,
        entry_at=(-33.6747, 151.3198),
        checked=False,
    ),
    SpearSpot(
        "Bungan Head", 90, {"NE": 0.8, "E": 1.0, "SE": 0.8, "S": 0.6}, 8, entry_at=(-33.6640, 151.3239), checked=False
    ),
    SpearSpot(
        "Newport Reef",
        100,
        {"NE": 0.7, "E": 0.9, "SE": 0.7, "S": 0.5},
        6,
        entry_at=(-33.6545, 151.3240),
        checked=False,
        entry_note="Off the rocks at Newport's south end",
    ),
    SpearSpot(
        "Bilgola Head", 80, {"NE": 0.8, "E": 1.0, "SE": 0.7, "S": 0.5}, 8, entry_at=(-33.6438, 151.3339), checked=False
    ),
    SpearSpot(
        "Avalon (north headland)",
        100,
        {"NE": 0.6, "E": 0.9, "SE": 0.7, "S": 0.5},
        6,
        entry_at=(-33.6340, 151.3335),
        checked=False,
        entry_note="Under Bangalley Head, off Avalon's north end",
    ),
    SpearSpot(
        "Little Head", 70, {"NE": 0.8, "E": 0.9, "SE": 0.6, "S": 0.4}, 8, entry_at=(-33.6065, 151.3359), checked=False
    ),
    SpearSpot(
        "Barrenjoey Head",
        0,
        {"NE": 0.6, "E": 0.4, "SE": 0.15, "S": 0.05},
        8,
        entry_at=(-33.5800, 151.3260),
        entry="cove",
        water="bay",
        outlet="estuary",
        best_tide="incoming",
        wind_shelter=(150, 230),
        entry_note="Strong tidal current at the head",
    ),
]

NORTHERN_SPEAR_COORDS = {sp.name: sp.entry_at for sp in NORTHERN_SPEAR}

# The survey's pin wins: on the reef nearest the entry, at diving depth
for _sp in (*SPEAR_SPOTS, *NORTHERN_SPEAR):
    if _sp.reef:
        (SPEAR_COORDS if _sp in SPEAR_SPOTS else NORTHERN_SPEAR_COORDS)[_sp.name] = tuple(_sp.reef["pin"])
