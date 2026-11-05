# Sydney Northern Beaches Knowledge Base (for a daily beach-picker)

Compiled 2026-11-04. It is the companion to `beach-knowledge.md` (eastern suburbs) and uses the same conventions: it turns local, surfer and agency knowledge into rules a scoring script can use with Open-Meteo weather and marine forecasts, BOM rain gauges and the Beachwatch pollution forecast. It covers Manly to Palm Beach, plus a short list of harbour and Pittwater swims.

How to read the confidence tags:
- **[SRC]**: the number or fact is stated in the cited source.
- **[DERIVED]**: worked out from a sourced fact, for example a facing bearing measured from the OSM coastline, or offshore wind taken as the opposite of a sourced facing.
- **[HEURISTIC]**: no published number exists. This is a starting value to calibrate against what you see at the beach. Every heuristic says which sourced fact it rests on.

Source IDs such as `[N4]` refer to the **Sources** list at the end. `[S…]` IDs refer to the sources in `beach-knowledge.md`; the Sydney-wide patterns there (§3.2 to §3.5: bluebottle mechanism, upwelling, NE sea breeze, southerly busters) apply here unchanged and are not repeated.

---

## 0. Key findings to read first

1. **One marine point and one forecast point are enough.** Over the last 30 days plus the 7-day forecast, the three Open-Meteo wave cells along this coast track each other closely: the cell off Manly reads 0.86× and the cell off Avalon 0.89× the cell off Narrabeen (p10–p90 0.84–0.92). SST and tide differ by ≤0.05 °C and ≤0.01 m. That spread is far smaller than the uncertainty in the per-beach `k` values, so one point is enough. `Region` also only takes one of each. [N15 own test]
2. **The rock pools are drained overnight on a fixed weekday and often stay shut until 5pm the next day.** The council publishes a dated 2026 roster for each pool. The pool closes in the afternoon or evening of day D (Pittwater pools: "not available approximately three hours prior… and approximately 12 hours after"). It re-opens at 5am on D+1 in about a third of weeks and at **5pm on D+1 in about two-thirds**. The **morning after** is therefore the session most often lost, not the cleaning day itself. Fairy Bower (Wednesdays) and Fairlight (Thursdays) are cleaned in the daytime. North Curl Curl is never cleaned. [N7, N8]
3. **Lagoon outflows matter at four beaches**: Queenscliff (Manly Lagoon), North Curl Curl (Curl Curl Lagoon), Long Reef (Dee Why Lagoon) and North Narrabeen (Narrabeen Lagoon). Beachwatch: "Swimming is not recommended at ocean beaches located near lagoon entrances if the lagoon is open." [N2] Council does not publish whether a lagoon is open. It opens the entrances by machine once the water reaches set levels: Manly 1.4 m AHD, Curl Curl and Dee Why 2.2 m AHD, Narrabeen 1.0–1.3 m AHD. That is, after heavy rain. [N11]
4. **Patrols start at 9am**, not 7am as in the east. Council lifeguards work "every day from 9am – 5pm and longer in the summer peak" from the last weekend of September to the last weekend of April. Manly is patrolled all year. [N9, N10] Weekday-morning hours before 9am are therefore unpatrolled everywhere.
5. **Shelly Beach (Manly) faces west, not east.** Waves "have to refract 270˚ round Blue Fish Point to reach the beach" [N1 Shelly]. The OSM coastline at the sand runs at 290° seaward [N14, DERIVED]. It is the region's Clovelly: Beachsafe hazard 2, inside the Cabbage Tree Bay aquatic reserve, and sheltered from S/SE swell and wind. Its water quality is its weak point: Poor in 2024-25, Good in 2026 [N4, N5].

---

## 1. Forecast points, rain gauges and favourite

| Setting | Recommendation | Why |
|---|---|---|
| `forecast_point` | **(-33.752, 151.297)**, Dee Why Beach | The weather blend averages the Open-Meteo land and sea cells either side. This point gives land (-33.708, 151.267), the low ground beside Narrabeen Lagoon (elev. 3 m), and sea (-33.779, 151.343), ~5 km off Curl Curl [N15]. Both cells sit in the middle of the 25 km coast. The point north of Newport, (-33.66, 151.32), gives a sea cell far out in Broken Bay (-33.568, 151.338) [N15], so avoid it. |
| `marine_point` | **(-33.70, 151.37)** with `cell_selection=sea` | It snaps to the MFWAM cell (-33.7083, 151.3750), ~6 km off Narrabeen and clear of headlands. The other choices: (-33.80, 151.33) snaps to (-33.7917, 151.2917), which is effectively on Manly's beachfront and reads 14% lower. (-33.62, 151.37) snaps to (-33.625, 151.375) and reads 11% lower [N15]. |
| Optional second points | Only if the region is ever split in two: Manly–Narrabeen on the points above, and Newport–Palm Beach on forecast (-33.64, 151.31) and marine (-33.62, 151.37). | Pittwater beaches get the southerly change some minutes later and sit nearer the Broken Bay cells. The test above shows little difference in swell [N15]. Not worth a code change now. |
| `rain_gauges` | **("94759", "94768")**: Terrey Hills + Observatory Hill | Both are in the BOM bundle the bot already reads, and both report `rain_trace` (checked 2026-11-04). Terrey Hills (-33.691, 151.225) is the only rain gauge on the peninsula. North Head (95768) and Sydney Harbour (95766) report "-" for rain [N16]. Terrey Hills is ~200 m up on the plateau, ~8 km inland of Mona Vale, so expect it to read a little wetter than the beaches. That suits the "take the wetter station" rule. |
| `favourite` | **"Shelly Beach"** | It plays the role Clovelly does in the east. It is the lowest-hazard ocean swim on the coast (Beachsafe 2 [N1]), the bay's best snorkelling (Cabbage Tree Bay aquatic reserve, no fishing since 2002 [N18]), and it stays calm when the open beaches are big from the S/SE ([N1]; "small S or SE swell often suits Shelly" [N17]). It faces W, so it shrugs off the southerly buster too. **Manly** is the alternative: it is patrolled all year [N9, N10], but it is hazard 6 with 218 rescues a year [N1], and its south end only partly avoids the swell. Caveat: Shelly's water quality is its weak point (Poor in 2024-25 [N4], Good in 2026 [N5]; "occasionally" fails after little or no rain [N2]), so a tie-break toward it should still respect the rain rules. |

---

## 2. Per-location table: ocean swimming beaches

Bearings are the direction the beach faces, looking out to sea. Wind and swell directions are the direction they come FROM. Pins are the centre of the OSM `natural=beach` polygon [N14]. Where the polygon's area centroid fell outside its own outline, the pin is the nearest point inside it. Facings come from the Beachsafe description where one is given [N1] and were checked against the bearing of the OSM coastline within 250 m of the pin [N14, DERIVED].

