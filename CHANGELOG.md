# Changelog

What changed and why, newest first. Dates are Sydney time.

## 2026-11-06

- The poo in the About dialog's stormwater picture is drawn in SVG instead of an emoji (a floater, not a cartoon pile), so it looks the same on every device and in both themes.
- **No penalty for unpatrolled hours.** Exposed beaches (Beachsafe hazard 6 or more: Bondi, Tamarama, Bronte, Maroubra and the northern equivalents) lost 15 points before 7am and after 7pm (5pm in winter) for having no flags up. That's gone: a dawn or dusk swim is scored on the conditions.
- **The About dialog covers everything a score takes in**, with a figure for each: water quality after rain (how much rain each beach can take, with a stormwater drain and what comes out of it), warmth by where the day is heading (a day going to 30° with a southerly), what rain, cloud, storms and air and water temperature are worth in points, ocean pools and the tide, and the winds that bring bluebottles. The figures load from `web/src/about/` on their own, and the map drawing decides land from sea with three rays instead of one (Maroubra came out inside out).
- **The About dialog's wind step is drawn, not just a compass.** A side-on picture of the same swell under an offshore wind (smooth and clear) and an onshore one (chop and whitecaps), and Coogee's map with arrows blowing in from every 15°, coloured offshore, cross-shore or onshore. The text now also covers wind strength: glassy under about 8 km/h, offshore stops helping past about 25 km/h, and gusts count against any wind.
- **The About dialog walks through the swell model step by step**, with figures drawn from the bot's own data (`scripts/draw_about_figures.py`, replacing `draw_bondi_example.py`): finding North Bondi's open ocean from the coastline, up close and zoomed out to Maroubra (the lines just west of south cross the bay and land between Bronte and Maroubra), Collaroy's share by direction at 8 s and 14 s (soft window edges and wrap round Long Reef), how much of a swell reaches North Bondi from each direction (a fan of lines coloured green, amber and red, in the same style as the first figure), breaking height by period at a beach and a surf break, and which winds are offshore at Coogee. It also covers each wave train being scored on its own direction and the blend with local knowledge. The sources list now credits the OpenStreetMap coastline for the swell windows.
- **Fewer "event updated" emails.** An event is now only rewritten when its title (score, spot, session), times, place, or the top 3 spots and their scores change. The 4am run rewrote Saturday's Clovelly event because the sea forecast nudged from just under 20° to 20°, which dropped a "cold water" note from the top 3 spots. Spot notes and the best window no longer count.

## 2026-11-05 (night): longer sessions, and warmth by the day

