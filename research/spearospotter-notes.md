# SpearoSpotter notes (ben-charlton/spearoSpotter, read 2026-11-10)

## 1. What it is
- Picks **one** recommended spearfishing spot per day (next 7 days) for Sydney, live at spearospotter.online. Small repo, last push Feb 2025.
- Stack: Express + TypeScript backend, Postgres via Knex, Redis cache (6 h), React + Vite + MUI frontend, deployed on GKE.
- Data: **Stormglass** only (paid API key), `sg` source.
  - `/v2/weather/point` params: `cloudCover, waveHeight, airTemperature, swellDirection, swellHeight, swellPeriod, secondarySwellPeriod, secondarySwellDirection, secondarySwellHeight, waterTemperature, windDirection, windSpeed`.
  - `/v2/tide/extremes/point` (high/low times and heights).
  - Both use **one point for every spot**: Long Reef (-33.740149, 151.317036) (`backend/src/services/weatherService.ts`, `tideService.ts`).
  - Only wind, swell and tide go into the score. Cloud, air and water temperature and waveHeight are displayed but don't affect it.
- **No license.** Use it for ideas only and don't copy code.

## 2. Spots and scoring
Spots (`backend/knex/seeds/seed_data.ts`). Every spot is northern beaches or Manly, with **no eastern suburbs**. The `fish` table is commented out, so there are no species.

| Spot | lat, lon | facing | protected_from | swell/wind/tide/refr sens | best_at | depth |
|---|---|---|---|---|---|---|
| Long Reef | -33.7401, 151.3170 | 67.5 | 180 | .5/.8/.3/.1 | low | 10 |
| Deadmans | -33.8015, 151.3023 | 67.5 | 180 | .9/.4/.7/.9 | high | 20 |
| Avalon | -33.6262, 151.3414 | 112.5 | 0 | .9/.6/.7/.9 | high | 20 |
| Newport Reef N | -33.6594, 151.3285 | 45 | 180 | .5/.9/.8/.4 | low | 15 |
| Newport Reef S | -33.6613, 151.3275 | 135 | 0 | .5/.9/.8/.4 | low | 15 |
| Bungan Rockpool | -33.6762, 151.3199 | 100 | 30 | .6/.9/.8/.5 | low | 20 |
| North Curl Curl | -33.7675, 151.3028 | 90 | 0 | 1/.6/.7/.9 | high | 20 |
| Freshwater | -33.7822, 151.2960 | 112.5 | 35 | .5/.6/.2/.6 | low | 20 |

Each spot also has free-text `description` and `entrance` (for example "Rock off, best with high tide and small swell"). Avalon's text is copied from Deadmans and mentions Shelly Beach.

Scoring (`backend/src/recommendation/recommendationModel.ts`): `score = 60 - (swell + wind + refraction + tide)`, floored at 0. The top spot is returned.
- **Swell:** power `H²·T` (primary + secondary) × `swell_sensitivity` × interaction. The interaction is `(0.9·exp(-(Δ1/45)²) + 0.3·exp(-(Δ2/45)²))·swell_sensitivity − (swells >90° apart ? 0.2 : 0)`. Sensitivity is applied twice.
- **Wind:** `wind_speed × sens × 0.5(1+cos(wind−protected_from)) × exp(-((wind−facing)%360/90)²)`.
- **Refraction:** `max(0,(1−cos(swellDir−facing)))·sens·10`. It doesn't depend on swell size.
- **Tide:** takes the extreme nearest 07:00 and computes `height·tide_sensitivity`, then multiplies by `×0.5` if it matches `best_at`, otherwise `×1.5`.
- **Time of day:** weather is read at `day.setUTCHours(7)` (`models/weatherModel.ts`), which is **17:00–18:00 Sydney time**, not the 7 am dive the README describes.

## 3. Visibility
**No visibility model.** There is no rain, runoff, prior-day swell, SST trend or water-quality input. The only nod is a seed comment: "wind_sensitivity … Higher means wind significantly impacts visibility." Every factor is a single snapshot hour with no history. Nothing would catch the case "fine on the surface, milky at ~3 m". That is a subsurface layer: a turbid layer under a clear surface, resuspended sediment from earlier groundswell, plankton, or cold upwelled water. Catching it needs lagged swell energy, rain/runoff history and SST drops, and SpearoSpotter has none of these.

## 4. Strengths, gaps, questionable assumptions
Strengths:
- Spot fields like facing, protected_from, best_at, depth and entrance.
- H²T swell energy and use of the secondary swell.
- Tide is treated as a per-spot preference.

Gaps and bugs:
- One forecast point for all spots, and the forecast is taken at 5–6 pm local.
- **Wind protection is inverted:** `protectionScale` is 1 when wind comes *from* `protected_from`.
- The `%360` without wrapping means 350° vs 10° counts as 340° apart.
- The opposing-swell "penalty" *reduces* demerits.
- Refraction penalises swell from *behind* the spot, even when it's flat.
- Tide height is relative to MSL (Stormglass default), so lows are negative. A "wrong" low tide becomes a 1.5× **bonus**.
- Stormglass windSpeed is m/s, but the UI labels it km/h.
- The tide request has no date, so future days likely reuse today's extremes.
- Weights are hand-set and nothing is validated against dives.
- Only the winner is shown, with no per-spot scores and no reasons.

## 5. Borrow (ranked)
1. Per-spot `best_tide` + `tide_sensitivity`, using an hourly tide curve (state of tide at dive time, not the nearest extreme).
2. Per-spot entry notes and an entry gate: rock entries need small swell + the right tide. Make this a hard "no-go" rule, not a demerit.
3. Swell energy ∝ H²T summed over trains, with a direction kernel per spot. Our OSM swell windows already do this better; just add the energy term.
4. A "picks up wrapping south swell" flag (their refraction_sensitivity), done properly via our exposure windows.
5. Depth per spot (shallow spots suffer more from resuspension).
6. Species and season (their unused `fish` table): a nice later extra.

Beach Bot already does these better:
- Per-spot hourly Open-Meteo marine data (free, no key) versus one point.
- Geometric swell exposure versus hand-set facing and sensitivity numbers.
- Rain rules and Beachwatch, which are the core of a visibility model.
- Lifeguard reports as ground truth.
- Hourly scoring with reasons for every spot.
- Backtesting on dated sessions.

For the milky-at-3 m case, build what SpearoSpotter lacks: lagged swell energy (24–72 h), rain over 48–72 h and runoff/estuary proximity, SST drop (upwelling), and dive reports to calibrate.
