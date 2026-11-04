# Changelog

What changed and why, newest first. Dates are Sydney time.

## 2026-11-04 (night): northern beaches and harbour beaches

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
