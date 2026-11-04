# Eastern suburbs additions: harbour beaches and missing ocean pools

Compiled 2026-11-04. This file adds to `beach-knowledge.md` and uses its conventions:
- **[SRC]**: the fact is stated in the cited source.
- **[DERIVED]**: worked out from a sourced fact or from map geometry.
- **[HEURISTIC]**: a starting value with no published number behind it. Calibrate it.

Source IDs `[S10]`, `[S12]`, `[S40]` and `[S50]` are the ones already in `beach-knowledge.md`. New sources start at `[H1]`.

What this covers:
1. A new **harbour** category: Shark Beach (Nielsen Park), Camp Cove, Parsley Bay, Watsons Bay and Murray Rose Pool. Milk Beach and Rose Bay Beach were checked and left out.
2. Two **missing ocean pools**: McIver's Ladies Baths and South Maroubra Rockpool, plus a sweep for other eastern-suburbs pools.

## 0. Key findings to read first

1. **Beachwatch's site-details endpoint gives each site's current annual grade.** It is `GET https://api.beachwatch.nsw.gov.au/site/{id}/details`, where `{id}` is the `id` from the GeoJSON feed. It also returns site type, patrol text, live sewage-overflow alerts and the BOM rain gauge Beachwatch uses for the site. It is undocumented: I found it in the beachwatch.nsw.gov.au JS bundle, and it worked without a key on 2026-11-04. [H1]
2. **The 2025–26 grades, read from that endpoint on 2026-11-04** [H1]:

   | Site | Grade |
   |---|---|
   | Nielsen Park | **Very Good** |
   | Camp Cove | **Very Good** |
   | Parsley Bay | Good |
   | Watsons Bay | Good |
   | Murray Rose Pool | Good |
   | Rose Bay Beach | **Poor** |
   | South Maroubra Rockpool | Good |

   Time Out's write-up of the 2026 report agrees: Nielsen Park and Camp Cove are "top tier" and Rose Bay is Poor [H2]. I could not find the 2025–26 Sydney-region PDF, so the per-site rain sensitivity below comes from the 2022–23 [S10] and 2023–24 [H3] reports.
3. **All five harbour sites have a live Beachwatch `pollutionForecast`**, so rule R-R1 works for them as it is. On 2026-11-04 all five read "Likely" after rain. South Maroubra Rockpool has **no** daily forecast ("This site does not have daily forecast data"). [S12, H1]
4. **The harbour rain rule is 3 days, not 1.** Beachwatch's default advice for harbour and estuarine sites is to avoid swimming for up to 3 days after rain [S10]. Woollahra Council says "at least three days after heavy rain" for Murray Rose Pool and its other harbour sites [H6, H10]. Beachwatch classes all five sites as **Estuarine**, not ocean beach [H1]. The 1-day fallback in R-R2 is too short for them (see the proposed R-H1 in §4).
5. **Beachwatch uses the Sydney (Observatory Hill) rain gauge for every harbour site**, not Sydney Airport. It uses Sydney Airport AMO for South Maroubra. [H1]
6. **Shark Beach net history**:
   - The site reopened on 12 Dec 2024 after a 3-year seawall rebuild [H4].
   - Large waves damaged the enclosure in August 2025. NPWS warned that the damaged nets "do not provide a total barrier" [H5].
   - Repairs were reported as finished in early December 2025 [H11].
   - On 18 Jan 2026 a 12-year-old boy was fatally bitten while swimming **outside** the net [H11].
   - On 2026-11-04 the NPWS alerts API had **no** live alert for the enclosure [H5]. I could not confirm the current state of the net beyond that.
7. **Beachsafe gives the southern harbour beaches no hazard rating** (`hazard: 0`). Its text says they are "relatively calm with usually only low wind waves", and that "only the deep water off some of the beaches and boat traffic pose a risk" [H7]. The hazard values below are therefore heuristics.

---

## 1. Harbour beaches

Bearings are the direction the beach faces, looking out over the water. Winds come FROM the direction given.