| Location | Pin lat, lon (source) | Beachwatch site (lat, lon) [N3] | Faces | Offshore wind | Sheltered from / exposed to | Hazard [N1] | Patrol | Notes |
|---|---|---|---|---|---|---|---|---|
| **Manly** (South Steyne) | -33.7981, 151.2893 (OSM "Manly Beach" polygon = the South Steyne section) | "South Steyne Beach" (-33.7989, 151.2903) | ENE ~75° (south end curves NE; coastline 56–86°) [DERIVED] | WSW–W [N12 Manly-South Steyne / N Steyne] | "Waves tend to be a little lower toward Manly" [N1]; "some shelter here from south winds" [N12]. Exposed to NE/E swell and the NE sea breeze | 6 (whole beach averages 218 rescues/yr) [N1] | **Year-round** [N9, N10] | Rips along the whole beach. "The efficient Escalator" rip persists even in small surf [N1]. North Steyne is folded in here (§2a) |
| **Queenscliff** (north end of Manly beach) | -33.7878, 151.2881 (OSM relation "Queenscliff Beach") | "Queenscliff Beach" (-33.7869, 151.2887) | ESE ~105° (coastline 113°) [DERIVED] | NW [N12 Queenscliff] | Gets more of the southerly swell than the Manly end ([N1]; "waves a little lower toward Manly"). Manly Lagoon enters just north of the SLSC [N1] | 6 [N1] | Sept–Apr [N2, N9] | **Lagoon outflow** (Manly Lagoon) [N2, N11]. Queenscliff bombora breaks only above 3 m [N1] |
| **Shelly Beach** (Manly) | -33.8006, 151.2980 (OSM "Shelly Beach") | "Shelly Beach (Manly)" (-33.8005, 151.2977) | **W–WNW ~290°** [N1 "faces the west"; OSM coastline 290°, DERIVED]. The bay mouth opens N–NE | E–SE (blows off the land behind the beach) [DERIVED] | S/SE swell and wind: sheltered (waves must refract 270° round Blue Fish Point [N1]; "small S or SE swell often suits Shelly" [N17]). E/NE long-period swell surges on the outer reef while the surface looks calm [N17]. "Shore break heavy during big seas" [N1] | **2** [N1] | Unpatrolled most of the year. The council page says "Lifeguards do not patrol this beach at this time of year" (Nov 2026) [N9]; Beachwatch 2022-23 says "not patrolled" [N2] | **Snorkel**: Cabbage Tree Bay aquatic reserve [N18], max depth ~6 m [N18]; "high tide often improves visibility" [N17]. Water quality is the weak point (§5) |
| **Freshwater** | -33.7818, 151.2909 (OSM "Freshwater Beach") | "Freshwater Beach" (-33.7816, 151.2908) | SE ~130° [N1 "faces southeast"; coastline 128°] | NW [N12] | North side handles NE swell and "offers some protection from summer northeast winds" [N1]. Exposed to E–S | **7** (121 rescues/yr; three permanent rips, one against each headland plus one shifting in the centre) [N1] | Late Aug – late May [N9] | Rock pool on the northern platform [N1] |
| **North Curl Curl** | -33.7680, 151.2979 (north part of the OSM "Curl Curl Beach" polygon, split at -33.770) | "North Curl Curl Beach" (-33.7676, 151.2982) | SE ~130° (coastline 138°) [DERIVED]. Beachsafe gives ESE for the whole beach [N1] | NW–WNW [N12] | Dee Why Head shades the NE swell a little [HEURISTIC]. "Receives all southerly swell… blown out in southerlies" [N1] | 6 [N1] | Sept–Apr [N2] | **Lagoon outflow** (Curl Curl Lagoon; Beachwatch says the site is "near the entrance") [N2] |
| **South Curl Curl** | -33.7720, 151.2943 (south part of the same polygon) | "South Curl Curl Beach" (-33.7734, 151.2933) | ESE ~115° (coastline 121°) [DERIVED] | WNW [N12] | Fully exposed. Averages 1.6 m waves, five beach rips plus permanent headland rips [N1] | **7** [N1] | Sept–Apr [N2] | Largest rip runs out past the southern rock pool [N1] |
| **Dee Why** (south end) | -33.7505, 151.2990 (OSM "Dee Why Beach") | "Dee Why Beach" (-33.7533, 151.2973) | SE ~125° (coastline 128°) [DERIVED] | NW [DERIVED] | "Inside the point is a kiddies corner when the waves are lower" [N1]. Exposed to E–S | 6 [N1] | Year-round [N9] or Sept–May [N10] (conflict, §8) | Rock pool and seawall at the south end [N1] |
| **Long Reef** | -33.7447, 151.3075 (OSM "Long Reef Beach") | "Long Reef Beach" (-33.7452, 151.3059) | **SSE ~155°** (coastline 153°) [DERIVED] | **NE–N** at the north end ("summer northeast winds blow offshore") [N1] | Long Reef headland shelters it from NE wind and swell. Exposed to SE/S; "in winter it is exposed and often blown out" [N1] | 6 [N1] | Sept–Apr [N2] | **Lagoon outflow** (Dee Why Lagoon enters south of the SLSC) [N1, N2]. Useful on summer NE sea-breeze evenings |
| **Collaroy** | -33.7286, 151.3007 (OSM "Collaroy Beach") | "Collaroy Beach" (-33.7326, 151.3029) | **ENE ~75°** [N1 "faces east-northeast"; coastline 77°] | WSW–SW [N12] | "**Sheltered from the southerlies**, while exposed to summer northeasterlies, with waves usually less than 1 m" [N1]. "Summer northeast winds and waves can create strong rips" [N1] | **5** (lowest of the open beaches) [N1] | Sept–Apr [N2] | Big seas bring in seaweed [N1]. **Most rain-sensitive ocean beach here**: "often" fails after 5 mm [N2] |
| **North Narrabeen** | -33.7072, 151.3046 (OSM "North Narrabeen Beach") | "North Narrabeen Beach" (-33.7056, 151.3064) | ESE ~110° (coastline 115°; surfnerd ESE [N13]) | NW [N13] | Exposed. "Strong rips and higher waves… often heavy plunging wave at low tide" [N1] | **7** [N1] | Sept–Apr [N2] | **Lagoon outflow and entrance currents**: "the lagoon entrance can be a problem when deep at high tide and with swift currents on a falling tide" [N1] |
| **Warriewood** | -33.6904, 151.3087 (OSM "Warriewood Beach") | "Warriewood Beach" (-33.6911, 151.3092) | ENE ~80° [N1; coastline 89°] | W [DERIVED]; surf guides favour SSW [N12] | "Turimetta Head affords the beach some protection from southerly waves and winds" [N1] | 6 [N1] | Holiday periods in 2022-23 [N2]. Council took over this stretch from Sept 2025 [N10] (season unconfirmed) | Warriewood WWTP outfall is a listed pollution source [N2]. Steep access road [N1] |
| **Mona Vale** | -33.6826, 151.3122 (OSM "Mona Vale Beach") | "Mona Vale Beach" (-33.6797, 151.3140) | ESE ~115° (coastline 118°) [DERIVED] | NW [N12] | The north-end reef has "slight protection from summer north-east winds" [N1]. Exposed to E–S | **7** (5–6 beach rips; permanent rip past the pool) [N1] | Sept–Apr [N2] | Swim in the north, between the flags or in the pool [N1] |
| **Bungan** | -33.6675, 151.3192 (OSM "Bungan Beach") | "Bungan Beach" (-33.6659, 151.3208) | ESE ~115° [N1; coastline 117°] | NW [N12] | Northern corner has "some protection from summer northeast sea breezes" [N1] | **7** [N1] | **Late Dec – end Jan only** (2022-23) [N2]. Council took over this stretch from 2025 [N10] (unconfirmed) | Steep access, limited parking, "never gets crowded" [N1] |
| **Newport** | -33.6537, 151.3237 (OSM "Newport Beach") | "Newport Beach" (-33.6540, 151.3237) | E ~95° [N1 "faces east"; coastline 101°] | W [DERIVED] | **Newport Reef** "substantially reduces the east and southeast swell toward the south… 1 m in the north to less than 0.5 m in the south" [N1] | 6 (half the rescues of its neighbours) [N1] | Sept–Apr [N2] | Swim south of the club, or in the pool [N1] |
| **Bilgola** | -33.6454, 151.3281 (OSM "Bilgola Beach") | "Bilgola Beach" (-33.6453, 151.3288) | SE ~125° [N1; coastline 121°] | NW [N12 NNW] | Newport Reef gives "some protection from southeast waves" [N1]. North end sheltered from NE wind [N1] | 6 (83 rescues/yr). Southern rip, the "Newport Express" [N1] | Sept–Apr [N2] | Pool on the southern platform [N1] |
| **Avalon** | -33.6351, 151.3329 (OSM relation "Avalon Beach") | "Avalon Beach" (-33.6357, 151.3326) | SE ~125° [N1; coastline 124°] | W [N13] | Exposed. Averages 1.6 m waves, bars usually detached [N1] | **7** (58 rescues/yr) [N1] | Sept–Apr [N2] | Bluebottles in summer NE winds [N13] |
| **Whale Beach** | -33.6106, 151.3317 (OSM "Whale Beach") | "Whale Beach" (-33.6112, 151.3323) | E ~95° [N1; coastline 98°] | W [DERIVED] | "North end… some protection from north winds… in winter the south end offers the same protection from south winds" [N1] | **7** (78 rescues/yr) [N1] | Sept–Apr [N2] | Two stormwater drains empty onto the centre of the beach [N1] |
| **Palm Beach** (south end) | **-33.5978, 151.3251**: the centre of the southern 600 m of the OSM relation "Palm Beach". The whole polygon's centre (-33.5901, 151.3257) sits at North Palm, the rougher half | "Palm Beach" (-33.5988, 151.3258) | ENE ~75° at the patrolled south end (coastline 68°). The 2.3 km beach as a whole faces E [N1] | W [N12] | "Increasing protection from Little Head", so S swell is lower at the south end. But "the southern rips do however intensify during northeast waves and winds" [N1] | 6 (south end, 78 rescues/yr). North Palm is 7 (148/yr) [N1] | Sept–Apr [N2] | Best water quality on the coast (Very Good every year) [N2, N4, N5] |

