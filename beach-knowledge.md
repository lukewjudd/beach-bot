# Sydney Eastern Suburbs Beach Knowledge Base (for a daily beach-picker)

Compiled 2026-11-02. Purpose: turn local, surfer and agency knowledge into rules a scoring script can use with Open-Meteo weather and marine forecasts.

How to read the confidence tags:
- **[SRC]**: the number or fact is stated in the cited source.
- **[DERIVED]**: worked out from a sourced fact, for example offshore wind taken as the opposite of the sourced facing direction.
- **[HEURISTIC]**: no published number exists. This is a starting value to calibrate against what you see at the beach. Every heuristic says which sourced fact it rests on.

Source IDs such as `[S4]` refer to the **Sources** list at the end.

---

## 0. Key findings to read first

1. **Open-Meteo marine returns `null` waves at every one of these beaches with the default `cell_selection=land`.** You must pass `cell_selection=sea`. With that setting all nine beaches collapse onto only **two** MeteoFrance MFWAM cells, about 2–4 km offshore: (-33.875, 151.292) for Bondi–Clovelly and (-33.958, 151.292) for Coogee–Little Bay. ECMWF WAM with `cell_selection=sea` snaps Coogee/Maroubra/Malabar/Little Bay to (-33.989, 151.236), which sits near the Botany Bay entrance, so avoid it. **Per-beach differences therefore have to come from the orientation and shelter rules below, not from the model.** [S30 own API test, S29]
2. **Beachwatch has an undocumented public JSON/GeoJSON API**: `https://api.beachwatch.nsw.gov.au/public/sites/geojson` (246 sites; per-site `pollutionForecast` of Unlikely/Possible/Likely/Forecast not available, plus `latestResult` and `latestResultRating`). It works without a key (tested 2026-11-02). [S12]
3. Beachwatch rates **Gordons Bay as more rain-sensitive than Clovelly**: Gordons Bay "often after 10 mm", Clovelly "often after 20 mm". Beachwatch classes both as **ocean beaches, not enclosed waters**, so the 3-day harbour/estuary rule does not apply to them. [S10]
4. **Coogee has been graded Poor** (2022-23 and again in 2026). Poor-grade advice is to avoid swimming **for up to 3 days after rain**, not 1 day. [S10, S54]

---

## 1. Per-location table: beaches

Bearings are the direction the beach faces, looking out to sea. Wind and swell directions are the direction they come FROM.

