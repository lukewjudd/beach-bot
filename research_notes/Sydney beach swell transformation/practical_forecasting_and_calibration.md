# Practical swell-to-spot surf height methods and their calibration (for an Open-Meteo-based Sydney beach bot)

Research note scope: how commercial forecasters (Surfline, MSW, Swellnet, Surf Captain, StormSurf, surf-forecast.com) and open-source projects turn offshore model swell into a per-spot surf height, and how such a model can be calibrated against cheap observations. Several primary pages (Surfline LOTUS page, Surfline Labs Medium post, Swellnet 2013 methodology article, the bookdown sea-kayak chapter, the Caldwell & Aucan JCR paper) returned HTTP 403 or empty content to the fetcher, so some findings rely on search-result snippets of those pages. This is flagged where it applies.

## 1. How commercial forecasters go from offshore swell to spot height

### Takeaway
None of the commercial providers publish their spot formulas. Their published descriptions follow the same pattern, though. They run a spectral wave model (WW3-based), take an offshore output point per spot, and partition its spectrum into the 2–3 largest swell trains. Each train then goes through a proprietary "surf height" algorithm that uses height and period and, implicitly, direction and exposure. Per-spot corrections are then fitted from human, cam and buoy observations. Surfline openly describes the last step as ML-based correction against forecaster reports and cams.

