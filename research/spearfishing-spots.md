# Spearfishing (breath-hold, shore entry): rules and spots for both regions

Compiled 2026-11-10. This file uses the same tags as `beach-knowledge.md`:
- **[SRC]**: the fact is stated in the cited source.
- **[DERIVED]**: worked out from a sourced fact or from map geometry (OSM, a published GPS mark).
- **[HEURISTIC]**: general local knowledge, or a starting value with no published source behind it. Treat these as a calibration starting point, not as fact.

Source IDs in this file start at `[SP1]` (listed in §6).

**Checked live on 2026-11-11 in a browser** (the automated fetches on 2026-11-10 got HTTP 403). Pages read:
- DPIRD spearfishing closures (Schedule 4): https://www.dpird.nsw.gov.au/fishing/closures/spearfishing-closures
- DPIRD location closures and each Sydney sub-page (Bungan Head, Narrabeen, Dee Why/Curl Curl/Manly, Shelly Beach Headland, Sydney Harbour, Bondi–Mackenzies Point, Clovelly/Gordons, Magic Point, Long Bay, Botany Bay, Port Hacking)
- DPIRD aquatic reserve pages: Barrenjoey Head, Narrabeen Head, Long Reef (and its "visiting the reserve" page), Cabbage Tree Bay, North (Sydney) Harbour, Bronte–Coogee, Cape Banks, Boat Harbour, Towra Point, Shiprock
- DPIRD grey nurse shark fishing and diving rules
- NSW Environment & Heritage, Bare Island Bridge closure (21 Aug 2026)

What the live pages confirm or change:
- **Schedule 4, Sydney entries, unchanged:** ocean beaches (except 20 m at each end), Clovelly Bay + Gordons Bay (same polygon), Narrabeen Lake, Port Hacking west of Glaisher Pt–Port Hacking Pt, Port Jackson (North Harbour, Manly Cove, Little Manly Cove, Spring Cove north of Grotto Pt–outer North Head; Chowder Bay). The pages still cite the **Fisheries Management (General) Regulation 2019**. The only recent change is Crescent Head (Oct 2025), outside our area.
- **North (Sydney) Harbour Aquatic Reserve bans spearfishing across the whole reserve,** North Head to Dobroyd Head (about 260 ha). That is wider than the Schedule 4 line. Line fishing for finfish only.
- **Towra Point is not in Schedule 4,** but its reserve only allows hook and line (and some nets) in the refuge zone and nothing in the sanctuary zone. So no spearing, in effect.
- **Shiprock Aquatic Reserve** (Port Hacking) is no-take. It is inside the Port Hacking closure anyway.
- **Cabbage Tree Bay** is no-take. Confirmed.
- **Long Reef:** finfish "by hand-held line or spear only". No invertebrates, no bait collecting. Confirmed.
- **Barrenjoey Head, Narrabeen Head, Cape Banks, Boat Harbour:** line fishing and spearfishing allowed. Abalone, rock lobster, sea lettuce and bait weed may be taken; no other invertebrates. Confirmed.
- **Bronte–Coogee:** DPIRD says "You can spearfish, but not in Clovelly Bay, Gordons Bay and surrounding waters". The Randwick Council claim of a reserve-wide ban is wrong.
- **Magic Point:** grey nurse critical habitat. Bait line fishing is banned and spearfishing is "Permitted" (rules as of 1 Jul 2014). The bot still treats it as "legal, but don't".
- **Intertidal protected areas** (Bungan Head, Mona Vale headland, Dee Why headland, Shelly Beach headland, Bondi–Mackenzies Point, Long Bay, Inscription Point, Cabbage Tree Point, all Sydney Harbour foreshores): these ban taking cunjevoi and invertebrates (except abalone and rock lobster) from the shore out to 10 m past low water. They do not ban spearing finfish.
- **Bare Island:** closed to all visitors from Monday 24 Aug 2026 until about late 2027. Confirmed. The notice says nothing about the water.

---

## 0. Key findings to read first

1. **Spearfishing is legal on most of the open-coast headlands in both regions.** It is banned in these places:
   - **every ocean beach** except the last 20 m at each end;
   - **Clovelly Bay + Gordons Bay**, out to Shark Point (a defined polygon);
   - **Cabbage Tree Bay** (Manly), which is no-take;
   - **North Harbour / Manly Cove / Little Manly / Spring Cove** (north of the Grotto Point–North Head line), and **Chowder Bay**;
   - **Narrabeen Lake**;
   - **Port Hacking** (west of Glaisher Pt–Port Hacking Pt);
   - **North (Sydney) Harbour Aquatic Reserve**, the whole reserve from North Head to Dobroyd Head (reserve rules, wider than Schedule 4);
   - **Towra Point Aquatic Reserve** (reserve rules allow only hook and line and some nets) and several inner Botany Bay areas;
   - **all inland waters**.

   [SP2 Sch 4; SP3]
2. **Long Reef, Narrabeen Head, Barrenjoey Head, Bronte–Coogee (outside Clovelly/Gordons), Cape Banks and Boat Harbour aquatic reserves all allow spearfishing for finfish.** In every one of them you cannot take or harm invertebrates. The bait-weed and rock-lobster exemptions apply to all of them except Long Reef. [SP3; SP6]
3. **Absolute bans by species:**
   - **Eastern blue groper**: no take by any method. Spearing it has been banned since 1969, and line take has been closed since 1 Mar 2024 (trial), renewed for 3 years from **1 Mar 2025**. [SP2 cl 49; SP4]
   - Protected fish: **blue drummer (bluefish, *Girella cyanea*)**, which is easy to confuse with black drummer; **eastern blue devil**; elegant wrasse; Ballina angelfish; **estuary cod (goldspotted rockcod)**; Queensland groper; all seahorses, seadragons and pipefish; ghostpipefish; seamoths; Herbst's nurse shark. [SP2 cl 14]
   - Threatened species: **black rockcod (black cod)** and **grey nurse shark**. [HEURISTIC: FM Act threatened-species schedules, not fetched]
4. **Gear:**
   - No taking fish while using **any air supply** (scuba or hookah). [SP2 cl 51]
   - No **lights** with a speargun. [SP2 cl 52(1)(c)]
   - No **explosive heads**. [SP2 cl 52(2)]
   - Licence fee: you must pay the NSW recreational fishing fee. [SP3]
   - Note that some shop blogs say torches are legal, for example Adreno [SP12]. **They are wrong.**
5. **Bare Island (La Perouse) is closed to all visitors from 24 Aug 2026 to about late 2027** for bridge repairs [SP7]. The best-known south-side shore spear spot is therefore off the menu for this season. The La Perouse mainland entries (Astrolabe Cove, Larpa Point) and Kurnell are unaffected.
6. **Magic Point (Malabar) is grey nurse shark critical habitat.** That covers a 200 m radius of 33°57.359′S 151°15.864′E, excluding 50 m from shore. DPI's table lists spearfishing there as *permitted*, but bait line fishing is banned. [SP8]

   Treat it as a **don't-spear zone** in the bot anyway: it is a protected-shark aggregation, it is a boat dive, and the optics are bad.
7. **Little Bay has an informal 2019 agreement.** It came out of a DPI-convened meeting after resident complaints: spearfishers stay **east of a marked line** and **do not enter or exit from the beach**. It is not a legal closure. [SP9]

   Randwick Council says spearfishing is **banned in its ocean pools** [SP10]. Its 2017 release also claims it is banned in the Bronte–Coogee reserve, which contradicts DPI (see §1.4).
8. **Visibility killers** (detail in §3):
   - **Diamond Bay**: a cliff-face sewage outfall, still discharging in 2026; the diversion is under construction [SP11].
   - **Turimetta Head**: the Warriewood WRRF outfall sits right on the head [SP13].
   - **Lagoon openings**: Manly (Queenscliff), Curl Curl, Dee Why (south Long Reef) and Narrabeen.
   - **The ebb plume out of Botany Bay.**
   - **The Hawkesbury/Pittwater ebb** at Barrenjoey.
   - **The harbour** for about 3 days after rain.
