"""Fit spearfishing's visibility model (spear.py, R-SP1) to the Reef Life Survey's dated visibility readings.

    vis = base[water] x exp(-a x swell memory) x exp(-b x rain index) x season

Each survey site is put down as open coast, bay or harbour (HARBOUR and BAY below), and takes its swell exposure
from the nearest of our spearfishing spots of the same kind (sites further than MAX_KM from any are dropped). Its
swell memory and rain index are worked out at 10am that day exactly as the live score does, from hourly history.
log(vis) is then linear in the parameters, so it's ordinary least squares. Leave-one-year-out testing says how well
it does on years it hasn't seen.

  uv run python scripts/fit_spear_vis.py NRMN.csv HISTORY.pkl

NRMN.csv: the IMOS NRMN survey list for Sydney (WFS imos:ep_survey_list_public_data, CSV, bbox 151.1,-34.1,
151.4,-33.55). HISTORY.pkl: {"eastern": hours, "northern": hours} of Open-Meteo marine + archive hourly fields
(2009 on). Neither is kept in the repo.
"""

import csv
import math
import pickle
import sys
from collections import defaultdict

import numpy as np

from beach_bot import spear
from beach_bot.beaches import EASTERN, NORTHERN
from beach_bot.forecast import Context

MAX_KM = 8
# Survey sites inside Sydney Harbour or Port Hacking, and in Botany Bay or Broken Bay (by NRMN site name)
HARBOUR = (
    "camp cove",
    "middle head",
    "inside north head",
    "inside south head",
    "fairlight",
    "old mans hat",
    "the blocks",
    "chowder",
    "clifton",
    "neilsen",
    "neilson",
    "georges head",
    "dobroyd",
    "quarantine",
    "steel point",
    "shark island",
    "green point",
    "kiribilly",
    "shiprock",
    "lilli pilli",
)
BAY = ("bare island", "kurnell", "la perouse", "henrys head", "browns rock", "cruwee", "dragon alley")


def water_of(site):
    s = site.lower()
    return "harbour" if any(k in s for k in HARBOUR) else "bay" if any(k in s for k in BAY) else "open"


WINTER, SUMMER = (6, 7, 8, 9), (12, 1, 2)


def km(a, b):
    dy = (a[0] - b[0]) * 111.3
    dx = (a[1] - b[1]) * 111.3 * math.cos(math.radians(a[0]))
    return math.hypot(dx, dy)


def fill(hours):
    """Before late 2021 the history has only the whole sea: read it as one swell, the way the live forecast falls
    back when it isn't split into trains."""
    for h in hours.values():
        if h.get("swell_wave_height") is None and h.get("wave_height") is not None:
            h["swell_wave_height"] = h["wave_height"]
            h["swell_wave_direction"] = h.get("wave_direction")
            h["swell_wave_period"] = h.get("wave_period")
        h.setdefault("wind_speed_10m", h.get("wind_speed_10m") or 0)
        h.setdefault("wind_direction_10m", h.get("wind_direction_10m") or 0)
    return hours


def rows(nrmn, hist):
    spots = [(sp, region.pin(sp), region.id) for region in (EASTERN, NORTHERN) for sp in region.spear]
    ctxs = {r: spear.SpearContext(Context(fill(hist[r]))) for r in hist}
    seen = defaultdict(list)
    for r in csv.DictReader(open(nrmn)):
        if not r["visibility"] or float(r["visibility"]) <= 0.5:  # 0 is how a missing reading comes through
            continue
        here = (float(r["latitude"]), float(r["longitude"]))
        water = water_of(r["site_name"])
        d, sp, rid = min((km(here, pin), sp, rid) for sp, pin, rid in spots if sp.water == water)
        if d > MAX_KM:
            continue
        seen[r["survey_date"], r["site_name"], sp.name].append(float(r["visibility"]))
    out = []
    for (day, _site, name), vis in seen.items():
        sp, _, rid = next(x for x in spots if x[0].name == name)
        sctx = ctxs[rid]
        t = f"{day}T10:00"
        if t not in sctx.ctx.index or sctx.ctx.hours[t].get("wave_height") is None:
            continue
        mem, _ = sctx.memory(sp, t)
        api = sctx.rain_index(t)
        out.append(
            {
                "day": day,
                "spot": name,
                "water": sp.water,
                "vis": float(np.median(vis)),
                "mem": mem,
                "api": api * (spear.OUTLET_RAIN if sp.outlet or sp.water != "open" else 1),
                "month": int(day[5:7]),
            }
        )
    return out


def design(rs):
    waters = sorted({r["water"] for r in rs})
    x = [
        [1.0 * (r["water"] == w) for w in waters]
        + [-r["mem"], -r["api"], 1.0 * (r["month"] in WINTER), 1.0 * (r["month"] in SUMMER)]
        for r in rs
    ]
    return np.array(x), np.log([r["vis"] for r in rs]), waters


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    rs = rows(sys.argv[1], pickle.load(open(sys.argv[2], "rb")))
    print(f"{len(rs)} spot-days, {len({r['day'] for r in rs})} dates")
    for w in sorted({r["water"] for r in rs}):
        print(f"  {w:<8} {sum(r['water'] == w for r in rs)}")
    x, y, waters = design(rs)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    base = {w: round(float(math.exp(beta[i])), 1) for i, w in enumerate(waters)}
    a, b, win, summ = beta[len(waters) :]
    print("base", base)
    print(
        f"a (swell memory) {a:.4f}  b (rain index) {b:.4f}  winter x{math.exp(win):.2f}  summer x{math.exp(summ):.2f}"
    )
    pred = x @ beta
    print(f"in-sample: Spearman {spearman(pred, y):.2f}, median error x{math.exp(np.median(np.abs(pred - y))):.2f}")
    # Leave one year out
    years = sorted({r["day"][:4] for r in rs})
    held_p, held_y = [], []
    for yr in years:
        tr = [i for i, r in enumerate(rs) if r["day"][:4] != yr]
        te = [i for i, r in enumerate(rs) if r["day"][:4] == yr]
        if not te:
            continue
        bt, *_ = np.linalg.lstsq(x[tr], y[tr], rcond=None)
        held_p += list(x[te] @ bt)
        held_y += list(y[te])
    held_p, held_y = np.array(held_p), np.array(held_y)
    base_only = np.array([np.median([y[j] for j, q in enumerate(rs) if q["water"] == r["water"]]) for r in rs])
    print(
        f"held-out years: Spearman {spearman(held_p, held_y):.2f},"
        f" median error x{math.exp(np.median(np.abs(held_p - held_y))):.2f}"
        f" (each water's median alone: x{math.exp(np.median(np.abs(base_only - y))):.2f})"
    )
    # By memory band, observed vs predicted medians
    for lo, hi in ((0, 5), (5, 15), (15, 40), (40, 1e9)):
        idx = [i for i, r in enumerate(rs) if lo <= r["mem"] < hi]
        if idx:
            print(
                f"  memory {lo:>3}-{hi:<6} n={len(idx):>3}  observed {math.exp(np.median(y[idx])):.1f} m"
                f"  predicted {math.exp(np.median(pred[idx])):.1f} m"
            )


if __name__ == "__main__":
    main()