| Spot | Pin lat, lon (source) | Faces | Netted? | Patrol | Grade 22-23 → 23-24 → 25-26 | Rain: "occasionally" / "often" exceeds after | Wind: choppy when | Swell | Snorkel | Local notes |
|---|---|---|---|---|---|---|---|---|---|---|
| **Shark Beach, Nielsen Park** (Beachwatch "Nielsen Park") | **-33.8502, 151.2675**: interior point of the OSM `natural=beach` way 4354480 "Shark Beach". The plain centroid (-33.8505, 151.2667) rounds to <1 m from the polygon edge, so I used a point 16 m inside. [S50, H8] Beachwatch pin: -33.8499, 151.2662 [S12] | NNW, **~340°** [DERIVED from the OSM polygon's long axis, 069°/249°, harbour side] | **Yes, Oct–Apr**: "approximately 150 m long and is netted from October to April" [S10, H3]. Damaged Aug 2025, reported repaired Dec 2025 [H5, H11] | **Unpatrolled** [H1] | Good (down from VG) → Good (site closed for construction) → **Very Good** [S10, H3, H1] | "occasionally exceeding the safe swimming limit after rainfall"; no "often" threshold given [S10, H3]. Dry-weather pass rate 98% (22-23), 100% (23-24) | N–NE onshore and cross-shore, across open harbour [DERIVED]. S–SW is offshore (Vaucluse behind) [DERIVED] | **The most swell-exposed of the five.** Beachsafe: "only Nieslen Park picking up rideable waves during very big outside swell" [H7]. Storm waves wrecked the 1930s seawall [H4] and damaged the net in Aug 2025 [H5]. It lies SW of the Heads, roughly in line with NE swell entering the harbour [DERIVED] | Yes: netted, sheltered bay; travel-blog sources only [H12] | Run by NPWS, not the council. Café/kiosk; parking on Greycliffe Ave [H13]. Fatal shark bite **outside** the net, Jan 2026 [H11] |
| **Camp Cove** | **-33.8398, 151.2789**: the OSM way 172983356 "Camp Cove Beach" is a crescent, so its centroid falls just outside the sand. I took the nearest interior point (6 m away, 5.5 m from the edge). [S50, H8] Beachwatch: -33.8394, 151.2788 [S12] | NW, **~310°** [DERIVED: polygon long axis 041°] | **No.** "not netted" [S10, H3]. There is a boat exclusion zone "for the protection of swimmers" [H9] | **Lifeguards on weekends from the last weekend of October to the Anzac Day long weekend, and 7 days a week in the Dec/Jan school holidays**. This season: 31 Oct 2026 – 25 Apr 2027 [H9, H1] | Good → Good → **Very Good** [S10, H3, H1] | 22-23: "often… after 20 mm or more". 23-24: "often… after 5 mm or more". No "occasionally" threshold. Pass rate 94% / 96% [S10, H3] | W–NW onshore, from across the harbour toward Middle Head [DERIVED]. NE sea breeze is cross-shore. S/SE/E are offshore, sheltered by South Head [DERIVED] | Low. Beachsafe calls it "one of the more open beaches" but says waves are "usually only low wind waves" [H7]. Facing NW, it sees E/NE swell only after it bends round inside the Heads [DERIVED]. **I found no source for swell surging into Camp Cove**, so the k values are guesses | **Yes.** Woollahra: bring a snorkel for "fish, octopus, cuttlefish, frogfish" and possibly seahorses [H10]. Reef at both ends [H12] | Limited street parking on Cliff St and Victoria St; dogs banned; kiosk; beach mat in summer [H9] |
| **Parsley Bay** | **-33.8515, 151.2775**: centroid of the OSM beach way 4354470 (unnamed, tagged with the Parsley Bay photo); 25 m from the edge [S50, H8]. Beachwatch: -33.8499, 151.2764 (in the netted area) [S12] | N/NNW, **~335°** [DERIVED: bearing from the beach centroid to the centroid of the OSM swimming-area relation 20380675] | **Yes.** "netted swimming area" [S10, H3]. Floating net, **removed every winter** for maintenance [H14]. Exact dates not found | **Unpatrolled** ("No life saving services") [H15] | Good → Good → Good [S10, H3, H1] | 22-23: occasionally after **light rain**, regularly after **5 mm**. 23-24: occasionally after **little or no rain**, regularly after **5 mm**. Pass rate 93% [S10, H3] | N–NNE wind blows straight up the narrow inlet [DERIVED]. Sheltered from E, S and W by the steep valley [DERIVED] | Very low (narrow inlet off the harbour) [DERIVED] | Some: Woollahra says you can watch snorkellers from the suspension bridge [H10] | **Car park and vehicle access closed 29 May 2024 to "late 2026"** (Sydney Water works). Walk in from Fitzwilliam Rd or The Crescent. Kiosk closed during works [H15] |
| **Watsons Bay** (Watsons Bay Baths) | **-33.8443, 151.2816**: centroid of the OSM beach way 179732278 "Watsons Bay" [S50, H8]. The baths enclosure (OSM relation 6504008) is at -33.8451, 151.2808. Beachwatch: -33.8451, 151.2805 (at the baths) [S12] | W, **~275°** [DERIVED: polygon long axis 005°] | **Yes.** "Installation of new secure shark netting" (2010 upgrade); a "year-round swimming enclosure" with two pontoons [H16]. Beachwatch describes it as a "20 by 40 m enclosed tidal swimming area" [S10, H3] | **Unpatrolled** [H16, H1] | Good → Good → Good [S10, H3, H1] | Occasionally after **light rain**, often after **10 mm** (both years). Pass rate 96% [S10, H3] | **W–SW onshore**, the longest over-water fetch of the five, down the harbour [DERIVED]. NE/E offshore, sheltered by the Heads peninsula [DERIVED] | Very low (deep in the lee of South Head) [DERIVED] | Not noted | Next to the Watsons Bay **ferry wharf** [H16]. Ferry and boat wash is likely but I found no source for it. Shallow water and seagrass: "Beware of shallow water when diving" [H16]. Sewage-overflow alert on 5 Oct 2026, since cleared [H1] |
| **Murray Rose Pool** (Redleaf, Double Bay) | **-33.8719, 151.2474**: centroid of the unnamed OSM beach way 314236405, the sand inside the enclosure, 5 m from the edge [S50, H8]. The enclosure itself (OSM `leisure=swimming_area` way 993893902 "Murray Rose Pool") is centred at **-33.8716, 151.2472**, 28 m from its edge. Use that if the pin should sit on the water. Beachwatch: -33.8713, 151.2470 [S12] | NNW, **~330°** [DERIVED: polygon normal 331°, and the beach-to-enclosure vector] | **Yes.** "netted swimming enclosure" [S10, H3]. Woollahra calls it a "year-round swimming enclosure" with pontoons [H6] | **Unpatrolled** ("No life saving services are provided") [H6] | Good → **Poor** → Poor (24-25, news [H17]) → **Good** [S10, H3, H17, H1]. **Changes grade often** | 22-23: occasionally after light rain, often after **5 mm**. 23-24: occasionally after **little or no rain**, often after **5 mm**. Pass rate 96% → 92% [S10, H3] | N–NW onshore across Double Bay [DERIVED]. Sheltered from S, E and W by Point Piper and Darling Point [DERIVED] | Effectively none (deep inside the harbour, ~4 km from the Heads) [DERIVED] | No | "Popular cooling-off spot" [H10]. Busy on summer weekends [H1]. Limited weekday street parking; Council Chambers car park on weekends [H6] |

### 1a. Checked and left out

| Spot | Pin lat, lon | Grade | Why it's left out |
|---|---|---|---|
| **Milk Beach** (Vaucluse) | -33.8565, 151.2673: centroid of the OSM beach way 4354525 (34 m long, 6 m from the edge) [S50, H8] | **Not monitored by Beachwatch.** There is no site in the GeoJSON feed [S12] | Tiny (Beachsafe: 50 m; "Reflective + Sand Flats"; no hazard rating) [H7]. Not netted. Known for snorkelling and clear water, but the sources are travel blogs [H12]. Without its own Beachwatch site, the bot would have to borrow Nielsen Park's forecast, ~700 m away [DERIVED]. **Optional:** add it as a snorkel-only spot with `beachwatch="Nielsen Park"`. Facing ≈ N (~350°) [DERIVED, rough: the polygon is too small to give a reliable axis] |
| **Rose Bay Beach** | -33.8689, 151.2688: interior point of the OSM beach way 176726580. The centroid rounds to 1 m from the edge. [S50, H8] Beachwatch: -33.8700, 151.2659 [S12] | **Poor** every year: 22-23, 23-24, 24-25 and 25-26 [S10, H3, H17, H1] | Poor grade. Not netted. Dry-weather pass rate only 75–80%. Exceeds the limit "after little or no rain", often after 5 mm [S10, H3]. Two Sydney Water sewage-overflow alerts in October 2026 (9 Oct and 24 Oct) [H1]. Beachsafe calls Rose Bay "predominantly tidal flats" [H7]. Rose Bay also has a ferry wharf and a seaplane base (well known, not sourced here). If you add it anyway: `rain_occ=1, rain_often=5, poor_grade=True`, facing ~312° [DERIVED] |

Other harbour beaches near these that are also out of scope: Lady Bay (nudist; Beachsafe "one of the more open beaches"; not monitored), Gibsons Beach, Kutti Beach, Hermit, Tingara and Queens beaches, Seven Shillings and Double Bay. None of them is a Beachwatch site, except possibly ones I didn't check further west.

---

## 2. Missing eastern ocean pools

| Pool | Pin lat, lon (source) | Shares water with | Exposure / when it's bad | Best tide | Cleaning | Hours / access | Beachwatch |
|---|---|---|---|---|---|---|---|
| **McIver's Ladies Baths** (Coogee; **women and children only**) | **-33.9242, 151.2587**: centroid of the OSM `leisure=swimming_pool` way 173669301, tagged `female=yes`, `male=no` [S50, H8]. `beach-knowledge.md` §2 has -33.9243, 151.2587, which is the same spot | Coogee (south end, between Ross Jones and Wylie's) [S40] | High tide plus strong swell = "washing machine" [S40]. More sheltered than Ross Jones (0.9) and more exposed than Wylie's (0.6), so **0.7** [HEURISTIC]. Faces E (~096° from the polygon), close to Coogee's 100°, so no `facing_override` is needed [DERIVED] | **Low** [S40] (R-P2) | **Tuesdays**; "can change at short notice" depending on tide and weather [S40, H18] | **7am–7pm Oct–Mar; 7am–4pm Apr–Sep** [S40, H18]; OSM `opening_hours` agrees [H8]. Entry is a small fee: $2 or $2.50, sources differ [H18] | No site of its own. It follows Coogee (Poor; 3-day rule) [R-R5] |
| **South Maroubra Rockpool** (two "ring of rocks" pools on the sand at the south end) | **-33.9536, 151.2583**: centroid of the larger OSM `leisure=swimming_pool` way 1374295963 "South Maroubra Rock Pools", 16 m inside the polygon. The smaller ring, way 1374295962, is at -33.9533, 151.2581. [S50, H8] Beachwatch: -33.9535, 151.2580 [S12] | South Maroubra (Maroubra Beach, in the lee of Magic Point) [S10] | The rocks are hard to see at high tide: "only the largest rocks remain above the incoming waves" [H19]. Waves wash straight over, so **0.8** [HEURISTIC; between Mahon (1.0) and the more sheltered pools]. Faces ENE, ~70° [DERIVED: polygon normals 064° and 038°, and §1 of beach-knowledge.md has South Maroubra as E–NE] | **Mid–high.** "During very low tides, the rockpool may be empty" [S10, H3]. A reviewer says to go "as close to high tide as possible" [H19] | None (no structure to drain) [DERIVED] | Free, always open. Beachwatch's site details say "Patrolled all year round" [H1]; the 23-24 report says "not patrolled" [H3] (conflict). Kids' wade, not laps | **Its own site, "South Maroubra Rockpool"**: Good (22-23, 23-24, 25-26). Occasionally exceeds after **little or no rain**, often after **5 mm**; pass rate 85–88% [S10, H3, H1]. **No daily pollution forecast** [H1] |