### 2a. Merged, dropped and optional
- **North Steyne** is merged into **Manly**. It is the middle of the same 1.5 km beach and the same rip system (Beachsafe uses one text for Queenscliff, North Steyne and Manly [N1]). It keeps its own Beachwatch site ("North Steyne Beach", -33.7910, 151.2880; occ. 5 mm, often 20 mm [N2]). Add it as its own spot only if you want a third pin on that beach.
- **Long Reef** is kept although it is the north end of the Dee Why beach. It is the one beach where the summer NE sea breeze blows offshore [N1]. On a hot weekday evening that is useful. Drop it if you want fewer pins: its water is Dee Why Lagoon's [N2].
- **Bungan** is kept but has the thinnest patrol record (only late Dec–Jan in 2022-23 [N2]). Its hazard of 7 will usually rank it low.
- **Not swim spots / left out**: Fairy Bower beach is "a sliver of sand… a few metres… at low tide" [N1], so it is a pool only (§4). Turimetta is unpatrolled, with "rocks in the surf, together with rips and often dumping waves" [N1]. Narrabeen and South Narrabeen are the middle of the 3.5 km Narrabeen–Collaroy beach, covered by Collaroy and North Narrabeen. **The Basin** (Mona Vale, "Bongin Bongin") is a calm option to add later: hazard 3, waves ~0.5 m behind a reef, shares the Mona Vale pool [N1]. But it is unpatrolled and has no Beachwatch site of its own.

---

## 3. Harbour and Pittwater swims (category "harbour")

No ocean swell to speak of. These are estuarine sites, so Beachwatch's 3-day rain advice applies [N2]. Shortlist:

| Location | Pin lat, lon (source) | Beachwatch site (lat, lon) [N3] | Faces | Swim area | Notes |
|---|---|---|---|---|---|
| **Manly Cove** (west of the wharf) | -33.7989, 151.2827 (OSM beach polygon w371494483, next to the "Manly Cove Tidal Pool" swimming area) | "Manly Cove" (-33.7994, 151.2825) | S–SSW ~195° (OSM polygon axis; Beachsafe: the eastern half is SW-facing) [N1, DERIVED] | Netted enclosure at the centre of the beach by the ferry wharf [N2] | Easiest to reach (ferry). S winds blow onshore across North Harbour [DERIVED]. "Occasionally" fails after little or no rain [N2] |
| **Little Manly Cove** | -33.8065, 151.2866 (OSM "Little Manly Cove") | "Little Manly Cove" (-33.8072, 151.2868) | S ~190° [N1 "faces south"] | 30 m square enclosure at the east end [N2] | Popular family beach with a park and boat ramp [N1] |
| **Fairlight** | -33.7999, 151.2750 (OSM "Fairlight Beach") | "Fairlight Beach" (-33.8007, 151.2748) | S ~190° [N1] | Small beach plus a council rock pool (§4) | "Receives low swell through the heads, which surges up the steep beach" [N1], so give it a small k |
| **Forty Baskets** | -33.8035, 151.2700 (OSM "Forty Baskets Beach"; the netted pool polygon is at -33.8032, 151.2706) | "Forty Baskets Pool" (-33.8031, 151.2706) | NE ~60° [N1 "faces northeast"] | 20 × 40 m netted swimming area [N2] | Quiet. Street parking on Beatty St [N1] |
| **Paradise Beach Baths** (Pittwater) | -33.6243, 151.3168 (OSM "Paradise Beach") | "Paradise Beach Baths" (-33.6238, 151.3165) | W ~275° (OSM coastline 277°) [DERIVED] | 30 × 20 m netted enclosure [N2] | The best Pittwater option with road access. NW–W winds blow onshore across Pittwater [DERIVED] |

Considered and not recommended for now: **Clareville** (a "narrow strip of high tide sand fronted by 50 m wide intertidal sand flats" with moored boats and dinghies [N1], so it is no swim at low tide). **Taylors Point Baths** (15 × 20 m, Good [N2], but small and a naval facility next door [N1]). **The Basin, Pittwater** (Very Good water [N2, N4], but reached only by ferry or a long walk). **Bayview Baths** (Poor [N2, N4]). **Clontarf Pool** (Fair in 2024-25 [N4]). **Narrabeen Lagoon** sites (Poor [N2, N4, N5]).

---

## 4. Per-location table: ocean rock pools

Water quality follows the beach next to it (R-R5 in the east). Pins are the centre of the OSM `leisure=swimming_pool` polygon (or the nearest point inside it) [N14]. For pools with a toddler pool beside them, the pin is on the main pool. "Cleaning" is from the council's dated 2026 roster [N7]. D = the weekday it closes. Re-opening is at 5am or 5pm on D+1; the 5am/5pm counts are for 2026. Closing times vary with the tide, mostly afternoon to late evening (some after midnight, which is still the night of D).

