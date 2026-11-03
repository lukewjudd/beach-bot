# Changelog

What changed and why, newest first. Dates are Sydney time.

## 2026-11-04

### Calendar
- Event titles and descriptions drop the 🏖️ 🏊 🏄 💨 ⏰ emoji; only 🔥 stays for 9/10+. Surf spots say "surf" after the name, e.g. `8/10 Clovelly · Maroubra surf 1.4m · NE 12 km/h gust 20 · 24°/21° water`.

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