### 2a. Other eastern-suburbs ocean pools (from an OSM sweep of `leisure=swimming_pool|swimming_area` from Bondi to Malabar) [H8]

| Pool | OSM centroid | Worth adding? |
|---|---|---|
| **Wally Weekes Pool** (North Bondi; also "North Bondi Bogey Hole") | -33.8915, 151.2823 (way 448038496) | **Maybe.** A real ocean pool, but tide-bound. Waverley says it "can be used for protected swimming at high tide and empties with each low tide". Best about 1 h after high tide; it takes hours to refill [H20]. Waverley cleans it about 4 h before low tide; **the day was not found** [H20]. It would be `Pool("Wally Weekes Pool", _BEACH["Bondi (north end)"], 0.9, best_tide="mid_high")` [HEURISTIC]. It shares Bondi's water (Beachwatch "Bondi Beach") |
| **North Bondi Children's Pool** (Mermaid Pool) | -33.8912, 151.2823 (way 448038497) | **No.** A shallow kids' pool built in 1947, with water depth depending on the tide [H20]. Same cleaning pattern as Wally Weekes |
| **Bronte Bogey Hole** | -33.9046, 151.2689 (way 592332752, `leisure=swimming_area`) | **No.** A natural rock-enclosed wading area next to Bronte Baths. Bronte Baths already covers it |
| **Clovelly Ocean Pool** (Geoff James Pool) | -33.9142, 151.2669 (way 173257825) | **No.** It sits inside Clovelly, which is already scored, and Clovelly's water and conditions apply. Could become a note on Clovelly ("lap pool on the south side") |
| **Rob Walker Rockpool** (north Maroubra / Lurline Bay) | -33.9376, 151.2598 (way 1304421852) | **No.** A small natural rock pool (14 m polygon); no sources on access or tide |
| **Ivor Rowe Rockpool** | -33.9334, 151.2617 | Already left out on purpose (beaches.py comment; R-P4) |