| Pool | Pin lat, lon | Fed by | Exposure (waves over the walls) | Tide | Cleaning (closes → re-opens) | Notes |
|---|---|---|---|---|---|---|
| **Fairy Bower** (20 m, triangular, 1929) | -33.8008, 151.2945 | Shelly Beach (Cabbage Tree Bay) [DERIVED] | Sits on the Bower point. The Bower surf break starts working above 1.5 m and has been surfed to 7 m [N1], so big SE swell breaks just seaward. [HEURISTIC 0.7] | Not found. Low tide is suggested for calm [N20, travel blog, weak] | **Every Wednesday, daytime** [N7, N8] | Faces N into the bay (OSM coastline ~8°) [DERIVED] |
| **Queenscliff** (50 m) | -33.7863, 151.2894 | Queenscliff | North end of Manly beach, where most S swell arrives [N1]. [HEURISTIC 0.9] | – | **Tue → Wed** (re-opens 5am ×14, 5pm ×29) [N7] | Widened ramp, ladder at the deep end [N7] |
| **Freshwater** (50 m) | -33.7816, 151.2948 | Freshwater | Northern rock platform of a 1.5 m-wave beach [N1]. [HEURISTIC 0.9] | – | **Wed → Thu** (5am ×15, 5pm ×28) [N7] | |
| **North Curl Curl** (25 m) | -33.7676, 151.3016 | North Curl Curl | **Most exposed.** At the tip of Dee Why Head. In big surf "waves crashing into the rock shelf then flowing over the rock pool"; the gate is "locked in big surf" [N20]. [HEURISTIC 1.0] | **Low–mid only**: reached along the beach at low tide, "during high tide it can only be accessed via the coastal walk" [N7, N20] | **Never cleaned** ("because of the difficult access") [N7] | Expect it to be green and weedy |
| **South Curl Curl** (50 m + toddler pool) | -33.7745, 151.2934 | South Curl Curl | The beach's largest rip runs out past it [N1]. [HEURISTIC 0.9] | – | **Sun → Mon** (5am ×19, 5pm ×23) [N7] | Built 1925 [N1] |
| **Dee Why** (50 m + toddler area) | -33.7552, 151.2988 | Dee Why | Beside Dee Why Point (a break that works above 1.5 m [N1]). [HEURISTIC 0.8] | – | **Thu → Fri** (5am ×11, 5pm ×32) [N7] | Also refreshed after busy weekends [N7 search snippet] |
| **Collaroy** | -33.7335, 151.3044 | Collaroy | South end of a beach "sheltered from the southerlies". "The Kick" breaks off the pool in big SE swell [N1]. [HEURISTIC 0.7] | – | **Mon → Tue** (5am ×16, 5pm ×25) [N7] | Disability access [N7] |
| **North Narrabeen** (50 m, 8 lanes) | -33.7035, 151.3093 | North Narrabeen | On the headland at the lagoon entrance. [HEURISTIC 0.8] | – | **Mon → Tue** (5am ×16, 5pm ×25) [N7] | Swimming clubs all year [N7]. Lagoon outflow affects its water |
| **Mona Vale** (30 m + toddler pool) | -33.6787, 151.3166 | Mona Vale | On the reef/tombolo between The Basin and Mona Vale [N1]. [HEURISTIC 0.9] | – | **Wed → Thu** (5am ×15, 5pm ×28) [N7] | |
| **Newport** (50 m) | -33.6585, 151.3246 | Newport | South end, in the lee of Newport Reef [N1]. One reviewer saw "waves still pouring over the edge at low tide" in a big swell [N21]. [HEURISTIC 0.6] | Feet get wet reaching it at high tide [N21] | **Wed → Thu** (5am ×15, 5pm ×28) [N7] | |
| **Bilgola** (50 m, 8 lanes) | -33.6474, 151.3278 | Bilgola | Southern platform. [HEURISTIC 0.8] | – | **Tue → Wed** (5am ×14, 5pm ×29) [N7] | |
| **Avalon** (25 m) | -33.6376, 151.3322 | Avalon | "Best avoided when the swell is large and high tide" [N21]. The reef off the pool breaks in SE swell [N1]. [HEURISTIC 0.9] | Avoid high tide in a big swell [N21] | **Thu → Fri** (5am ×11, 5pm ×32) [N7] | |
| **Whale Beach** (25 m) | -33.6135, 151.3322 | Whale Beach | Southern platform. [HEURISTIC 0.8] | High-tide access means wading [N21] | **Thu → Fri** (5am ×11, 5pm ×33) [N7] | Closes in storms [N21] |
| **Palm Beach** (50 m) | -33.5998, 151.3278 | Palm Beach | South end, in the lee of Little Head [N1]. [HEURISTIC 0.7] | – | **Sun → Mon** (5am ×19, 5pm ×23) [N7] | |
| **Fairlight** (harbour, + paddling pool) | -33.8002, 151.2755 | Fairlight (harbour) | Only harbour surge [N1]. [HEURISTIC 0.2] | – | **Every Thursday, daytime** [N7, N8] | |

General pool facts [N7, N8]:
- Weekly cleaning by two night crews (north and south); fortnightly May–August per council news [N8]. The 2026 roster nevertheless lists a closure in almost every week, 41–44 a year [N7].
- Refilling depends on tide and swell, and the pool stays shut "until full". In Nov 2026 council warns of slow refills: "limited swell… high tides at the lower end of their cycle" [N7].

---

## 5. Water quality (Beachwatch)

### 5.1 Rain thresholds and grades
Rain thresholds come from the 2022–23 State of the Beaches Sydney report (the same report as S10 in the east) [N2]. Mapping, as in the east: "light rain" or "little or no rain" → 1 mm; "regularly" or "frequently" → "often". The grades come from that report [N2], the 2024-25 report [N4] and the 2026 report [N5].

| Site | Occasionally fails after | Often fails after | Dry-weather pass rate | Grade 22-23 / 24-25 / 2026 | Bot `rain_occ` / `rain_often` |
|---|---|---|---|---|---|
| South Steyne (Manly) | "no rain" | 10 mm | 95% | G / G / – | 1 / 10 |
| North Steyne | 5 mm | 20 mm | 98% | G / G / – | (merged into Manly) |
| Queenscliff | light rain | 10 mm | 97% | G / G / – | 1 / 10 |
| **Shelly Beach (Manly)** | "little or no rain" | 10 mm | 95% | G / **Poor** / G | 1 / 10 |
| Freshwater | light rain | 20 mm | 93% | G / G / – | 1 / 20 |
| North Curl Curl | 10 mm | 20 mm | 93% | G / G / – | 10 / 20 |
| South Curl Curl | 5 mm | 20 mm | 93% | G / VG / VG | 5 / 20 |
| Dee Why | 10 mm | 20 mm | 98% | G / G / VG | 10 / 20 |
| Long Reef | 5 mm | 20 mm | 98% | G / G / – | 5 / 20 |
| **Collaroy** | light rain | **5 mm** | 97% | G / G / – | 1 / 5 |
| North Narrabeen | light rain | 20 mm | 95% | G / G / – | 1 / 20 |
| Warriewood | 5 mm | 20 mm | 95% | G / G / – | 5 / 20 |
| Mona Vale | light rain | 20 mm | 100% | G / G / VG | 1 / 20 |
| Bungan | light rain | 20 mm | 98% | G / VG / VG | 1 / 20 |
| Newport | light rain | 20 mm | 100% | G / VG / VG | 1 / 20 |
| Bilgola | 10 mm | 20 mm | 96% | G / VG / VG | 10 / 20 |
| Avalon | 20 mm | (none stated) | 100% | VG / VG / VG | 20 / 30 [HEURISTIC "often"] |
| Whale Beach | 10 mm | (none stated) | 98% | VG / VG / VG | 10 / 20 [HEURISTIC "often"] |
| Palm Beach | 10 mm | 20 mm | 98% | VG / VG / VG | 10 / 20 |
| Manly Cove (harbour) | little or no rain | 20 mm | 91% | G / G / – | 1 / 20 |
| Little Manly Cove (harbour) | 5 mm | 20 mm | 92% | G / G / – | 5 / 20 |
| Fairlight (harbour) | 5 mm | 20 mm | 94% | G / G / – | 5 / 20 |
| Forty Baskets Pool (harbour) | 5 mm | 20 mm | 96% | G / G / – | 5 / 20 |
| Paradise Beach Baths (Pittwater) | light rain | 10 mm | 98% | G / G / – | 1 / 10 |
| Clareville (Pittwater) | light rain | 10 mm | 100% | G / G / – | – |
| Taylors Point Baths (Pittwater) | 10 mm | 20 mm | 98% | G / G / – | – |
| The Basin (Pittwater) | 10 mm | 20 mm | 94% | VG / VG / – | – |
| Narrabeen Lagoon (Birdwood Park) | "no rain" | "after rain" | 82% | Poor / Poor / Poor | not a swim spot |

"–" in the 2026 column means the 2026 summary does not name that site [N5].

