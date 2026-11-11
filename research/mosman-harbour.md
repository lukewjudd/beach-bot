# Mosman, Middle Harbour and lower north shore harbour spots

Compiled 2026-11-11. Same tags as `eastern-additions.md`:
- **[SRC]**: stated in the cited source.
- **[DERIVED]**: worked out from a sourced fact or from OSM geometry.
- **[HEURISTIC]**: a starting value with no published number behind it. Calibrate it.

Sources are `[M1]`… at the bottom. Forty Baskets, Fairlight, Manly Cove and Little Manly are already in `beaches.py`, so they're not repeated here.

## 0. Read this first

1. **Grades come from the Beachwatch API, not PDFs.** From 2024-25 on there is no Sydney-region PDF. The report moved to the web [M4]. The data is behind these endpoints (found in `main-32E54E4O.js`, no key needed, tested 2026-11-11) [M1]:
   - `GET /trend/annualgrade?id={siteId}`: CSV of grades by report year. "2026" is the 2025-26 report, "2025" is 2024-25 and "2024" is 2023-24.
   - `GET /report/{year}/site/{siteId}`: the per-site report text. It includes `WaterQualityAndRainfall` (the "occasionally after X, often after Y mm" sentence), `DryWeatherPercentage`, `SanitaryInspectionCategory` and `GradeTrend`.
   - `GET /report/{year}/sites/geojson`: every site with its grade for that year.
   - `GET /reports`: the list of available years.
   The bot could pull `rain_occ` / `rain_often` from this every year instead of hand-copying them.
2. **The latest report is 2025-26** (published 2026). The user asked for 2024-25 and 2023-24, so I give all three years.
3. **All eight Beachwatch sites are `Estuarine`, unpatrolled, and use the Sydney (Observatory Hill) rain gauge** [M2]. Harbour rule: avoid swimming for up to **3 days** after rain [M3, p.~77; M8]. That means `poor_grade=True`, the same as the other harbour entries.
4. **Gurney Crescent Baths is closed and being removed.** Beachwatch has carried a "Site temporarily closed … structural instability of the baths and jetty" alert since 17 Aug 2023 [M2]. Northern Beaches Council decided to "decommission and remove the pool in 2026" (Pickering Point) [M9]. **Don't add it.**
5. **Sharks:**
   - On 11 Mar 2026, 1–1.5 m sharks got **inside** the Balmoral Baths net. A witness said they came in over the top of the net at high tide (not confirmed). The baths were closed until divers checked the net on 13 Mar [M10, M11].
   - In January 2026, several people were bitten in Sydney Harbour after heavy rain. One case, a 12-year-old off Vaucluse, is already in eastern-additions [M12].
   - NSW advice (2 Mar 2026): avoid murky water, avoid dawn and dusk, and take extra care within 1 km of harbours "especially after rain or flooding" [M13].
   - A shark listening station is planned at Balmoral [M12].
   The 3-day rain rule already covers the murky-water/bull-shark window.
6. **No net in this area is documented as seasonal.** I found nothing saying the Mosman, Clontarf or Northbridge nets come out in winter. Compare Parsley Bay, which is documented as seasonal. Treat them as **year-round, unconfirmed**.

## 1. Beachwatch-tested sites

Grades are 23-24 → 24-25 → 25-26 [M1, M3]. The rain columns use the latest (25-26) report text [M1]. `rain_occ`/`rain_often` mapping, as for the existing harbour entries: "no / little or no / light rain" → 1, otherwise the mm figure.