---

## 3. How the rain thresholds were set (following `beach-knowledge.md` §3.1 and the existing BEACHES values)

The existing code maps the report wording to numbers like this:
- "little or no rain" or "light rain" → `rain_occ = 1`
- "N mm" → N
- an "often" or "regularly" threshold → `rain_often`

Where the 22-23 and 23-24 reports differ, I took the stricter (more recent) one.

| Site | rain_occ | rain_often | Basis |
|---|---|---|---|
| Nielsen Park | 5 | 20 | [HEURISTIC]. Both reports say only "occasionally… after rainfall", with no "often" threshold. Dry pass 98–100%, now Very Good. Set to match Bondi and Maroubra, the other Good/VG sites with a vague "occasionally" |
| Camp Cove | 5 | 10 | [DERIVED / HEURISTIC]. "Often" was 20 mm (22-23), then 5 mm (23-24), then the grade rose to Very Good. 10 mm splits the two. No "occasionally" was given, so 5 is a guess. **Flagged** |
| Parsley Bay | 1 | 5 | [SRC] S10, H3 |
| Watsons Bay | 1 | 10 | [SRC] S10, H3 |
| Murray Rose Pool | 1 | 5 | [SRC] S10, H3. It was Poor in 23-24 and 24-25, so consider `poor_grade=True` if the grade drops again |
| Rose Bay (not added) | 1 | 5 | [SRC] S10, H3; `poor_grade=True` |
| South Maroubra Rockpool | 1 | 5 | [SRC] S10, H3. **But** a `Pool` takes its rain rule from its parent beach, and Maroubra uses 5/20. See §5 |