- Northern Sydney ocean beaches were 100% Good or Very Good in 2022-23 [N2]. Nine of Sydney's ten cleanest sites in 2024-25 were on the Northern Beaches [N6].
- **Shelly Beach** was Poor in 2024-25, with a mean of 79.4 cfu/100 mL, "nearly double" the limit. Overwhelmed stormwater and sewer overflows are blamed [N6]. It was back to Good in 2026 [N5].
- **Harbour/Pittwater** sites are estuarine. Beachwatch advises staying out "for up to 3 days in estuarine and lagoon areas" [N2], so set `poor_grade=True` to get the 3-day rule [DERIVED].
- **Lagoon entrances**: "Swimming is not recommended at ocean beaches located near lagoon entrances if the lagoon is open" [N2]. Beachwatch names the lagoon discharge as a pollution source at North Narrabeen, Long Reef, North Curl Curl and Queenscliff/North Steyne [N2]. The Narrabeen entrance has been dredged every 4–5 years in the past, moving to smaller clearances every 2–3 years under the 2022 strategy [N2].

### 5.2 Live data
The Beachwatch GeoJSON (`https://api.beachwatch.nsw.gov.au/public/sites/geojson`, 246 sites, no key) lists every site above under the exact names in this file (checked 2026-11-04) [N3]. On that day after rain, Manly (South/North Steyne, Queenscliff, Shelly) and North Narrabeen were "Likely", the middle beaches "Possible", and Newport to Palm Beach "Unlikely". That is a typical north–south gradient [N3].

---

## 6. Surf breaks