| Spot (Beachwatch name) | OSM point (on sand/pool) | Faces | Net / size | Grades | Rain (25-26 text) → occ/often | Dry pass |
|---|---|---|---|---|---|---|
| **Balmoral Baths** | -33.8272, 151.2533: centroid of OSM `swimming_area` way 207465199 (the enclosure) [M5] | **~45° NE** [DERIVED: south part of the Balmoral Beach polygon, axis 136°] | Netted, boardwalk around it [M3, M14]. OSM enclosure ≈ 80×80 m [DERIVED] | G → G → G | "after no rain, and often after 10 mm" → **1/10**. (24-25: 5 mm / 10 mm) | 93% |
| **Edwards Beach** | -33.8210, 151.2512: inside the north half of the OSM Balmoral Beach way 179913855 [M5]. The Beachwatch point (-33.8214, 151.2528) is in the water. OSM "Edwards Beach Shark Net" sign is at -33.8231, 151.2528 | **~90° E** [DERIVED: north part of the polygon, axis 178°] | "rock pool at the northern end and a netted pool at the southern end" [M2]. Size not found | G → G → G | "after 5 mm or more … often after 20 mm" → **5/20**. The most rain-tolerant here | 93% |
| **Chinamans Beach** | -33.8147, 151.2484: centroid of OSM beach way 179934230 [M5] | **~65° ENE** [DERIVED: normal to the 241 m polygon] | **Not netted** (Beachwatch says nothing about a net). ~250 m beach [M3] | G → G → G | "after light rain, and regularly after 10 mm" → **1/10** | **98%** |
| **Clifton Gardens** | -33.8398, 151.2527: centroid of OSM `swimming_area` way 552509270 [M5] | **~116° ESE** [DERIVED: enclosure normal]. Chowder Bay opens S–SE | "large netted swimming area at the western end of a 250 m long beach" [M3]. OSM enclosure ≈ 110×75 m [DERIVED]. (Mosman's venue page reportedly says "no net". Beachwatch, OSM and [M14] all say netted) | G → G → G. 25-26 is microbial **Category A** | "after little or no rain, and often after 10 mm" → **1/10** | 95% |
| **Clontarf Pool** | -33.8060, 151.2519: centroid of OSM `swimming_area` way 41691439 [M5]. Beach: -33.8029, 151.2524 | **~240° WSW** [DERIVED: normal to the Clontarf Beach polygon] | Netted tidal enclosure, rebuilt and lengthened to **64 m** [M15], "most heavily used tidal enclosure" in the LGA. Its net is White's seahorse habitat [M15] | **G → Fair → Fair** (declined 24-25) | "after little or no rain, and often after 10 mm" → **1/10**. Sanitary inspection: **High** | 90% |
| **Northbridge Baths** | -33.8064, 151.2222: centroid of OSM `swimming_area` way 264247021 [M5] | **~66° ENE** down Sailors Bay [DERIVED: polygon normal; check the side on a map] | "30 by 65 m enclosed swimming area … open year-round" [M3]. OSM outline ≈ 100×80 m incl. structures | **Poor → Fair → Fair** | "after little or no rain, and frequently after 10 mm" → **1/10**. Sewage overflow 14 Sep 2026 (cleared) [M2] | 94% |
| **Gurney Crescent Baths** | -33.7935, 151.2354: OSM `swimming_area` way 392406762 [M5] | ~210° [DERIVED, low confidence] | 20 m square netted [M3]. **Closed since Aug 2023, removal planned 2026** [M2, M9] | Poor → Fair → Fair | 1/5 | 92% |
| **Hayes Street Beach** | -33.8416, 151.2194: centroid of OSM beach way 133028222 [M5] | **~157° SSE** [DERIVED] | **Not netted**, ~50 m, next to the Hayes St ferry wharf [M3] | G → G → G | "after little or no rain, and often after 5 mm" → **1/5**. Sewage overflow 25 Oct 2026; forecast "Possible" on 2026-11-11 [M2] | **84%** (lowest) |

### Wind
The bot's `wind_kind` rule is onshore within ±45° of `facing` [DERIVED]:

| Spot | NE sea breeze (045) | Southerly (180) | Westerly (270) | Notes |
|---|---|---|---|---|
| Balmoral Baths | **onshore** | cross/off | offshore | Hunters Bay opens NE–E to the Middle Harbour mouth: the best fetch for a NE breeze |
| Edwards | onshore-ish (cross at 45° exactly) | cross | offshore | |
| Chinamans | **onshore** | offshore/cross | offshore | |
| Clifton Gardens | cross | **cross/onshore, open fetch from the main harbour** | offshore | The southerly buster spot. Sheltered from NE by the Middle Head ridge |
| Clontarf | **offshore** | cross | **onshore** | The good NE-breeze afternoon option; complements Balmoral |
| Northbridge | onshore but ~1 km fetch | offshore | offshore | Very sheltered all round |
| Hayes St | cross | **onshore** | cross | |
| MacCallum | offshore | onshore-ish | **onshore** | Westerlies slop into the pool |

### Swell `k` [HEURISTIC]
- Balmoral, Edwards, Chinamans: `{"NE":0.0,"E":0.05,"SE":0.05,"S":0.0}`. A big E–SE swell refracts round Middle Head into the Middle Harbour mouth; this is unsourced, so calibrate it.
- Clifton, Clontarf, Northbridge, Hayes, MacCallum: all 0.
- Hazard: 1. Beachsafe doesn't rate harbour beaches [eastern-additions H7].

### Amenities, dogs, boats
- **Lifeguards:** none. Beachwatch says every site "is not patrolled" [M2]. Mosman has shark-bite kits at Balmoral, Edwards, Chinamans, Clifton Gardens and Sirius Cove [M6].
- **Amenities** [M2]:
  - Balmoral, Edwards, Clifton: cafe, parking, park, showers, toilets.
  - Chinamans: no cafe.
  - Clontarf: also BBQ.
  - Northbridge: cafe/kiosk, change rooms, hot showers [M2, M8].
  - Hayes St: cafe, parking, toilets.
  - Gurney: none.
- **Parking:** Clifton Gardens car park has an NPWS vehicle entry fee [M16].
- **Dogs:** Mosman bans dogs from beaches except designated off-leash areas [M17]. One secondary source says Clifton Gardens is off-leash only **east of the jetty** [M17b]; Sirius Park is an off-leash area. Unverified for Clontarf and Northbridge.
- **Boats:**
  - Clifton Gardens has a wharf, and dive entry is off the jetty steps [M16, M18].
  - Hayes St is next to a ferry wharf [M3].
  - Balmoral Baths: "popular location for paddleboarding" [M2].
  - Moorings in Hunters Bay, Sailors Bay and off Clontarf/the Spit are local knowledge, not sourced.

### Snorkelling / diving
- **Clifton Gardens / Chowder Bay:** the best spot here. NPWS calls it "a popular spot for scuba diving" [M16]. Under the jetty there are White's seahorses, nudibranchs, frogfish and decorator crabs; enter from the jetty steps [M18, M19]. `snorkel=True`.
- **Cobblers Beach:** NPWS lists snorkelling [M20]. Not Beachwatch-tested.
- **Clontarf:** seahorses live on the net [M15]. Fine for a look, not a destination.
- No other snorkelling sources found.

## 2. Spots Beachwatch doesn't test

| Spot | OSM point | Faces | What's there | Verdict |
|---|---|---|---|---|
| **MacCallum Pool** (Cremorne Point) | -33.8453, 151.2280: OSM `swimming_pool` way 50875309 [M5] | ~222° SW [DERIVED] | 33 m pool "filled with water directly from the harbour" [M7]. Free and unfenced; open 24 h except cleaning [M7, M21]. Cleaned **weekly, tide-dependent**. Closures run over two days, sometimes from 12:30 am. Listed dates for late 2026: Nov 5–6, 9–10, 19–20, Nov 30–Dec 1, Dec 7–8, 15–16, 22–23, 29–30 [M7]. No fixed weekday, so `cleaning_day` doesn't fit; scrape the council page or leave it null. Not tested: borrow **Hayes Street Beach** (~800 m west, same reach) [DERIVED] | **Add** as a `Pool` on a harbour beach. Iconic, and the friends will expect it. `exposure` ~0.1 [HEURISTIC] |
| **Cobblers Beach** (Middle Head) | -33.8259, 151.2630: OSM beach way 10420683 [M5] | ~345° NNW [DERIVED] | Nude bathing; paddling and snorkelling; stingray habitat ("be careful") [M6, M20]. Paid parking at Middle Head; walking track [M20] | Optional snorkel spot; borrow Balmoral Baths' water quality. Sheltered from southerlies |
| **Obelisk Beach** | -33.8298, 151.2609: OSM beach way 112266963 [M5] | ~148° SSE [DERIVED] | Nude; steep rocky track [M6, M22] | Skip: southerly-exposed, no data, awkward access |
| **Sirius Cove** | Not found as a beach in Nominatim | ~S [rough] | Mosman council beach with a shark kit [M6]. "Little Sirius Cove" is still in Beachwatch's download list but has no grades and no live site (404) [M1], so testing has stopped | Skip: no water-quality data, faces southerlies |
| **Reef Beach** (Balgowlah Hts) | -33.8076, 151.2740: OSM beach way 179541460 [M5] | ~40° NE [DERIVED] | Bush-track beach next to Forty Baskets. Not tested | Skip, or borrow Forty Baskets Pool (already in the bot) |
| **Taylors Bay / Bradleys Head** | Not found in Nominatim | ~S | Bushland bays, no facilities, no testing | Skip |
| Whiting Beach (Taronga) | -33.8444, 151.2385: OSM way 179913213 | ~194° | Not tested | Skip |

## 3. Ranking (worth adding)
1. **Balmoral Baths**: Good every year, a big net, full amenities. NE breeze is onshore.
2. **Clifton Gardens**: Good (Cat A), netted, the best snorkel/dive. Southerly-exposed. `snorkel=True`.
3. **Chinamans Beach**: Good, 98% dry pass, quiet. No net.
4. **Edwards Beach**: Good and the most rain-tolerant (5/20). Netted pool at the south end. It's next door to Balmoral, so it could be one card with two Beachwatch sites.
5. **Clontarf Pool**: Fair, but a 64 m net and offshore in a NE breeze, so it's the afternoon pick.
6. **MacCallum Pool**: no testing (borrow Hayes St). Irregular cleaning closures.
7. **Northbridge Baths**: Fair, very sheltered, year-round.
8. **Hayes Street Beach**: Good but the lowest dry pass (84%), tiny, ferry wharf.
9. Cobblers (snorkel/nude, optional). **Skip:** Gurney Crescent (closed/being removed), Obelisk, Sirius Cove, Reef, Taylors Bay.

## Draft entries (unverified against tests)
```python
Beach("Balmoral Baths", 45, {"NE":0.0,"E":0.05,"SE":0.05,"S":0.0}, 1, 10, 1, "Balmoral Baths", swim_limit=0.5, poor_grade=True, harbour=True),
Beach("Edwards Beach", 90, {"NE":0.0,"E":0.05,"SE":0.05,"S":0.0}, 5, 20, 1, "Edwards Beach", swim_limit=0.5, poor_grade=True, harbour=True),
Beach("Chinamans Beach", 65, {"NE":0.0,"E":0.05,"SE":0.05,"S":0.0}, 1, 10, 1, "Chinamans Beach", swim_limit=0.5, poor_grade=True, harbour=True),
Beach("Clifton Gardens", 116, {"NE":0.0,"E":0.0,"SE":0.0,"S":0.0}, 1, 10, 1, "Clifton Gardens", poor_grade=True, snorkel=True, harbour=True),
Beach("Clontarf", 240, {"NE":0.0,"E":0.0,"SE":0.0,"S":0.0}, 1, 10, 1, "Clontarf Pool", poor_grade=True, harbour=True),
Beach("Northbridge Baths", 66, {"NE":0.0,"E":0.0,"SE":0.0,"S":0.0}, 1, 10, 1, "Northbridge Baths", poor_grade=True, harbour=True),
Beach("Hayes Street Beach", 157, {"NE":0.0,"E":0.0,"SE":0.0,"S":0.0}, 1, 5, 1, "Hayes Street Beach", poor_grade=True, harbour=True),
# MacCallum: Pool("MacCallum Pool", <Hayes Street Beach>, 0.1, facing_override=222)  (cleaning dates irregular)
```
Coords for the `COORDS` dict:
- Balmoral Baths (-33.8272, 151.2533)
- Edwards (-33.8210, 151.2512)
- Chinamans (-33.8147, 151.2484)
- Clifton (-33.8398, 151.2527)
- Clontarf (-33.8060, 151.2519)
- Northbridge (-33.8064, 151.2222)
- Hayes (-33.8416, 151.2194)
- MacCallum (-33.8453, 151.2280)

## Sources
- **M1** Beachwatch API (undocumented; endpoints in https://www.beachwatch.nsw.gov.au/main-32E54E4O.js). Fetched 2026-11-11:
  - https://api.beachwatch.nsw.gov.au/trend/annualgrade?id=…
  - https://api.beachwatch.nsw.gov.au/report/2026/site/… and /report/2025/site/…
  - https://api.beachwatch.nsw.gov.au/data-download-sites
  - Site IDs: Balmoral Baths `e6daf905-fb81-4aea-911d-fa3350abd298`, Edwards `70704ffa-ebc9-4d90-825a-a62461f7ed11`, Chinamans `90ce83b9-78a8-48c2-bb26-4af4e31111c6`, Clifton Gardens `442ebbc9-d136-4279-b452-609dd1ad9e36`, Clontarf Pool `6c79de5b-7c82-48bc-91df-318374838a43`, Northbridge `3f60c91f-138b-4230-953f-b668e88a2635`, Gurney Crescent `3397c49e-fd59-4b4f-a2d6-57c2a08450a6`, Hayes Street `eefcfac8-c063-47b7-9d19-0340f5fa450f`.
- **M2** Beachwatch site details: https://api.beachwatch.nsw.gov.au/site/{id}/details. Fields used: SiteType, AnnualGrade, PatrolDescription, Amenities, Description, Alerts, RainGaugeName. Fetched 2026-11-11.
- **M3** State of the Beaches 2023-24, Sydney region (pp. 78–87): https://www.environment.nsw.gov.au/sites/default/files/state-of-the-beaches-2023-24-sydney-region-240254.pdf
- **M4** Pittwater Online News on the 2024-25 report (webpage only; Clontarf and Gurney rated Fair): https://www.pittwateronlinenews.com/State-of-the-Beaches-Report-2024-25.php
- **M5** OSM Nominatim (search, reverse, lookup with polygon_geojson), UA "beach-bot research", ≤1 req/s.
- **M6** Mosman Council, beaches: https://mosman.nsw.gov.au/recreation/beaches
- **M7** North Sydney Council, MacCallum Pool: https://www.northsydney.nsw.gov.au/directory-record/1523/maccallum-pool
- **M8** Willoughby Council, Northbridge Baths: https://www.willoughby.nsw.gov.au/Council/Venues/Northbridge-Baths
- **M9** Northern Beaches Your Say, Pickering Point tidal pool decommissioning (seen in search results; the page returned 404 to a direct fetch): https://yoursay.northernbeaches.nsw.gov.au/pickering-point-seaforth-tidal-pool-decommissioning
- **M10** Mosman Collective, sharks inside Balmoral Baths (Mar 2026): https://mosmancollective.com/general/mosman-council-confirms-sharks-still-inside-balmoral-baths-with-specialist-divers-set-to-return-on-friday/
- **M11** https://mosmancollective.com/general/sharks-spotted-inside-netted-zone-at-balmoral-baths-as-swimmers-scramble-from-the-water/
- **M12** Mosman Collective, Balmoral listening station (31 Mar 2026): https://mosmancollective.com/general/balmoral-beach-named-as-site-for-new-shark-listening-station-after-horror-summer-of-attacks/
- **M13** NSW Govt, bull shark release (2 Mar 2026): https://www.nsw.gov.au/ministerial-releases/increased-bull-shark-activity-expected-around-beaches-and-waterways-following-heavy-rainfall
- **M14** North Shore Mums, harbour beaches (Oct 2025): https://www.northshoremums.com.au/harbour-beaches-swimming-enclosures-sydney
- **M15** Northern Beaches Council, Clontarf tidal pool (search snippets; page 404 to a direct fetch): https://yoursay.northernbeaches.nsw.gov.au/clontarf-tidal-pool
- **M16** NPWS, Chowder Bay – Gooree: https://www.nationalparks.nsw.gov.au/things-to-do/swimming-spots/chowder-bay-gooree
- **M17** Mosman Council, companion animals: https://mosman.nsw.gov.au/residents/Pets/companion-animals
- **M17b** https://findadogpark.com.au/new-south-wales/mosman/clifton-gardens-reserve-dog-off-leash-area
- **M18** https://scubadiverlife.com/muck-diving-chowder-bay/
- **M19** https://www.sydney.com/articles/best-snorkelling-in-sydney
- **M20** NPWS, Cobblers Beach: https://www.nationalparks.nsw.gov.au/things-to-do/swimming-spots/cobblers-beach
- **M21** https://australiatravelquestions.com/?p=41407 (24 h, free)
- **M22** https://www.freebeach.com.au/beach/obelisk-beach-sydney