9. **Shark context.** These are recent fatal bites near spots in this file:
   - **Long Reef**, 6 Sep 2025: surfer, likely white shark [SP14];
   - **Shark Beach, Nielsen Park** (harbour), 18 Jan 2026: a 12-year-old outside the net; the same week saw bites at Manly and elsewhere, mostly bull sharks after heavy rain [SP15; eastern-additions.md H11];
   - **Little Bay**, Feb 2022: swimmer [HEURISTIC, widely reported].

   Speared fish on a float line are an attractant. The bot should push "murky + recent heavy rain + warm water" toward **no**, especially in the harbour and at Barrenjoey.

---

## 1. The law

### 1.1 Statute and where to read it

| Instrument | What it does for spearos | Link |
|---|---|---|
| Fisheries Management Act 1994 (NSW) | s 8 fishing closures (DPI notices), s 19 protected fish, threatened species schedules, the recreational fishing fee | https://legislation.nsw.gov.au/view/html/inforce/current/act-1994-038 |
| **Fisheries Management (General) Regulation 2019** [2019-407] | cl 14 protected fish; cl 49 groper; cl 51 scuba; cl 52 spear guns; **Schedule 4: waters where spearfishing is prohibited**; Schedule 1 bag limits; size limits in Part 2 | https://legislation.nsw.gov.au/view/html/inforce/current/sl-2019-0407 (403 to bots). Copy actually read: FAOLEX https://faolex.fao.org/docs/pdf/nsw225309.pdf (compiled 20 Jan 2023) [SP2] |
| Fisheries Management (Eastern Blue Groper Fishing Closure) Notification 2025 and Possession Limit Order 2025 | No take by recreational fishers; possession limit zero. From 1 Mar 2025 for 3 years | NSW Gazette 2025 No 81, https://gazette.nsw.gov.au/gazette/2025/2/2025-2_81-gazette.pdf [SP4] |
| Marine Estate Management (Aquatic Reserves) rules | Rules for the reserve zoning below | DPI aquatic reserves index: https://www.dpi.nsw.gov.au/fishing/marine-protected-areas/aquatic-reserves |

Official DPI pages to check by hand (all were 403 to bots):
- Spearfishing closures: https://www.dpird.nsw.gov.au/fishing/closures/spearfishing-closures
- Spearfishing in NSW: https://www.dpird.nsw.gov.au/fishing/recreational/resources/spearfishing
- Recreational Spearfishing Guide (Jan 2024): https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0018/602118/Recreational-Spearfishing-Guide-January-2024.pdf
- Sydney North guide (Apr 2024): https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0019/614512/Recreational-Fishing-Guide-Sydney-North-April-2024.pdf
- Sydney South guide (2025): https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0020/614522/Recreational-Fishing-Guide-Sydney-South-2025.pdf
- Botany Bay & Georges River closures: https://www.dpird.nsw.gov.au/fishing/closures/location-closures/botany-bay-and-georges-river
- Sydney Harbour closures: https://www.dpird.nsw.gov.au/fishing/closures/location-closures/sydney-harbour-port-jackson
- Grey nurse rules: https://www.dpi.nsw.gov.au/fishing/species-protection/what-current/critically/grey-nurse-shark/new-fishing-and-diving-rules
- Blue groper rules: https://www.dpi.nsw.gov.au/fishing/recreational/fishing-rules-and-regs/new-blue-groper-fishing-rule-changes

### 1.2 Gear and method rules (verbatim where quoted) [SP2]

- **cl 51 Scuba diving**: "A person must not, while using any apparatus capable of supplying air to facilitate breathing underwater, take fish by any method." The exemptions are a snorkel, scallops, sea urchin, and commercial abalone/urchin/turban. **So breath-hold only.**
- **cl 52(1)**: you must not "(a) use a spear gun in inland waters…, (b) use a spear gun … in any of the waters described in Schedule 4, or (c) use a spear gun aided by lights in any waters". 52(2) bans explosive-fitted spear guns. "Spear gun includes a spear or similar device."
- **cl 49 Groper**: groper (*Achoerodus viridis*: eastern blue, blue, brown or red groper) may be taken only by rod and line or handline. Since 1 Mar 2025 the Gazette closure bans **all** recreational take [SP4], so blue groper is fully off-limits.
- DPI's guide [SP3] lists what spearfishers may use: a snorkel when taking fish; scuba/hookah for scallops and urchins only; bare or gloved hand for lobsters. It lists what they may not use: a light with a spear; a spear to take blue, brown or red groper or any protected fish; powerheads or explosives.
- **Recreational fishing fee** applies to spearfishing (anyone 18+) [SP3].
- **Distance from swimmers.** Shop blogs quote "50 m" [SP12] or "20 m" [SP17]. **I could not find either distance in the regulation.** DPI's safety guidance says to avoid popular swimming areas, never load or unload out of the water, and not to carry loaded guns through crowds [SP9]. Treat a distance as best practice, not law.

### 1.3 Schedule 4: Sydney waters closed to spearfishing (verbatim) [SP2, SP3]

| Area | Exact description |
|---|---|
| **Ocean Beaches** | "The whole of the waters within territorial limits on the whole of the ocean beaches within the State of New South Wales, but exclusive of 20 metres at each extremity of each ocean beach." |
| **Clovelly Bay and Gordons Bay** | "The whole of the waters of Clovelly Bay and Gordons Bay including waters encompassed by a line commencing at the southeastern extremity of Shark Point, extending southeasterly for 100 metres to a point 33°54.950′S, 151°16.300′E, then generally southwesterly to a point 33°55.100′S, 151°15.800′E, then 100 metres northwesterly to the easternmost point of the southern headland of Gordons (or Thompsons) Bay, then by the mean high water mark to the point of commencement." Decimal corners: **(-33.91583, 151.27167)** and **(-33.91833, 151.26333)** [DERIVED] |
| **Narrabeen Lake** | "The whole of the waters of Narrabeen Lake and its tributaries." |
| **Port Jackson** | "The whole of the waters of North Harbour, Manly Cove, Little Manly Cove and Spring Cove and their tributaries, north of a line drawn between Grotto Point and outer North Head and those waters of Chowder Bay west of a line drawn from the easternmost extremity of Chowder Head, to the foreshore of the southeasternmost extremity of Georges Head on the eastern side of the Army Maritime School." So **Fairlight, Manly Cove, Little Manly, Spring Cove/Quarantine Beach, Dobroyd's inner side, Clifton Gardens and Chowder Bay are closed.** |
| **Port Hacking** | "The whole of the waters of Port Hacking and its tributaries west of a line drawn from the eastern extremity of Glaisher Point to the northern extremity of Port Hacking Point." (Out of scope but adjacent: this includes Shiprock.) |

**Not in Schedule 4**:
- the rest of Sydney Harbour: Camp Cove, Watsons Bay, Nielsen Park, Middle Harbour and Balmoral;
- Botany Bay as a whole;
- Pittwater and Broken Bay;
- the Dee Why, Curl Curl and Manly lagoons.

Inland waters are closed anyway, and the coastal lagoons are mostly "inland"/tidal-entrance waters that nobody spears. **[HEURISTIC]: treat all four northern-beaches lagoons as no-spear.**

### 1.4 Aquatic reserves (in or near both regions)

All the open-coast reserves extend **100 m seaward from mean low water**, except Cabbage Tree Bay and North Harbour [SP3].