## 4. Proposed rules for the harbour category

- **R-H1 (3-day rule) [DERIVED from S10, H6, H10]**: for harbour beaches, run the R-R2 fallback over 72 h, not 24/48 h:
  - IF `rain24 ≥ rain_often` → NO.
  - IF `rain24 ≥ rain_occ` → −25.
  - IF the rain from 24–72 h ago ≥ `rain_often` → −15.

  This is gentler than R-R3, which is for Poor-grade sites. Keep R-R3 (`poor_grade=True`) only for Poor sites. In practice R-R1 (the live `pollutionForecast`) should decide most days, because all five sites have a forecast.
- **R-H2 (swell) [HEURISTIC]**: the harbour k values are near 0 (§6), so swell almost never matters. The exceptions are Nielsen Park and, less so, Camp Cove, in a large NE/E swell. The code currently uses **k = 0.1 outside the NE/E/SE/S sectors**. For harbour beaches that default should be 0.
- **R-H3 (wind) [DERIVED]**: the existing on/offshore logic (§4.1) works as it is, given the facings above. The harbour is mostly sheltered from wind-swell, but the onshore direction still decides how choppy it gets:
  - Watsons Bay is the most exposed to W–SW winds.
  - Camp Cove is the most exposed to W–NW winds.
  - Shark Beach, Parsley Bay and Murray Rose are the most exposed to N–NE winds, including the summer NE sea breeze.

  R-W4 (wind ≥ 40 km/h at exposed beaches) should not apply to these sites.
- **R-H4 (nets) [SRC S10, H14]**: the Shark Beach net is in only from Oct to Apr, and the Parsley Bay net comes out each winter. Consider a "no net" note or a small penalty from May to Sep. Murray Rose and Watsons Bay are year-round enclosures [H6, H16]. Camp Cove is never netted.
- **R-H5 (patrol)**: Camp Cove is patrolled on weekends from late October to Anzac Day, plus 7 days in the Dec/Jan school holidays [H9]. Treat it like the R-PT4 weekend bonus in season. The rest are unpatrolled.

## 5. Gaps, conflicts and design notes

1. **No 2025–26 Sydney-region PDF was found.** The 2025–26 grades come from the live site-details API [H1], which is undocumented. Time Out [H2] corroborates them. The rain wording is from 22-23 and 23-24. The 24-25 report reportedly dropped the per-site detail [H21].
2. **Nielsen Park's net**: Aug 2025 damage [H5] → reported repaired Dec 2025 [H11] → fatal bite outside the net Jan 2026 [H11] → no live NPWS alert on 2026-11-04 [H5]. **I could not confirm that the net is in for the 2026–27 season.** The NPWS venue page didn't render its alerts.
3. **Camp Cove swell.** No source quantifies swell reaching Camp Cove from inside the Heads. The k values are guesses.
4. **Hazard ratings.** Beachsafe gives every one of these harbour sites `hazard: 0` (unrated) [H7]. The proposed `hazard` values (1 for netted enclosures, 2 for Camp Cove) are [HEURISTIC]. They only affect R-PT1.
5. **Facings** come from OSM beach-polygon geometry, not from a published source.
6. **The `Beach` dataclass has no category field.** The constructors below put the harbour beaches in a separate `HARBOUR_BEACHES` list, so `beaches.py` needs no new field. The site would then need to show that list under a "Harbour" heading.
7. **McIver's has two problems with the current `Pool` dataclass**:
   - It closes at **4pm**, from **1 April**, while the dataclass's winter season starts on 13 April. `closes_winter=16` fixes the hour; the season boundary differs by 12 days.
   - There is **no field for "Women only"**. It needs a new field (for example `label: str | None`) or handling by name in the website code.
