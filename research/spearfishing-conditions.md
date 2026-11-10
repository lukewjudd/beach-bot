# Spearfishing (breath-hold) conditions: what to score and the data behind it

Researched 10 Nov 2026 for a Beach Bot spearfishing mode covering the eastern suburbs (Bondi to La Perouse and
Kurnell) and the northern beaches (Manly to Palm Beach).

Rules followed: no logins, no getting around bot checks or paywalls, no Wayback. Several sources refused automated
fetches: Seabreeze, Swellnet, DeeperBlue forums, Reddit, the NSW DPIRD spearfishing pages and guide PDF, NSW Marine
Estate, and a Griffith repository PDF. For those I used only the search-engine summary and say so. Facebook groups
and Instagram need a login, so I did not read them. Anything marked **(judgement)** is my own reasoning, not a
sourced number.

---

## Short answer

1. **Local spearos and dive shops judge a day on swell first, then rain, then wind.** Visibility (vis) follows swell
   size and direction, how many dry days there have been since rain, and how sheltered the site is. Wind mostly
   matters at the surface. Tide matters at harbour, bay and estuary sites. The rules of thumb in their own words:
   - swell "0.5–1 m" with a short period is ideal
   - a 1 m swell at 12 s surges harder than 1.2 m at 7 s
   - wait "two or three days of dry weather" after big rain
   - vis is best on flat days or with a northerly swell, and worst after a southerly groundswell
   - a normal day is 5–10 m, a great day is over 15 m, and winter is clearest

   Nobody publishes a calibrated rule.
2. **Being clear on the surface and "milky by 3 m" is a known kind of event, and it can be partly flagged ahead of
   time.** The likeliest causes off Sydney:
   - (a) cold water creeping onto the shelf along the bottom. Off Bondi this happened 29 times in 5 years, mostly in
     summer, and it is usually driven by the East Australian Current (EAC) rather than by wind.
   - (b) a near-bottom layer of fine sediment that earlier swell stirred up and that has not settled yet.
   - (c) less often, a layer of plankton or plume water sitting at a density step.

   A whitish, "milky" look points to fine mineral particles, so (b), or to the edge of a layered water column.
   Green points to plankton, so (a). Brown or tea-coloured points to runoff. Satellites only see the top optical
   layer, so they will miss a clear-over-milky profile. The bot can still raise a "may be murky below the surface"
   flag from:
   - swell energy at the site over the last 1–3 days, especially long-period groundswell
   - a run of north-easterly (NE) wind together with a drop in sea-surface temperature (SST)
   - recent rain, a lagoon recently opened, or the ebb tide out of Botany Bay or the harbour
3. **The best free data is satellite light attenuation (Kd490) and suspended sediment, plus Sentinel-2.**
   - NOAA CoastWatch ERDDAP serves gap-filled Kd490 and suspended particulate matter (SPM) at 2 km. No login, CC0,
     daily from 2018, about 12 days behind.
   - The near-real-time chlorophyll products at about 4 km run about 3 days behind.
   - IMOS THREDDS serves NOAA-20 VIIRS Kd490 and chlorophyll for Australia at about 830 m, CC-BY, about 3 days
     behind. It is often masked by cloud and by its coastal mask.
   - Sentinel-2 at 10–20 m can resolve individual coves and is available with no login through Earth Search STAC.
     It passes every 2–3 days, and about a third of passes are clear enough.

   Everything else the bot needs it mostly has already: Open-Meteo waves, ocean currents and SST, BOM rain gauges,
   Beachwatch and tides (UHSLC hourly sea level for Fort Denison, station 333).
4. **I found no published model that predicts diver visibility from weather.** The closest are:
   - Secchi-depth models from chlorophyll, freshwater and wind (Gullmar Fjord)
   - Chesapeake Bay's sediment-plus-algae forecast
   - Great Barrier Reef photic-depth studies that remove wave and tide effects statistically
   - commercial "vis predictors" (Vizzbud, ScubaDownUnder Viz Check, dive-forecast) that publish their inputs but
     not their weights or accuracy
5. **Pilot calibration, run here: IMOS Reef Life Survey (NRMN) data has 612 dated Sydney visibility readings in
   metres (2009–2025, 217 dates), with a public WFS endpoint.** Against ERA5 swell and rain, and against satellite
   Kd490, it shows:
   - open coast: vis falls with swell over the last 3 days (Spearman ρ −0.28) and with 7-day rain (ρ −0.28)
   - Botany Bay sites react more to rain (ρ −0.40 for 3-day rain)
   - harbour sites barely react to either
   - gap-filled Kd490 gives ρ −0.41 against open-coast and Botany vis (98 site-days), the strongest single signal

   That data set is the calibration base. The proposed bars are in §5.

---

## 1. What Sydney spearos and divers judge a day on

The best sources were dive shops (Abyss, Frog Dive, Dive Centre Manly), Sydney vis guides (Vizzbud,
beginnerspearfishing.com.au), Fishing Monthly reports, the Illawarra Flame "Hello Fish" column and Swellnet. Forum
threads (DeeperBlue, Reddit, Spearfishing Downunder) were blocked or redirected, so I have only their search
summaries.

### 1.1 Visibility, and how people guess it beforehand