| Reserve | Boundary (as published) | Spearfishing? | Other |
|---|---|---|---|
| **Cabbage Tree Bay AR** (Manly) | "Whole foreshore of the bay from Manly Surf Life Saving Club to the northern end of Shelly Beach Headland, and encompasses all of Cabbage Tree Bay" [SP3]. Ref point -33.8001, 151.2942 [SP6] | **NO**: no-take, all methods; no feeding or burley | Includes Fairy Bower and Shelly Beach |
| **North (Sydney) Harbour AR** | "A line between headlands at North Head and Grotto Point, and another line joining Little Manly Point, Manly Point and Forty Baskets Beach … up to the mean high water mark" [SP3] | **NO**: finfish "by hand held line only" [SP3], and Sch 4 also closes it | USFA has lobbied to reopen it since 1982 [SP16] |
| **Long Reef AR** | "From Collaroy rock baths south to Long Reef surf lifesaving club" [SP3] | **YES, finfish only**: "Fin fish can be taken by line or spear only but you must bring your own bait. With the exception of fin fish, you cannot collect or harm any other marine plants or animals" [SP3] | No lobster or bait-weed exemption here. USFA (Apr 2026) is lobbying for a "Spearfishing Reserve" title because others want a sanctuary [SP18]. Watch for changes |
| **Narrabeen Head AR** | "Whole foreshore from the south end of Turimetta Beach to the rock baths at Narrabeen Head" [SP3] | **YES** "(subject to normal restrictions)" | Rock lobster, sea lettuce and bait weed may be taken; all other invertebrates and cunjevoi are banned |
| **Barrenjoey Head AR** | "Rocky platform around Barrenjoey Head from the northern end of Station Beach to the northern end of Palm Beach" [SP3]; about 30 ha [SP19] | **YES** | Same as Narrabeen Head |
| **Bronte–Coogee AR** | "Whole foreshore from the southern end of Bronte Beach to the rock baths at Coogee Beach: 4000 metres of coastline … 100 metres seaward" [SP3] | **YES, except** the Clovelly/Gordons Sch 4 polygon | Same invertebrate rules. Includes Wedding Cake Island waters? [DERIVED: WCI is ~600 m offshore, so it is outside the 100 m reserve band anyway] |
| **Cape Banks AR** (La Perouse) | Not fetched. Browns Rock lies just outside [SP6] | **YES**: line and spear permitted [SP6, citing the 2024-25 DPI text]. Older sources say "no-take". **Verify** | No invertebrates |
| **Boat Harbour AR** (Kurnell, ocean side) | Not fetched | **YES** [SP6] | No invertebrates |
| **Towra Point AR** (Botany Bay south shore) | Map: https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0007/633580/Towra-Point_web.pdf | **NO**: sanctuary zones are "No fishing, spearfishing or collecting"; refuge zones are line fishing only [search extract of the DPI map] | |
| **Shiprock AR** (Port Hacking) | | **NO** (no-take; Port Hacking is Sch 4 anyway) | |

**Intertidal Protected Areas (IPAs).** Fishing (including spearing) is allowed in these, but you cannot collect invertebrates or cunjevoi between MHW and 10 m seaward of MLW [SP3]. They are:
- **Bondi (Mackenzies Point)**;
- **Long Bay (Malabar)**;
- **Dee Why Head**;
- **Mona Vale Headland**;
- **Bungan Head**;
- **Shelly Beach Headland**;
- **the entire Sydney Harbour shoreline**, including Middle Harbour, except North Harbour from Manly Point to Forty Baskets [SP3].

### 1.5 Botany Bay

- **Botany Bay is not in Schedule 4.** Spearing is legal around the heads: La Perouse, Bare Island (when open), Henry Head, Kurnell/Inscription Point and the Kurnell ocean side.
- Areas closed to spearing [SP16; DPI search extracts]:
  - **Towra Point AR**;
  - **the waters between the Sydney Airport runways**, closed to all methods including spearfishing;
  - **Cooks River**;
  - **Penrhyn Estuary**;
  - **the Caltex/Ampol Kurnell pier**;
  - **the Port Botany terminals**.