| Spot | Pin (just off the break) | Breaks off (water) | Works from (swell) | Starts / holds | Offshore wind | Tide | Notes |
|---|---|---|---|---|---|---|---|
| **Manly** (North Steyne – Queenscliff beachies) | -33.7925, 151.2905 [DERIVED, ~250 m E of North Steyne sand] | Manly | NE best (N Steyne, Queenscliff) [N12]; SE best (surf-forecast "Manly") [N12] (conflict). S swell is lower at the south end [N1] | Beachie, ~0.6 m+. Queenscliff bombie only above 3 m [N1] | W–WSW (Manly end), NW (Queenscliff) [N12] | – | Best "into the northern rip, and about 150 m south of the surfboat shed" [N1] |
| **Freshwater** | -33.7830, 151.2925 [DERIVED, ~210 m SE] | Freshwater | E–ENE best [N12]. "Southern end best during east and southeast swell… northern side handles the northeast swell better" [N1] | Beachie | NW, "some shelter here from northeast winds" [N12] | All tides [N12] | Rated "sheltered beach break" [N12] |
| **Curl Curl** (North Curlie) | -33.7695, 151.3000 [DERIVED, ~270 m SE] | North Curl Curl | SE best [N12]; "receives all southerly swell" [N1] | "Can usually produce a wave when there is little else around" [N1] | WNW; "some shelter from northeast winds"; "blown out in southerlies" [N1, N12] | All tides [N12] | Curl Curl Point (SE swell) at the south end [N12] |
| **Dee Why Point** | -33.7548, 151.3008 [DERIVED, ~135 m off the point] | Dee Why | S–SSE best [N12] | **Starts at 1.5 m, holds to 4 m** [N1] | S to WSW (S wind is offshore at the point) [N12] | All tides [N12] | "Steep take off over rocks"; crowded [N1, N12] |
| **Long Reef** (beach, No Man's Land) | -33.7488, 151.3060 [DERIVED, ~330 m E of mid-beach] | Long Reef | E–SE; "picks up any east to southeast swell" [N1]; SE best [N12] | Beachies whenever there is swell. The bombies (First 1.5 m, Second 3 m, Outer/German Bank tow-in) need S swell >1 m and an offshore wind [N1] | W–WNW [N12] | Bombie: mid, rising [N12] | Also a windsurf and kite spot [N1] |
| **North Narrabeen** | -33.7045, 151.3075 [DERIVED, ~90 m off the lagoon-mouth bank] | North Narrabeen | NE best (long lefts "best in moderate to high northeast swell") [N1, N13]; works NE–S [N13] | 0.3–4.6 m range; "holds size when the swell is up" [N13] | NW; NW–NE "can make the lefts come alive" [N13] | Rising best [N13] | World-class. Lagoon-mouth sandbank. Water quality follows the lagoon outflow |
| **Warriewood** | -33.6898, 151.3112 [DERIVED, ~210 m ENE] | Warriewood | ESE best [N12]; "most popular during moderate southeast swell" [N1] | "Very reliable" [N12] | SSW; shelter from S winds [N12, N1] | – | Good choice in a southerly |
| **Newport** (The Peak) | -33.6500, 151.3265 [DERIVED, the north-end inshore reef] | Newport | E–NE in "low to moderate swell" [N1]. Newport Reef (SE, big) and Crosswaves (E–NE) are separate [N1, N12] | Small–moderate | W (beach) [DERIVED]; SW (Newport Reef) [N12] | – | Tom Carroll's home break [N1] |
| **Avalon** | -33.6366, 151.3350 [DERIVED, ~255 m SE] | Avalon | NE best [N13]; North Avalon left in NE–E "holding up to several metres"; south reef right in SE [N1] | 0.3–4.6 m [N13] | W (NW ok) [N13] | Rising best [N13] | "Very consistent". Bluebottles in summer NE [N13] |
| **Palm Beach** | -33.5905, 151.3285 [DERIVED, ~260 m off mid-beach] | Palm Beach | SE best [N12]. NE swell gives a left in the lee of Barrenjoey; better to the south in big winter swell and S winds [N1] | "Pretty consistent" [N12] | W [N12] | All tides [N12] | Rips make it dangerous [N12] |

Not modelled (big-wave or experienced-only): **Fairy Bower / Winkipop** (point; "only really begins working when waves exceed 1.5 m and has been surfed to 7 m"; SE swell, SW wind [N1, N12]). **Queenscliff bombie** (>3 m [N1]). **Long Reef bombies** (tow-in). **Whale Beach Wedge** (NE swell; inconsistent [N12]).

---

## 7. Rules specific to this coast (if/then)

Notation as in `beach-knowledge.md` §4: `Hs`, `dir`, `wind_kmh`, `wind_dir`, `rain24/48/72`, `tide`. The generic eastern rules (R-W1–R-W5, R-S1, R-S7, R-R1–R-R3, R-R5, R-T*, R-P3) apply unchanged. Where an eastern rule is keyed on a beach name (R-S3/R-S5 at Clovelly and Gordons, R-W6/R-W7 at Bondi, the R-B1 bluebottle table), the northern equivalent is below.

### 7.1 Wind and shelter
- R-NW1 Southerly (wind_dir 160–220°, ≥ 20 km/h): Collaroy +10, Warriewood +5, Shelly +10, Manly +5, Palm Beach (south end) +5 [N1 shelter statements; N12 Manly/Warriewood]. Curl Curl (both), Long Reef, Queenscliff and Freshwater −10 ("blown out in southerlies" [N1]). Mostly captured by `facing` already; this adds the headland shelter the bearing misses. [HEURISTIC sizes]
- R-NW2 NE wind (20–70°, ≥ 15 km/h; the summer sea breeze, `beach-knowledge.md` §3.4): Long Reef +10 (offshore at the north end [N1]). Freshwater, Bilgola and Bungan +5 (their north corners shelter from it, but the pins are mid-beach, so only partly) [N1]. Manly, Collaroy, Warriewood and Palm Beach are onshore and handled by `facing`. Shelly 0 (cross-shore; it ruffles the bay mouth but the beach is in the lee [DERIVED]).
- R-NW3 Southerly buster (R-W5 in the east): Shelly takes the reduced −20 (like Clovelly and Bronte); every other open beach −40. Harbour sites facing S (Manly Cove, Little Manly, Fairlight) −30 (onshore chop across North Harbour [DERIVED]).

### 7.2 Swell and swim limits
- R-NS1 Shelly swim: NO when Hs > 2.0 m from NE/E, or Hs > 1.5 m from NE/E with period ≥ 12 s ("strong surge in long-period east swell" [N17]; "shore break heavy during big seas" [N1]). S/SE swell does not trigger it. [HEURISTIC]
- R-NS2 Shelly snorkel: Hs < 1.0 m (any direction) or a S/SE swell < 2.0 m → +25 ("small S or SE swell often suits" [N17]). E/NE Hs 1.0–1.5 → 0. E/NE > 1.5 or period ≥ 12 s from E → snorkel NO. Rain48 ≥ 10 mm → −20, and ≥ 20 mm → NO ("occasionally" fails after little or no rain [N2]). Within 2 h of high tide → +5 ("high tide often improves visibility" [N17]). [HEURISTIC thresholds]
- R-NS3 North Narrabeen: swim_limit 1.0 (one step stricter) because of the lagoon-entrance currents on a falling tide and the low-tide plunging wave [N1]. If tide is falling and within 3 h after high → −10. [HEURISTIC]
- R-NS4 Newport: the lowest-energy open beach south of the club [N1]. Its k is set low for SE/S (Newport Reef). There is no extra rule.

### 7.3 Water quality and lagoons
- R-NL1 Lagoon outflow: IF rain72 ≥ 30 mm (enough to fill and open a lagoon [HEURISTIC]; council opens them at 1.4–2.2 m AHD [N11]) → Queenscliff, North Curl Curl, Long Reef, North Narrabeen and the North Narrabeen pool −20 for 72 h after the rain stops, even when R-R2 has cleared them. Beachwatch's advice: avoid beaches near an open lagoon entrance [N2]. The Beachwatch forecast, when available, takes priority (R-R1).
- R-NL2 Harbour/Pittwater sites use `poor_grade=True` (3-day rule [N2]). The Beachwatch forecast still overrides on the day.
- R-NL3 Shelly is Good in 2026 but was Poor in 2024-25 [N4, N5]. Keep `poor_grade=False`, but revisit each spring when the new report comes out.

### 7.4 Pools
- R-NP1 Cleaning (overnight): for pools with a dated roster, closure runs from ~3 h before the listed closing time on day D until 5am or 5pm on D+1 [N7]. With only a weekday to go on (`cleaning_day`), set it to **D+1**: that morning is shut in ~60–75% of weeks [N7]. Better: also penalise the evening of D, or scrape the roster table (dated rows of "Closes / Re-opens" on each pool's council page) [N7].
- R-NP2 Daytime cleaning: Fairy Bower every Wednesday, Fairlight every Thursday → treat like Ross Jones in the east (−15 warning that day) [N7, N8].
- R-NP3 North Curl Curl: low–mid tide only (|time to low| ≤ 3 h → +10; within 2 h of high → −15 for access). IF Hs ≥ 2.0 → NO (gate locked in big surf [N20]). Never cleaned → −5 always. [HEURISTIC numbers]
- R-NP4 Avalon, Whale, Newport: big swell plus high tide → apply R-P3 (−20, NO at surge ≥ 2.5) [N21].

### 7.5 Bluebottles (replaces the R-B1 name table for this region)
Wind drives them; NE and southerly winds both bring them in [S25]. Locally, Manly is "more vulnerable than… Freshwater, due to the width of the beach and the fact it faces directly towards the Pacific" [N19]; Avalon gets them in summer NE winds [N13]. Nov–Mar, next day after NE or S/SE onshore ≥ 20 km/h:
- After NE: Manly −15, Collaroy −10, Warriewood −10, Palm Beach −10, Queenscliff −10, Whale −8, Avalon −8, Newport −8. Freshwater, Curl Curl, Dee Why, Mona Vale, Bungan and Bilgola −5. Long Reef −3. Shelly −3.
- After S/SE: SE-facing beaches −10 (Freshwater, Curl Curl, Dee Why, Long Reef, Bilgola, Avalon). ENE-facing −5 (Manly, Collaroy, Warriewood, Palm). Shelly −2.
- Harbour sites and pools: 0. Double the penalty if the wind is ≥ 30 km/h (as in the east).

[HEURISTIC: ranked by how directly each beach faces the wind, using [S25]'s orientation mechanism and [N19]]

### 7.6 Patrols and time slots
- R-NPT1 Council lifeguards work 9am–5pm daily ("longer in the summer peak") from the last weekend of September to the last weekend of April [N9]. **Manly** is patrolled all year [N9, N10]. **Freshwater** from the last weekend of August to late May [N9]. **Dee Why** all year per the council beaches page [N9], or Sept–May per the June 2025 release [N10] (conflict). Volunteer SLSC patrols run on weekends and holidays in season [N10].
- R-NPT2 So hazard ≥ 6 beaches lose 15 points before 9am, and after 5pm (6pm Dec–Jan) — not 7am / 7pm as in the east [N9]. Weekday morning sessions are always unpatrolled. **Removed 2026-11-06**: the bot no longer takes points off for unpatrolled hours.
- R-NPT3 Bungan and Warriewood: treat as unpatrolled on weekdays outside school holidays unless the 2025-26 roster says otherwise. In 2022-23 Bungan was patrolled only late Dec–Jan and Warriewood only in holidays [N2]. Council took over "9 beaches from Warriewood to North Palm Beach" from Sept 2025 [N10], which may have extended this.

### 7.7 Surf
- R-NSU1 North Narrabeen works IF dir is NE–SE (30–150°) AND 0.6 ≤ Hs ≤ 3.0 AND wind is NW–W or < 10 km/h. NE gets the bonus (long lefts) [N1, N13]. Rising tide +5 [N13].
- R-NSU2 Dee Why Point works only IF Hs ≥ 1.5 AND dir is SE–S; it holds to 4 m. Wind S–WSW is offshore here [N1, N12]. Below 1.5 m, score it as flat. **The `SurfSpot` dataclass has no minimum size**, so this needs a `min_hs` field or a name check.
- R-NSU3 In a southerly (wind 160–220°, ≥ 15 km/h): Warriewood and Dee Why Point are the only sheltered breaks [N1, N12]. Curl Curl and Long Reef are blown out [N1].
- R-NSU4 Curl Curl is the "when there's nothing else" spot. Its k stays high in S/SE so it lights up on small south swells [N1].
- R-NSU5 Avalon and Palm Beach: rising tide +5 (Avalon [N13]). Palm Beach in big winter S swell: the south end is better [N1]. The one pin can't express this.

### 7.8 Tie-break
- R-NTB1 After all rules, IF Shelly Beach's score ≥ (best − `FAVOURITE_TOLERANCE`) AND Shelly is not "NO" → pick Shelly (`favourite="Shelly Beach"`).

---

## 8. Gaps and conflicts

1. **All `k` values, swim limits and pool exposures are heuristics.** Each is ranked from the Beachsafe wave-height and shelter statements [N1] and calibrated to nothing. Check them against Northern Beaches lifeguard reports or the Beachsafe app's daily wave heights.
2. **Dee Why patrol season**: "We patrol Manly and Dee Why all year round" (council beaches page [N9]) vs "Dee Why and Freshwater… 40 weeks, from the start of September to the end of May" (June 2025 release [N10]).
3. **Pittwater patrols after the 2025 change**: council took over the ALS-contracted beaches from Warriewood to North Palm Beach [N10]. Season dates for Bungan and Warriewood are not confirmed; the 2022-23 report's dates predate the change.
4. **Shelly patrols**: Beachsafe sets a patrol flag on Shelly [N1]. The council page says lifeguards don't patrol it "at this time of year" (November) [N9], which suggests peak summer only. Unconfirmed.
5. **Swell-direction disagreements**: Manly NE (surf-forecast North Steyne) vs SE (surf-forecast "Manly"). Collaroy NE (surf-forecast) vs SE for the point (Beachsafe). Bilgola NE (surf-forecast) vs SE-facing (Beachsafe). Avalon NE (surfnerd) vs SE (surf-forecast pages not found) [N1, N12, N13].
6. **Long Reef facing**: the north end (where the pin and SLSC are) faces SSE, and NE winds blow offshore there [N1]. The central No Man's Land faces E–ESE, with WNW offshore [N12]. The swim entry uses the north end; the surf entry uses mid-beach.
7. **Pool exposure facts are thin.** No official wave-over-wall statements exist for Queenscliff, Freshwater, South Curl Curl, Dee Why, Collaroy, North Narrabeen, Bilgola or Palm Beach. One search result attributed "waves crash all the way over the edge at high tide" to Fairy Bower, but the source was describing **Mahon Pool**, so it is not used here.
8. **Rain thresholds are 2022-23 numbers** [N2]. The 2024-25 and 2026 reports were read only as grade summaries [N4, N5]. Avalon and Whale have no "often" threshold in the report; the values given are [HEURISTIC].
9. **Pool rosters are dated for 2026 only** [N7]. The weekday pattern (D → D+1) should hold for 2027, but check.
10. **Surf pins are [DERIVED]** (offsets seaward of the sand, checked to fall on the water side of the OSM coastline [N14]); verify them on the map. Beach and pool pins are OSM polygon centres.
11. **Not found**: an official Cabbage Tree Bay snorkel visibility figure; bluebottle statistics for any northern beach; Northern Beaches lagoon open/closed status (council directs readers to Manly Hydraulics Laboratory water levels [N11]).

---

## 9. Proposed code values

Matches the current `beaches.py` (with `Region`, `Beach.harbour`, `SurfSpot.beach` and `Pool.women_only`). Argument order: `Beach(name, facing, k, rain_occ, rain_often, hazard, beachwatch, swim_limit=…, poor_grade=…, snorkel=…, harbour=…)`; `SurfSpot(name, facing, k, max_hs=…, bonus_dirs=…)`; `Pool(name, beach, exposure, best_tide=…, cleaning_day=…, …, facing_override=…)`. The rules in §7 that mention specific beaches (R-NS1–3, R-NL1, R-NP1/R-NP3, R-NSU2, the bluebottle table) need code; they can't be expressed through these fields alone.

```python
# ---------------------------------------------------------------- Northern beaches (northern-beaches-knowledge.md)
NORTHERN_BEACHES = [
    # §2. Ocean beaches, south to north
    Beach("Manly", 75, {"NE": 0.7, "E": 0.8, "SE": 0.6, "S": 0.4}, 1, 10, 6, "South Steyne Beach"),
    Beach("Shelly Beach", 290, {"NE": 0.3, "E": 0.3, "SE": 0.15, "S": 0.1}, 1, 10, 2, "Shelly Beach (Manly)",
          swim_limit=0.6, snorkel=True),  # faces W into Cabbage Tree Bay; R-NS1, R-NS2
    Beach("Queenscliff", 105, {"NE": 0.7, "E": 0.9, "SE": 0.8, "S": 0.7}, 1, 10, 6, "Queenscliff Beach"),  # R-NL1
    Beach("Freshwater", 130, {"NE": 0.6, "E": 0.9, "SE": 0.9, "S": 0.8}, 1, 20, 7, "Freshwater Beach"),
    Beach("South Curl Curl", 115, {"NE": 0.7, "E": 1.0, "SE": 1.0, "S": 0.9}, 5, 20, 7, "South Curl Curl Beach"),
    Beach("North Curl Curl", 130, {"NE": 0.5, "E": 0.9, "SE": 1.0, "S": 0.9}, 10, 20, 6, "North Curl Curl Beach"),  # R-NL1
    Beach("Dee Why", 125, {"NE": 0.6, "E": 0.9, "SE": 0.8, "S": 0.7}, 10, 20, 6, "Dee Why Beach"),
    Beach("Long Reef", 155, {"NE": 0.3, "E": 0.7, "SE": 1.0, "S": 0.9}, 5, 20, 6, "Long Reef Beach"),  # NE wind offshore; R-NL1
    Beach("Collaroy", 75, {"NE": 0.8, "E": 0.7, "SE": 0.4, "S": 0.25}, 1, 5, 5, "Collaroy Beach"),  # sheltered from southerlies
    Beach("North Narrabeen", 110, {"NE": 0.9, "E": 1.0, "SE": 0.9, "S": 0.7}, 1, 20, 7, "North Narrabeen Beach",
          swim_limit=1.0),  # R-NS3, R-NL1
    Beach("Warriewood", 80, {"NE": 0.9, "E": 0.9, "SE": 0.6, "S": 0.4}, 5, 20, 6, "Warriewood Beach"),
    Beach("Mona Vale", 115, {"NE": 0.8, "E": 1.0, "SE": 0.9, "S": 0.7}, 1, 20, 7, "Mona Vale Beach"),
    Beach("Bungan", 115, {"NE": 0.7, "E": 1.0, "SE": 0.9, "S": 0.8}, 1, 20, 7, "Bungan Beach"),  # R-NPT3
    Beach("Newport", 95, {"NE": 0.7, "E": 0.6, "SE": 0.45, "S": 0.3}, 1, 20, 6, "Newport Beach"),  # Newport Reef lee
    Beach("Bilgola", 125, {"NE": 0.6, "E": 0.9, "SE": 0.7, "S": 0.7}, 10, 20, 6, "Bilgola Beach"),
    Beach("Avalon", 125, {"NE": 0.7, "E": 1.0, "SE": 1.0, "S": 0.9}, 20, 30, 7, "Avalon Beach"),  # "often" [HEURISTIC]
    Beach("Whale Beach", 95, {"NE": 0.9, "E": 1.0, "SE": 0.9, "S": 0.7}, 10, 20, 7, "Whale Beach"),  # "often" [HEURISTIC]
    Beach("Palm Beach", 75, {"NE": 0.8, "E": 0.8, "SE": 0.5, "S": 0.35}, 10, 20, 6, "Palm Beach"),  # south end
    # §3. Harbour and Pittwater: estuarine, so the 3-day rain rule (R-NL2)
    Beach("Manly Cove", 195, {"NE": 0.0, "E": 0.1, "SE": 0.1, "S": 0.05}, 1, 20, 1, "Manly Cove",
          poor_grade=True, harbour=True),
    Beach("Little Manly Cove", 190, {"NE": 0.0, "E": 0.1, "SE": 0.1, "S": 0.05}, 5, 20, 1, "Little Manly Cove",
          poor_grade=True, harbour=True),
    Beach("Fairlight", 190, {"NE": 0.05, "E": 0.15, "SE": 0.15, "S": 0.1}, 5, 20, 1, "Fairlight Beach",
          poor_grade=True, harbour=True),  # "receives low swell through the heads"
    Beach("Forty Baskets", 60, {"NE": 0.0, "E": 0.1, "SE": 0.1, "S": 0.05}, 5, 20, 1, "Forty Baskets Pool",
          poor_grade=True, harbour=True),
    Beach("Paradise Beach Baths", 275, {"NE": 0.0, "E": 0.0, "SE": 0.0, "S": 0.0}, 1, 10, 1, "Paradise Beach Baths",
          poor_grade=True, harbour=True),
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
    calendar_env="NORTHERN_CALENDAR_ID",
    tiles="northern-beaches",
    bounds=((-33.83, 151.22), (-33.56, 151.36)),  # = the northern-beaches.pmtiles bbox
    rain_gauges=("94759", "94768"),  # Terrey Hills, Observatory Hill
)
REGIONS = [EASTERN, NORTHERN]
```

Notes on the code values:
- Names are unique across beaches, pools and surf in this region; surf pins use the `"<name> surf"` key as the Region expects. "Manly", "Freshwater", "North Narrabeen", "Long Reef", "Warriewood", "Newport", "Avalon" and "Palm Beach" are both a beach and a surf spot, like "Maroubra" in the east.
- Surf `facing` is chosen so that the sourced offshore wind is `facing + 180°` (the scorer uses it only for wind). That is why Dee Why Point is 40° and Warriewood 60°, not the beach bearings.
- `poor_grade=True` on harbour sites is for the estuarine 3-day rule, not a Poor grade.
- `hazard=1` on harbour sites: Beachsafe gives them 0 ("not rated") [N1].

---

## Sources

- **N1** Beachsafe (SLSA) beach pages, read through the undocumented JSON `https://beachsafe.org.au/api/v4/beach/<slug>` on 2026-11-04. Each gives the hazard rating, the description, and swimming and surfing notes. Slugs: `manly`, `north-steyne`, `queenscliff`, `shelly-15`, `fairy-bower`, `freshwater`, `north-curl-curl`, `curl-curl`, `dee-why`, `long-reef`, `collaroy`, `narrabeen`, `north-narrabeen`, `warriewood`, `turimetta`, `mona-vale`, `the-basin-2`, `bungan`, `newport`, `bilgola`, `avalon-2`, `whale-2`, `palm`, `north-palm`, `palm-beach-4`, `little-manly-cove`, `manly-cove-e`, `fairlight-beach`, `forty-baskets`, `clareville`, `taylors`. Web pages are at e.g. https://beachsafe.org.au/beach/nsw/manly/manly/shelly-15
- **N2** NSW Beachwatch, State of the Beaches 2022–23, Sydney region (Northern Sydney chapter pp. 10–47; harbour sites pp. 86–90): https://www.environment.nsw.gov.au/sites/default/files/state-of-the-beaches-2022-23-sydney-region-230279.pdf
- **N3** Beachwatch public API (undocumented; fetched 2026-11-04): https://api.beachwatch.nsw.gov.au/public/sites/geojson
- **N4** Pittwater Online News, State of the Beaches Report 2024-25 (site-by-site grades): https://www.pittwateronlinenews.com/State-of-the-Beaches-Report-2024-25.php
- **N5** Time Out Sydney, best and worst Sydney beaches for water quality in 2026 (25 Sep 2026; = S54): https://www.timeout.com/sydney/news/revealed-the-best-and-worst-sydney-beaches-for-water-quality-in-2026-092526
- **N6** Manly Observer, "Smelly Shelly takes the shine off…" (21 Oct 2025; Oct 2024–Oct 2025 data): https://manlyobserver.com.au/smelly-shelly-takes-the-shine-off-but-northern-beaches-dominate-with-clean-water-testing/
- **N7** Northern Beaches Council rockpool pages, with the dated 2026 cleaning rosters (fetched 2026-11-04): https://www.northernbeaches.nsw.gov.au/things-to-do/recreation-area/ + `fairy-bower-rockpool`, `queenscliff-rockpool`, `freshwater-rockpool`, `north-curl-curl-rockpool`, `south-curl-curl-rockpool`, `dee-why-rockpool`, `collaroy-rockpool`, `north-narrabeen-rockpool`, `mona-vale-rockpool`, `newport-rockpool`, `bilgola-rockpool`, `avalon-rockpool`, `whale-beach-rockpool`, `palm-beach-rockpool`, `fairlight-rockpool`
- **N8** Northern Beaches Council news on how the 15 rockpools are cleaned (weekly; fortnightly May–Aug; night crews; daytime at Fairy Bower and Fairlight; via search snippet): https://www.northernbeaches.nsw.gov.au/council/news/ever-wondered-how-our-iconic-rockpools-are-cleaned ; https://www.northernbeaches.nsw.gov.au/council/news/flushing-out-your-local-rock-pools
- **N9** Northern Beaches Council, Beaches listing (patrol seasons and hours; Shelly's patrol status; fetched 2026-11-04): https://www.northernbeaches.nsw.gov.au/things-to-do/beaches ; Manly Beach page: https://www.northernbeaches.nsw.gov.au/things-to-do/recreation-area/manly-beach
- **N10** Northern Beaches Council media release, "Single service for beach safety across the Northern Beaches" (5 Jun 2025): https://www.northernbeaches.nsw.gov.au/council/news/media-releases/single-service-beach-safety-across-northern-beaches
- **N11** Northern Beaches Council, Lagoons (entrance opening levels; no status published; monitoring): https://www.northernbeaches.nsw.gov.au/environment/coast-and-waterways/lagoons
- **N12** Surf-forecast break guides (fetched 2026-11-04): https://www.surf-forecast.com/breaks/ + `Manly`, `Manly-North-Steyne`, `Manly-South-Steyne`, `Queenscliff`, `Queensie-Bombie`, `Fairy-Bower`, `Freshwater`, `Curl-Curl`, `Curl-Curl-Point`, `Dee-Why-Point`, `Long-Reef`, `Long-Reef-Bombie`, `No-Mans-Land`, `Collaroy`, `Warriewood`, `Mona-Vale-Beach`, `Bungan-Beach`, `Newport-Reef`, `Bilgola-Beach`, `Palm-Beach`, `The-Wedge` (note: `/breaks/Newport` is Newport in Wales)
- **N13** Surfnerd: North Narrabeen https://www.surfnerd.com/surf-forecast/north-narrabeen ; Avalon https://www.surfnerd.com/surf-forecast/avalon
- **N14** OpenStreetMap via Overpass (https://overpass-api.de/api/interpreter, queried 2026-11-04): `natural=beach`, `leisure=swimming_pool|swimming_area` and `natural=coastline` in the bbox (-33.83, 151.22, -33.56, 151.36). Pins are polygon area centroids, or the nearest interior point when the centroid falls outside the polygon. Facings were checked against the coastline bearing within 250 m (water on the right of the way's direction). © OpenStreetMap contributors, ODbL.
- **N15** Own reproducible Open-Meteo tests, 2026-11-04. Marine: `https://marine-api.open-meteo.com/v1/marine?latitude=-33.70&longitude=151.37&hourly=wave_height,swell_wave_direction,sea_surface_temperature,sea_level_height_msl&models=best_match&cell_selection=sea&past_days=30&forecast_days=7`, the same at (-33.80, 151.33), (-33.62, 151.37) and (-33.92, 151.33). Weather cells: `https://api.open-meteo.com/v1/forecast?latitude=-33.752&longitude=151.297&hourly=temperature_2m&cell_selection=land|sea`
- **N16** BOM NSW observations bundle `ftp://ftp.bom.gov.au/anon/gen/fwo/IDN60910.tgz` (fetched 2026-11-04): station 94759 Terrey Hills (-33.6908, 151.2253) reports `rain_trace`. 95768 North Head and 95766 Sydney Harbour report "-".
- **N17** Abyss Scuba Diving, "Understanding diving conditions" (Shelly and Cabbage Tree Bay swell and tide notes): https://www.abyss.com.au/blog/diving/understanding-diving-conditions
- **N18** Snorkeling Report, Shelly Beach Manly (aquatic reserve, no fishing since 2002, max depth ~6 m, no lifeguard): https://www.snorkeling-report.com/spot/snorkeling-shelly-beach-manly/
- **N19** Manly Observer, "Red, white and blue bottles: Oz Day in Manly" (Manly more exposed than Freshwater; via search snippet): https://manlyobserver.com.au/red-white-and-blue-bottles-oz-day-in-manly/
- **N20** North Curl Curl rock pool, visitor and photography guides (big-surf wash-over, gate locked in big surf, low–mid tide access; via search snippets): https://www.locationscout.net/australia/30549-north-curl-curl-ocean-pool-big-wave-new-south-wales ; https://www.freephotoguides.com/?p=27661 ; https://oceanpoolsnsw.net.au/north-curl-curl-rock-pool-nsw-2099/
- **N21** Ocean Pools NSW reviews (Avalon, Newport, Whale Beach; via search snippets): https://oceanpoolsnsw.net.au/avalon-rock-pool-avalon-nsw-2107 ; https://oceanpoolsnsw.net.au/newport-rock-pool-newport-nsw-2106/ ; https://oceanpoolsnsw.net.au/?p=2610
- **S25** (shared with `beach-knowledge.md`) UNSW / The Conversation, bluebottle drift and wind: https://theconversation.com/want-to-avoid-a-bluebottle-sting-heres-how-to-predict-which-beach-theyll-land-on-179947