- **Calendar titles are just the call**: "8/10 Clovelly · Sat morning". The wind and the air/water temperatures ("23°/20° water") move out of the title; they were already in the description.
- **Events are only rewritten when the call changes** (the score, the spot, the times, the best window or the top 3 spots). The description's "Updated" time changed every run, so every hourly run rewrote the event and Google emailed an "event updated" each time.
- **Calmer wind trails on the map.** They scale with how wind feels (its force grows with the square of its speed), so 8 km/h is a slow, faint drift and 30 km/h still streaks. Gusts are a brief puff every several seconds instead of the trails surging up to the full gust value half the time: forecast gusts are the strongest few seconds in the hour. Saturday's 8 km/h gusting 21 at Clovelly peaked at the speed of a 21 km/h wind before; it now moves at about a fifth of that.
- **Weekday sessions run to 10am and start at 4pm** (were 9am and 5pm). Weekends are unchanged (to 11am, from 2pm).
- **Warmth counts where the day's heading**, not just the hour. A morning gets credit for the warmth still to come up to 1pm, and an evening keeps the afternoon's, less 3° either way, so the full warmth bonus effectively needs a day of about 29°. After a southerly change (4° or more below the afternoon's peak) an evening is scored on the temperature it actually is. A 7am Clovelly swim on a day going to 30° used to score as a 22° swim and couldn't reach 10/10. The temperatures shown on the site and in events are still the real ones.
- Backtest since 2023: 68 good days a year instead of 43 (321 posts instead of 191), and 🔥 days from about 6 to 18 a year. Summer (January to March) averages about 15 posts a month, up from 11. Without the 3° allowance it was about 100 good days a year, too many to mean "go today".

## 2026-11-05 (evening): swell from the coastline

- **Each spot's swell window is measured from the coastline** instead of four hand-set numbers. From just off each beach (and from each surf break, near the sand where it breaks) a line is drawn every 2° out to sea against the OpenStreetMap coastline: bearings that reach open ocean are the window, and the headlands are the shadow. It picks up Ben Buckler over Bondi's north end, Wedding Cake Island off Coogee, Long Reef over Collaroy and Barrenjoey over Palm Beach without being told. `scripts/build_swell_windows.py` rebuilds it; the result is `swell_windows.json`.
- **Swell bends and wraps by period.** Long-period swell bends further toward the beach as it shallows, so a south groundswell gets into corners a short south swell doesn't (Collaroy in SSE: 0.58 of the swell at 8 s, 0.75 at 14 s). Window edges are soft, about 0.7 of the height right at a headland's line and fading behind it (Kraus's fit to Goda's diffraction diagrams), and wind chop spreads further round than groundswell. Oblique swell loses some height spreading along the coast.
- **Period scales height smoothly** instead of jumping 1.3× at 12 s: period^0.4 at the swimming beaches (Komar & Gaughan's breaker formula), period^0.7 at the surf breaks (fitted to the old size-by-period table and the Bondi webcam check).
- **The hand-set exposures stay as local knowledge**: each spot's result is halfway (in log terms) between the geometry and the old NE/E/SE/S numbers, until real data replaces them. They mostly agree for E and SE swell; harbour beaches keep their hand-set numbers.
- Backtest since 2023: 191 posts instead of 185. Bondi's north end wins 8 more easterly-swell days that Clovelly used to lead (the geometry has Ben Buckler sheltering it more from the east than the old 0.5), and three south-swell surf days at Bondi's south end drop out (1.4 m of S swell now reads about 1.1 m at the break, below the sweet spot).
- **How it works, on the site**: the About dialog has a North Bondi example, drawn from the bot's own data (`scripts/draw_bondi_example.py`): the coastline, Ben Buckler, the open swell window, how much of a NE, E, SE and S swell gets in, and which winds are offshore there.
- Next: the NSW Nearshore Wave Tool (CC BY 4.0) has a modelled transfer to the 10 m contour off every open beach. Access has been requested; its numbers would replace the geometry and the hand-set prior.

## 2026-11-05

- **Smarter swell at the beaches** (ideas from spearoSpotter). Each beach's exposure to swell is now blended smoothly between NE, E, SE and S instead of four buckets (a 112° and a 113° swell used to be treated differently). And the sea is weighed as separate wave trains, the main swell, a second swell and the local wind chop, each against how exposed the beach is from its own direction, so a beach facing away from a south groundswell isn't hit by it just because an east chop is running too. Surf breaks keep the combined sea height (just with the smooth blend), since their size bands were set against it.
- Backtest since 2023: 185 posts instead of 173 (about 3 more a year), nearly all Bondi's north end on northerly days with an ENE swell, where it's tucked behind Ben Buckler. Surf posts are unchanged bar two borderline days.
- **More room for the map on desktop.** The week toggle sits beside the days, each day's AM and PM sit side by side under its date, the day heading shares a row with the verdict, and the coast ratings move into a column beside the stat lines. At 1440×900 the top goes from 529px to 349px and the map from 355px to 535px tall. Phones are unchanged.
- Desktop week strip: AM and PM are centred in each day (they were spilling past the card's right edge), and on narrower desktop windows each label sits over its score.

## 2026-11-04 (night): northern beaches and harbour beaches

- **Harbour beaches are extras**: scored and shown, but they never lead a session, never make it "worth it" and never post to the calendar. On the site they're off until you tick Harbour, so the eastern map opens on the ocean coast as before; ticking it takes the map out to include them.
- **"Worth it" says why**, from the lead spot's best conditions ("Calm water · clean water · light NE wind · 24° and dry").
- **A pool leads when it's what makes the session worth it**, instead of the favourite beach taking the headline with the pool's score.
- **Clicking a map pin zooms in** to it, the same as clicking its card.
- **Northern beaches**, Manly to Palm Beach, as a second region with its own calendar (`CALENDAR_ID_NORTH`; scored but not posted until it's set). 18 ocean beaches, 5 harbour and Pittwater spots, 15 rock pools and 10 surf breaks, from `northern-beaches-knowledge.md`. Shelly Beach is the favourite. Forecasts from Dee Why with swell off Narrabeen, and rain from the Terrey Hills and Observatory Hill gauges.
- **Harbour beaches** as their own category: Shark Beach, Camp Cove, Parsley Bay, Watsons Bay and Murray Rose Pool in the east. Next to no swell (only a very big NE/E swell reaches Shark Beach), no bluebottles, the 3-day rain rule, and left out of the coast-wide summary. On the site they're labelled Harbour, with their own activity filter.
- **Missing eastern pools**: McIver's Ladies Baths (labelled Women only) and South Maroubra Rockpool.
- **Eastern / Northern switch** on the site, remembered per browser and defaulting to Eastern; a calendar link opens the right region. Each region has its own map tiles and scores file (`scores-<region>.json`; `scores.json` stays as the eastern copy for older links).
- Every map pin was checked against OpenStreetMap's beach and pool outlines.
- **Wider map tiles** for both regions (eastern 8MB, northern 7.6MB), reaching well inland, so a wide screen never shows a blank strip beside the coast, and the map can zoom out one more level to fit the whole northern coastline.

## 2026-11-04 (evening): site redesign

From a round of UI feedback.

- **A week at a glance.** Days run Monday to Sunday, with morning and evening inside each day, and there's a "Next week" view as far as the swell forecast reaches (about 9 days). Anything more than two days out is marked as an early forecast (dashed day, a note in the summary), and the calendar still only posts two days ahead.
- **Every day shows its AM and PM score**, labelled, so the whole week reads at a glance; tap either to open that session. The summary heading just says the day and morning or evening (no clock times), and the conditions include sunrise and sunset.
- **Sessions that have finished stay for the rest of the week**, greyed out and not clickable, showing the call the bot made before they started (frozen when they start, so it's what you were told, not a rescore with hindsight). They clear on Monday. The bot keeps no history of its own: each run carries them forward from the last scores.json.
- **Calendar links open their own session** (`?s=beach20261107am`), and the page keeps that link as you move around, so it can be shared.
- **Summary card** has a heading saying which session it is, then the stats on labelled lines by what they describe: **Weather** (wind, air, rain), **Ocean** (swell, water temperature, tides), **Sun** (sunrise for a morning or sunset for an evening, UV) and **Coast** (the coast-wide ratings: bars on desktop, coloured numbers on phones). Wind and swell lead their lines, and only that half of the day's tides shows. Chips that are good or bad for a swim get a traffic-light border using the bot's own rules (wind and swell from the coast's ratings, air and rain from the scoring bands, water by how it feels going in: 20°+ green, 17–19° amber, colder red, though cool water still never costs points); tides, sun and UV stay plain.
- **Traffic lights**: red, amber and green for every score, using Beachwatch's red. Ruled-out spots show 0 in red instead of "–".
- **Spots**: an Activity filter you can tick several of (Swim, Snorkel, Pool, Surf; all by default) and Sort (Best first, North to south, By place, which groups a beach with its surf break and pools).
- **Conditions live in the spot's card**: tap a card to open it, and tap a pin to open and scroll to its card. Pools are rated on calm in the pool and the tide, surf spots on wave size and wave quality.
- **Map**: pins show an icon for the kind of spot plus the score (just the score when zoomed out), popups just name the spot with a link to its details, the zoom buttons and a proper Wind on/off switch sit bottom-left, and phones get a List / Map toggle.
- **No water temperature row** in the conditions: it's one sea temperature for the whole coast, already a stat in the summary. It still counts in the scores, and "cold water" (under 20°) still shows as a note.
- **Spot cards use the same icon-and-score badge as their map pin.** Clicking a pin opens its popup (name, score, kind, Details) and its card; the pins no longer redraw underneath, which was closing the popup. Opened cards scroll fully into view below the filters.
- **About the data**: an info button top right explains how often the bot runs, what a score means, and the sources (Open-Meteo, BOM rain gauges, NSW Beachwatch, local knowledge, the map). Notes just say "pollution likely" now instead of crediting Beachwatch on every card.
- **Freshness**: the page fetches new scores every 5 minutes and when you come back to the tab, and warns when they're over an hour old.

## 2026-11-04

### Pools and wind
- Pools now feel the wind direction like the beach next to them, at about half the weight (the walls keep the chop out, but you're on the deck in the same breeze). Ross Jones scored 8 for wind in an onshore NE while Coogee beach scored 6; they now match. Icebergs faces east rather than Bondi's south-east.
- Fixed the backtest, which broke when the calendar emoji went, and added a test so CI catches that.

### Calendar
- Event titles and descriptions drop the 🏖️ 🏊 🏄 💨 ⏰ emoji; only 🔥 stays for 9/10+. Surf spots say "surf" after the name, e.g. `8/10 Clovelly · Maroubra surf 1.4m · NE 12 km/h gust 20 · 24°/21° water`.
- Events end with a link to the map site, and say they're removed below 7/10.

### Site tidy-up (from a UI review)
- "Not worth it" gets one line on why, without naming a spot: the reason most spots are ruled out ("pollution likely at 12 of 15 beaches and pools"), or else the weakest conditions.
- Spot cards show what kind of spot it is (Beach, Pool, Surf, Snorkel) as labels on the right, instead of "swim · ..." at the start of the notes.
- No more kind emoji. Pins are shaped by kind instead (beach circle, pool rounded square, surf diamond), and the Beaches / Pools / Surf filters show the matching shape as the legend. The wind chip just says "Wind", and the wind trails switch is a plain square button above the map's zoom buttons.
- Score pills meet contrast: darker grey, amber and green (4.5:1 or better).
- Tabs and filters are 44px tall and map pins are bigger, so they're easier to tap.
- When nothing's worth it, the conditions panel shows the whole coast (the typical beach across all of them) instead of naming a spot.
- Warning notes (pollution, rain, murky water, closures, storms) are amber with a ⚠, so they stand out from things like "wave pool fun".
- The Wind trails switch lives on the map now.
- Finished sessions drop off the tabs.
- "Updated" shows how long ago ("updated 25 min ago") and goes amber after two hours.
- Spots can be picked with the keyboard, pills read as "3 out of 10" to screen readers, and decorative emoji are hidden from them.
- "fresh water" is now "cold water", since fresh water sounds like runoff.
- No "top pick" ring on the map when nothing's worth it.


After a night of thunderstorms (about 22mm at Sydney Airport), the 4am run still gave Little Bay 6/10.

### Fixed
- **Stale Beachwatch forecasts.** Beachwatch publishes around 6am, so the 4am run read the previous day's "pollution unlikely" from before the storm, and that overrode the rain rules. Only forecasts issued today are used now; otherwise it goes off recent rain.
- **Rain that's already fallen comes from BOM's rain gauges** at Observatory Hill and Sydney Airport (whichever is wetter), via BOM's public FTP. The model had 6mm for that night; the gauges had 50mm at Observatory Hill and 22mm at the airport. If BOM is down, past rain falls back to the 75th percentile across six weather models, which leans wet (12.5mm that night).
- **Thunderstorms rule out swimming and pools**, and drop surf spots to 1/10. Storm risk is a thunderstorm weather code, or high storm energy (CAPE ≥ 1000) with rain likely.
- **Surf spots now count water quality**, so a surf spot can't rank well straight after heavy rain.

- **"Good snorkelling" only shows when the water is clear.** It used to go on swell alone, so it showed the morning after 50mm of rain. Now rain in the last 48 hours (10mm+) or a Beachwatch pollution warning gives "murky for snorkelling" instead, and an onshore wind rules it out too.
- **Ruled-out spots show why they're ruled out.** The map popup for Clovelly said "Good snorkelling" when it was actually closed for pollution, because it showed the first note rather than the reason.

### Changed
- Runs every hour from 4:15am to 9:15pm instead of 4am, 3pm and 7pm. The 6:15 run lands just after Beachwatch's daily update.
- A posted event stays until the session drops below 7/10, instead of disappearing the moment it slips under 8. The site's "Worth it" follows the calendar.
- Site: the Worth it / Not worth it verdict leads the summary card, and wind is a chip alongside swell, air and water. When it's not worth it, the card no longer names a "best option".
- Conditions: swimming spots and pools show **Calm water** only, and surf spots show **Surf quality** in its place. The old "Surf" row on a swimming beach read like good news when it meant big waves.

## 2026-11-03

- Site: on phones the page scrolls normally, so the spots list is reachable.

## 2026-11-02

- Site: the spots list ranks spots the same way as the headline, and "show top pick" respects the filters and flies to the pin.
- Water quality: Beachwatch's forecast always wins over the rain rules.
- Map: animated wind trails, off by default.
- Conditions for every spot, not just the area.
- Pools: unknown cleaning windows are a warning rather than a closure.
- Every surf spot is graded (1/10 at worst) instead of only showing ones that work.
- Ocean pools scored, with Beaches / Pools / Surf filters on the site.
- Map moved to Leaflet with self-hosted Protomaps tiles, served from a Sydney bucket.
- Project split into `bot/` (Python, ruff, pytest) and `web/` (Vite + TypeScript), with CI and GitHub Pages deploys.
- First version: forecast scoring, calendar sync, Cloud Run deploy and the map site.