| Location | Swim-area lat, lon | Faces (approx bearing) | Offshore wind (from) | Sheltered from | Ruined by (onshore) | Swell exposure E / NE / SE / S | Best for | Beachsafe hazard (1–10) | Patrol |
|---|---|---|---|---|---|---|---|---|---|
| **Bondi – North** (North Bondi SLSC end) | -33.8905, 151.2805 [S50 club -33.8900,151.2811, moved into water] | SSE–SE, ~150° [S1 "faces southeast"; S14 "faces nearly dead south"] | NNW–NW [S18, S19] | NE wind (Ben Buckler headland) [S19/S55]; E swell shadowed by Ben Buckler [S14] | S, SE, SSE onshore [DERIVED] | E: low–mod (shadowed) [S14] · NE: low (shadowed) [S14] · SE: high · S: **highest** (Bondi is a "south swell magnet") [S14, S15] | Calm swim when small. "Lowest waves and best swimming is in the northern half" [S1] | Beach overall 7 [S1]; north end commonly quoted 4/10 [S37] | Lifeguards year-round [S1, S10]; SLSC volunteers in summer [S1] |
| **Bondi – South** (Backpackers rip / Icebergs end) | -33.8925, 151.2765 [approx, S50] | SE, ~140° [S1] | NNW–NW [S18] | Partly from S wind by the south headland [HEURISTIC] | S/SE onshore | Higher energy than the north. "The left into the southern headland rip holding waves up to 2.5 m" [S1] | Surf (boards are restricted to the south) [S1, S19] | South end 7/10; Backpackers rip [S37] | Year-round lifeguards [S1] |
| **Tamarama** | -33.9007, 151.2709 [S12, S2] | E–ESE, ~100° [DERIVED from map; Beachsafe gives no bearing] | W–NW [S20] | Little shelter; narrow, deep embayment [S2] | E, NE, SE onshore | All E-sector swells hit it. "Energetic wave climate… at least one and often two rips" [S2] | Experienced swimmers only; **closed to boards during patrol hours** [S2] | **8** (Sydney's highest rescue rate, 5.5 per 1000 swimmers) [S2] | Late Sept to April [S10]; Waverley lifeguards year-round per [S2] (conflict) |
| **Bronte** | -33.9031, 151.2688 [S12, S3] | E, ~90° [DERIVED] | W / WNW [S21] | South-end reef is sheltered from S wind by cliffs [S21] | NE, E, SE onshore. NE wind brings bluebottles to the south end [S56] | E: high (best surf direction per surfnerd) · NE: high · SE: high (best per surf-forecast) · S: lower but the reef still works [S21] | Surf (Bronte Reef rights in E–SE swell; beach-break left in the north half) [S3]. Swim between the flags only. **Bronte Baths** for laps | 7. Rips at both ends, including the "Bronte Express" at the south; 130 rescues a year [S3] | Sept to May [S10] |
| **Clovelly** (favourite) | -33.9138, 151.2666 [S4] | SE, inlet axis ~120° [S4 "southeast-facing gap"]. UNSW calls it "south-facing" [S25] | NW [S22] | **Almost landlocked**: "most wave energy is expended breaking on the seaward arms" [S4]. Sheltered from N–NE wind (it blows down or off the inlet) [DERIVED] | SE wind blows straight down the inlet axis [DERIVED] | Low for all directions. SE is the most direct, through the mouth [DERIVED from S4]. A swell surge still enters the inlet [S46] | **Calm swim, snorkel** (popular SCUBA site [S4]), small pool on the south side | **2** ("lowest energy and quietest patrolled beach in Sydney") [S4] | Since May 2024: council lifeguards **every day, all year, sunrise to sunset** [S33]. Older Beachwatch text says late Sept to April [S10] |
| **Gordons Bay** | -33.9158, 151.2648 (snorkel trail start) [S50]; Beachwatch site -33.9157, 151.2646 [S12] | E, ~90° [DERIVED]. Wider mouth than Clovelly [S5] | W [DERIVED] | Beach is "deep at the rear and consequently well protected from most waves" [S5] | E, NE onshore [DERIVED] | More exposed than Clovelly. "Do not enter the water if there are waves in the bay" [S44] | **Snorkel/dive** (underwater nature trail). Not a beach swim: hard access, boat storage [S5] | **2** [S5] | **Unpatrolled** [S10] |
| **Coogee** | -33.9208, 151.2582 [S12, S6] | Bay opens SE per Beachsafe [S6]; beach faces ~E–ESE, ~100° [DERIVED] | W [S23] | SE and S swell blocked by **Wedding Cake Island**, 700 m offshore [S6, S23] | E, NE onshore. "Even a light onshore ruins the surf" [S23] | E: moderate · NE: moderate · SE: **low** (island lee) · S: low [S6, S23] | Swim (steep, reflective beach, rips usually absent; 0.4 rescues per 1000 beachgoers) [S6]; ocean pools at both ends | **4** [S6] | Lifeguards year-round [S10]; council hours 7am–7pm in daylight saving, 7am–5pm in winter [S34]; SLSC volunteers on weekends and holidays, late Sept–April [S34] |
| **Maroubra** (north/central) | -33.9475, 151.2572 [S7]; Beachwatch -33.9489, 151.2575 [S12] | E, ~90° [S7 "east-facing bay"] | W, NW, SW [S24] | Some protection from N wind [S57], though a summer N wind "can ruin the lot" at the north-end reefs [S57] | E, NE, SE onshore | E: **highest** · NE: high (The Reef works in NE–E) · SE: high · S: lower than Bondi [S7, S14, S24] | **Surf** (National Surfing Reserve) [S7] | **6**. 4–5 rip systems; Maroubra SLSC averages **285 rescues a year**, the most in NSW [S7] | Lifeguards year-round [S10] |
| **South Maroubra** (very south end) | -33.9514, 151.2573 [S12] | E–NE (lee of Magic Point) [DERIVED from S7] | W [DERIVED] | "Usually has lower waves" [S7]; S swell partly blocked by Magic Point [HEURISTIC] | E, NE onshore | Lower than the main beach [S7] | Swim at the southern end [S7]; South Maroubra Rockpool | Lower than the main beach (80 rescues a year) [S7] | Lifeguards year-round [S10] |
| **Malabar** (Long Bay) | -33.9644, 151.2523 [S8, S12] | SE / ESE, ~110° (1.3 km deep bay) [S8] | NW [DERIVED] | Deep bay: "lowered waves averaging less than 1 m" [S8] | E, SE straight up the bay [DERIVED] | E/SE: moderate (refracted) · NE: low · S: low [DERIVED from S8] | Calm swim, but "deep water just offshore" [S8]; left reef on the northern rocks in large SE swell [S8] | **3** [S8] | **Unpatrolled** (lifeguard tower only) [S8, S10] |
| **Little Bay** (south beach) | -33.9799, 151.2514 [S12, S9] | Bay faces E; the popular south beach faces **NE** [S9] | W–SW [DERIVED] | 100 m shallow rocky entrance lowers the waves. "Usually low wave to calm conditions inside the bay" [S9] | NE, E onshore at the south beach [DERIVED] | E: moderate (breaks at the entrance) · NE: moderate · SE/S: low [DERIVED from S9] | **Calm swim, beginner snorkel** [S9, S58] | **2** [S9] | **Unpatrolled** [S9, S10] |

### 1a. Surf-specific: when each spot starts working

| Spot | Works from (swell direction) | Starts working at (open-ocean Hs) | Holds / maxes out | Wind | Tide | Notes |
|---|---|---|---|---|---|---|
| Bondi South | S, SE best. Window NE–S [S19] | ≈0.6 m ("at least 2 ft" [S19]) | Left into the south rip holds up to **2.5 m** [S1]; closes out above head height [S55] | NNW/NW offshore [S18] | Mid, rising [S19] (another guide: all tides) | Hard boards are restricted to the south end [S19] |
| Bondi North / Ben Buckler | Big S/SE swell | **≥2 m** [HEURISTIC; Beachsafe: "during big swell the northern point, Ben Buckler, produces a good left" S1] | – | NW | – | Beginner-friendly beach break when small [S55] |
| Tamarama | NE–E (surfnerd) vs SE (surf-forecast): **conflict** [S20] | ≈0.6 m (surfnerd range 1–8 ft) [S20] | Inconsistent reef [S20] | NW [S20] | – | Closed to boards in patrol hours [S2]; "most dangerous beach in Sydney" [S59] |
| Bronte (beach + reef) | E best (surfnerd) / SE best (surf-forecast); "still works on a south swell" [S21] | ≈0.8 m [HEURISTIC]. Reef "gets hollow in moderate east swells" [S21] | – | W / WNW [S21]. Reef sheltered from S wind [S21] | Works all tides; rising best [S21] | Rocks off the south end [S3] |
| Clovelly (outside the bay) / Clovelly Bombie | SE (Clovelly break) [S22]; ENE (Bombie) [S22] | Big swell only, **≥2 m** [HEURISTIC; "rideable left break over the rocks outside the bay" S4] | – | NW [S22] | – | No surf inside the bay [S4] |
| Coogee | E (SE/S blocked by Wedding Cake Island) | **≥1.5–2 m E** [HEURISTIC; "usually just a small shorebreak" S6] | "The Southy" offshore reef in big swell [S6] | W [S23] | – | Summer is usually flat [S23] |
| Maroubra | NE–S, best E / NE / ESE [S24] | ≈0.5 m. Most consistent in the east [S7, S24] | "Can max out with a big swell" [S59] | W / NW / SW [S24] | – | Breaks: The Point, Dunnybowl, Stromies (north), Skatepark, Southies, The Reef (NE–E rights) [S7] |
| Malabar | Larger SE swell [S8] | **≥2 m SE** [HEURISTIC; "larger southeast swell" S8] | – | NW–W | – | Left reef on the northern rocks [S8] |

---

## 2. Per-location table: ocean pools

| Pool | lat, lon [S50] | Exposure / when it's bad | Tide effect | Cleaning closure | Hours / access | Best for |
|---|---|---|---|---|---|---|
| **Bondi Icebergs** | -33.8953, 151.2744 | South end of Bondi. "A strong swell sends water crashing over the southern wall"; may close in big swells [S36]. Damaged by waves in April 2025 [S36], since reopened | Open on summer Thursdays only "when the tides permit" [S36] | **Closed most Thursdays** [S36, S35] | Run by the Icebergs club, not the council; entry fee; conditions line 02 9130 4804 [S36] | 50 m lap pool (fee) |
| **Bronte Baths** | -33.9052, 151.2693 | Closed for dangerous surf in a storm (2024) [S51]; storm repairs in 2022 [S51] | Cleaned in a window that ends at low tide [S35] | **Wednesdays, about 4 h before low tide** [S35] | Free, council | Lap pool, free |
| **Giles Baths** (north Coogee) | -33.9202, 151.2606 | "Can be rough during strong surf" [S38]. Strong swell sends waves up to the concrete above the pool [S38] | Low tide is shallow. **Mid tide + slight swell is ideal**; mid–high is fun but wavy [S38] | Not found | Free, unpatrolled [S38] | Snorkel/splash in small swell (fish life) [S38] |
| **Wylie's Baths** | -33.9256, 151.2594 | Calms down as the tide drops [S39] | **Calmest within ±3 h of low tide** [S39] | Possible closures for events and maintenance [S39] | **7am–7pm 1 Oct–12 Apr; 7am–5pm 13 Apr–30 Sep. Adult $6.50** [S39]. Has a webcam and conditions report on its website [S39] | Laps / long swim (tidal) |
| **McIver's Ladies Baths** | -33.9243, 151.2587 | High tide + strong swell = "washing machine" [S40] | Calm swim at **low tide** [S40] | **Tuesdays** (can change at short notice) [S40] | **Women and children only**. 7am–7pm Oct–Mar; 7am–4pm Apr–Sep [S40] | Calm swim (if eligible) |
| **Ross Jones Memorial Pool** (south Coogee, by the SLSC) | -33.9228, 151.2578 | Waves spill over the walls at high tide and in rough seas, even 3 h after high tide [S41] | Swimmable at any tide; trickier at a big high tide plus swell [S41] | **Mondays** (can change) [S41] | Free | Laps when calm |
| **Ivor (Ivo) Rowe Rockpool** (South Coogee) | -33.9334, 151.2617 | Covered at high tide; rough surf [S42] | **Low tide only**; "the tide can come in very fast" [S42] | – | Free, small (~10 m), waist deep [S42] | Novelty dip, not laps |
| **Mahon Pool** (north Maroubra) | -33.9430, 151.2639 | "Waves crash all the way over the edge at high tide… during very high seas, it becomes unsafe to swim" [S43] | Mid–high tide is the "wave pool" experience. At low tide it's calmer but shallow [S43] | Not found | Free | Scenic dip; laps only when calm |
| **South Maroubra Rockpool** (bonus; Beachwatch monitors it) | -33.9535, 151.2580 [S12] | – | "During very low tides, the rockpool may be empty" [S10] | – | Free | Kids' wade |

---

## 3. Sydney-wide patterns (with numbers)

### 3.1 Rain and water quality (Beachwatch)
- **Default advice**: avoid swimming at ocean beaches "during and for up to one day following" heavy rain, and for up to 3 days at harbour or estuarine sites. [S10, S11]
- **Poor-grade sites**: "avoid swimming at all times during and for up to 3 days following rainfall". **Fair**: up to 3 days. [S10]
- **"Dry weather"** is defined as no rain recorded in the previous 24 h. [S10]
- **Per-site rain sensitivity** (2022-23 report; enterococci exceeding the safe limit) [S10]:

| Site | Grade (22-23) | "Occasionally" exceeds after | "Often/regularly" exceeds after | Dry-weather pass rate |
|---|---|---|---|---|
| Bondi | Good | 5 mm | 20 mm ("regularly") | 98% |
| Tamarama | Good | light rain | **5 mm** | 98% |
| Bronte | Good | light rain | 10 mm | 90% |
| **Clovelly** | Good (down from Very Good) | 10 mm | **20 mm** | 98% |
| **Gordons Bay** | Good | light rain | **10 mm** | 97% |
| Coogee | **Poor** (still Poor in 2026 [S54]) | little or no rain | 10 mm ("regularly") | 86% |
| Maroubra | Good (2026: Good [S54]) | 5 mm | 20 mm | 95% |
| South Maroubra | Good | 5 mm | 20 mm | 91% |
| South Maroubra Rockpool | Good | little or no rain | 5 mm | 88% |
| Malabar | **Poor** in 22-23 (improved by 2026 [S54]) | little or no rain | **5 mm** | 88% |
| Little Bay | Good | little or no rain | 10 mm | 89% |

- **Enclosed bays vs ocean beaches**: Beachwatch classes Clovelly and Gordons Bay as **ocean beaches**, so the 1-day rule applies. Harbour and estuarine sites recover more slowly "due to lower levels of flushing". [S10] Gordons Bay is more rain-sensitive than Clovelly. [S10]
- **Ocean pools**: Beachwatch monitors only South Maroubra Rockpool among these pools. Its advice is to avoid it for 1 day after rain. [S10] The other pools are filled by the sea next to beaches with the grades above. Treat each pool like its adjacent beach. [HEURISTIC]
- **Beachwatch data access**:
  - **Undocumented live API**: `GET https://api.beachwatch.nsw.gov.au/public/sites/geojson` returns a GeoJSON FeatureCollection with `siteName`, `pollutionForecast` (Unlikely/Possible/Likely/Forecast not available), `pollutionForecastTimeStamp`, `latestResult` (Good/Bad…), `latestResultRating` and `latestResultObservationDate`. Tested 2026-11-02 with no key. Undocumented, so wrap it in try/except. [S12]
  - Official open data on CKAN: `https://data.nsw.gov.au/data/dataset/beachwatch` (CC-BY 3.0; datastore_search API, location resource id `52f93d20-45dd-4202-9992-536428cf7de3`) plus RSS pollution-forecast feeds per region. [S13]
  - Unofficial Python wrapper: PyPI `beachwatch` (github.com/ben-n93/beachwatch). [S13]
  - Forecasts are rainfall-driven (Unlikely / Possible / Likely). [S60]

### 3.2 Bluebottles
- **Wind is the main driver.** NE winds and southerly winds both push bluebottles toward the east coast. They drift about **50° left or right of the wind direction**. [S25]
- **Probabilities (UNSW, 4 years of data at Maroubra, Coogee and Clovelly)**: after a summer **NE** wind, Maroubra has a **24%** chance of bluebottles the next day. **Clovelly: 4% after NE, rising to 12% after southerlies.** Ranking: Maroubra > Coogee > Clovelly. [S25]
- **Season**: they peak in summer, "a few weeks before maximum ocean temperatures", but are also recorded in winter and spring. [S25]
- Winds **over 30 km/h** dominated drift direction in replica experiments. [S25 via search summary]
- Bronte's southern end is especially exposed to NE winds. [S56]

### 3.3 Upwelling (cold water) and water temperature
- **Mechanism**: a NE wind along the coast pushes surface water out to sea (Ekman transport), and cold water upwells. "It usually takes a couple of days of nor'easters to see any noticeable change." "Three or more days of NE winds" is an early warning. [S16]
- **Magnitude**: Swellnet reported water falling from **24–25 °C to ~20 °C** in March 2016, while the EAC offshore stayed at ~25 °C. Water was also greener, with plankton. [S17] A 2013 comment reports 23–24 °C falling sharply after one strong NE day. [S16]
- **Recovery**: lasts "until we see a southerly wind change" pushing the warm water back. A Newcastle event took ~3 weeks. [S16, S17]
- Long weak NE sea-breeze cycles can also cause it, e.g. nearly two weeks of afternoon NE breezes in 2016. [S17]
- **Monthly sea temperature at Bondi (approx. averages)** [S47]: Jan 22.9 · Feb 23.5 · Mar ~23 (not given; interpolated) · Apr 21.5 · May 19.8 · Jun 18.4 · Jul ~17 · Aug 17.7 · Sep 18.3 · Oct 19.2 · Nov 20.5 · Dec 21.9 °C. Summer range 17–25 °C, depending on upwelling and the EAC. [S61]
- **EAC**: it strengthens and extends south in summer and weakens in winter. Its eddies make near-shore temperatures deviate strongly from the monthly mean, more often in summer. [S62]
- Live SST: Open-Meteo `sea_surface_temperature` (MeteoFrance, ~8 km, 6-hourly). [S29]

### 3.4 NE sea breeze
- Forms at right angles to the coast, then turns anticlockwise to **NE by mid-afternoon**, peaking mid-to-late afternoon. Typical speed **15–20 kn (28–37 km/h)**. A weak sea breeze dies just after sunset; a strong one can last until near midnight. Mainly late spring and summer. [S26]
- The upwelling-cooled sea strengthens it. [S16]

### 3.5 Southerly busters
- BoM definition: a southerly change with gusts **>29 kn (54 km/h)** and a temperature drop of **≥5 °C within 3 h**. Falls of 10–15 °C in under 1 h are common. Strong ones gust **≥40 kn (74 km/h)**. Record at Sydney Airport: 61 kn. [S27]
- Frequency: **~5 a year** [S27] vs **~10 a year** near Sydney [S28] (conflict). Mostly **October–February**, arriving **late afternoon or early evening**, often after hot N–NW days. Gusts usually ease within **30–60 min**. [S27]
- After the change, a S swell builds. This hits Bondi hardest and Maroubra less. [S14, S15]

### 3.6 Snorkel visibility (Clovelly and Gordons Bay)
- Typical visibility: Clovelly **10–15 m** ("up to 30 inside the bay") [S45]; Gordons Bay **5–10 m**, exceptional days 15 m [S45b].
- Even with swell surging into the Clovelly inlet, "underwater visibility is great". [S46]
- Gordons Bay: "quite exposed… visibility may be poor… do not enter the water if there are waves in the bay". [S44]
- Drivers: (1) **swell/surge stirring sediment** [S44, S63]; (2) **rain runoff**. A general rule is to wait up to a few days after a rainstorm [S63], which fits Beachwatch's 10–20 mm sensitivity [S10]; (3) **wind**: an anecdote says strong SW winds of 20+ kn in the past 1–3 days leave water murky even with low swell [S49, anecdotal]; (4) **upwelling** brings cold, green, plankton-laden water [S16, S17].
- **No published numeric swell limit was found** for snorkelling at either site. The thresholds in §4 are heuristics.

### 3.7 Data sources: reliability near shore
- **Open-Meteo marine** [S29]:
  - Models: MeteoFrance MFWAM 0.08° (~8 km, 3-hourly, 10 days); ECMWF WAM 9 km hourly (15 days); GFS Wave 0.25° (~25 km).
  - Docs: "Accuracy at coastal areas is limited"; "not suitable for coastal navigation".
  - `cell_selection` = land (default) / sea / nearest.
- **Own test (2026-11-02)** [S30]:
  - Default `cell_selection=land` returns `wave_height: null` for all beach coordinates.
  - With `cell_selection=sea`, `best_match` uses MFWAM cells (-33.875, 151.292) and (-33.958, 151.292).
  - `ecmwf_wam` returned no swell partition variables at the offshore point tested.
  - **Recommendation**: query ONE fixed offshore point, e.g. `-33.92, 151.33`, with `cell_selection=sea&models=best_match`. Read `wave_height`, `swell_wave_height/direction/period` and `wind_wave_*`. Apply the per-beach exposure coefficients in §4.2.
- **Tides**:
  - Open-Meteo `sea_level_height_msl` (MeteoFrance SMOC, ~8 km, hourly) includes tides plus the inverse-barometer effect. It is referenced to **mean sea level, not LAT**, and is "reasonably accurate near unobstructed coasts". It works at the offshore point (0.26–0.28 m in the test). Use it for rising/falling and high/low timing, not absolute depth. [S29, S30]
  - Official Fort Denison predictions: free NSW tide-table PDFs (National Tidal Centre / BoM), heights relative to the Fort Denison gauge zero. [S31] No official free API was found. Third-party APIs exist, e.g. tidesatlas (free key; terms unverified). [S31b]

---

## 4. Scoring rules (if/then)

Notation: `Hs` is the offshore significant wave height from Open-Meteo (`wave_height`) at the single offshore point. `dir` is `swell_wave_direction` (degrees FROM). `wind_kmh` and `wind_dir` come from the Open-Meteo forecast API at the beach (10 m, km/h). `rain24`/`rain48`/`rain72` are summed `precipitation` over the previous 24/48/72 h. `tide` is `sea_level_height_msl`. Scores are 0–100. A hard "NO" removes the location from that slot.

### 4.1 Wind relative to beach
Compute `rel = angle_diff(wind_dir, facing_bearing)`, where `facing_bearing` is the direction the beach faces (§1). Then:
- `rel ≤ 45°` → **onshore**
- `45° < rel < 135°` → **cross-shore**
- `rel ≥ 135°` → **offshore**

[DERIVED: offshore = wind from behind the beach, consistent with the sourced offshore directions in §1]

- R-W1: IF offshore AND wind_kmh ≤ 25 → +10 (glassy; best surf and snorkel). [S18–S24 all list offshore as best]
- R-W2: IF onshore AND wind_kmh ≥ 15 → −15 for swim/snorkel and −30 for surf. [HEURISTIC; "even a light onshore ruins the surf" at Coogee, S23]
- R-W3: IF onshore AND wind_kmh ≥ 28 → −35 swim (choppy, whitecaps; matches the 15–20 kn sea-breeze range in S26). Surf → NO. [HEURISTIC]
- R-W4: IF wind_kmh ≥ 40 from any direction → −25 at exposed beaches (Bondi, Tamarama, Bronte, Maroubra). [HEURISTIC]
- R-W5: IF wind_gusts ≥ 54 km/h from S–SW AND temperature drop forecast ≥ 5 °C within 3 h → flag "southerly buster". Weekday-evening slot −40 for every beach except Bronte reef and Clovelly (−20). [S27 definition; shelter from S21, S4]
- R-W6: IF wind_dir is 0–70° (N–NE) → Bondi North +10 (Ben Buckler shelter) [S19/S55]. Clovelly +5 (NE blows across or off the SE-facing inlet) [DERIVED]. Gordons Bay, Little Bay south beach and Bronte south end −10 (onshore; bluebottles) [DERIVED, S56].
- R-W7: IF wind_dir is 160–200° (S) → Bondi −15 (onshore) [DERIVED]. Bronte reef +5 [S21]. Maroubra −5. Coogee 0 (the S headland gives partial shelter, HEURISTIC).

### 4.2 Swell exposure and "too rough" limits

> Since 2026-11-05 the bot measures each spot's swell window from the coastline and models refraction and period (`bot/src/beach_bot/swell.py`). The k coefficients below are now its prior: the result sits halfway between them and the geometry.
Effective height at the beach is `Hb = Hs × k(beach, swell_sector)`. Swell sectors: NE 22.5–67.5°, E 67.5–112.5°, SE 112.5–157.5°, S 157.5–202.5°. Outside these sectors (W/N) use k = 0.1.

**k coefficients [HEURISTIC]**, ranked using the sourced exposure statements in §1 (S14, S15 for Bondi; S6, S23 for Coogee's Wedding Cake Island shelter; S4, S5, S8, S9 for the sheltered bays):

| Location | NE | E | SE | S |
|---|---|---|---|---|
| Bondi North | 0.3 | 0.5 | 0.8 | 0.9 |
| Bondi South | 0.4 | 0.6 | 0.9 | 1.0 |
| Tamarama | 0.8 | 1.0 | 0.9 | 0.6 |
| Bronte | 0.8 | 1.0 | 0.9 | 0.6 |
| Clovelly | 0.15 | 0.25 | 0.35 | 0.25 |
| Gordons Bay | 0.4 | 0.5 | 0.35 | 0.2 |
| Coogee | 0.6 | 0.6 | 0.35 | 0.25 |
| Maroubra | 0.9 | 1.0 | 0.9 | 0.6 |
| South Maroubra | 0.6 | 0.7 | 0.6 | 0.4 |
| Malabar | 0.25 | 0.45 | 0.5 | 0.3 |
| Little Bay | 0.35 | 0.4 | 0.35 | 0.2 |

**Swim/snorkel limits on `Hb` [HEURISTIC]**, anchored where sources give numbers:
- R-S1 Calm swim: Hb < 0.5 m → +20; 0.5–0.8 → 0; 0.8–1.2 → −20; >1.2 m → NO (patrolled exposed beaches: swim between the flags only; Beachsafe hazard ≥6 at Bondi South, Tamarama, Bronte, Maroubra [S1–S3, S7]).
- R-S2 Tamarama: one step stricter (NO at Hb > 0.9 m). [Hazard 8; highest rescue rate, S2]
- R-S3 Clovelly swim: NO only when **Hs > 2.5 m from SE/E** (inside-bay Hb > ~0.8). Randwick lifeguards logged Clovelly as "rough" at a 2 m report. [S52] Beachsafe calls it the quietest patrolled beach [S4].
- R-S4 Snorkel at Clovelly: Hs < 1.0 m → +25; 1.0–1.5 → 0; 1.5–2.0 → −25; >2.0 → NO. [HEURISTIC; S46 says visibility holds with surge; S52 says rough at 2 m]
- R-S5 Snorkel at Gordons Bay: stricter. Hs < 0.8 m AND swell not from E/NE → +25; Hs 0.8–1.2 → −10; Hs > 1.2 m from NE/E/SE → NO. [HEURISTIC; "do not enter the water if there are waves in the bay", S44]
- R-S6 Little Bay snorkel: Hs < 1.0 → +15; > 1.8 → NO ("higher waves break at the bay entrance", S9). [HEURISTIC]
- R-S7 Any location: IF swell_period ≥ 12 s → multiply Hb by 1.3. Long-period groundswell wraps into bays and adds surge. [HEURISTIC; the NSW hazardous-surf warnings use height **and** period, S64]

### 4.3 Surf rules (where surf is a slot activity)
- R-SU1 Bondi South works IF dir is SSE–S (135–200°) AND 0.6 ≤ Hs ≤ 2.5 AND wind is NNW–NW or < 10 km/h. [S1, S18, S19]
- R-SU2 Maroubra works IF dir is NE–SE (30–150°) AND 0.5 ≤ Hs ≤ 2.5 AND wind is W/NW/SW or < 10 km/h. Prefer Maroubra over Bondi in E swell; prefer Bondi in S swell. [S7, S14, S15, S24]
- R-SU3 Bronte works IF dir is E–SE AND 0.8 ≤ Hs ≤ 2.5 AND wind is W/WNW. A S wind is tolerable at the reef. Rising tide +5. [S21]
- R-SU4 Coogee works only IF dir is E AND Hs ≥ 1.5. [HEURISTIC, S6, S23] Malabar left only IF SE AND Hs ≥ 2. [HEURISTIC, S8]
- R-SU5 Tamarama: never during patrol hours (boards banned) [S2].
- R-SU6 Surf period (added 2026-11-09): read the longer of the swell period and the whole sea's period. The forecast's swell partition (MeteoFrance) reads about 3 s short of the peak period on groundswell days. On 11 Apr 2024 (6–8 ft barrels at Bronte) it read 6.8 s, against 9.3 s for the whole sea and a 9.65 s ERA5 peak. [research/surf-history.md]
- R-SU7 Offshore wind for surf (added 2026-11-09): judge an offshore of 8 km/h or more against the breaking-wave speed c = √(g·Hb/0.78), with r = offshore component ÷ c. Full points up to r 0.8, then 0.85 at r 1.3, 0.6 at 2, 0.35 at 3 and 0.25 from 3.5. Gusts are judged the same way: ×0.85 from 3c and ×0.7 from 4c. Anything ≥45 km/h, or gusting ≥70, gets 2 points. The physics says offshore wind holds waves up and makes them plunge, and that strong offshores don't spoil the wave's shape. What they spoil is catching the wave, and bigger, faster waves tolerate more. The breakpoints are judgement, tuned on the backtest. Cross-shore and onshore scoring is unchanged. [research/offshore-wind-surf.md]
  - Backtest against 39 dated days since 2023, with R-SU6 and R-SU7 together:
    - Good days: median 5/10 → 7, and 2 → 5 reaching 8+.
    - Maroubra on 12 Apr 2026 (4–6 ft, W 21 gusting 49): 7 → 9.
    - High-confidence blown-out days: still 1–4.
    - Days with a break at 8+: about 9 a year → 28.

- R-SU8 Reefs and bombies (added 2026-11-09): Ben Buckler (expert), Clovelly Bombie (advanced), Wedding Cake Island (expert), Lurline Bay (advanced), Malabar (advanced) and Mackenzies (intermediate). Each has a `level`, a `min_hs` at the break (none for Mackenzies), the swell range it breaks on (`works_from`), and where known a best tide. Below 0.7× min it's not breaking; up to min it's only just breaking; from min to max it gets full size points with groundswell (11 s+), less at 9–11 s, and little under 9 s. Swell from outside its range scores as nothing. A best tide is ±3 points of quality. The bombies and the Malabar point have their swell window measured at the pin, not walked back to the shore. Ben Buckler and Wedding Cake are out past the drains, so rain there is a warning, not a closure. Advanced and expert breaks never make the session's surf call, the event's top 3 or the calendar. Pros-only slabs (Cape Solander, Voodoo, Honeycomb) and unnamed spots are left out. Maroubra's north point is left out: two rounds of searching found no dated session that names the point itself. Maroubra (north end) is scored instead. It's the "Dunny Bowl" corner: intermediate, a touch smaller than the open beach, and sheltered from N–NE wind (`wind_shelter`, which scores that wind at half strength). Its sand is stripped by big winter S swells, which the model can't see. [Wannasurf Sydney South, Surf-forecast, research/surf-history.md, research/eastern-reefs-dated.md, research/maroubra-north.md]
  - Checked against dated sessions (mostly a local's daily filmed surf check, 2023–2026):
    - Clovelly Bombie: 8, 8, 8 on its three good days. The forecast had E swell each time, as Wannasurf says.
    - Wedding Cake: 5–8 on good days. The outer bank needs far more swell than the inside "Southie".
    - Malabar needs a big swell, E round to S. Dated good days had 2.6–4.6m at the pin. Two of them score 1 because rain closes it on water quality, which is deliberate.
    - Mackenzies is best at low tide in a solid S swell. Its good days have a median of 7 and its so-so days 5.
    - Maroubra (north end): on ten dated north-corner days, good days have a median of 6 and the flat day 2. Two of the three poor days score 6–7: one fell when ABC reported the corner's sand stripped (Aug 2024), and the other we can't explain. In a N–NE wind of 12 km/h or more it scores 1–3 points above the open beach.
  - Backtest 2023-01 to 2026-11, days a year at 8+: Ben Buckler 1.3, Wedding Cake 1.6, Clovelly Bombie 2.9, Lurline 2.9, Malabar 2.6, Mackenzies 13, Maroubra (north end) 15. The original four breaks are unchanged.

- R-SU9 Pros-only spots (added 2026-11-10, research/pro-spots-dated.md). Scored so people know when to go and watch, never the surf call or the calendar (level "pro", tagged "Pros only", each with `watch_from`):
  - Cape Solander ("Ours", Kurnell): an E swell 2m+ at the break, 45–160°, high tide. Watch from the whale-watching platform.
  - Queenscliff Bombie: a big E swell only, 3m+ at the break, 60–130°.
  - Deadmans (under North Head): S and E both work, 2m+, high tide, out of the S–SW wind.
  - Long Reef Bombie: S–SE swell 2.5m+.
  - Ben Buckler and Wedding Cake Island stay "expert" and now have watch-from spots too.
  - Backtest against dated sessions:
    - Cape Solander: good days 6, 7, 8 and 8.
    - Queenscliff Bombie: 1 on every big S swell that only "tickled" it, and 7 on the E swell of 5 Aug 2025.
    - Long Reef Bombie: its good day 8, its poor day 2.
    - Deadmans: the ridden day 7, good days 5–6, and most so-so days 1–3, after facing it ENE (sheltered by North Head).
  - Days a year at 8+: Solander 2.3, Queenscliff Bombie 0.4, Long Reef Bombie 0.2, Deadmans 3.1.
  - Still left out: Voodoo (Bate Bay, outside the region's swell, one dated session), Honeycomb (part of Lurline Bay), Diamonds and Diggers Rights (no dated sessions), Kelso Beach (no location), Lighthouse Rights (no pin).

- R-SU10 Not checked yet (added 2026-11-10). Breaks set up from the surf guides alone, with too few dated sessions to check them against. They're scored and shown, tagged "Not checked yet", and kept out of the surf call and the calendar (`checked=False`) until real days back them up:
  - Eastern: Diamonds (pros only, Diamond Bay) and Voodoo (pros only, Bate Bay, faces S).
  - Northern: Diggers Rights (pros only), Turimetta and Little Avalon (advanced), the Wedge (advanced, the north end of Whale Beach, measured at the pin), and Bungan, Bilgola and Whale Beach (intermediate).
  - Days a year at 8+ over the archive: Diamonds 5.4, Voodoo 2.1, Diggers Rights 0.2, Turimetta 6.6, Little Avalon 5.6, the Wedge 3.1, Bungan 5.0, Bilgola 7.4, Whale Beach 8.7.

### 4.4 Rain / water-quality rules
- R-R1 IF the Beachwatch API `pollutionForecast` for the site = "Likely" → NO. = "Possible" → −30. [S12, S60]
- R-R2 Fallback when the API fails, using the per-site thresholds in §3.1 [S10]:
  - IF rain24 ≥ "often" threshold → NO.
  - IF rain24 ≥ "occasionally" threshold → −25.
  - IF rain in the previous 24–48 h ≥ "often" threshold → −15 (1-day rule).
- R-R3 Poor-graded sites (Coogee; Malabar until confirmed Good): IF rain72 ≥ 5 mm → NO. IF rain72 ≥ 1 mm → −20. [S10 Poor = up to 3 days]
- R-R4 Snorkel visibility: IF rain48 ≥ 10 mm → Clovelly and Gordons snorkel −20; IF rain48 ≥ 20 mm → snorkel NO. [S10 thresholds + S63]
- R-R5 Pools inherit the adjacent beach's rain rule. Icebergs/Bondi; Bronte Baths/Bronte; Giles, Ross Jones, Wylie's and McIver's/Coogee; Ivor Rowe/Coogee; Mahon/Maroubra. [HEURISTIC]

### 4.5 Temperature / upwelling / bluebottle rules
- R-T1 IF wind_dir is NE (20–70°) with daily mean ≥ 15 km/h on ≥ 3 of the last 4 days → expect SST −2 to −5 °C below Open-Meteo's offshore SST (the model at ~8 km may lag) → −10 for all swim slots and add a note "cold upwelling likely". [S16, S17]
- R-T2 IF Open-Meteo SST < 18 °C → −10 (wetsuit territory). IF > 22 °C → +5. [HEURISTIC using S47 monthly ranges]
- R-B1 Bluebottle risk, Nov–Mar, next day after NE or S/SE onshore wind ≥ 20 km/h:
  - Maroubra −20 (24% next-day risk after NE)
  - Coogee −10
  - Bronte south and Tamarama −10
  - Clovelly −3 after NE, −8 after S (4% / 12%)
  - Pools −0 (minor)
  - IF wind ≥ 30 km/h, double the penalty.

  [S25, S56]

### 4.6 Tide rules (pools mainly)
- R-P1 Wylie's: IF |time to low tide| ≤ 3 h → +15; IF within 2 h of high tide AND Hs ≥ 1.5 → −20. [S39]
- R-P2 McIver's: low tide +10. High tide AND Hs ≥ 1.5 → −20. Eligibility: women and children only. If the user is not eligible, exclude it. [S40]
- R-P3 Ross Jones, Mahon, Giles, Icebergs: IF within 3 h of high tide AND Hs ≥ 1.5 (SE/E/S) → −20. IF Hs ≥ 2.5 at high tide → NO ("unsafe in very high seas", waves over the walls). [S36, S38, S41, S43; HEURISTIC numbers]
- R-P4 Ivor Rowe: only within ±2 h of low tide; otherwise NO. [S42]
- R-P5 Giles: mid tide AND Hs < 1.0 → +15 (snorkel-friendly). [S38]
- R-P6 South Maroubra Rockpool: very low tide → NO (may be empty). [S10]
- R-P7 Cleaning days:
  - Icebergs Thursday → NO (unless a summer Thursday with a favourable tide; treat it as NO).
  - Bronte Baths Wednesday → NO within the 4 h before low tide.
  - McIver's Tuesday → NO.
  - Ross Jones Monday → NO.

  [S35, S36, S40, S41]
- R-P8 Opening hours: Wylie's 7am–7pm (1 Oct–12 Apr) / 7am–5pm; McIver's 7am–7pm (Oct–Mar) / 7am–4pm. Weekday early-morning slots before 7am → NO for these two. [S39, S40]
- R-P9 Clovelly: big high tide (king tide) floods the concourse. Minor −5 for access only. [S65]
- R-P10 Bronte (surf): rising tide +5 [S21]. Bondi South: mid, rising tide +5 [S19].

### 4.7 Patrol / time-slot rules
- R-PT1 Weekday early morning (before ~7am) and evening (after 7pm): no patrols anywhere. Prefer low-hazard locations: Clovelly (2), Little Bay (2), Gordons (2), Malabar (3), Coogee (4) [S4–S9]. Then apply exposed beaches (hazard ≥6) −15. [Beachsafe hazard ratings] **Removed 2026-11-06**: no points are taken off for unpatrolled hours; the bot no longer scores patrols.
- R-PT2 Clovelly has lifeguards every day, sunrise to sunset, all year (since 2024) [S33]. Coogee and Maroubra 7am–7pm in daylight saving, 7am–5pm otherwise [S34]. Bondi year-round [S1]. Tamarama late Sept–Apr [S10]. Bronte Sept–May [S10]. Gordons, Malabar and Little Bay are unpatrolled [S10].
- R-PT3 Summer weekday evening (Oct–Mar): assume a 28–37 km/h NE sea breeze from mid-afternoon to sunset or later [S26]. Apply R-W6 automatically even if the model under-forecasts. This favours Bondi North, Clovelly and pools over Gordons, Little Bay and Bronte. [DERIVED]
- R-PT4 Weekend daytime: patrol bonus +5 at patrolled beaches. SLSC volunteers are on duty on weekends and holidays, late Sept–April [S34].

- R-LG1 Lifeguard reports (added 2026-11-09). Randwick Council's lifeguards post a report for each beach they patrol each morning, about 6:45–8:30am: beach status, summary, wave height, rips, bluebottles, water temperature and a free-text description. It is published as an RSS feed [S-LG]. The feed currently covers Clovelly, Coogee and Maroubra, and the reports page also lists Little Bay. A beach's item stays in the feed until its next report, so a report from an earlier day is ignored. The rules apply to today only:
  - Beach status "Closed" → NO for that beach for the rest of the day, with the reason "closed by lifeguards". Its ocean pools are scored as usual.
  - Bluebottles sighted → the beach's R-B1 penalty applies whatever the wind, with the note "bluebottles reported".
  - "None sighted" → R-B1's wind-based penalty is dropped.
  - Wave height is logged next to the swell model's height at that beach and hour, for calibrating exposure (§4.2). On 9 Nov 2026, with a 2m south swell, the lifeguards had 2m at Coogee and "+2m" at Maroubra; the model had 0.9 m and 1.2 m.
  - Water temperature, rips and the description are shown only.

### 4.8 Tie-break
- R-TB1 After all rules, IF Clovelly's score ≥ (best score − 5) AND Clovelly is not "NO" → pick Clovelly. (User preference. A 5-point tolerance acts as a soft tie.)

---

## 5. Gaps and conflicts

1. **No published swell numbers for "too rough to swim/snorkel"** at any of these locations. All the Hb limits and k coefficients are heuristics, ranked from the sourced exposure statements. Calibrate them against Randwick and Waverley lifeguard daily reports, which give wave height per beach; Randwick's showed "Clovelly 2 m rough" [S52].
2. **Bondi orientation**: Beachsafe says the beach "faces southeast" [S1]; Swellnet says "nearly dead south" [S14]. Using ~150°.
3. **Clovelly orientation**: Beachsafe says SE-facing [S4]; UNSW calls it south-facing [S25].
4. **Best swell direction disagreements**:
   - Tamarama: NE (surfnerd) vs SE (surf-forecast) [S20].
   - Bronte: E vs SE [S21].
   - Maroubra: NE (surf-forecast) vs E/NE/ESE (Surfline) vs NE–S (surfnerd) [S24].
   - Bondi: S (surf-forecast) vs SE (surfnerd) [S18, S19].
5. **Southerly busters per year**: ~5 [S27] vs ~10 [S28].
6. **Patrol seasons**:
   - Clovelly: the Beachwatch report says late Sept–Apr, but it predates May 2024. Council lifeguards are now year-round [S33].
   - Tamarama: "late Sept–Apr" [S10] vs "year round" [S2].
   - Council websites (Randwick, Waverley) block automated fetching (Cloudflare), so hours come from search snippets and news. Verify manually.
7. **Beach grades change yearly.** Coogee is Poor in 2022-23 and 2026. Malabar was Poor in 2022-23 and had improved by 2026 [S10, S54]. Prefer the live API over hard-coded grades.
8. **Gordons Bay shelter**: one source says the bay stays calm "even when the open coast is rough" [S45b]; another says it is "quite exposed" [S44]. The rules use the cautious view.
9. **Mahon Pool exposure**: one reviewer says "open to the south-westerly swell" [S43]. SW swell does not reach this east-facing coast, so this is likely a mistake for S/SE swell.
10. **Not found**: cleaning days for Giles and Mahon; Bondi Icebergs fee and hours; an official Beachwatch API spec; an official free Fort Denison tide API; Beachsafe API terms (the `/api/v4/beach/{slug}` endpoint used here is undocumented).

---

## Sources
- [S-LG] Randwick City Council lifeguard reports, RSS feed: https://www.randwick.nsw.gov.au/integration/feeds/lifeguard-reports (the reports page links to it; read 2026-11-09).

- **S1** Beachsafe (SLSA), Bondi Beach: https://beachsafe.org.au/beach/nsw/waverley/bondi-beach/bondi-beach (data read via undocumented JSON https://beachsafe.org.au/api/v4/beach/bondi-beach)
- **S2** Beachsafe, Tamarama: https://beachsafe.org.au/beach/nsw/waverley/tamarama/tamarama (JSON /api/v4/beach/tamarama)
- **S3** Beachsafe, Bronte: https://beachsafe.org.au/beach/nsw/waverley/bronte/bronte (JSON /api/v4/beach/bronte)
- **S4** Beachsafe, Clovelly: https://beachsafe.org.au/beach/nsw/randwick/clovelly/clovelly (JSON /api/v4/beach/clovelly)
- **S5** Beachsafe, Gordon's Bay: https://beachsafe.org.au/beach/nsw/randwick/clovelly/gordon-s-bay (JSON /api/v4/beach/gordon-s-bay)
- **S6** Beachsafe, Coogee: https://beachsafe.org.au/beach/nsw/randwick/coogee/coogee (JSON /api/v4/beach/coogee)
- **S7** Beachsafe, Maroubra: https://beachsafe.org.au/beach/nsw/randwick/maroubra-south/maroubra (JSON /api/v4/beach/maroubra)
- **S8** Beachsafe, Malabar/Long Bay: https://beachsafe.org.au/beach/nsw/randwick/malabar/malabar-long-bay
- **S9** Beachsafe, Little Bay 1 & 2: https://beachsafe.org.au/beach/nsw/randwick/little-bay/little-bay-2-2
- **S10** NSW Beachwatch, State of the Beaches 2022–23, Sydney region (per-beach rain thresholds, grades, patrol notes, grade definitions): https://www.environment.nsw.gov.au/sites/default/files/state-of-the-beaches-2022-23-sydney-region-230279.pdf
- **S11** NSW Beachwatch, State of the Beaches 2023–24 statewide summary: https://www.environment.nsw.gov.au/sites/default/files/state-of-the-beaches-2023-24-statewide-summary-240249.pdf
- **S12** Beachwatch public API (undocumented; tested 2026-11-02): https://api.beachwatch.nsw.gov.au/public/sites/geojson
- **S13** Data.NSW Beachwatch dataset (CKAN API, RSS): https://data.nsw.gov.au/data/dataset/beachwatch ; https://data.gov.au/data/dataset/nsw-beachwatch ; wrapper https://pypi.org/project/beachwatch , https://github.com/ben-n93/beachwatch
- **S14** Swellnet, "South facing vs north facing: what is your beach?": https://swellnet.com/news/swellnet-analysis/2013/10/25/south-facing-vs-north-facing-what-your-beach
- **S15** Swellnet forecaster notes, 25 Jun 2014 (Bondi "south swell magnet" 3 ft vs Maroubra 1.5 ft): https://swellnet.com/reports/forecaster-notes/sydney-hunter-illawarra/2014/06/25/continuing-flukey-south-swells-and-gusty
- **S16** Swellnet, "Why does the water get colder in Sydney after a nor'easter?": https://www.swellnet.com/news/swellnet-analysis/2006/07/03/why-does-water-get-colder-sydney-after-noreaster
- **S17** Swellnet, "Sydney's cold water episode explained" (2016): https://www.swellnet.com/news/swellnet-analysis/2016/03/10/sydneys-cold-water-episode-explained
- **S18** Surf-forecast, Bondi Beach: https://www.surf-forecast.com/breaks/Bondi-Beach
- **S19** Surfnerd, Bondi Beach: https://www.surfnerd.com/surf-forecast/bondi-beach
- **S20** Surf-forecast, Tamarama Reef: https://www.surf-forecast.com/breaks/Tamarama-Reef ; Surfnerd Tamarama: https://www.surfnerd.com/surf-forecast/tamarama
- **S21** Surfnerd, Bronte: https://www.surfnerd.com/surf-forecast/bronte ; Surf-forecast Bronte Reef: https://www.surf-forecast.com/breaks/Bronte-Reef ; Bronte Beach: https://www.surf-forecast.com/breaks/Bronte-Beach
- **S22** Surf-forecast, Clovelly: https://www.surf-forecast.com/breaks/Clovelly-1 ; Clovelly Bombie: https://www.surf-forecast.com/breaks/Clovelly-Bombie
- **S23** Surf-forecast, Coogee guide and reviews: https://www.surf-forecast.com/breaks/Coogee ; https://www.surf-forecast.com/breaks/Coogee/reviews
- **S24** Surf-forecast Maroubra: https://www.surf-forecast.com/breaks/Maroubra-Beach ; Surfline Maroubra (403 to fetch; summary via search): https://www.surfline.com/travel/zones/sydney/surf-guide/maroubra/5842041f4e65fad6a7708bf5 ; Surfnerd: https://surfnerd.com/surf-forecast/maroubra
- **S25** The Conversation / UNSW, "Want to avoid a bluebottle sting?": https://theconversation.com/want-to-avoid-a-bluebottle-sting-heres-how-to-predict-which-beach-theyll-land-on-179947 ; https://www.unsw.edu.au/news/2022/03/want-to-avoid-a-bluebottle-sting--here-s-how-to-predict-which-be
- **S26** Weatherzone, "Sydney sea breezes and extreme heat, part 1": https://www.weatherzone.com/au/news/sydney-sea-breezes-and-extreme-heat-part-1/181613
- **S27** Bureau of Meteorology, "The big bust: southerly busters explained": https://media.bom.gov.au/social/blog/18/the-big-bust-southerly-busters-explained/
- **S28** BoM aviation education, "Flying in south-east Australia": https://www.bom.gov.au/aviation/data/education/flying-se.pdf
- **S29** Open-Meteo Marine Weather API docs: https://open-meteo.com/en/docs/marine-weather-api ; launch post: https://openmeteo.substack.com/p/marine-weather-forecast-api
- **S30** Own reproducible test, 2026-11-02: `https://marine-api.open-meteo.com/v1/marine?latitude=-33.9138&longitude=151.2666&hourly=wave_height&models=best_match&cell_selection=land` (returns null) vs `...&cell_selection=sea` (snaps to -33.875, 151.292)
- **S31** NSW tide tables (Fort Denison, National Tidal Centre): https://www.nsw.gov.au/driving-boating-and-transport/using-waterways-boating-and-transport-information/conditions-weather-and-tides/nsw-tide-tables ; e.g. https://www.nsw.gov.au/sites/default/files/2023-06/nsw_tides_2023–2024.pdf
- **S31b** Tidesatlas Fort Denison (third-party API; unverified terms): https://tidesatlas.com/en/australia/new-south-wales/fort-denison
- **S33** Yahoo News (17 May 2024), Clovelly year-round lifeguards: https://au.news.yahoo.com/major-change-popular-sydney-swim-223200535.html
- **S34** Randwick Council, Coogee Beach page (patrol hours; via search snippet, Cloudflare blocks fetch): https://randwick.nsw.gov.au/facilities-and-recreation/beaches-and-coast/beaches/coogee-beach ; Lifeguards: https://www.randwick.nsw.gov.au/facilities-and-recreation/beaches-and-coast/lifeguards
- **S35** Waverley Council, ocean pool cleaning schedules (Bronte Wed, North Bondi Thu, ~4 h before low tide; via search snippet): https://www.waverley.nsw.gov.au/recreation/beaches_and_coast/pool_cleaning_schedule/bronte_pool_cleaning_schedule
- **S36** Visit Bondi Beach, Icebergs: https://www.visitbondibeach.com/bondi-blog/can-anyone-swim-at-bondi-icebergs-swimming-pool ; April 2025 closure: https://visitbondibeach.com/bondi-blog/2025/4/2/bondi-icebergs-closed-due-to-destructive-waves ; https://icebergs.com.au/contact
- **S37** Waverley Council heritage page, Backpackers' Rip: https://celebrating.waverley.nsw.gov.au/nodes/view/73513
- **S38** Ocean Pools NSW, Giles Baths review: https://oceanpoolsnsw.net.au/giles-baths-coogee-nsw-2034/ ; Randwick: https://www.randwick.nsw.gov.au/facilities-and-recreation/beaches-and-coast/ocean-pools/giles-baths
- **S39** Wylie's Baths, location, hours and fees: https://wylies.com.au/information ; tide advice: https://australiatravelquestions.com/?p=23341 ; https://oceanpoolsnsw.net.au/?p=2564
- **S40** Randwick, McIver's Ladies Baths: https://randwick.nsw.gov.au/facilities-and-recreation/beaches-and-coast/ocean-pools/mcivers-baths ; https://oceanpoolsnsw.net.au/mcivers-baths-coogee-nsw-2034/
- **S41** Randwick, Ross Jones Memorial Pool: https://www.randwick.nsw.gov.au/facilities-and-recreation/beaches-and-coast/ocean-pools/ross-jones-memorial-pool ; https://oceanpoolsnsw.net.au/ross-jones-memorial-pool-coogee-nsw-2034/
- **S42** Ocean Pools NSW, Ivo Rowe: https://oceanpoolsnsw.net.au/ivo-rowe-rock-pool-south-coogee-nsw-2034/ ; https://australiaunseen.com/pages/rock-pool/ivo-rowe-pool
- **S43** Time Out, Mahon Pool: https://www.timeout.com/sydney/sport-and-fitness/mahon-pool ; https://oceanpoolsnsw.net.au/?p=3990
- **S44** Snorkeling Report, Gordons Bay: https://www.snorkeling-report.com/spot/snorkeling-gordons-bay-cogee/
- **S45** Secret Sydney, Clovelly (visibility 10–15 m): https://secretsydney.com/clovelly-beach-sydney/ ; **S45b** Dive Planner Pro, Gordons Bay (5–10 m): https://diveplannerpro.com/spots/au/australia/australia-gordons-bay
- **S46** Lonely Planet, Clovelly Beach: https://www.nonprod.lonelyplanet.com/points-of-interest/clovelly-beach/368097 (URL as returned by search)
- **S47** Visit Bondi Beach, average sea temperatures by month: https://visitbondibeach.com/bondi-blog/2024/8/28/average-sea-temperatures-at-bondi-beach-month-by-month-guide
- **S49** Seabreeze forum (anecdotal SW-wind visibility): https://seabreeze.com.au/forums/Surfing/Shortboards/Predicting-the-best-time-for-surfing
- **S50** OpenStreetMap Nominatim geocodes (queried 2026-11-02): https://nominatim.openstreetmap.org/
- **S51** Waverley Council news, Bronte Pool closures: https://www.waverley.nsw.gov.au/top/news_and_media/council_news/all/2022/coastal_damage_from_high_seas ; https://www.visitbondibeach.com/bondi-blog/2024/4/6/storm-chaos-forced-closures-around-bondi-beach
- **S52** Randwick Council lifeguard report (Clovelly 2 m "rough"; via search snippet): https://www.randwick.nsw.gov.au/home
- **S54** Time Out, best and worst Sydney beaches for water quality, 2026 (25 Sep 2026): https://www.timeout.com/sydney/news/revealed-the-best-and-worst-sydney-beaches-for-water-quality-in-2026-092526
- **S55** The Surf Atlas, Bondi (north/south differences; Ben Buckler shelter from NE): https://thesurfatlas.com/australia-surfing/bondi-surf/ ; https://visitbondibeach.com/bondi-blog/bondi-beach-surf-guide
- **S56** City Hub, bluebottles at Bronte's NE-exposed south end: https://cityhub.com.au/waverley-council-to-clean-up-bronte-beach-after-invasion-of-bluebottles ; Australian Museum: https://australianmuseum.net.au/Bluebottle
- **S57** The Surf Atlas, Maroubra: https://thesurfatlas.com/australia-surfing/surfing-in-maroubra/
- **S58** Sydney Coastal Councils Summerama, snorkelling at Little Bay: https://www.sydneycoastalcouncils.com.au/summerama/summerama-blog/snorkelling-at-little-bay%e2%80%af2-sessions/ ; Concrete Playground snorkel spots: https://concreteplayground.com/sydney/travel-leisure/the-ten-best-snorkelling-spots-in-sydney/amp
- **S59** Mondo.surf Tamarama / Maroubra guides: https://www.mondo.surf/surf-spot/tamarama/guide/9954 ; https://www.mondo.surf/surf-spot/maroubra-beach/guide/9951
- **S60** Beachwatch forecast method (rainfall-driven Unlikely/Possible/Likely; described by Derwent Estuary program): https://derwentestuary.org.au/assets/Information_regarding_forecasting_program_2024-25.pdf ; dataset metadata https://datasets.live.lz.seed.nsw.gov.au/dataset/beachwatch/metaexport/iso19115_pdf
- **S61** OceanFit, "Coriolis effect: when the water gets cold in summer" (17–25 °C summer range): https://oceanfit.com.au/education/coriolis-effect-when-the-water-gets-cold-in-summer/
- **S62** Macquarie Univ., "Annual cycling in wind, temperature and along-shore currents on the Sydney shelf": https://researchers.mq.edu.au/en/publications/annual-cycling-in-wind-temperature-and-along-shore-currents-on-th/ ; UTS EAC overview: https://opus.lib.uts.edu.au/handle/10453/18064
- **S63** General snorkel-visibility guidance (rain/waves stir sediment): https://canvas.ubc.ca/eportfolios/45097/entries/141320 ; https://www.scubadoctor.com.au/downloads/how-to-assess-visibility-at-snorkel-sites-2.pdf
- **S64** Transport for NSW, checking the weather (hazardous surf = wave height and period; max waves up to 2× Hs; gusts 40% above mean): https://www.nsw.gov.au/driving-boating-and-transport/waterways-safety-and-rules/before-you-go-boating/checking-weather ; BoM Hazardous Surf Warning launch: https://media.bom.gov.au/releases/373/new-service-to-improve-safety-for-rock-fishers-boaters-and-swimmers
- **S65** Ocean Pools NSW, Clovelly (king tide over concourse): https://oceanpoolsnsw.net.au/clovelly-ocean-pool-nsw-2096/