8. **South Maroubra Rockpool** has its own, stricter Beachwatch site (1/5 mm, no forecast), but `Pool` follows its parent beach (`Maroubra`, 5/20 mm, with a forecast). Either accept the looser Maroubra rule, or add a hidden `Beach("South Maroubra", …, "South Maroubra Rockpool")` as its parent. Its patrol status also conflicts between sources [H1, H3]. **My recommendation: low priority.** It is a kids' wade on the sand, and `beaches.py` already leaves it out on purpose.
9. **Parsley Bay car park.** "Closed until late 2026" [H15]. Check whether it has reopened.
10. **Not found**: the Parsley Bay and Shark Beach net-in/net-out dates for this season; ferry-wash effects at Watsons Bay; the Waverley cleaning day for Wally Weekes and North Bondi Children's Pool (Waverley's site returns 403 to automated fetches).

---

## 6. Proposed code values

The argument order matches `beaches.py`: `Beach(name, facing, k, rain_occ, rain_often, hazard, beachwatch, swim_limit=…, poor_grade=…, snorkel=…, patrolled_all_daylight=…)`, and `Pool(name, beach, exposure, best_tide=…, cleaning_day=…, cleaning_before_low=…, opens=…, closes_summer=…, closes_winter=…, facing_override=…)`.

**About k:** swell barely reaches inside Sydney Harbour [H7], so every harbour k is near 0. Nielsen Park gets the highest values, because Beachsafe says it alone picks up waves "during very big outside swell" [H7], and storm waves have damaged its seawall and net [H4, H5]. All k and swim_limit values are [HEURISTIC].

```python
# Harbour beaches (eastern-additions.md §1). Inside Sydney Harbour: almost no ocean swell
# (k near 0), wind-chop only; rain is the main risk (R-H1 3-day rule). Beachwatch type "Estuarine".
HARBOUR_BEACHES = [
    # Netted Oct-Apr; picks up swell only in very big NE/E swells (Beachsafe; Aug 2025 net damage)
    Beach(
        "Shark Beach (Nielsen Park)",
        340,
        {"NE": 0.15, "E": 0.1, "SE": 0.05, "S": 0.0},
        5,
        20,
        1,
        "Nielsen Park",
        swim_limit=0.5,
        snorkel=True,
    ),
    # Not netted; boat exclusion zone; lifeguards weekends late Oct-Anzac Day + Dec/Jan holidays
    Beach(
        "Camp Cove",
        310,
        {"NE": 0.08, "E": 0.05, "SE": 0.02, "S": 0.0},
        5,
        10,
        2,
        "Camp Cove",
        swim_limit=0.5,
        snorkel=True,
    ),
    # Netted inlet; net removed each winter
    Beach("Parsley Bay", 335, {"NE": 0.05, "E": 0.03, "SE": 0.0, "S": 0.0}, 1, 5, 1, "Parsley Bay", snorkel=True),
    # Year-round netted tidal baths next to the ferry wharf; westerlies are onshore
    Beach("Watsons Bay", 275, {"NE": 0.03, "E": 0.02, "SE": 0.0, "S": 0.0}, 1, 10, 1, "Watsons Bay"),
    # Year-round netted enclosure in Double Bay; grade flips Good/Poor between years
    Beach("Murray Rose Pool", 330, {"NE": 0.0, "E": 0.0, "SE": 0.0, "S": 0.0}, 1, 5, 1, "Murray Rose Pool"),
]
# Milk Beach (no Beachwatch site; snorkel only) and Rose Bay (Poor every year, not netted) are left out

HARBOUR_COORDS = {
    "Shark Beach (Nielsen Park)": (-33.8502, 151.2675),  # inside OSM beach way 4354480
    "Camp Cove": (-33.8398, 151.2789),  # OSM way 172983356 is a crescent; nearest point on the sand to its centroid
    "Parsley Bay": (-33.8515, 151.2775),  # centroid of OSM beach way 4354470
    "Watsons Bay": (-33.8443, 151.2816),  # centroid of OSM beach way 179732278 (baths are at -33.8451, 151.2808)
    "Murray Rose Pool": (-33.8719, 151.2474),  # sand inside the enclosure (OSM way 314236405); water: (-33.8716, 151.2472)
}

# Pools: append to POOLS
POOLS += [
    # R-P2/R-P7/R-P8: women and children only (needs a label field); Tuesdays; 7am-7pm Oct-Mar, 7am-4pm Apr-Sep
    Pool("McIver's Ladies Baths", _BEACH["Coogee"], 0.7, best_tide="low", cleaning_day=1, opens=7, closes_winter=16),
    # R-P6: ring of rocks on the sand at South Maroubra; empty at very low tide. Low priority (see §5.8)
    Pool("South Maroubra Rockpool", _BEACH["Maroubra"], 0.8, best_tide="mid_high", facing_override=70),
]

POOL_COORDS.update({
    "McIver's Ladies Baths": (-33.9242, 151.2587),  # centroid of OSM pool way 173669301
    "South Maroubra Rockpool": (-33.9536, 151.2583),  # centroid of the larger OSM ring, way 1374295963
})
```