### Cited Findings
- Surfline introduced LOLA in 2001, combining satellite data, bathymetry and nearshore buoy data — [Science Friday, "Catching A Break"](https://www.sciencefriday.com/articles/catching-a-break/).
- Surfline's successor model LOTUS draws on historical surf reports, camera stream data, satellite assimilation, bathymetry and forecaster input. Spot tuning (Del Mar example) collects forecaster reports, surfer feedback and cam-based observations, then uses machine learning to decide how much to adjust the model. Surfline evaluates this with mean absolute error and how often each model configuration occurs. These details come from search snippets; the page returned 403 to direct fetch — [Surfline, LOTUS swell model](https://www.surfline.com/lp/whatsnew/features/lotus-swell-model).
- Surfline's published Del Mar accuracy: for the 4–6 ft range, the forecast was within 1.5 ft about 62% of the time ("clearly room for improvement"). The model also undercalled NW long-period swells, which needed roughly +2 ft. This is a direction-and-period dependent bias fixed by spot tuning (snippet) — [Surfline LOTUS page](https://www.surfline.com/lp/whatsnew/features/lotus-swell-model).
- A 2018 Surfline Labs post claimed an early ML system was on average 30% more accurate than the original LOLA surf-height forecasts (blog claim, not audited; snippet only) — [Surfline Labs, "Machine Learning for Surf Forecasting"](https://medium.com/surfline-labs/machine-learning-for-surf-forecasting-4a007f13b3e3).
- The Surfline API exposes per-spot "optimal" flags. v1 `showOptimal` returns 0/1 arrays per swell and wind forecast, available only with the `sort` resource. v2 `optimalScore` is 0 (suboptimal), 1 (good) or 2 (optimal), and the meta-surf-forecast author says only 0 and 2 ever appear. So Surfline holds a per-spot optimal swell-direction (and wind) definition internally but does not publish its ranges — [swrobel/meta-surf-forecast README (MIT)](https://github.com/swrobel/meta-surf-forecast).
- Surf Captain runs its own WW3-based model. At an offshore output point per location, it statistically splits the 360° spectrum into swell categories and uses the two most energetic. It estimates how much of each swell reaches the location, checks against buoys, and feeds both swells into a proprietary "Surf Captain algorithm". Forecast heights represent "average to better breaks" in a region. Bathymetry matters: deep water off Hawaii gives larger surf, and Florida's wide shallow shelf gives smaller surf from the same swell — [Surf Captain, "Understand the surf height forecast"](https://surfcaptain.com/blog/1/understand-the-surf-height-forecast).
- StormSurf's buoy "Swell Rating System" uses primary swell height and period with a proprietary formula. It only analyses energy at periods ≥5.88 s. It outputs face height of the average set wave plus a larger "biggest sets" number, and notes individual waves up to 2x sea height about once an hour. Results are for a theoretical break with no enhancement or reduction. Islands, points, shoals and reefs reduce size, and deep trenches feeding reefs enhance it, all left to local knowledge. For buoys at least 100 nm offshore, heights are "calibrated to estimate surf height at the beach closest to the buoy" (method not disclosed) — [StormSurf buoy FAQ](https://www.stormsurf.com/buoy/mht/faqs.html).
- Surf-forecast.com chooses an "optimum grid node" per break because the wave model does not resolve the shore. For one example break the node is 10 km away — [surf-forecast.com, The Spot surf stats](https://www.surf-forecast.com/breaks/The-Spot/surf-stats).
- MSW: no official method was found. Third-party commentary says forecasts combine model inputs in an algorithm. Some spot notes are buoy-based, others "incorporate local surfers' experienced conversions from wave buoy height to surf on beach height" — [UK Rivers Guidebook forum](https://www.ukriversguidebook.co.uk/forum/viewtopic.php?p=480200) (forum, low authority).
- Swellnet (Sydney): forecaster notes routinely adjust one regional figure by exposure, e.g. "expect smaller surf at beaches with less southerly exposure". Its 2013 system article (snippet) says East Coast regions show "a large range in size depending on which direction the swell is coming from". It also says NE-facing Sydney spots can pick up more size than open beaches from some swells — [Swellnet, "Understanding our new forecasting system" (2013)](https://swellnet.com/news/swellnet-analysis/2013/10/21/understanding-our-new-forecasting-system); [Swellnet Sydney forecaster notes](https://swellnet.com/reports/forecaster-notes/sydney-hunter-illawarra/2016/05/27/early-peak-sly-swell-saturday-smaller).
- Swellnet forecasters note a "poor correlation between buoy data and surf size" for Sydney south swells. They treat buoy observations further south and surf in Victoria as qualifying the model, which is an informal upstream-buoy validation — [Swellnet forecaster notes (search snippet)](https://swellnet.com/reports/forecaster-notes/sydney-hunter-illawarra/2018/02/16/strong-swells-entire-period-biggest).

### Inferences
- The common architecture is: partition, then a per-train transfer function f(H, T, θ) with a spot-specific direction response, then a statistical bias correction from observations. A hobby bot can copy this exactly with Open-Meteo's primary swell, secondary swell and wind wave partitions.
- Surfline's NW long-period undercall shows that residual bias depends on both direction and period. A single multiplicative coefficient per spot will leave structured error. A coefficient as a function of direction (or direction × period bin) is the natural next refinement.
- For Sydney, very S swells (160–190°) are where exposure differences between beaches are largest. These swells also correlate least with offshore buoy Hs, so calibration effort should concentrate there.

### Gaps
- No public numeric spot coefficients, optimal direction ranges or period scaling from Surfline, MSW or Swellnet. Their help and methodology pages returned 403 or were not indexed.
- MSW was absorbed into Surfline (2023). I could not fetch any MSW "sweet spot" documentation.
- Windy and Stormglass: no evidence found that either does spot-level surf transformation. They appear to serve raw model fields (ECMWF WAM / WW3 / MFWAM), but I did not confirm this from their docs.

## 2. Open-source code and published empirical formulas

### Takeaway
The open-source landscape is thin. Most projects (cli-surf, pysurfline, meta-surf-forecast) either display raw Open-Meteo or buoy data or scrape Surfline. Heuristics in the wild are crude, e.g. H × T × 0.1. The best-grounded public formulas are the Komar & Gaughan (1972) breaker-height relation and Caldwell & Aucan's (2007) empirical deepwater-Hs-and-Tp-to-surf method for narrow shelves.

### Cited Findings
- meta-surf-forecast (Rails, MIT licence) aggregates Surfline and Spitcast. It plots "approximate wave height (swell height × period × 0.1)" from NDBC buoys. Its rating heuristic is max swell rating × 5, halved if wind is not optimal. Spots are seeded with lat/lon, Surfline ID and subregion — [swrobel/meta-surf-forecast](https://github.com/swrobel/meta-surf-forecast).
- cli-surf is a command-line ocean data tool (FastAPI/Uvicorn, Open-Meteo as data source) that shows wave height, direction and period. No spot-transformation logic was seen — [ryansurf/cli-surf](https://github.com/ryansurf/cli-surf); [PyPI](https://pypi.org/project/cli-surf/2.4.0/).
- pysurfline pulls Surfline spot forecasts (swell height, period, direction) into pandas — [Mircobrb/pysurfline](https://github.com/Mircobrb/pysurfline).
- felix-last/wave-forecast predicts surf height from the K1 buoy using multiple linear regression (README description only) — [felix-last/wave-forecast](https://github.com/felix-last/wave-forecast).
- Komar & Gaughan breaker relation as quoted in surf and sea-kayak guidance: surf height ≈ 0.62 × H^0.8 × T^0.4 (SI units). The underlying source page was 403 and this is a snippet — [Breakfinder/sea-kayak references via search](https://buymeacoffee.com/72vxkvpm3/breaking-wave-height); [R. Bown, Sea Kayak Navigation 3.6](https://bookdown.org/rbown250/sea_kayak_navigation/swell-and-surf-forecasts.html).
- Caldwell & Aucan, "An Empirical Method for Estimating Surf Heights from Deepwater Significant Wave Heights and Peak Periods in Coastal Zones with Narrow Shelves", Journal of Coastal Research 23(5) (2007). The page content could not be retrieved, so the coefficients are not captured here — [BioOne](https://bioone.org/journals/Journal-of-Coastal-Research/volume-23/issue-5/04-0397R.1/An-Empirical-Method-for-Estimating-Surf-Heights-from-Deepwater-Significant/10.2112/04-0397R.1.full).
- Caldwell (2004, 8th Waves Workshop) on Hawaiian surf forecasting: visual breaker observations are the best means of verifying a surf forecast (snippet; PDF timed out) — [Caldwell 2004, IFREMER WW3 bib](https://data-ww3.ifremer.fr/BIB/Caldwell_8WIF2004.pdf).
- Anecdotal rule: breaking waves are ~50–75% of swell height at typical beaches. At ≥10 s period they equal or exceed swell height — [Paignton Canoe Club, Predicting Surf in Torbay](https://paigntoncanoeclub.org.uk.clayheritage.org/Surf-Torbay.html) (anecdotal).

### Inferences
- Algebra check: the classical Komar–Gaughan form is Hb = 0.39 g^(1/5) (T·H0²)^(2/5). With g = 9.81, 0.39 × 9.81^0.2 ≈ 0.616, which gives Hb ≈ 0.62 H0^0.8 T^0.4. This matches the quoted rule. It is an energy-flux-conserving breaker height for unrefracted normal incidence on a plain beach, so it is a good "open beach, ideal direction" baseline.
- Period sensitivity from Komar–Gaughan: Hb ∝ T^0.4, so going from 8 s to 14 s raises breaker height by (14/8)^0.4 ≈ 1.25. The face-height period multiplier tables surfers quote are usually steeper than this. The extra growth comes from refraction focusing and reef or bank effects that a per-spot fit should absorb.
- Recommended per-train model for the bot (inference, combining the above):
  `Hb_i = k_spot × 0.62 × H_i^0.8 × T_i^0.4 × E_spot(θ_i, T_i)`
  Combine trains energetically: `Hb = sqrt(Σ Hb_i²)`. E_spot is a direction-exposure weight, e.g. cos^n of the angle off the beach-normal inside the swell window and tapering to 0 outside. Allow a period-dependent widening, because long period wraps more. Fit k_spot (and optionally n or the window edges) from observations.
- Wind sea should go through the same function with its own direction. It is short period, so it gets little wraparound credit.

### Gaps
- The Caldwell & Aucan 2007 coefficients were not retrieved. Worth getting the PDF, since its narrow-shelf setting resembles Sydney's.
- No GitHub repo was found that implements a full per-spot swell-window plus Komar–Gaughan pipeline. The absence is itself a finding: this would be relatively novel hobby work.

## 3. Treatment of period (size boost and wraparound)

### Takeaway
All sources agree that longer period means bigger surf for the same offshore Hs and more wrap into sheltered spots. Published quantification is limited to Komar–Gaughan's T^0.4 and anecdotal rules. Surfline's own spot-tuning example shows the base model still underestimating long-period swells.

### Cited Findings
- "A high swell period can result in a wave height at the beach much higher than the swell height forecast" — [Blue Coast Cullen, how to read a surf report](https://www.bluecoastcullen.co.uk/blog/how-to-read-a-surf-report).
- "The longer the period of the swell the more it tends to wrap into a spot" — [Witch's Rock Surf Camp, surf science](https://witchsrocksurfcamp.com/surf-science-how-to-properly-check-the-surf-forecast/).
- Swellnet Sydney notes expected larger surf from a period increase of 12 s to 16 s at similar height — [Swellnet forecaster notes (search snippet)](https://swellnet.com/forums/swellnet-forecast-notes/88181).
- Surfline's model undercalled NW longer-period swells by ~2 ft at Del Mar before tuning — [Surfline LOTUS](https://www.surfline.com/lp/whatsnew/features/lotus-swell-model).
- StormSurf ignores energy below 5.88 s period for surf height — [StormSurf FAQ](https://www.stormsurf.com/buoy/mht/faqs.html).

### Inferences
- Treat period in two places. (1) Breaker amplification: T^0.4 baseline, with the exponent possibly fitted up to ~0.5–0.7 on observations. (2) Exposure: widen the effective swell window with T, e.g. window half-width grows by about 1–2° per second above 10 s. Alternatively, use cos^n with n decreasing as T increases. These numbers are design suggestions, not sourced.
- A StormSurf-style cutoff (drop or heavily downweight T < 6 s components) matches what Sydney surfers experience with short local wind chop.

### Gaps
- No published period-multiplier table from a reputable forecaster was found. Circulating "face height = swell × X at Y s" tables could not be traced to a primary source.

## 4. Computing swell windows automatically from coastline data

### Takeaway
No surf-specific tool was found. Coastal ecology and engineering "fetch / relative exposure index" tools do exactly the needed ray casting: rays from a point in N directions against a coastline polygon, with a max distance. They are a ready template to adapt using OSM coastline or GSHHG.

### Cited Findings
- InVEST Coastal Vulnerability (Python, natcap.invest, open source) casts fetch rays in 16 directions from each shore point up to a maximum distance. It produces wave and wind exposure and a relative exposure index (REI), and writes the rays as linestrings — [InVEST docs](https://invest.readthedocs.io/en/3.7.0/ecosystem_service_analysis_tools/coastal_vulnerability.html); [API](https://invest.readthedocs.io/en/main/api/natcap.invest.coastal_vulnerability.coastal_vulnerability.html).
- lakefetch (R, rOpenSci) downloads boundaries from OpenStreetMap and computes directional fetch by ray casting — [lakefetch](https://docs.ropensci.org/lakefetch/reference/lakefetch-package.html).
- Canadian Scotian Shelf fetch indices use unweighted fetch on 32 headings and effective fetch on 8 headings. Effective fetch is a weighted average of rays around a heading, which damps irregular-coastline noise. That is useful for smoothing a beach's exposure function — [donnees.iriu.ca dataset](https://donnees.iriu.ca/dataset/9f43c64c-4cbc-4e54-8199-7765331445f3).
- Great Lakes effective fetch/REI dataset with Python scripts — [U-Michigan Deep Blue](https://deepblue.lib.umich.edu/data/concern/data_sets/fx719n140?locale=en).
- Breakfinder describes the swell-window concept: each spot picks up a range of directions, and energy aimed outside it slides past — [Breakfinder blog](https://breakfinder.surf/de/blog/how-to-read-a-surf-forecast).

### Inferences
- Practical recipe: load the OSM land polygons (osmdata.openstreetmap.de "land-polygons", or GSHHG full-res) with shapely/geopandas, projected to a metric CRS (e.g. EPSG:28356, MGA56). From a point ~200–500 m seaward of each beach, cast rays every 1–2°. Record the distance to the first land hit, capped at ~50–200 km. Mark directions with cap-reached as "open". Smooth with an effective-fetch style cosine-weighted average (±45° at 9° steps is the classical effective-fetch scheme) so that headland edges taper rather than step.
- For Sydney, a short-range cap (~5–20 km) captures headland shadowing, e.g. Bondi's south corner, Manly vs Shelly, and Palm Beach. A long cap catches open-ocean exposure, but the Tasman Sea is open, so it matters little. Two caps can give "near-shadow" and "far" components.
- Geometric rays ignore refraction and diffraction, which is exactly where long-period wrap comes from. That is why the window should widen with period and why k_spot calibration remains necessary.

### Gaps
- No surf-forecasting project found that publishes coastline ray-cast swell windows. Licence notes: InVEST is Apache-2.0 per my general knowledge (not verified here). The OSM coastline is ODbL. GSHHG is LGPL (not verified in this session).

## 5. Calibration and validation with cheap observations (Sydney)

### Takeaway
Surfline itself calibrates from forecaster reports, surfer feedback and cams using MAE and hit rate. A hobby bot can do the same thing with free Sydney sources. Use the MHL offshore Sydney Waverider buoy to separate model error from transfer-function error. Use human-reported heights (lifeguard and council reports, Swellnet and Surfline reports, own observations) to fit per-beach coefficients. Fit on log heights with shrinkage towards a regional prior, because observations per beach will be sparse.

### Cited Findings
- Manly Hydraulics Laboratory (MHL) runs NSW Waverider buoys, including Sydney. They give real-time Hs, period and (for directional units) direction, at mhl.nsw.gov.au/Data. QC'd archives are on AODN THREDDS (NSW-OEH/Manly_Hydraulics_Laboratory/Wave). Hs is the mean of the highest third. Annual wave climate summaries are published — [data.gov.au MHL Waverider](https://data.gov.au/data/dataset/000cb6d7-dea9-4e3a-869e-08f99e5f3434); [MHL wave climate summary 2023–24](https://s3-ap-southeast-2.amazonaws.com/www-data.manly.hydraulics.works/www/publications/oeh/2024/mhl3067%20wave%20climate%20annual%20summary%202023-2024%20final.pdf); [Science of the Surf, Waves in real time](https://www.scienceofthesurf.com/blogs-2023/waves-in-real-time).
- CoastSnap (UNSW WRL) started in Sydney with stations at Manly (17 May 2017) and North Narrabeen (23 May 2017). The fixed-position smartphone photos are designed for shoreline position, and shoreline accuracy was comparable to professional surveys — [UNSW WRL CoastSnap](https://www.unsw.edu.au/research/wrl/projects-and-research/coastsnap); [iTnews](https://www.itnews.com.au/news/how-data-crowdsourced-from-beachside-happy-snaps-became-as-good-as-expensive-surveys-525514); [NSW Environment CoastSnap](https://www.environment.nsw.gov.au/coastsnap).
- Beachsafe (SLSA) gives location, weather, surf conditions and hazards for every Australian beach. A stakeholder report cites 12,416 beaches and about 128.7k monthly active users — [Beachsafe app](https://apps.apple.com/us/app/id397699623); [Beachsafe stakeholder report](https://beachsafe-reports.pages.dev/Beachsafe_Stakeholder_Report.html).
- Visual breaker observations are considered the best surf-forecast verification (Caldwell 2004, snippet) — [Caldwell 2004](https://data-ww3.ifremer.fr/BIB/Caldwell_8WIF2004.pdf).
- Surfline reports accuracy as "% within ±1.5 ft" in a size band, plus MAE — [Surfline LOTUS](https://www.surfline.com/lp/whatsnew/features/lotus-swell-model).

### Inferences (calibration design)
- Two-stage validation:
  1. Open-Meteo offshore vs MHL Sydney buoy (Hs, Tp, direction). This measures model error separately from beach transfer error.
  2. Predicted beach height vs observed reports.
- Per-beach fit: model log(H_obs) = log(k_spot) + log(H_pred_baseline) + ε. The MLE of log k is the mean log ratio, i.e. the geometric-mean ratio, which is robust and multiplicative.
- Use partial pooling: log k_spot ~ N(μ_region, τ²). The posterior mean is the weighted average (n/σ² · mean_log_ratio + μ/τ²) / (n/σ² + 1/τ²). A beach with 3 reports stays near the regional prior, and one with 50 reports converges to its own ratio. This is a cheap Bayesian update that can run incrementally as each report arrives.
- Once ~30+ observations exist per beach, add a direction term, e.g. separate k for S (150–190°), SE (110–150°) and E–NE (45–110°) bins, or fit the cos^n exponent. Surfline's direction × period bias example motivates this.
- Metrics: MAE in metres, hit rate within ±0.3 m or within ±1 reported category, and bias by direction bin.
- Observation sources ranked for cost/quality: own observations and cam screenshots labelled by the user (highest consistency); lifeguard and council beach reports (daily, but coarse categories and "face vs back" ambiguity); Swellnet and Surfline written reports (consistent observer per region, but subject to ToS restrictions on scraping); Beachsafe hazard ratings (mostly static beach-type ratings, so likely unsuitable as wave height truth).
- Convert all reports to one convention before fitting. Pick metres face height of set waves. Store the raw report text, the source and the scale used, so a per-source scale factor can be fitted (log offset per source in the same regression).

### Gaps
- No public dataset found of Sydney council (Randwick, Waverley, Northern Beaches) lifeguard wave-height reports. Whether they are archived, machine-readable or in which units was not verified.
- Beachsafe hazard rating methodology and any live wave fields were not found. They are presumably beach-state ratings (Short & Hogan style), not daily heights; this is unverified.
- CoastSnap is designed for shoreline position, not wave height. No study using it for breaker height was found.
- No published example of a hobbyist fitting per-spot coefficients via Bayesian shrinkage. The approach above is a design recommendation, not a sourced practice.
- Terms of use for scraping Surfline, Swellnet or CoastalWatch cams and reports were not checked.

## 6. Known pitfalls

### Takeaway
The main traps are mismatched height conventions (Hs vs face vs Hawaiian/back), crude or unstable swell partitioning in global models (Open-Meteo secondary swell availability varies by model), model direction error in the shadow zone of Sydney headlands, coarse model resolution near the coast, and short-period energy contaminating "swell".

### Cited Findings
- Height conventions: Hs is the mean of the highest third. Face height is trough-to-crest as surfed. The Hawaiian/traditional scale is roughly half to two-thirds of face height. Conversions vary with break, tide and wind, and quoted factors (×2–2.5) come from low-authority sources — [Surfresearch, wave height](https://surfresearch.com.au/awaveheight.html); [Ocean Fit (AU)](https://oceanfit.com.au/education/wave-height-is-it-5-feet-head-high-or-overhead/); [Univ. of Hawaii, communicating wave sizes](https://www.manoa.hawaii.edu/exploringourfluidearth/physical/waves/wave-and-wave-properties/weird-science-communicating-wave-sizes-local-scale); [Illawarra Flame, Dr Rip on wave height](https://www.theillawarraflame.com.au/science--nature/a-word-about-wave-height?amp=1).
- Open-Meteo marine models: ECMWF WAM (9 km hourly, 15 d), ECMWF WAM 0.25°, MeteoFrance MFWAM (0.08°, 3-hourly, 10 d), NCEP GFS Wave 0.25° (global) and 0.16° (52.5°N–15°S, so it does not cover Sydney at ~34°S), DWD GWAM, DWD EWAM (Europe) and ERA5-Ocean. Default "best match" picks per location. Variables are wind wave, primary swell, secondary swell ("only available for some models") and tertiary swell (GFS Wave only). Open-Meteo states "Accuracy at coastal areas is limited" — [Open-Meteo marine API docs](https://open-meteo.com/en/docs/marine-weather-api).
- Swell partitions in other providers are ranked by energy (first, second and third partition, each from the integral over the spectral partition). Partition identity can therefore swap between hours — [Meteomatics wave parameters](https://www.meteomatics.com/en/api/available-parameters/marine-parameters/wave-height/).
- Swellnet notes poor buoy-to-surf correlation for Sydney south swells — [Swellnet notes (snippet)](https://swellnet.com/reports/forecaster-notes/sydney-hunter-illawarra/2018/02/16/strong-swells-entire-period-biggest).
- StormSurf warns that swells "are not necessarily heading towards the closest beach" and that bathymetric features change size — [StormSurf FAQ](https://www.stormsurf.com/buoy/mht/faqs.html).

### Inferences
- Partition swapping: because "primary" means "most energetic", a S groundswell and an E swell can flip ranks hour to hour. Always process each partition with its own direction (the repo's latest commit already does this for swim beaches) rather than assuming primary = groundswell.
- Pin the model explicitly, e.g. `models=ecmwf_wam025` or MFWAM, rather than "best_match". Otherwise calibration coefficients can silently shift when Open-Meteo's backend changes. Check which models give secondary swell over Sydney, since GFS 0.16° is out of domain there.
- A 9–25 km grid cell nearest a Sydney beach may sit inside a headland or bay shadow, or be flagged as land. Like surf-forecast.com, choose a single exposed offshore node (e.g. ~10–20 km off the coast near the MHL Sydney buoy) for all beaches. Let the per-beach exposure function do the sheltering, so sheltering is not counted twice.
- Direction error: global WAM direction errors of ±10–20° are plausible (not sourced here). For beaches whose window edge sits near the dominant S/SSE direction, this can flip "in window" to "shadowed". A smooth (cos^n or effective-fetch-smoothed) exposure function reduces the sensitivity. Also validate model direction against the MHL directional buoy.
- Wind sea vs swell: in WAM, the wind-sea/swell split is based on the local wind forcing. Building or short-period E–NE sea under a strong onshore wind is classified as wind wave. If only the swell fields are used, NE windswell days will be underpredicted at NE-facing beaches. Include wind_wave_* through the same transfer function.
- Mixing conventions in calibration (lifeguard "1 m" = face? back? Hs?) can bias k by a factor of 1.5–2. A per-source offset term in the fit handles this.