- **Inscription Point (Kurnell)** has a closure on cunjevoi and invertebrates (except abalone and rock lobster), **not** on finfish [search extract of DPI closed-waters list].
- **Kamay ferry wharves** (Kurnell and La Perouse; Transport for NSW): TfNSW asks snorkellers, divers and spearfishers to "keep clear of the wharves for their own safety". Anchoring near the Kurnell wharf is banned to protect seagrass. **This is advice, not a closure** [search extract of https://www.transport.nsw.gov.au/projects/current-projects/kamay-ferry-wharves].
- **Bare Island precinct closed 24 Aug 2026 → about late 2027**. Bridge, island and fort are "closed to all visitors". No water exclusion zone is mentioned [SP7].
- Botany Bay has been a Recreational Fishing Haven (no commercial fishing) since 2002.

### 1.6 Grey nurse shark critical habitat: Magic Point (Malabar)

- Critical habitat is "the waters extending 200 metres in all directions around a point centred on 151°15.864′E, 33°57.359′S, excluding the waters within 50 metres of the mainland shore". Decimal: **-33.95598, 151.26440** [SP2 cl 152 table; SP8].
- DPI's 2014 summary table: bait line fishing is **prohibited**, spearfishing is **permitted**. The commercial notice [SP5] extends the line-fishing and burley exclusion to 500 m (+500 m for burley) for commercial fishers only.
- Diver code: do not touch, chase or block grey nurse sharks, and do not use electronic shark deterrents near them [HEURISTIC: DPI GNS diver code, page not fetched].
- **[HEURISTIC] Bot rule: list Magic Point as "legal, but don't".** It is not a shore entry, and it is a protected-shark aggregation site.

### 1.7 Harbour food advice (Sydney Harbour dioxins) [SP3]

- **West of the Harbour Bridge: don't eat anything.**
- **East of the bridge:** general advice is ≤150 g of fish a month. Higher amounts are allowed for some species: **kingfish 12 serves a month, luderick 12, bream 1, silver trevally 5, tailor 1**. Only Camp Cove, Watsons Bay and Nielsen Park matter here.
- Botany Bay has separate PFAS advice for some areas (not fetched; fishare cites the NSW EPA Botany Bay PFAS page [SP6]).

### 1.8 Council and beach rules

- **Randwick ocean pools: spearfishing prohibited** (council release, Jan 2017) [SP10]. This applies to Mahon, Malabar (Long Bay), Coogee's pools, Clovelly and others. [HEURISTIC]: treat every ocean pool as no-spear, in every council.
- **Beaches:** Schedule 4 already bans spearing on beaches except the last 20 m at each end. Shark nets (Shark Meshing Program, 1 Sep–30 Apr) run off the patrolled beaches, and drumlines run at some, including Long Reef [SP14]. Neither creates a spearfishing rule, but nets mean you are on a beach, which is closed anyway.
- **Rock Fishing Safety Act 2016**: lifejackets are mandatory for *rock fishing* in declared LGAs, including Randwick and Northern Beaches. It is aimed at fishing from rocks, not in-water spearing. [HEURISTIC]: it doesn't apply to spearos in the water.
- **Little Bay** (Randwick): spear only east of the agreed line, and no beach entry or exit (2019 DPI-brokered, non-statutory) [SP9].

### 1.9 Bag and size limits for common targets [SP2 Sch 1 and Part 2, 2023 compilation; **verify in FishSmart**]

| Species | Min size | Daily bag |
|---|---|---|
| Yellowtail kingfish | 65 cm | 5 |
| Snapper (incl. squire) | 30 cm | 10 |
| Rock blackfish (black drummer, "pig") | 30 cm | 10 |
| Luderick (blackfish) | 27 cm | 10 (possession 20) |
| Yellowfin/black bream (combined with tarwhine) | 25 cm | 10 combined |
| Tarwhine | 20 cm | in bream group |
| Dusky flathead | 36 cm (only 1 over 70 cm) | 10 |
| Sand/tiger flathead | 33 cm | 10 combined |
| Silver trevally / *Caranx* trevallies | 30 cm (silver) | 10 combined |
| Australian bonito | none | 10 |
| Red morwong | 30 cm | 5 |
| Grey (rubberlip) morwong | 30 cm | 10 |
| Banded morwong | none | 5 |
| Tailor | 30 cm | 10 |
| Eastern Australian salmon | none | 5 |
| Mulloway | 45 cm | 5 (2 over 70 cm) |
| Samsonfish/amberjack | none | 5 combined |
| Leatherjackets | none | 20 combined |
| John Dory, silver drummer, sweep, others not listed | none | **20** (general limit, cl 10) |
| **Eastern blue groper** | — | **0** (closed) |
| Blue drummer (bluefish), eastern blue devil and other protected fish | — | **0** (protected) |

Rock lobster must be taken by hand only, never speared [SP3].

### 1.10 Pending and political changes

- The proposed **Sydney Marine Park** (Hawkesbury bioregion, 2018) had sanctuary zones at Long Reef, Bronte–Coogee, Cape Banks, Boat Harbour, North Harbour, Chowder Bay and others. Its no-take zones were dropped after objections [SP16; 2ser story "NSW government axes no fishing zones in proposed Sydney marine park"].
- As of **29 Apr 2026**, USFA reports pressure for a **Long Reef sanctuary** and a **Balmoral no-take zone**. No Sydney change had been made [SP18].
- **Re-check each season.**

---

## 2. Spots table

Region order follows the bot. "Legal" means legal to spear from shore under §1. "Confidence" covers the whole spot record, not just legality:
- **H** = sourced legality, sourced or published-GPS coords, and a sourced dive description;
- **M** = sourced legality, but the conditions are mostly heuristic;
- **L** = legality OK, but little published about the spot.

Coordinates are WGS84 decimal. "McF" means the GPS published by Michael McFadyen's dive-site pages [SP20], which are for scuba. They mark the reef, not the car park.

### 2.1 Eastern suburbs → Botany Bay heads

| # | Spot | Legal? | Coords | Faces / exposed to | Depth | Best wind · swell · tide | Main hazards | Conf. |
|---|---|---|---|---|---|---|---|---|
| E1 | Diamond Bay / Dover Heights cliffs | Legal, **not recommended** | -33.8620, 151.2819 (OSM Diamond Bay Reserve) [DERIVED] | E | 5–20 [HEURISTIC] | W; flat | 30 m cliffs with no safe entry; **active cliff sewage outfall** [SP11] | L |
| E2 | **North Bondi (Ben Buckler)** | Yes (enter at the boat ramp, not the beach) | -33.89422, 151.28492 (McF reef) | S–SE into Bondi Bay; open to E/SE/S | 3→15–18 (21 max) | N–NW–W · <1 m E/NE · any | Tinnies using the ramp at full speed; swimmers and surfers; Mackenzies Pt IPA (no inverts) | H |
| E3 | South Bondi (Flat Rock / Mackenzies Pt) | Yes | -33.8975, 151.2775 [DERIVED, OSM Mackenzies Pt -33.8985, 151.2765] | NE–E | 6–10 | W–NW · "slight SE swell, otherwise calm" [SP20] · any | Surge in the north gutters; cave collapse reported; IPA | M |
| E4 | Bronte–Tamarama points / Bronte south (Waverley Cemetery cliffs) | Yes (Bronte–Coogee AR, inverts banned) | -33.9065, 151.2700 (fishare's AR ref point) [SP6] | E | 5–15 [HEURISTIC] | W · <0.8 m · high | Platform surge; Bronte Beach itself closed except the 20 m ends | L |
| — | **Clovelly Bay, Gordons Bay, Shark Point to S. Gordons headland** | **NO** (Sch 4) | polygon in §1.3 | | | | | H |
| E5 | **Wedding Cake Island** (Coogee) | Yes | -33.92592, 151.26542 (OSM islet) | open ocean, all sides | 5–15 [HEURISTIC] | W–NW · <1 m · any | ~600 m swim from Coogee (Trenerry/Giles); boat traffic; break on the island | M |
| E6 | Coogee south: Trenerry Reserve → Lurline Bay | Yes (south of the Coogee rock baths, outside the AR) | -33.93751, 151.26176 (OSM Lurline Bay) | E–NE | 5–15 [HEURISTIC] | W–SW · <1 m S/SE · high | Platform entry; Lurline Bay is a surf break | L |
| E7 | **Mahon Pool / North Maroubra** | Yes (not inside the pool) | entry -33.9430, 151.2639 (OSM pool); reef -33.94203, 151.26948 (McF) | E | 7→24 (gutter 12–18) | W · **"millpond"** [SP20] · high | Hard exit (slit and rock); 300 m swim; Lurline Bay surfers | H |
| E8 | **South Maroubra (Arthur Byrne Reserve)** | Yes (enter at the platform inlet, not the beach) | -33.95351, 151.26058 (McF) | NE (tucked under Magic Pt) | 6–15 | S–SW–W · "diveable in all but the biggest southerly and south-easterly … seas" [SP20] · any | 250 m platform walk; rip by the pool; **GNS critical habitat starts 200 m SE** | H |
| E9 | Magic Point | Legal, **avoid** (GNS critical habitat) | -33.95598, 151.26440 [SP2] | E | 10–25 | boat only | Grey nurse aggregation | H |
| E10 | **Malabar – Long Bay (west side, golf-club pool)** | Yes (not in the pool; Long Bay IPA) | -33.96848, 151.25457 (OSM Malabar Ocean Pool) | E, inside the bay | 3–10 | W–SW–NW · "all but the biggest easterly and southerly seas" [SP20] · **high tide** for the exit | Boat ramp traffic (Malabar ramp, north shore); stormwater after rain | H |
| E11 | Boora / Tupia Point cliffs | Legal, boat/pro only | Tupia anchor -33.97731, 151.25920 (McF) | E | 10–20 | boat | No shore exit | L |
| E12 | **Little Bay (bay mouth and "4th Hole")** | Yes, **east of the agreed line, no beach entry or exit** [SP9] | bay -33.97852, 151.25163 (OSM beach); 4th Hole about -33.9792, 151.2545 [DERIVED from McF text: 100 m NE of the Coast Golf Club car park] | Bay faces E; outside faces E/NE | 3.5–13 | W–SW · only "slight seas"; "so long as the waves are not breaking at the entry and exit" [SP20] · mid–high (strong outflow at high tide [SP20]) | Swimmers and snorkellers; golfers; surge tunnels; **fatal shark bite 2022** | H |
| E13 | **Cape Banks** | Yes (AR permits spear [SP6], verify) | tip reef -34.00108, 151.25126 (McF) | S–SE–E | 10–20 | N–NE wind (USFA: "safe protection … from northerly winds and swell") · <1 m S · any | McF rates shore entry "not recommended"; exposed; current at the heads | M |
| E14 | Henry Head / Cruwee Cove | Yes | -33.99744, 151.24444 (OSM Cruwee Cove) | S (into the bay mouth) | 5–15 | N–NE · <1 m S · incoming | Shipping channel; McF rates shore entry "not recommended"; long walk | L |
| E15 | **La Perouse: Astrolabe Cove and Larpa Point** (Bare Island closed) | Yes | Astrolabe -33.99011, 151.23041; Larpa -33.98950, 151.22762 (McF) | S–SW into Botany Bay | 3–15 | N–NE–NW · **N–NE swell, or S under 1 m** · **incoming/high** (the bay ebb is murky) | Kamay ferry wharf (La Perouse); boat traffic; scuba groups | H |
| — | Bare Island (all sites) | Legal, but **land access closed 24 Aug 2026 → late 2027** [SP7] | east wall -33.99255, 151.23282; west reef -33.99168, 151.22953 (McF) | all | 5–21 | N–NE · southerly swell is the main limit [SP21] · high | — | H |
| E16 | **Kurnell: Monument → Inscription Pt / The Steps** | Yes (invert closure only) | Monuments -34.00077, 151.22260; Steps -34.00197, 151.22483 (McF) | N–NE (bay side) | 5–14 | S–SW–W wind; S/SE swell under ~1.5 m is fine; **incoming tide** [SP21] | Kamay ferry wharf (Kurnell); heavy scuba use; NPWS gate hours (no night); seadragons (protected) | H |
| E17 | **Kurnell: The Leap / Yena** | Yes | Leap -34.00458, 151.22938; Yena -34.00756, 151.23121 (McF) | E–SE (ocean side) | 10–25 | **W wind, flat sea** · "incoming tide near high" (Leap) [SP21]; Yena "really calm seas" [SP20] | Rock-shelf jump entry; one exit (at The Steps); drift; current | H |
| E18 | Cape Solander | Legal, **pros only** | -34.01661, 151.23178 (OSM) | SE–S | 10–24+ | W · "very calm seas" [SP21] | Cliffs; exposed; "experienced divers only" | M |
| E19 | Boat Harbour (Kurnell, AR) | Yes (AR permits spear) | -34.0365, 151.2016 (OSM hamlet) | S–SE | 2–10 [HEURISTIC] | N–NE · S <1 m · any | 4WD/permit access; surf break; USFA: "sheltered … important for novice and junior divers" [SP16] | M |

Harbour spots near the eastern region:

| # | Spot | Legal? | Coords | Faces | Depth | Best | Hazards | Conf. |
|---|---|---|---|---|---|---|---|---|
| H1 | **Camp Cove** | Yes (not Sch 4; harbour IPA) [SP16 says it is used by spearos] | -33.83892, 151.27865 (McF reef) | W/NW into the harbour | 3–19 | Southerly-buster refuge [SP20]; any swell under 2 m; **dry 3+ days** | Swimmers in summer; ferries and boats; harbour bull sharks; dioxin advice | M |
| H2 | Green Point / Laings Point (Watsons Bay) | Yes | -33.84009, 151.27676 (McF) | N/NW | 3–15 | same as H1 | same | M |
| H3 | Nielsen Park (Shark Beach) outer points | Yes (USFA: "safe and shallow") [SP16] | -33.8514, 151.2666 (OSM park) | N | 2–10 | same | Netted swim area; **fatal bull-shark bite Jan 2026**; crowds | L |
| — | Clifton Gardens / Chowder Bay, Manly Cove, Fairlight, Little Manly, Spring Cove, Shelly Beach, Fairy Bower | **NO** | | | | | | H |

### 2.2 Northern beaches

| # | Spot | Legal? | Coords | Faces / exposed to | Depth | Best wind · swell · tide | Main hazards | Conf. |
|---|---|---|---|---|---|---|---|---|
| N1 | North Head ocean side (Blue Fish Point → North Head) | Yes (outside Cabbage Tree Bay and the Port Jackson closure) | Blue Fish Pt -33.80732, 151.30686 (OSM) | E–SE | 10–30 | W · very flat · any | USFA: "very steep cliffs, swell, and dangerous currents pulling towards a very high boat traffic area" [SP16]; the only easy entry is through no-take Cabbage Tree Bay | M (legal) / pros only |
| N2 | **Queenscliff Head – Freshwater (Harbord) headland** | Yes (not in the pool) | Freshwater pool -33.78155, 151.29451; Queenscliff Head -33.78623, 151.29134 (OSM) | N side faces NE (Freshwater); S side faces SE | 3–8 [SP17] | W–SW · S swell (Freshwater side tucked) · high | Surge; **Manly Lagoon outflow** at Queenscliff after rain | M |
| N3 | Curl Curl north end → Dee Why Head | Yes (Dee Why Head IPA) | -33.76797, 151.30202 (OSM Dee Why Head) | E–SE | 3–12 [HEURISTIC] | W–NW · <1 m · high | **Curl Curl Lagoon** outflow; surfers; platform surge | L |
| N4 | **Long Reef (Fishermans Beach side and the point)** | Yes, **finfish only**, nothing else (AR) | Long Reef Pt -33.74198, 151.31711 (OSM); Fishermans Beach entry about -33.7390, 151.3090 [DERIVED] | Fishermans Beach faces N–NE; point open to E/SE/S | 2–15 | **S–SE wind** (Fishermans side in its lee) · S swell OK on the Fishermans side; NE swell needs the south side · mid–high | Wide shallow platform with surge; boat ramp traffic (Fishermans Beach); **Dee Why Lagoon** outflow on the south side; **fatal white-shark bite 6 Sep 2025** [SP14] | M |
| N5 | **Narrabeen Head** (AR, spear OK) | Yes | -33.70383, 151.30995 (OSM) | E–NE | 3–15 (USFA: "large area of <20m reef") [SP16] | W–SW · S swell under 1.2 m (head shelters the north side) · high | **Narrabeen Lagoon** entrance currents and murk after rain (the lake itself is Sch 4); surfers | M |
| — | Turimetta Head | Legal, **avoid** | outfall -33.69678, 151.31397 [SP13] | E | | | **Warriewood WRRF outfall at the head**; bypass events | H |
| N6 | Mona Vale Headland / Bungan Head | Yes (both IPAs) | Mona Vale Hd -33.67479, 151.31984; Bungan Hd -33.66404, 151.32389 (OSM) | E | 3–15 [HEURISTIC] | W · <1 m · high | Exposed platforms; long swims | L |
| N7 | Newport (south end) → Bilgola Head | Yes | Newport pool -33.65839, 151.32439; Bilgola Hd -33.64376, 151.33388 (OSM) | E–NE | 3–15 [HEURISTIC] | W–SW · S swell <1.2 m (north sides) · high | Surge; surfers | L |
| N8 | Avalon south headland / Bangalley Head | Yes | Bangalley Hd -33.62462, 151.34332 (OSM) | E | 5–20 [HEURISTIC] | W · flat | Cliffs at Bangalley; few exits | L |
| N9 | Whale Beach south → Little Head | Yes | Little Hd -33.60646, 151.33594 (OSM) | E–NE | 3–15 [HEURISTIC] | W–SW · S swell (north side) | Stormwater drains at Whale Beach; surge | L |
| N10 | **Barrenjoey Head** (AR, spear OK) | Yes | headland -33.58044, 151.32768 (OSM); Station Beach entry -33.58422, 151.32582 (OSM) | All sides: Pittwater (W), Broken Bay (N), ocean (E) | 3–15+ | **Southerly wind and swell** (USFA: "safe access and use in adverse southerly wind and swell") [SP16] · **flood tide / high** for clean ocean water | Strong tidal currents at the head; boat traffic (Palm Beach ferry, Barrenjoey ramp); **Hawkesbury ebb plume** after rain; bull sharks (estuary mouth) | M |

---

## 3. Conditions and visibility (shared by many spots)

**General Sydney pattern** [SP12, SP17, SP21; HEURISTIC]:
- **Best visibility:**
  - late summer–autumn, when East Australian Current water arrives (warm and blue, with pelagics: kingfish, bonito, sometimes mahi mahi);
  - **winter westerly spells**, when the sea is flat and clear (Abyss: Jul–Sep westerlies give "flat seas and excellent visibility" at Kurnell [SP21]).
- **Worst visibility:**
  - after southerly groundswell (it stirs sediment and kelp for 2–4 days);
  - after heavy rain (stormwater, lagoon openings, estuary plumes);
  - during NE-wind upwelling in spring and summer (cold, green, sometimes very clear but cold) [HEURISTIC].
- Beginner Spearfishing Australia says the northern beaches and Bare Island "tend to clear first when the swell drops", with best vis in flat conditions or a northerly swell [SP17].

**Local killers by spot:**

| Cause | Affects | Rule of thumb |
|---|---|---|
| Diamond Bay cliff outfall (Vaucluse/Diamond Bay; diversion still being built in Jan 2026) [SP11] | E1, and North Bondi in N–NE currents | Avoid E1 outright |
| Bondi, Malabar and North Head deepwater outfalls (3–4 km offshore) [SP20] | Rarely inshore; possible with onshore wind plus upwelling | Ignore [HEURISTIC] |
| Warriewood WRRF outfall at Turimetta Head [SP13] | Turimetta, Narrabeen Head north side, Warriewood | Avoid Turimetta; downgrade N5 in N–NE currents |
| Lagoon openings: Manly (1.4 m AHD), Curl Curl and Dee Why (2.2 m), Narrabeen (1.0–1.3 m) (`northern-beaches-knowledge.md` N11) | N2, N3, N4 south side, N5 | Same as R-NL1: rain72 ≥ 30 mm → no-go for 72 h |
| Botany Bay ebb plume | E14–E17 (bay side) | Prefer the **incoming** tide; Sutherland Pt "visibility can drop around low tide" [SP21] |
| Harbour runoff | H1–H3 | 3-day rain rule (`eastern-additions.md`) |
| Hawkesbury/Pittwater ebb | N10 | Flood tide; skip after rain |
| Stormwater drains (Whale Beach, Long Bay, Bondi) | local | Rain24 ≥ 10 mm → downgrade [HEURISTIC] |

**Shore-entry safety thresholds** [HEURISTIC; McFadyen's text is consistent with them: "if the waves are not breaking at the entry and exit points"]:
- Hs at the spot (after the bot's own exposure and shelter factor):
  - < 0.8 m: OK;
  - 0.8–1.2 m: only for sheltered entries (South Maroubra, Long Bay, Kurnell bay side, Fishermans Beach, Station Beach, Camp Cove);
  - > 1.5 m: no ocean shore entries.
- Long-period swell (≥ 12 s) surges much harder than its height suggests. Drop one step.

**Seasonal targets** [HEURISTIC unless tagged; general NSW fishing knowledge]:

| Species | Where | When |
|---|---|---|
| Yellowtail kingfish | Headland points and bommies, North Bondi, South Maroubra [SP20 saw schools], Kurnell, Barrenjoey, Long Reef | Dec–May, peak Feb–Apr |
| Australian bonito | Open headlands | Autumn–winter |
| Rock blackfish (drummer) | Whitewash, caves and gutters everywhere (Long Bay and Little Bay caves [SP20]) | All year, **best May–Sep** [getfishing, via search] |
| Luderick | Weedy platforms, Little Bay, Mahon [SP20], estuary mouths (Barrenjoey, La Perouse) | May–Sep |
| Bream | Everywhere, especially bay and harbour edges | All year; winter runs near the heads |
| Snapper | Reef–sand edges (Long Bay, South Maroubra, North Bondi [SP20]) | Winter–spring (bigger fish); squire all year |
| Silver trevally | La Perouse, Kurnell, harbour | Winter |
| Flathead (dusky, sand) | Sand edges (Long Bay [SP20], Cape Solander [SP17]) | Summer |
| John Dory | Harbour, Botany Bay, Kurnell bay side | Jun–Sep |
| Red morwong | Every reef (slow-growing resident; bag 5) | All year |
| Salmon, tailor | Headlands and washes | Autumn–winter |

**Look-alikes to avoid:**
- blue groper (juvenile green or brown);
- **blue drummer (*Girella cyanea*)**, a protected fish that looks like black or silver drummer;
- eastern blue devil (caves at North Bondi [SP20]).

---

## 4. Per-spot notes

### Eastern suburbs

**E1 Diamond Bay / Dover Heights.** These are sheer sandstone cliffs. There is no safe public entry, and the Diamond Bay outfall still discharges untreated wastewater; Sydney Water's "Refresh Vaucluse and Diamond Bay" is diverting it to Bondi, but the work was still in design and construction in Jan 2026 [SP11]. Listed only so the bot can say no.

**E2 North Bondi / Ben Buckler** [SP20].
- **Access:** the Ramsgate Ave car parks and the stairs to the platform.
- **Entries:** from the southern platform tip in very calm seas; at the "little break" 45° left of the stairs in slight seas; at the **boat ramp** in heavier seas. The ramp is also the preferred exit in all seas.
- **Bottom:** boulders at 5–6 m, then south to the sand at 15 m, deepening to 18–21 m.
- **Hazards:** tinnies run "at full speed up onto the specially designed ramp".
- **Fish:** silver trevally, bream, yellowtail, snapper, luderick, red morwong and sweep; "occasionally … large schools of yellowtail kingfish". Also blue groper and eastern blue devils, both protected.
- Bondi Beach itself is closed except the 20 m ends.
- Exposure: open to S/SE/E swell [DERIVED: the reef faces south into the bay].

**E3 South Bondi (Flat Rock)** [SP20].
- **Entry:** below Wilga St stairs.
- **Needs:** "slight south-easterly swells and otherwise calm seas".
- **Bottom:** 6 m boulders and sand, then a low kelp reef.
- **Hazards:** surgy to the north.
- **Fish:** red morwong and crays (hands only, not in the IPA band).

**E4 Bronte → Clovelly (Waverley Cemetery cliffs).**
- Legal inside the Bronte–Coogee AR, but there are no published spear entries [HEURISTIC]. Platform below the cemetery, big surge; low confidence.
- **Clovelly and Gordons Bay are closed**: Sch 4, the "Gus the groper" area, and the Gordons Bay underwater trail.
- A spearfisher killed "Gus" the groper at Clovelly in 2023. The fallout fed into the 2024 groper line ban [search extract, NZ Herald].

**E5 Wedding Cake Island** (-33.9259, 151.2654).
- An islet ~600 m off Coogee and a big-wave surf bombie.
- A JBL spearfishing promo was shot here [SP22].
- Swim out from Trenerry Reserve or Giles Baths [HEURISTIC]. You need a float and flag (Coogee boat traffic, jet skis), flat seas and a W wind.
- **Fish:** kingfish and bonito in summer–autumn; drummer and morwong on the island [HEURISTIC].

**E6 Coogee south / Lurline Bay.**
- South of the Coogee rock baths, so outside the AR.
- Platforms at Trenerry Reserve and Lurline Bay; Lurline is a surf break, so expect surfers [HEURISTIC]. Low confidence.

**E7 Mahon Pool / North Maroubra** [SP20].
- **Entry:** the small point at the NE of the pool.
- **Route:** snorkel 120 m east to the gutter start. Reef top is 7 m; canyon 12 m; stepped ledges 18 m; sand at **24 m**, ~300 m out. "Very good" vis reported (18 m+).
- **Fish:** lots of luderick near shore.
- **Exit:** "the millpond seas were still too rough to safely exit the water at this location" (it had been cancelled many times). **Needs the flattest days.** No spearing inside the pool [SP10].

**E8 South Maroubra** [SP20].
- **Access:** South Maroubra SLSC car park, then walk ~250 m along the platform to a small inlet. **Enter from the SE corner of the inlet, not the beach.**
- **Check:** "If the surf immediately next to the rock pool … is flat and there is not a strong rip … it is safe".
- **Depth:** 7 m wall, out to 12–15 m at the reef–sand edge.
- **Shelter:** "diveable in all but the biggest southerly and south-easterly winds and seas". It is one of the two southern-Sydney ocean sites McFadyen lists as southerly-buster refuges.
- **Fish:** "prolific", including yellowtail kingfish, snapper, bream, drummer and "the largest dusky flatheads".
- **Edges:** Magic Point GNS critical habitat lies ~300 m SE [DERIVED]. Don't drift onto it.

**E10 Long Bay (Malabar)** [SP20].
- **Entry and exit:** the old Randwick Golf Club pool on the west side (Bay Pde/Howe St car park). Exit is best "at or near high tide", through the channel next to the pool.
- **Depth:** 3 m out to 9–10 m (two big rocks), with sand edges at 6.5–8 m.
- **Fish:** "big numbers of … eastern rock blackfish"; bream, snapper, yellowtail, flathead and leatherjackets.
- **Shelter:** "diveable in all but the biggest easterly and southerly seas".
- **Hazards:** the Long Bay IPA (no inverts); the Malabar boat ramp on the north shore; old Malabar outfall history (fixed 1990).
- Malabar Beach itself is closed except the 20 m ends.

**E12 Little Bay** [SP20, SP9].
- **Bay route:** a 200 × 75 m bay. 3.5–5 m at the mouth, then a wall out east to 10 m and sand at 13 m.
- **Fish:** luderick and drummer in the overhangs near shore; yellowtail, sea pike and sweep.
- **"4th Hole" (Coast Golf Club):** a gully entry with 8–12 m walls and a cave "that shelters large numbers of big eastern rock blackfish and luderick". It needs slight seas: "so long as the waves are not breaking at the entry and exit points". There is "quite a tidal flow back out to sea" at high tide.
- **Social licence:** residents campaigned for a ban in 2019. DPI brokered "spearfishing … only east of a red line", with entry and exit only in the marked area.
- **The bot should say "enter from the rocks, not the beach".**
- A fatal shark bite on a swimmer happened here in Feb 2022 [HEURISTIC].

**E13 Cape Banks** [SP20, SP16].
- Boat mark 50 m south of the tip, at 12–15 m.
- McFadyen marks the shore entry (via the old Cape Banks bridge) "not recommended".
- USFA: it offers "safe protection to spearfishers from northerly winds and swell".
- AR rules: finfish only, nothing else.
- Treat it as an advanced spot [HEURISTIC].

**E15 La Perouse (Astrolabe Cove, Larpa Point)** [SP20].
- The mainland reefs either side of the Bare Island bridge. Fisheries sank fish-attraction structures in Astrolabe Cove (2006).
- Faces into Botany Bay, sheltered from N–NE.
- **Bare Island is closed until about late 2027** [SP7]. The water under the bridge may have work zones, so keep clear.
- **Fish:** drummer, luderick, bream, trevally [fishing guides via search]; John Dory in winter [HEURISTIC].

**E16–E17 Kurnell** (Kamay Botany Bay NP; pay entry; gates close at night) [SP20, SP21, SP23].
- **The Monument → Inscription Point / The Steps** is on the bay side: an easy rock entry and a 12–14 m wall. It is the most sheltered from S swell.
- **The Leap** is a jump from a rock shelf at the bottom of a narrow track (Abyss: "giant-stride entry"). It is a drift to 22 m that exits at The Steps, best on "incoming tide near high".
- **Yena** is SE of The Leap and needs "really calm seas" to exit.
- **Hazards:**
  - heavy scuba traffic (give divers a wide berth);
  - the new Kamay ferry wharf at Kurnell [TfNSW];
  - weedy seadragons (protected);
  - the Inscription Point invertebrate closure.
- **Fish:** kingfish, drummer, snapper, morwong, John Dory [HEURISTIC]. USFA's Alliman Shield competition has been held at Kurnell (2015) [search extract, usfa.org.au].

**E18 Cape Solander.**
- Abyss: max ~24 m, "rock entry and exit; experienced divers only", "very calm seas"; wobbegongs, bull rays and blue groper [SP21].
- Beginner Spearfishing: flathead on the sand, snapper on the drop-offs; exposed to southerlies and "can be rough" [SP17].
- Bot: pros only (consistent with the surf side of this repo).

**E19 Boat Harbour (Kurnell).**
- An aquatic reserve where spearing is OK.
- USFA: "historically and culturally important to spearfishers and its sheltered location is important for novice and junior divers" [SP16].
- Access is by 4WD (beach permit) or a long walk from Kurnell. It is just outside the bot's coverage.

### Harbour (eastern side)

**H1 Camp Cove / H2 Green Point** [SP20, SP21, SP16].
- **Access:** easy sand entry at Camp Cove. A shallow wall with swim-throughs drops to 19 m off Green Point.
- **Shelter:** one of McFadyen's southerly-buster refuges.
- USFA lists Camp Cove and Nielsen Park as "safe and shallow water spearfishing access".
- **Hazards:**
  - summer swimmers (spear well away from them; DPI's guidance);
  - ferries and boats;
  - harbour bull sharks, especially Dec–Apr after rain;
  - the dioxin intake advice (§1.7).
- **Fish:** bream, luderick, trevally, kingfish in summer, John Dory in winter [HEURISTIC].

### Northern beaches

**N1 North Head ocean side.**
- Legal, but USFA says the "only safe entry exit point frequented by spearfishers" is via the Shelly Beach headland, which is inside Cabbage Tree Bay.
- **[HEURISTIC]:** walking an unloaded gun through a no-take reserve to reach legal water is a grey area. Ask DPI.
- **Hazards:** steep cliffs, swell, currents, and the heavy boat traffic of the Heads.
- Bot: pros or boat only.

**N2 Freshwater (Harbord) / Queenscliff Head.**
- McFadyen lists "Harbord" as a shore dive (page not fetched).
- Beginner Spearfishing: "Freshwater to Curl Curl Headland: easy shore access … about 3–8 m … bream, luderick and occasionally snapper … the headland gives some protection from swell" [SP17].
- Manly Lagoon outflow (Queenscliff) ruins it after rain.
- The Freshwater side (faces NE) is tucked from southerlies [DERIVED from OSM geometry].

**N3 Curl Curl → Dee Why Head.**
- Platform and IPA; Curl Curl Lagoon is right there.
- Nothing published. Low confidence.

**N4 Long Reef** [SP3, SP16, SP14].
- **History:** where Australian spearfishing organised itself (USFA founded at Collaroy in 1948).
- **Rules:** AR, finfish by line or spear only. No crays, octopus or urchins here, unlike the other reserves.
- **Entry:** Fishermans Beach on the north side (N–NE facing, sheltered from southerlies; boat ramp traffic) [HEURISTIC]. The reef is a very wide, shallow platform with gutters, which suits drummer, luderick and bream. Fishermans also mention "Snapper Ledge" [Fishing Monthly via search].
- **Hazards:**
  - a shallow-water surge zone;
  - the **Dee Why Lagoon** outflow on the south side;
  - **a fatal white-shark bite on a surfer, 6 Sep 2025, ~100 m off Long Reef**. Long Reef has drumlines and no net [SP14].
- **Politics:** USFA (Apr 2026) reports a push for a sanctuary [SP18]. Re-check legality each season.

**N5 Narrabeen Head** [SP3, SP16].
- AR, spear OK. USFA: "a large area of <20m reef which is vital for safe spearfishing".
- Narrabeen Lake (Sch 4) and its entrance currents and plume sit on the south side.
- **Turimetta Head** (just north) has the Warriewood outfall, at about -33.6968, 151.3140 [SP13].
- **Bot:** prefer the head's south/lagoon side only when the lagoon is closed and dry. Downgrade in N–NE currents (outfall plume) [HEURISTIC].

**N6–N9 Mona Vale → Whale Beach headlands** (Mona Vale Hd, Bungan Hd, Newport south, Bilgola Hd, Avalon/Bangalley, Little Head).
- All legal (Mona Vale and Bungan are invert-only IPAs).
- **No publicly named spearfishing write-ups found.** Only Fishing Monthly notes "even bigger pigs [drummer] from the upper northern beach suburbs rocks like Barrenjoey".
- Include them as generic "northern headland" spots only if the bot needs coverage. Use the north-side-tucked-from-southerlies pattern [HEURISTIC]. Confidence L.

**N10 Barrenjoey Head** [SP3, SP16, SP19].
- AR (about 30 ha) from the northern end of Station Beach to the northern end of Palm Beach; line and spear OK.
- USFA: "significant land based access for spearfishers" with "safe access and use in adverse southerly wind and swell".
- **Entries:** Station Beach (Pittwater side, flat) or the north end of Palm Beach (the 20 m rule applies to the beach) [DERIVED].
- **Hazards:**
  - strong tidal streams at the head;
  - Palm Beach ferry, Barrenjoey boat ramp and Broken Bay traffic (float and flag essential);
  - the Hawkesbury ebb plume after rain;
  - bull sharks (estuary) [HEURISTIC].
- **Fish:** drummer ("bigger pigs"), kingfish, luderick, bream, snapper, salmon, tailor; flathead on the Pittwater sand [HEURISTIC + Fishing Monthly].
- **Bot:** this is the northern region's **southerly-day pick**.

---

## 5. Suggested bot wiring (not implemented)

- Add `spear_legal` (bool) plus `spear_notes` per spot. Never surface closed areas (§1.3, §1.4) as options. Show them only as "closed" if the user asks.
- Score from:
  - **Hs at the spot** (the existing exposure model);
  - **wind direction** relative to the spot's facing (offshore is best);
  - **rain72** (lagoon, harbour and estuary rules);
  - **tide stage** (incoming or high for Botany Bay and Barrenjoey; high for exit-limited spots: Long Bay, Little Bay 4th Hole, Mahon);
  - **days since southerly swell > 2 m** (vis recovery, 2–4 days) [HEURISTIC].
- Hard "no" cases:
  - Bare Island until NPWS reopens it;
  - Magic Point, Turimetta and Diamond Bay always;
  - lagoon-mouth spots for 72 h after rain72 ≥ 30 mm;
  - the harbour for 72 h after significant rain.
- Show a fixed reminder: breath-hold only, no lights, **no blue groper or blue drummer**, float and flag, stay away from swimmers, and don't load the gun out of the water.

---

## 6. Sources

- **SP1** NSW DPI/DPIRD spearfishing closures and guides (listed in §1.1). All returned 403 to bots and **were not read directly**; facts tagged with them come from search-engine extracts.
- **SP2** Fisheries Management (General) Regulation 2019 [2019-407], compiled version current from 20 Jan 2023, read via FAOLEX: https://faolex.fao.org/docs/pdf/nsw225309.pdf. Used: cl 10, 14, 49, 51, 52, 152; Sch 1 (bags); Part 2 size table; **Sch 4**. Official: https://legislation.nsw.gov.au/view/html/inforce/current/sl-2019-0407
- **SP3** NSW DPI, *Sydney Harbour and northern beaches Recreational Fishing Guide*, Aug 2017 (Fisheries Compliance Unit), republished by Sydney Coastal Councils: https://www.sydneycoastalcouncils.com.au/wp-content/uploads/2018/09/sydney-north-rec-fishing-guide.pdf. It covers aquatic reserve boundaries and rules, IPAs, spearfishing closures, gear and harbour dioxin advice. Its 2024 successor: https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0019/614512/Recreational-Fishing-Guide-Sydney-North-April-2024.pdf
- **SP4** NSW Government Gazette 2025 No 81 (28 Feb 2025): Eastern Blue Groper Fishing Closure Notification 2025 and Possession Limit Order 2025: https://gazette.nsw.gov.au/gazette/2025/2/2025-2_81-gazette.pdf
- **SP5** NSW Government Gazette 2020 No 100: OTL export approval closures incl. Magic Point (commercial): https://gazette.nsw.gov.au/gazette/2020/5/2020-100.pdf
- **SP6** fishare.app, "Sydney Aquatic Reserves" (third-party summary of the 2024-25 DPI text; used for Cape Banks, Boat Harbour, Towra and reference points): https://fishare.app/blog/sydney-aquatic-reserves-guide.html
- **SP7** NSW Environment & Heritage news, "Bare Island Bridge closes for essential restoration" (21 Aug 2026): https://www.environment.nsw.gov.au/news/bare-island-bridge-closes-essential-restoration
- **SP8** DPI grey nurse critical habitat and Magic Point (search extracts): https://www.dpi.nsw.gov.au/fishing/closures/location-closures/magic-point ; https://www.dpi.nsw.gov.au/fishing/species-protection/what-current/critically/grey-nurse-shark/new-fishing-and-diving-rules
- **SP9** Prince Henry Community Association, "Spearfishing at Little Bay" (2019 timeline, DPI meeting, agreed zone): https://princehenrycommunity.com.au/the-neighbourhood/call-to-action/spearfishing-at-little-bay/
- **SP10** Randwick City Council, "Fishers reminded spearfishing prohibited in Randwick City ocean pools" (Jan 2017): https://www.randwick.nsw.gov.au/about-council/news/news-items/2017/january/fishers-reminded-spearfishing-prohibited-in-randwick-city-ocean-pools
- **SP11** Sydney Water, Refresh Vaucluse and Diamond Bay (project page and Jan 2026 notice): https://www.sydneywater.com.au/water-the-environment/what-we-are-doing/projects-in-your-area/refresh-vaucluse-and-diamond-bay.html
- **SP12** Adreno, "NSW Spearfishing Sites" and "How to get started spearfishing in Sydney" (2021; note its wrong claim that torches are legal): https://adreno.com.au/pages/nsw_new_south_wales_spearfishing_dive_sites ; https://adreno.com.au/blogs/news/how-to-get-started-spearfishing-in-sydney
- **SP13** Clean Ocean Foundation, Warriewood monitoring summary (outfall coords) and the Surfrider 2014 report (cliff-face outfall at Turimetta Head), via search: https://www.nespmarine.edu.au/system/files/Warriewood%20Monitoring%20Summary%20-%20Clean%20Ocean%20Foundation_10Nov17.pdf
- **SP14** Long Reef fatal shark bite, 6 Sep 2025 (CBS News; The New Daily): https://www.cbsnews.com/news/shark-attack-details-surfer-killed-australia-mercury-psillakis
- **SP15** Jan 2026 Sydney bites (RTE, 20 Jan 2026): https://www.rte.ie/news/world/2026/0120/1554079-shark-attack-australia ; see also `eastern-additions.md` H11
- **SP16** USFA, "Spearfishers points of recommendation for the Hawkesbury Bioregion Marine Park" (2018): https://usfa.org.au/wp-content/uploads/2018/09/USFA-recommendations-HBRMP.pdf
- **SP17** Beginners Spearfishing Australia, "A Beginner's Guide to Spearfishing Sydney" (Mar 2026, updated Oct 2026): https://beginnerspearfishing.com.au/a-beginners-guide-to-spearfishing-sydney-nsw-best-spots-species-and-regulations/ . Also Frog Dive, "Spearfishing in NSW" (May 2026): https://www.frogdive.com.au/blogs/news/spearfishing-in-nsw-what-gear-you-need-what-the-rules-are-and-where-to-start
- **SP18** USFA Presidential Update (29 Apr 2026): https://usfa.org.au/?p=18028
- **SP19** Northern Beaches Council, Barrenjoey Head Aquatic Reserve: https://www.northernbeaches.nsw.gov.au/things-to-do/recreation-area/barrenjoey-head-aquatic-reserve
- **SP20** Michael McFadyen's Scuba Diving site, dive-site pages (WGS84 GPS, entries, depths, conditions): https://www.michaelmcfadyenscuba.info/viewpage.php?page_id=N with N =
  - 313 North Bondi; 280 Flat Rock; 303 Mahon Pool; 329 South Maroubra;
  - 300 Long Bay; 297 Little Bay; 298 Little Bay 4th Hole; 268 Cape Banks;
  - 293 Astrolabe Cove; 294 Larpa Pt; 256 and 261 Bare Island; 288 Inscription Pt/Steps; 311 Monuments; 295 The Leap; 777 Yena;
  - 335 Tupia Pt; 488 Fairy Bower; 267 Camp Cove; 283 Green Point; 271 Clifton Gardens.
- **SP21** Abyss Scuba, Sydney dive sites: https://www.abyss.com.au/sydney-dive-sites
- **SP22** ScubaBoard, "Recent spearfishing promo we shot in and off Sydney" (Wedding Cake Island, Camp Cove): https://scubaboard.com/community/threads/recent-spearfishing-promo-we-shot-in-and-off-sydney.369015
- **SP23** Pro Dive Sydney dive sites (Kurnell: The Steps, The Leap, The Monument; Camp Cove; Bare Island): https://www.prodive.com.au/sydney/dive-sites
- OSM Nominatim geocodes (queried 2026-11-10) for all coords tagged "(OSM)".

**Not found or not done:**
- **Spearfishing Downunder threads.** The search engine didn't index them for these spot names, and I did not log in anywhere.
- **Reddit threads.**
- **Dive Centre Manly and Frog Dive site guides** for northern-beaches spear spots.
- **YouTube videos** tied to specific northern-beaches headlands.
- **The current Cape Banks and Boat Harbour boundary text.**
- **The current DPIRD Botany Bay spearfishing closure list** (blocked).

No spot described anywhere as "secret" was included. Every spot here is a named public headland, beach end or published dive site.