- **Typical numbers:**
  - Abyss: "6–8 metres across most shore sites", "up to 15 metres at prime locations", winter "often exceed[s]
    20 metres", and below 2 m in affected areas soon after heavy rain
    ([Abyss, Understanding diving conditions](https://www.abyss.com.au/blog/diving/understanding-diving-conditions)).
  - Vizzbud's scale: under 3 m poor, 3–5 below average, 5–10 average, 10–15 good, over 15 great
    ([Vizzbud Sydney guide](https://vizzbud.com/blog/sydney-dive-visibility-guide)).
  - Beginners Spearfishing: 5–10 m on a normal day, over 15 m after "a few days of calm weather and offshore winds",
    especially on the northern beaches and the headlands south of Bondi
    ([beginnerspearfishing Sydney guide](https://beginnerspearfishing.com.au/a-beginners-guide-to-spearfishing-sydney-nsw-best-spots-species-and-regulations/)).
- **How they guess beforehand:**
  - check the swell forecast and a webcam on the morning of the dive
    ([Frog Dive](https://www.frogdive.com.au/blogs/news/spearfishing-in-nsw-what-gear-you-need-what-the-rules-are-and-where-to-start))
  - count the dry days since rain, and match the site's aspect to the swell (Vizzbud checklist)
  - forum users consistently say forecasting vis is guesswork and that the morning look is what counts (search
    summary of DeeperBlue threads; the pages themselves returned 403)
- **Who clears first:** "Visibility is best on flat conditions or a northerly swell, and worst after southerly
  groundswell". The northern beaches and Bare Island "clean up first" when swell drops (Frog Dive).
- **Season:** "Winter and early spring often deliver the cleanest water of the year" (Frog Dive). Abyss gives
  June–August in one place and July–October in another.

### 1.2 Swell size, direction, period and surge at depth

- Abyss:
  - "A 0.5–1 metre swell with a shorter period and light winds" is ideal for most divers.
  - "A 1.2 m swell at 7 seconds may be manageable, while a 1 m swell at 12 seconds creates powerful surge". A
    "12–14 second swell produces stronger surge; 7–8 s is usually easier for shore entries".
  - Surge is strongest in shallow water and around reefs.
  - Site notes: small S/SE swell suits Shelly Beach and Cabbage Tree Bay. Oak Park and Cape Solander get exposed in
    bigger southerly swell. Bare Island goes from beginner to intermediate-only in a building swell.
- Vizzbud:
  - "Swell is the single biggest driver of Sydney visibility."
  - Energy goes with height squared (1 m to 2 m is about 4×). 12 s and longer carries far more surge than under 7 s.
  - Good-day checklist: "swell under about 1m (or sheltered from its direction)".
- Beginners Spearfishing's public scoring script, which is useful as a community baseline:
  - swell under 0.5 m scores 100, under 1 m 80, under 1.5 m 55, under 2.5 m 30, otherwise 10
  - entry is "Easy" under 0.5 m and "Moderate" under 1 m
  - period is displayed but not scored
  ([spearfishing weather tool](https://beginnerspearfishing.com.au/spearfishing-weather/))
- Fishing Monthly (land-based, but the same water): the deeper east-facing headlands usually have cleaner water,
  and "current direction and swell direction can determine the water clarity at your local spot" (Apr 2022, via
  [issuu summary](https://issuu.com/fishingmonthly/docs/fmmapril2022issuu/s/15164145)).

### 1.3 Wind and onshore chop

- Abyss: wind "mainly affects surface comfort and chop, not underwater conditions". Westerlies flatten east-facing
  sites, strong NE sea breezes roughen afternoon exits, and "a southerly wind typically brings cleaner conditions to
  many sites". No numbers.
- Vizzbud: chop goes with wind speed squared. Light offshore is best, onshore is worse, and wind against swell is
  worst. Harbour sites go murky in wind.
- Beginners Spearfishing script, wind bands: under 8 km/h scores 100, under 12 km/h 80, under 18 km/h 55, under
  25 km/h 30, otherwise 10. Its prose says winds above 25 km/h are generally unsafe.

### 1.4 Tide: state, range, slack

- Abyss:
  - Ship Rock is best about 10 minutes before Fort Denison high tide. Chowder Bay is best about 2.5 h after high.
  - Bare Island: spring tides strengthen the current around the point, and many prefer high tide.
  - Shelly Beach and Cabbage Tree Bay: high tide often improves vis.
  - Oak Park is often best at low tide, for the entry.
  - "Many sites are best around high slack tide."
- Vizzbud:
  - At low tide, reefs and rock platforms block more swell. At high tide more energy gets through.
  - An incoming tide can improve vis near estuary entrances.
- Theunderwaterclub (search summary): high tide brings ocean water with less sediment.
- **Estuary ebb plumes are real and measured.** Botany Bay's low-density plume reached up to 11 km across the shelf
  on ebb tides. Its shape depended on tide, freshwater input and coastal currents (Kingsford & Suthers 1994,
  *Continental Shelf Research* 14:655–672; abstract via
  [search record](https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/40664435)).

### 1.5 Rain and runoff: how much, how long, which outlets

- Spearo and dive sources:
  - Vizzbud: "two or three days of dry weather" after a big event. A calm day straight after heavy rain can still be
    murky. No mm threshold.
  - Abyss: "dirty runoff water after heavy rain" is a no-go.
  - A Sydney site claimed in search snippets that heavy rain cuts vis for 48–72 h at Bare Island, Gordons Bay and
    Clovelly, which are near stormwater drains. I could not verify that page, so treat it as weak.
- Official (these are about bacteria, but they are the only official lags):
  - Northern Beaches Council: avoid ocean beaches "during and for one day after heavy rain"
    ([council, via search summary](https://northernbeaches.nsw.gov.au/council/news/rain-forecast-time-prepare)).
  - Woollahra: avoid the harbour "for up to three days following rainfall"
    ([Woollahra](https://www.woollahra.nsw.gov.au/Environment/water-and-our-harbour/Harbour-water-quality)).
- Science:
  - Sydney Harbour's plume was mixed away by the tide about 5 days after the event (Wolanski 1977, cited by Lee,
    Birch & Lemckert; [Griffith repository](https://research-repository.griffith.edu.au/server/api/core/bitstreams/f9209607-d5ca-51ad-becb-3e9fc853a1c1/content),
    403, so this is from the search summary).
  - Modelled Hawkesbury, Sydney Harbour, Botany Bay and Port Hacking plumes: in a wet event the freshwater area
    stays above baseline for about 6 days. River discharge peaks after 48 h and is back to base after 96 h. Plumes
    stay "trapped by the coast", under 12 km offshore and 13–20 m thick. Botany Bay plumes were historically
    2–8 m thick ([Li, Roughan, Kerry & Rao 2022, Front. Mar. Sci.](https://frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.815348/full)).
  - **Big floods are a different scale.** In 2022 the freshwater plume reached five times further than previously
    thought, ran as deep as about 50 m (per the NSW release), and low salinity lasted up to 2 months
    ([Malan, Roughan, Hemming & Ingleton 2024, Nature Comms](https://www.nature.com/articles/s41467-023-44398-2.pdf)).
    After Feb 2020 rain a Hawkesbury-derived plume sat past Terrigal for over 5 weeks
    ([NSW DPE Terrigal turbidity report](https://www.environment.nsw.gov.au/sites/default/files/towards-safer-swimming-terrigal-region-turbidity-and-discolouration-200413.pdf)).
- Lagoons:
  - Council opening levels: Narrabeen Lagoon at 1.0–1.3 m AHD, Dee Why Lagoon at 2.2 m AHD
    ([Northern Beaches lagoons page](https://www.northernbeaches.nsw.gov.au/environment/coast-and-waterways/lagoons)).
  - Narrabeen needs about 1 m above mean sea level to stay open, and is opened on a falling high tide when rain is
    flowing out (2020 council release, via search).
  - Beachwatch samples 2 Narrabeen Lagoon sites weekly and does not sample Manly, Curl Curl or Dee Why lagoons for
    swimming ([State of the Beaches reports](https://www.environment.nsw.gov.au/sites/default/files/state-of-the-beaches-2022-23-sydney-region-230279.pdf)).
- Outlets that matter (named across the sources):
  - Hawkesbury and Broken Bay, for Palm Beach, Barrenjoey and the far north
  - Narrabeen, Dee Why, Curl Curl and Manly lagoons
  - Sydney Harbour, for North Head, Blue Fish Point and the South Head, Camp Cove and The Gap side
  - Botany Bay, for Bare Island, Kurnell and Cape Banks
  - the stormwater drains at Gordons Bay, Clovelly and Bondi

  The deep ocean sewage outfalls (Malabar, Bondi, North Head) discharge 1.5–3 km offshore. They are designed and
  monitored to stay submerged in summer
  ([Sydney Water deep ocean outfalls assessment 2025](https://www.sydneywater.com.au/content/dam/sydneywater/documents/deep-ocean-outfalls-assessment.pdf)).
  I found no evidence that they set nearshore vis. **(judgement: ignore them for now.)**

### 1.6 Current, EAC eddies, and cold upwelling after NE winds

- The folk rule "a nor'easter brings cold, often green water" is well supported by the mechanism:
  - Persistent NE winds push surface water offshore (Ekman transport) and cooler water rises. "Usually you need a
    few days of strong north-east winds". Nearly two weeks of weaker afternoon NE sea breezes can do it too.
  - The MHL buoys are often too far offshore to see it (Swellnet analyses
    [2006](https://www.swellnet.com/news/swellnet-analysis/2006/07/03/why-does-water-get-colder-sydney-after-noreaster)
    and [2016](https://www.swellnet.com/news/swellnet-analysis/2016/03/10/sydneys-cold-water-episode-explained);
    both 403, so from search summaries).
  - Dec 2024: a 17–19 °C cool tongue off the coast after a spell of NE winds produced sea fog at Dee Why and Manly
    ([Weatherzone](https://www.weatherzone.com/au/news/coastal-upwelling-shrouds-sydney-coast-with-sea-fog/1890175)).
  - Jan 2007: the water dropped to a record 14 °C and was "greenish and cloudy", which an eddy about 100 km offshore
    pulled up ([OceanFit](https://oceanfit.com.au/education/coriolis-effect-when-the-water-gets-cold-in-summer/)).
  - Illawarra, Jan 2022: NE-wind and EAC upwelling, then plankton blooms, and murky diving that is "common over
    summer" ([Illawarra Flame](https://www.theillawarraflame.com.au/hello-fish-why-the-waters-been-so-murky/)).
- **Science specific to Sydney:**
  - A Bondi mooring recorded 29 cold-water events between May 2006 and Jun 2011, more often in summer.
  - "The major forcing mechanism was the interaction of a strong southward flowing current with the sea floor
    causing onshore movement of subsurface cooler water". Onshore bottom flows exceeded 0.07 m/s.
  - Events forced by wind alone "tended to be weaker and of a shorter duration". The biggest uplift came when strong
    southward current coincided with upwelling-favourable wind
    ([Wood & Roughan, EGU 2012 abstract](https://meetingorganizer.copernicus.org/EGU2012/EGU2012-6789.pdf)).
  - Current-driven uplift happens in a 10–20 m bottom boundary layer and "is generally confined to the subsurface",
    while wind-driven events can reach the surface (Schaeffer, Roughan & Wood 2014, *JGR Oceans* 119:4922; summary
    via [core.ac.uk related paper](https://core.ac.uk/download/36198275.pdf)).
- Practical current notes:
  - Current is stronger around headlands and channels and on bigger tidal ranges (Abyss).
  - Beginners Spearfishing's tool fakes current from wind, so it has no real data.
  - Open-Meteo Marine already provides `ocean_current_velocity` and `ocean_current_direction`. I verified both off
    Sydney.

### 1.7 Water temperature (and its link to vis and species)

- Seasons:
  - Abyss: summer 23–25 °C, autumn 20–23, winter 14–18, spring 18–22.
  - Frog Dive: winter 14–17 °C, summer 22–25 °C, with a 5 mm two-piece suit year-round.
  - Beginners Spearfishing's wetsuit bands: 24 °C and up boardshorts or rashie, 21 °C 2 mm shorty, 18 °C 3 mm,
    15 °C 5 mm, below that a hood.
- Vis link: cooler months are generally clearer (Vizzbud, Frog Dive). **Within summer, a sudden drop of a few
  degrees means upwelled water, which is often green and cloudy (§1.6), not clearer.**
- Species:
  - The EAC brings pelagics in summer and autumn. Kingfish work the headlands and offshore reefs in warmer months.
    Snapper are year-round but more common in cooler months (Beginners Spearfishing).
  - Kingfish feed less in cold water. Westerlies that cool the water cut kingfish numbers (Fishing Monthly, Dec
    2021 and Jul 2022 summaries).

### 1.8 Season, moon and light

- Moon: Beginners Spearfishing's prose says "a new moon is widely considered best" and that fish are "less active by
  day" around the full moon. Their own score ignores the moon. I found no evidence beyond lore.
  **(judgement: display only.)**
- Light: their score gives 20% to cloud cover, under the claim that low cloud with light wind and small swell
  "usually correlates" with vis above 10 m. That is not evidence that cloud changes water clarity. Cloud changes how
  much light there is and how far you can see a fish.
  **(judgement: a small "light" bar from sun elevation and cloud, kept separate from vis.)**

### 1.9 Rules that are hard constraints, not scores

- NSW bans spearfishing on all ocean beaches except the last 20 m at each end. Many lagoons, estuary entrances and
  aquatic reserves are closed, including Narrabeen Lake, Cabbage Tree Bay/Shelly Beach and Bronte–Coogee Aquatic
  Reserve. Never spearfish alone (the
  [NSW DPI spearfishing guide](https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0018/602118/Recreational-Spearfishing-Guide-January-2024.pdf)
  returned 403, so these come from search summaries. The bot should hard-code its closure list from the current
  guide).
- Bare Island shore access is closed for bridge repairs, expected until late 2027 (Beginners Spearfishing).
- After heavy rain, the state advises extra care within 1 km of river mouths and harbours because of bull sharks
  ([NSW gov release](https://www.nsw.gov.au/ministerial-releases/increased-bull-shark-activity-expected-around-beaches-and-waterways-following-heavy-rainfall)).
  That is a safety flag for spearos specifically, because speared fish give off blood and vibration.

---

## 2. Visibility science, and the "fine on the surface, milky by 3 m" question

### 2.1 What sets nearshore clarity off Sydney

| Driver | Mechanism | Time scale | Evidence |
|---|---|---|---|
| Swell resuspension | Wave motion at the bed lifts fine sand and silt. Long periods reach deeper. | Hours to about 1–2 days after the swell drops, longer for fine silt and clay | Palos Verdes shelf: a near-bed orbital velocity of 14 cm/s is the threshold for real resuspension, with events averaging 1.6 days at 60 m ([USGS](https://pubs.usgs.gov/publication/70024556)). The Massachusetts Bay stress metric uses Hs and Tp, and longer periods give more bed stress (search summary). Sydney dive shops rank swell first. |
| Runoff plumes | Fresh, turbid, tannin-stained water floats out of lagoons, the harbour and Botany Bay and is trapped against the coast | Typical event about 5–6 days; floods weeks to 2 months | Li et al. 2022; Wolanski 1977; Malan et al. 2024; the Terrigal report |
| Stormwater outfalls | Local brown and polluted water at drains | 1–3 days | Council and Beachwatch advice |
| Upwelling and slope-water intrusion | Cold, nutrient-rich water arrives, then a phytoplankton bloom follows, turning the water green | Days to weeks. Mostly summer. | Wood & Roughan 2012; Schaeffer et al. 2014; Illawarra Flame; OceanFit |
| Plankton seasonality | Spring and summer blooms; winter is clearer | Seasonal | Port Hacking 100 m station: chlorophyll peaks in late winter, early spring and summer, tied to slope-water intrusions ([CSIRO MF9930325](https://connectsci.au/mf/article-lookup/doi/10.1071/MF9930325)). Subsurface chlorophyll maxima are common on the 31.5–34°S shelf, with depth set by the EAC and its eddies ([Malan et al. 2023](https://unsw.edu.au/content/dam/pdfs/campus/2024-05-oceanography/malan-et-al-jgr-2023.pdf)). |
| Algal blooms | *Noctiluca* "red tides" at Sydney beaches, linked to upwelled nutrient-rich water | Days | 2012 Bondi closures ([CSM](https://m.csmonitor.com/World/Global-News/2012/1128/Red-algae-bloom-closes-Sydney-s-beaches-but-probably-not-for-long)) |
| Wind chop | Chop and breaking stir the top layer and cut light; the harbour is sensitive | Hours | Vizzbud |

### 2.2 "Looked fine on the surface, very milky by about 3 m": can it be explained and predicted?

**Yes, it can be explained. It can only partly be predicted.** It means the water column was layered, with a
clearer top layer over a more turbid one. Ranked by how likely each candidate is off Sydney's open-coast reefs
**(judgement, built on the sources above)**:

1. **A layer of fine sediment near the bottom, left over from earlier swell.** Swell (especially long-period S or SE
   groundswell) stirs fine material up from the sand next to the reef. Once the swell drops, the surface layer clears
   first and the suspended fines settle slowly through the lower few metres, so the murk sits near the bottom.
   - "Milky" (pale, whitish) is how fine mineral particles look. They scatter strongly and absorb little. Plankton
     looks green and runoff looks brown.
   - **Signals:** swell energy at the spot over the previous 24–72 h well above today's, and a falling swell. The
     bot already has per-spot exposure and the swell-train split.
   - As a rough Stokes-law guide **(judgement, worked here)**: 10 µm silt falls about 0.1 mm/s, so it takes about
     8 h to settle 3 m. 2 µm clay falls about 0.004 mm/s, so it takes days, unless it clumps together.
2. **Cold water creeping onto the shelf below a warm surface layer.** Off Bondi this is the dominant cold-water
   mechanism. It is driven by the current, mostly in summer, and "confined to the subsurface", so the surface can look
   normal while the water below a thermocline is colder, nutrient-rich and often greener or cloudier. At the interface
   divers often see a shimmering, blurry layer as warm and cold water mix.
   - **Signals:**
     - a run of NE wind (2 or more days of moderate to strong NE, or a week or more of afternoon NE sea breezes)
     - a drop in nearshore SST compared with a few days earlier or compared with offshore
     - the EAC or an eddy pressed against the shelf (IMOS OceanCurrent maps or GSLA currents)
     - in summer, a cold layer at depth that the satellite SST cannot see
3. **A plankton layer at the density step.** Possible in strongly layered summer water, but on the shelf these layers
   usually sit deeper than 3 m (Malan et al. 2023). Less likely at a 3–5 m reef unless the upwelled layer has
   pushed in close to shore. **Signal:** the same as 2, plus satellite chlorophyll rising over the following days.
4. **An estuary or lagoon plume.** Fresh plumes float, so they usually make the surface murkier, not the water below.
   Exceptions:
   - an older plume that has mixed down, with Botany Bay plumes 2–8 m thick and wet-event plumes 13–20 m
   - an ebb plume pushed under by a front
   - the blurry halocline layer where fresh water meets salt

   **Signals:** rain in the previous 1–6 days, a lagoon opened recently, ebb tide at a site near Botany Bay, the
   harbour or a lagoon.
5. **An optical illusion, and part of most cases.** From the surface you look down a short, sunlit path at
   bright sand, so the water looks clear. Horizontal vis at depth is shorter, and contrast falls as light drops. This
   makes a modest turbid layer look "suddenly" milky. Not a separate cause, but it is why the surface look misleads.

**What the bot can do:**

- Raise a "may be murky below the surface" flag when either is true:
  - (a) the swell energy at the spot peaked in the last 72 h at, say, 2× or more of today's, which is a sign of
    leftover stirred-up sediment
  - (b) an upwelling signal (a NE wind run plus an SST drop of 1.5–2 °C or more over 3 days) **(judgement
    thresholds, to be calibrated)**
- **Satellites cannot settle it.** Ocean-colour signals come from roughly the first optical depth, about 1/Kd. At a
  Kd490 of 0.1 m⁻¹ that is about 10 m, but at 0.3 m⁻¹ it is about 3 m. A clear top layer over a milky one will
  look clear to the satellite too.
- If the user gives the date and site of the milky dive, we can replay that day's swell, rain, wind run, SST and
  Kd490 to see which cause fits.

### 2.3 Turning optical measures into diver visibility

- Kd490 and Secchi depth are related but not convertible without a local regression
  ([NRL 1993](https://asprs.org/wp-content/uploads/pers/1993journal/mar/1993_mar_345-350.pdf)).
- Doron et al. 2007 retrieve [Kd(490)+c(490)]⁻¹ as a proxy for vertical visibility, and estimate horizontal
  visibility from reflectance, to within about a factor of 2–3
  ([JGR record](https://zendy.io/title/10.1029/2006jc004007)).
- A commercial blog matched about 43,000 Japanese dive-shop vis reports to SeaWiFS/MODIS 8-day Kd490
  ([dive-forecast](https://dive-forecast.vercel.app/blog/satellite-data-visibility-guide)). It reports no
  correlation coefficient and is not peer-reviewed:

  | Kd490 (m⁻¹) | Mean vis |
  |---|---|
  | under 0.05 | 19.9 m |
  | 0.05–0.10 | 13 m |
  | 0.10–0.15 | 10.3 m |
  | 0.15–0.20 | 8.9 m |
  | 0.20 or more | 7.7 m |
- **Sydney pilot (this research, §5.4):** open-coast and Botany Bay sites, 98 site-days, gap-filled 2 km Kd490
  against NRMN vis. Spearman ρ = −0.41:

  | Kd490 (m⁻¹) | n | Median vis |
  |---|---|---|
  | 0.07–0.10 | 6 | 9 m |
  | 0.10–0.15 | 19 | 7.5 m |
  | 0.15–0.25 | 39 | 6 m |
  | 0.25 or more | 33 | 5 m |

  The trend matches Japan's, but Sydney's Kd490 values near shore run higher.

---

## 3. Data sources (free and machine-readable)

Checked live on 10 Nov 2026 where it says "verified".

### 3.1 Satellite water clarity (Kd490, SPM, chlorophyll)

| Source | Endpoint / ID | Variables | Resolution | Latency | Licence / access | Notes |
|---|---|---|---|---|---|---|
| **NOAA CoastWatch ERDDAP, gap-filled (DINEOF) VIIRS+OLCI** (verified) | `https://coastwatch.noaa.gov/erddap/griddap/noaacwNPPN20S3AkdSCIDINEOF2kmDaily` (also `...AspmSCIDINEOF2kmDaily` for SPM, `...ASCIDINEOF2kmDaily` for chlorophyll) | `kd_490` (m⁻¹), SPM, `chlor_a` | 2 km, daily, 2018 to recent | About 12 days (latest 2026-10-29 on 2026-11-10) | CC0, no login | **No cloud gaps**, but filled values are statistical estimates. Good for calibration and backfill. Sample: `...csv?kd_490[(last)][(0.0)][(-33.95):(-33.85)][(151.25):(151.35)]`. Values off Bondi on 29 Oct were 0.08–0.30 m⁻¹, falling with distance offshore. |
| NOAA CoastWatch NRT VIIRS / OLCI (verified) | `noaacwN20VIIRSchlaDaily`, `noaacwS3AOLCIchlaDaily`; 750 m and 300 m sector products also exist (the Sydney sector code was not identified) | `chlor_a` | about 4 km (0.0375°) | About 3 days | CC0 | S-NPP ended 2026-11-02, so use NOAA-20, NOAA-21 or S3. The merged NRT Kd490 4 km product stopped in 2021. |
| **IMOS SRS ocean colour, NOAA-20 VIIRS, Australia** (verified) | `https://thredds.aodn.org.au/thredds/dodsC/IMOS/SRS/OC/gridded/noaa20/P1D/YYYY/MM/J.P1D.YYYYMMDDT053000Z.aust.K_490.nc` (also `chl_oci`, `chl_gsm`, `owtd_csiro` = optical water type, `par`, `sst`) | K_490, chlorophyll, PAR, optical water type | 0.0075° (about 830 m) | About 3 days (latest 07 Nov on 10 Nov) | CC-BY 4.0 with IMOS acknowledgement, no login, OPeNDAP | Sampling 4, 5 and 7 Nov off Bondi and Botany: only 5 Nov had any valid pixels, about 3 km out (0.045–0.125). The coastal strip is masked, so **expect gaps**. |
| Copernicus Marine OC NRT | `OCEANCOLOUR_GLO_BGC_L3_NRT_009_101`, e.g. `cmems_obs-oc_glo_bgc-transp_nrt_l3-olci-4km_P1D` ([product](https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L3_NRT_009_101)) | KD490, **ZSD (Secchi depth)**, SPM, chlorophyll | 4 km for transparency; 300 m for plankton and reflectance | About 1 day | Free, but **needs registration** (not tested, per the no-login rule) | ZSD gives a direct Secchi estimate. |
| **Sentinel-2 L2A via Earth Search STAC** (verified) | `POST https://earth-search.aws.element84.com/v1/search` with collection `sentinel-2-l2a`, tile **56HLH** | Surface reflectance; turbidity from band 4 (665 nm) and band 5 with the Nechad algorithm; ACOLITE recommended for water | 10–20 m | Hours to 1 day; a pass every 2–3 days (S2A, B, C) | Open data on AWS, no login | 29 passes 10 Sep–10 Nov 2026; about 10 under 20% scene cloud. **The only source that resolves individual coves.** Needs water atmospheric correction and glint handling. |
| NASA OB.DAAC (MODIS-Aqua, VIIRS L2/L3) | oceancolor.gsfc.nasa.gov | Kd490, chlorophyll, Rrs | 1 km (L2), 4 km (L3) | 1–2 days NRT | Needs an Earthdata login | Use the ERDDAP or IMOS mirrors instead. |

**Pixel size compared with coves:** Gordons Bay, Clovelly and Shelly Beach are 100–400 m wide. A 2–4 km pixel
covers the whole coastal strip and mixes in offshore water. The standard L2 flags mask pixels next to land and
"straylight", so the nearest valid VIIRS pixel is usually 1–3 km out. In the pilot the median distance to the
nearest valid gap-filled pixel was 0.9 km. **Treat 1–4 km products as "the water mass offshore of the reef", not
the cove.** Only Sentinel-2 or Landsat get inside coves.

**Has anyone related satellite turbidity to diver vis?**
- Not in peer-reviewed work that I found.
- Closest: Doron et al. on horizontal visibility; the Secchi Disk seafarer citizen-science comparison
  ([PLOS ONE 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5795334)); the GBR photic depth calibrated to Secchi
  ([Fabricius et al. 2016](https://portfolio.jcu.edu.au/publications/JCU158687)); and the commercial Japanese
  table.
- The Sydney pilot in §5.4 is new.

### 3.2 SST, SST anomaly, upwelling

- Open-Meteo Marine `sea_surface_temperature`, hourly (verified, already in use). Model SST is smooth and will miss
  nearshore upwelling tongues.
- **IMOS GHRSST L3S-1d** (verified catalogue):
  - `https://thredds.aodn.org.au/thredds/catalog/IMOS/SRS/SST/ghrsst/L3S-1d/` (day, night, day+night), about 2 km
  - also L3S-3d/6d/14d, L3C-1h (Himawari, `h08` folder) and L4
  - CC-BY
  - Use it for a 3-day SST drop at the coast compared with 20–30 km offshore, as an **upwelling index**
    **(judgement)**.
- IMOS OceanCurrent maps (SST, SST anomaly, chlorophyll, currents, Brisbane–Sydney region) at
  oceancurrent.aodn.org.au. These are images, good for a human check. The NRT feeds are not fully quality-controlled
  ([site notes](https://oceancurrent.aodn.org.au/whatsshown.htm)).
- MHL Waverider buoy SST: the buoys sit too far offshore to catch nearshore upwelling (Swellnet).
  [AODN/THREDDS](https://data.gov.au/data/dataset/manly-hydraulics-laboratory-waverider-buoys-sea-surface-temperature-data).
- **A cheap upwelling proxy the bot can compute now** (judgement):
  - the alongshore wind run: sum of the NE component over the last 3–5 days
  - the SST drop over 3 days
  - the coast is oriented about 20–30° east of north at Sydney, so NE winds are upwelling-favourable

### 3.3 Waves (Sydney buoys)

- MHL Sydney directional Waverider (offshore). History is via AODN THREDDS (above). The real-time map is at
  [mhl.nsw.gov.au/Data-Wave](https://mhl.nsw.gov.au/Data-Wave).
  - The site's JavaScript calls an undocumented API (`api.manly.hydraulics.works`) with a public username. I did
    not use it.
  - For a supported feed, ask `data-request@mhl.nsw.gov.au`.
- The NSW nearshore wave forecast is linked from MHL: [forecast.waves.nsw.gov.au](https://forecast.waves.nsw.gov.au).
- The bot already has Open-Meteo wave partitions and per-spot exposure. That is enough to score.

### 3.4 Lagoon entrance status

- **There is no machine-readable "open or closed" feed that I found.**
- Council news posts each Narrabeen opening
  ([examples](https://northernbeaches.nsw.gov.au/council/news/update-narrabeen-lagoon-entrance); Pittwater Online
  News also reports them).
- MHL's real-time water-level map lists level stations. A sharp fall in lagoon level marks a breakout, using the
  opening levels: Narrabeen 1.0–1.3 m AHD, Dee Why 2.2 m AHD. I could not confirm which lagoon gauges are public
  without the undocumented API.
- Proxy: Beachwatch lagoon results and pollution forecasts (already in use), and Sentinel-2 imagery, where the
  entrance channel is visible at 10 m.
- **(judgement)** For a first version, hand-enter known openings, or treat "over 50 mm in 48 h" as "lagoons likely
  flowing out".

### 3.5 Tides

- **UHSLC fast-delivery hourly sea level, Fort Denison, station 333** (verified): ERDDAP
  `https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_fast` with `uhslc_id=333`. Fit harmonics locally
  (for example with UTide) for predictions.
- BOM tide predictions for Fort Denison are on the web, not an API.
- Open-Meteo `sea_level_height_msl` is already in the bot. It is model-based, so check its phase against Fort
  Denison.

### 3.6 Currents

- **Open-Meteo Marine `ocean_current_velocity` and `ocean_current_direction`** (verified: values of 0.2–1.0 km/h at
  −33.96, 151.29 on 10 Nov). Coarse, but already reachable through the same API.
- IMOS OceanCurrent GSLA NRT (verified catalogue): `https://thredds.aodn.org.au/thredds/catalog/IMOS/OceanCurrent/GSLA/NRT/`.
  Sea-level anomaly and geostrophic currents, daily, about 0.2°. Shows the EAC and eddies.
- BOM OceanMAPS/Bluelink and Copernicus GLO physics give 3-D forecasts. Copernicus needs registration, and I did not
  check OceanMAPS access.
- **IMOS ANMN NSW moorings** (verified catalogue: `.../IMOS/ANMN/NSW/` has ORS065 off Bondi, SYD100, SYD140 and
  PH025–PH140 off Port Hacking). Delayed-mode temperature profiles. Use them for thermocline climatology and a list
  of past cold-water events, not live.

### 3.7 Rain and runoff

- BOM gauges and multi-model past rain are already in the bot (`forecast.py`).
- Beachwatch pollution forecasts are already in.
- The BOM Sydney (Terrey Hills) radar is images only.
- **(judgement)** Gauges plus an antecedent-rain index (§5) are enough.

### 3.8 Ground truth: dated visibility reports for calibration

| Source | What | Access | Use |
|---|---|---|---|
| **IMOS NRMN / Reef Life Survey survey list** (verified) | **612 dated Sydney transects with visibility in metres, 2009–2025, 217 dates, about 50 sites** (Shelly, Fairy Bower, Blue Fish Point, Gordons Bay, Clovelly, The Gap, Bare Island, Kurnell, Camp Cove, Middle Head and more) | WFS: `https://geoserver-123.aodn.org.au/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=imos:ep_survey_list_public_data&outputFormat=csv&BBOX=151.1,-34.1,151.4,-33.55`. Fields include `visibility`, `survey_date`, `hour`, `depth` and lat/lon. | **Main calibration set.** Bias: surveys run on calm days, mostly scuba at 3–10 m. |
| Michael McFadyen's dive logs (yearly PDFs) | Thousands of dated dives since the 1990s, mostly Bare Island, Kurnell and Inscription Point. Fields: weather, sea condition, vis **as a word** (Very poor / Poor / Fair / Good / Excellent), water temp, depth, time. | e.g. `https://mail.michaelmcfadyenscuba.info/downloads/2023dives.pdf` (text extracts cleanly with pdftotext) | Ordinal calibration for the Botany Bay mouth, plus water temperature at depth |
| IMOS NRS Port Hacking 100 m | Monthly Secchi depth and TSS since about 2009 | [data.gov.au record](https://data.gov.au/data/dataset/6ab2a576-adc9-4e85-bfd9-e39f192ca311) (moving to the AODN "Combined Biogeochemical" collection) | Offshore seasonal baseline and plankton, not cove vis |
| Abyss "Today's Sydney Dive Conditions" | A dated daily vis range (e.g. "5–8 m" on 10 Nov 2026) plus a site rating | [abyss.com.au/dive-conditions](http://www.abyss.com.au/dive-conditions). No archive or feed; ask before scraping. | Forward-going daily log |
| Dive Centre Manly / ProDive posts | Tide, wind, water temp; vis rarely | Site blogs | Weak |
| ScubaDownUnder Viz Check | User vis reports and their own model | [scubadownunder.com/viz-check](https://scubadownunder.com/viz-check); no API | Possibly ask them |
| "VIZ Sydney Diving Visibility Reports" (Facebook), Instagram shop posts | Daily diver reports | Needs a login; not accessed | Manual only |
| **Our own log** | The user's spearing sessions: date, time, site, vis at the surface and at 5 m, colour (clear/green/milky/brown), temperature, surge | A form in the web app | Best long-term data **(judgement)** |

---

## 4. Published or community models and rules of thumb

| Model | Inputs | Output | Validation | Source |
|---|---|---|---|---|
| Vizzbud conditions score | Live swell and wind forecasts plus each site's exposure (aspect, shelter, refraction) | Green, yellow or red for "water movement", hourly. Explicitly **not vis**, with no rain or plankton term. | None published | [Vizzbud](https://vizzbud.com/blog/sydney-dive-visibility-guide) |
| ScubaDownUnder Viz Check | Recent swell height and period, wind speed, 48 h rain, tide phase and height, diver reports | Vis in m, hourly, 24 h ahead; green means 8 m or more; a confidence % | None published | [Viz Check](https://scubadownunder.com/viz-check) |
| Beginners Spearfishing score | Wind 35%, swell 30%, cloud 20%, rain probability 15% (bands in §1) | 0–100 | None | [tool](https://beginnerspearfishing.com.au/spearfishing-weather/) |
| dive-forecast (Japan) | Kd490 and chlorophyll (8-day), plus an unpublished ML model | Vis | Band means only | [blog](https://dive-forecast.vercel.app/blog/satellite-data-visibility-guide) |
| Gullmar Fjord Secchi model | Chlorophyll, freshwater height, wind | Secchi depth; r rises from 0.63 with chlorophyll alone to 0.75 with all three | Peer-reviewed | [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0924796305002046) |
| Chesapeake CBEFS | Modelled suspended sediment (waves, rivers) and algae | Secchi forecast | Peer-reviewed (Turner et al. 2021) | [VIMS](https://www.vims.edu/research/products/cbefs/water_clarity/) |
| GBR photic depth | MODIS photic depth, with waves and tides removed statistically, against river discharge | Clarity drops to 47% of maximum after floods and takes months to recover | Peer-reviewed | [Fabricius et al. 2014/2016](https://portfolio.jcu.edu.au/publications/JCU158687) |
| Resuspension threshold | Near-bed orbital velocity of 14 cm/s or more from buoy Hs and T | Count and duration of resuspension events | Peer-reviewed (Palos Verdes) | [USGS](https://pubs.usgs.gov/publication/70024556) |

---

## 5. Recommended spearfishing score

The bars, weights and thresholds below are **(judgement)** unless a source is given. They follow the style of the
bot's other modes (parts with caps, plus hard gates).

### 5.1 Hard gates, applied before scoring

- **Closed area:** the site is in a no-spearfishing zone or on an ocean beach away from the 20 m ends. Not offered.
- **Unsafe entry or exit:** the bot's breaking-wave estimate at the site's entry exceeds a per-site limit, about
  1.0 m Hs for platform entries and 1.5 m for sheltered coves. Score capped at "poor". The Abyss no-go is "waves
  breaking across the entry or exit".
- **Lightning or storm:** the existing `storm()` rule.
- **Flood or plume:** 7-day rain of 100 mm or more, or the 2022-style long event. Cap vis at "poor" for all open
  coast within about 10 km of the Hawkesbury, harbour or Botany Bay mouths until 7 or more dry days have passed (Li
  2022, Malan 2024 for scale).
- **Bull shark advisory:** rain of 20 mm or more in 48 h and the site within 1 km of a river or harbour mouth. Show a
  warning, not a score change (NSW advice).

### 5.2 Bars

| Bar | Weight | Inputs | Scoring (0–1) | Confidence |
|---|---|---|---|---|
| **1. Visibility (predicted)** | 40% | Site baseline; swell-energy memory; antecedent rain index; outlet proximity and tide; Kd490 nudge; season | Predict vis in m, then map: 3 m or less → 0; 5 m → 0.4; 8 m → 0.75; 12 m or more → 1. **Formula:** `vis = base_site × f_swell × f_rain × f_season × f_sat`. **base_site:** median NRMN vis (open coast about 8 m, Botany mouth about 5 m, harbour about 5 m; per-site where n ≥ 10). **f_swell = exp(−a·E72)**, where E72 = max over the last 72 h of (Hs at spot² × Tp), decayed with a 24 h half-life. **f_rain = exp(−b·API)**, where API = Σ_d rain_d·0.6^d over 7 days; b is multiplied by 1.5–2 for sites within about 2 km down-current of a lagoon, estuary or drain. **f_season:** winter (Jun–Sep) ×1.2, summer upwelling ×0.8. **f_sat:** when a valid Kd490 within 3 km and 3 days exists, blend toward the table in §2.3. | Medium-low. Direction is well supported; coefficients need fitting (§5.4). |
| **2. Surge at depth** | 25% | Hs at spot, Tp (dominant train), target depth (5 m and 10 m) | Linear-theory bottom excursion **A = Hs / (2·sinh(k·h))**. A ≤ 0.4 m → 1; 0.8 m → 0.6; 1.2 m → 0.3; 1.8 m or more → 0. Worked: 1 m at 12 s at 8 m gives A ≈ 1.0 m; 1.2 m at 7 s gives A ≈ 0.6 m. This matches Abyss ("1 m at 12 s worse than 1.2 m at 7 s"). The peak bottom velocity is about 0.5 m/s in both cases, so **excursion, not velocity, is what tells the two apart**. | Medium. Physics sound; thresholds are judgement. |
| **3. Surface (wind and chop)** | 15% | Wind speed, gusts, onshore component at the site, from the existing `wind_points` logic | Under 10 km/h → 1; 10–18 → 0.7; 18–25 → 0.4; over 25 → 0.1 (close to the Beginners Spearfishing bands). Onshore direction ×0.7; offshore over 30 km/h ×0.6 for drift and float safety. | Medium |
| **4. Tide** | 10% | Fort Denison tide phase and range; site type | **Harbour, Botany and lagoon-adjacent sites:** flood tide to high slack → 1; ebb in the first 3 days after 20 mm or more of rain → 0.2; other ebb → 0.6. Ship Rock and Chowder Bay use the Abyss offsets. **Open coast:** high slack → 1, other states 0.7; spring range above 1.8 m → ×0.8 at headlands for current. | Medium-low (dive-shop lore plus plume physics) |
| **5. Light** | 5% | Sun elevation, cloud cover | Sun elevation 30° or more and cloud under 50% → 1; dawn, dusk or overcast → 0.5 | Low; mostly comfort and spotting fish |
| **6. Water temperature** | 5% (comfort) plus a flag | Open-Meteo SST, IMOS L3S SST, 3-day change | Comfort curve for a 5 mm suit; **flag "cold, possibly green" if SST drops 1.5 °C or more in 3 days, or NE wind run ≥ X** | Medium for the flag, low for the weight |

Display only, not scored: moon phase (lore only), and a species and season hint (kingfish when the water is warm and
the EAC is near; snapper in cool months).

**"May be murky below the surface" flag (§2.2):** raise it when swell energy at the spot peaked at 2× or more of
today's in the last 72 h, or when the upwelling flag is on, or when 20 mm or more of rain fell in the previous
1–6 days near an outlet. Show which one.

### 5.3 Why these weights

Swell and rain drive both vis and safety (all sources agree). The pilot shows that swell and rain explain part of
open-coast vis but not harbour vis. Surge is a separate thing from vis: a breath-hold diver on a 5–10 m reef is
held back by water movement even in clear water. Wind is mainly a surface issue (Abyss). Tide matters only at
certain sites. Moon has no evidence.

### 5.4 Calibration, with the pilot already run

**Pilot setup.** NRMN visibility for Sydney, grouped by date and site group:
- open coast: 108 dates
- Botany Bay mouth: 43 dates
- harbour: 98 dates

Matched against Open-Meteo ERA5 daily maximum wave height at −33.92, 151.30 and ERA5 rain at Sydney, and, for 2018
on, against the gap-filled 2 km Kd490 at the nearest valid pixel within 6 km.

**Spearman ρ against vis:**

| | Hs, same day | Hs, max of last 3 days | Period | Rain, 1 day | Rain, 3 days | Rain, 7 days | Kd490 |
|---|---|---|---|---|---|---|---|
| Open coast | −0.22 | −0.28 | −0.34 | −0.19 | −0.23 | −0.28 | −0.41 (with Botany, 98 site-days) |
| Botany mouth | −0.35 | −0.35 | −0.22 | −0.37 | −0.40 | −0.32 | (as above) |
| Harbour | −0.09 | −0.12 | −0.23 | +0.10 | −0.03 | −0.19 | – |

**Open-coast medians:**
- By 3-day maximum swell: under 1.5 m → 10 m vis (n = 5); 1.5–2 m → 8 m; 2–2.5 m → 6.8 m; 3 m or more → 6 m.
  ERA5 is offshore and biased low; these are not at-spot heights.
- By 7-day rain: under 10 mm → 8 m; 10–30 mm → 7 m; 30–60 mm → 6.5 m; 60 mm or more → 6 m.
- By month: June–July are the clearest (medians about 8–10 m against 5–7 m in summer), in line with dive-shop lore.

**Caveats:** surveys are run on calm days, dates are few, ERA5 is coarse, and transects on the same day are not
independent. The correlations are modest, which is what you'd expect.

**Next steps:**
1. Rebuild this with the bot's at-spot swell (exposure-weighted) and BOM gauge rain.
2. Fit `log(vis) ~ site + swell-energy memory + API + month + Kd490`, with leave-one-year-out testing.
3. Add McFadyen's ordinal logs for Bare Island and Kurnell as an ordinal model.
4. Log Abyss's daily range going forward, if they allow it.
5. Add a vis form for the user's own dives (surface and 5 m vis, colour, temperature, surge).

Scripts and data from the pilot are in the session scratchpad:
`/private/tmp/claude-502/pilot/` (`marine.json`, `rain.json`, `rows.json`, `kd.json`) and
`/private/tmp/claude-502/nrmn_syd.csv`. Move them into the repo if you want to keep them.

### 5.5 Confidence summary

- **High:** swell, rain and season set vis; surge rises with period; NE wind and EAC events bring cold, often green
  water; plumes are trapped against the coast for about a week, longer after floods.
- **Medium:** the Kd490 relationship (ρ about −0.4); the tide effects at harbour and Botany sites; the explanation
  of milky-below-the-surface.
- **Low:** every threshold and weight in §5.2 until it is fitted; the moon; how much light matters.

---

## Sources

- Abyss, Understanding Diving Conditions: https://www.abyss.com.au/blog/diving/understanding-diving-conditions
- Abyss, Today's Sydney Dive Conditions: http://www.abyss.com.au/dive-conditions
- Vizzbud, Sydney Dive Visibility guide: https://vizzbud.com/blog/sydney-dive-visibility-guide
- Frog Dive, Spearfishing in NSW: https://www.frogdive.com.au/blogs/news/spearfishing-in-nsw-what-gear-you-need-what-the-rules-are-and-where-to-start
- Beginners Spearfishing, Sydney guide: https://beginnerspearfishing.com.au/a-beginners-guide-to-spearfishing-sydney-nsw-best-spots-species-and-regulations/
- Beginners Spearfishing, weather tool: https://beginnerspearfishing.com.au/spearfishing-weather/
- ScubaDownUnder Viz Check: https://scubadownunder.com/viz-check
- dive-forecast satellite guide: https://dive-forecast.vercel.app/blog/satellite-data-visibility-guide
- Fishing Monthly (issuu summaries): https://issuu.com/fishingmonthly/docs/fmmapril2022issuu/s/15164145
- Illawarra Flame, murky water: https://www.theillawarraflame.com.au/hello-fish-why-the-waters-been-so-murky/
- Illawarra Flame, waiting for the water to clear: https://www.theillawarraflame.com.au/hello-fish-waiting-for-the-water-to-clear/
- Swellnet, NE wind cold water (403, search summary): https://www.swellnet.com/news/swellnet-analysis/2006/07/03/why-does-water-get-colder-sydney-after-noreaster
- Swellnet, 2016 cold episode (403, search summary): https://www.swellnet.com/news/swellnet-analysis/2016/03/10/sydneys-cold-water-episode-explained
- Weatherzone, upwelling and sea fog, Dec 2024: https://www.weatherzone.com/au/news/coastal-upwelling-shrouds-sydney-coast-with-sea-fog/1890175
- OceanFit, summer cold water: https://oceanfit.com.au/education/coriolis-effect-when-the-water-gets-cold-in-summer/
- Wood & Roughan 2012, EGU abstract: https://meetingorganizer.copernicus.org/EGU2012/EGU2012-6789.pdf
- Schaeffer, Roughan & Wood 2014, JGR Oceans, doi:10.1002/2013JC009284 (record: https://zendy.io/title/10.1002/2013jc009284)
- Malan et al. 2023, JGR (subsurface chlorophyll maxima): https://unsw.edu.au/content/dam/pdfs/campus/2024-05-oceanography/malan-et-al-jgr-2023.pdf
- Malan et al. 2024, Nature Comms (2022 flood plumes): https://www.nature.com/articles/s41467-023-44398-2.pdf
- Li, Roughan, Kerry & Rao 2022, Front. Mar. Sci.: https://frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.815348/full
- Kingsford & Suthers 1994, Cont. Shelf Res. 14:655: https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/40664435
- NSW DPE Terrigal turbidity report: https://www.environment.nsw.gov.au/sites/default/files/towards-safer-swimming-terrigal-region-turbidity-and-discolouration-200413.pdf
- Sydney Water deep ocean outfalls assessment 2025: https://www.sydneywater.com.au/content/dam/sydneywater/documents/deep-ocean-outfalls-assessment.pdf
- Northern Beaches Council, lagoons: https://www.northernbeaches.nsw.gov.au/environment/coast-and-waterways/lagoons
- State of the Beaches 2022–23, Sydney: https://www.environment.nsw.gov.au/sites/default/files/state-of-the-beaches-2022-23-sydney-region-230279.pdf
- Woollahra, harbour water quality: https://www.woollahra.nsw.gov.au/Environment/water-and-our-harbour/Harbour-water-quality
- NSW DPI Recreational Spearfishing Guide (403, search summary): https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0018/602118/Recreational-Spearfishing-Guide-January-2024.pdf
- NSW bull shark advice: https://www.nsw.gov.au/ministerial-releases/increased-bull-shark-activity-expected-around-beaches-and-waterways-following-heavy-rainfall
- USGS, Palos Verdes resuspension: https://pubs.usgs.gov/publication/70024556
- Fabricius et al., GBR water clarity: https://portfolio.jcu.edu.au/publications/JCU158687
- Gullmar Fjord Secchi model: https://www.sciencedirect.com/science/article/abs/pii/S0924796305002046
- VIMS CBEFS water clarity: https://www.vims.edu/research/products/cbefs/water_clarity/
- Doron et al. 2007: https://zendy.io/title/10.1029/2006jc004007
- NRL 1993, Secchi and Kd: https://asprs.org/wp-content/uploads/pers/1993journal/mar/1993_mar_345-350.pdf
- Seafarer Secchi citizen science (PLOS ONE): https://pmc.ncbi.nlm.nih.gov/articles/PMC5795334
- Port Hacking chlorophyll (CSIRO MF9930325): https://connectsci.au/mf/article-lookup/doi/10.1071/MF9930325
- CSMonitor, 2012 Noctiluca bloom: https://m.csmonitor.com/World/Global-News/2012/1128/Red-algae-bloom-closes-Sydney-s-beaches-but-probably-not-for-long
- NOAA CoastWatch ERDDAP: https://coastwatch.noaa.gov/erddap/
- IMOS THREDDS: https://thredds.aodn.org.au/thredds/catalog/IMOS/catalog.html
- IMOS OceanCurrent: https://oceancurrent.aodn.org.au/
- Copernicus Marine OC NRT: https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L3_NRT_009_101
- Earth Search STAC: https://earth-search.aws.element84.com/v1
- UHSLC ERDDAP: https://uhslc.soest.hawaii.edu/erddap/
- MHL real-time: https://mhl.nsw.gov.au/Data-Real-time
- MHL SST/waves on data.gov.au: https://data.gov.au/data/dataset/manly-hydraulics-laboratory-waverider-buoys-sea-surface-temperature-data
- IMOS NRS Secchi/TSS: https://data.gov.au/data/dataset/6ab2a576-adc9-4e85-bfd9-e39f192ca311
- IMOS NRMN survey metadata: https://metadata.imas.utas.edu.au/geonetwork/srv/api/records/997c2e15-b345-438f-afac-49a4ac19be38
- McFadyen dive logs (e.g. 2023): https://mail.michaelmcfadyenscuba.info/downloads/2023dives.pdf