Every pin above was checked with a point-in-polygon test after rounding to 4 decimal places. Each one falls inside its OSM beach or pool polygon. Distances to the polygon edge: Shark Beach 16 m, Camp Cove 5.5 m, Parsley Bay 25 m, Watsons Bay 4 m, Murray Rose sand 5 m, McIver's 2 m (the pool is only 36 m long), South Maroubra 16 m. [H8]

---

## Sources

- **S10, S12, S40, S50**: as in `beach-knowledge.md` (State of the Beaches 2022–23 Sydney region; the Beachwatch GeoJSON API, fetched 2026-11-04; Randwick / Ocean Pools NSW, McIver's; OSM Nominatim).
- **H1** Beachwatch site-details API (undocumented; endpoint found in https://www.beachwatch.nsw.gov.au/main-32E54E4O.js as `siteDetailsUrl: apiBaseUrl + "/site/{id}/details"`; fetched 2026-11-04 with no key). The fields used were `SiteType`, `AnnualGrade`, `PatrolDescription`, `Alerts`, `RainGaugeName` and `PollutionDescription`. Example: https://api.beachwatch.nsw.gov.au/site/816de31e-1418-41c9-8987-992538b32c07/details (Nielsen Park). Site IDs: Camp Cove `4904afcf-6313-4456-9f14-cc037087dd76`; Watsons Bay `aaaefe71-5959-40e0-a3a0-a620e8bb49ce`; Parsley Bay `29df3246-4dc4-4a19-9b01-b13fca311257`; Murray Rose Pool `18141cd1-d0ef-4858-b22a-3fcc5c84f604`; Rose Bay Beach `93c7a40f-bf76-420d-9c53-2435adda70b9`; South Maroubra Rockpool `6908705e-c176-4f65-bfd1-39b19ca1d340`
- **H2** Time Out Sydney, "Revealed: the best and worst Sydney beaches for water quality in 2026" (25 Sep 2026): https://www.timeout.com/sydney/news/revealed-the-best-and-worst-sydney-beaches-for-water-quality-in-2026-092526
- **H3** NSW State of the Beaches 2023–24, Sydney region (per-site pages for Camp Cove, Watsons Bay, Parsley Bay, Nielsen Park, Rose Bay Beach, Murray Rose Pool and South Maroubra Rockpool): https://www.environment.nsw.gov.au/sites/default/files/state-of-the-beaches-2023-24-sydney-region-240254.pdf
- **H4** NSW Environment, Nielsen Park seawall rebuild project ("Shark Beach reopened on 12 December 2024"): https://www.environment.nsw.gov.au/topics/parks-reserves-and-protected-areas/park-management/community-engagement/sydney-harbour-national-park/nielsen-park-seawall-rebuild-project ; Secret Sydney (13 Dec 2024): https://secretsydney.com/shark-beach-reopens-in-sydney/
- **H5** NSW National Parks, The Nielsen local alerts (Aug 2025 enclosure damage; alert from 30 Oct 2025, last reviewed 11 Dec 2025, via search summary): https://www.nationalparks.nsw.gov.au/venues/the-nielsen/local-alerts ; live alerts API checked 2026-11-04 (no Shark Beach alert): https://api-prd.nswparks.cloud/api/v1/AlertsClosures/alerts/AD1E62CD-1182-456A-9397-EB08FF3EC793
- **H6** Woollahra Council, Murray Rose Pool: https://www.woollahra.nsw.gov.au/Recreation/Harbourside-Beaches-Bays-and-Baths/Murray-Rose-Pool
- **H7** Beachsafe (SLSA) undocumented JSON (fetched 2026-11-04): https://beachsafe.org.au/api/v4/beach/camp-cove , `/shark-beach`, `/parsley-bay`, `/milk-beach`, `/lady-bay`, `/seven-shillings`, `/double-bay`
- **H8** OpenStreetMap via the Overpass API (queried 2026-11-04; `natural=beach` and `leisure=swimming_pool|swimming_area` in the bbox -33.96,151.235,-33.83,151.29; `out geom` for polygons). Centroids are area-weighted polygon centroids. Where a centroid fell outside or within ~1 m of the edge, I used an interior point. Facings come from the polygon's principal axis: https://overpass-api.de/api/interpreter
- **H9** Woollahra Council, Camp Cove Beach: https://www.woollahra.nsw.gov.au/Recreation/Harbourside-Beaches-Bays-and-Baths/Camp-Cove-Beach
- **H10** Woollahra Council, "5 top spots to keep cool this summer" (5 Jan 2026): https://www.woollahra.nsw.gov.au/News/5-top-spots-to-keep-cool-this-summer
- **H11** 1News / AAP, shark attack at Nielsen Park, 18 Jan 2026 (outside the net; net repaired early Dec): https://www.1news.co.nz/2026/01/18/boy-fights-for-life-after-shark-attack-at-popular-sydney-beach ; https://aapnews.aap.com.au/news/boy-fights-for-life-after-shark-attack-at-popular-beach ; reports of his death: https://www.netfm.net/news/9news/parents-of-sydney-harbour-shark-attack-victim-12-join-poignant-bondi-paddle-out
- **H12** Snorkel guides (travel and commercial blogs; weak sources): https://www.australiantraveller.com/nsw/sydney/snorkelling-sydney ; https://www.islands.com/1899940/sydney-milk-beach-off-beaten-trail-secret-secluded-city-skyline-views ; https://secretsydney.com/best-snorkelling-in-sydney/
- **H13** Woollahra Council, Nielsen Park (NPWS-managed; parking): https://www.woollahra.nsw.gov.au/Recreation/Harbourside-Beaches-Bays-and-Baths/Nielsen-Park
- **H14** Dictionary of Sydney, Parsley Bay shark net (floating net, removed every winter): https://dictionaryofsydney.org/index.php/structure/parsley_bay_shark_net
- **H15** Woollahra Council, Parsley Bay Swimming Enclosure (car park closed 29 May 2024 to late 2026): https://www.woollahra.nsw.gov.au/Recreation/Harbourside-Beaches-Bays-and-Baths/Parsley-Bay-Swimming-Enclosure
- **H16** Woollahra Council, Watsons Bay Baths: https://www.woollahra.nsw.gov.au/Recreation/Harbourside-Beaches-Bays-and-Baths/Watsons-Bay-Baths
- **H17** 2024–25 State of the Beaches news coverage (Rose Bay and Murray Rose Pool Poor; via search summary, as the page returned 403): https://www.inkl.com/news/coogee-beach-among-sydney-swimming-spots-ranked-most-polluted-with-faecal-matter
- **H18** Randwick Council, McIver's Ladies Baths (hours; Tuesday cleaning): https://randwick.nsw.gov.au/facilities-and-recreation/beaches-and-coast/ocean-pools/mcivers-baths ; fee from https://cityhub.com.au/seaside-swim-mciver-ladies-baths and https://www.timeout.com/sydney/sport-and-fitness/mcivers-ladies-baths
- **H19** Ocean Pools NSW, South Maroubra Rock Pools (ring-of-stones pools; go near high tide): https://oceanpoolsnsw.net.au/tag/chalk-espresso ; https://australiaunseen.com/pages/rock-pool/south-maroubra-rock-pools
- **H20** Wally Weekes Pool and North Bondi Children's Pool: https://australiaunseen.com/pages/rock-pool/wally-weekes-pool ; https://australiaunseen.com/pages/rock-pool/north-bondi-childrens-pool ; Waverley pool cleaning schedule (via search snippet; 403 to fetch): https://www.waverley.nsw.gov.au/recreation/beaches_and_coast/pool_cleaning_schedules
- **H21** Pittwater Online News, State of the Beaches 2024–25 (the report shows "only overall results"): https://www.pittwateronlinenews.com/State-of-the-Beaches-Report-2024-25.php
