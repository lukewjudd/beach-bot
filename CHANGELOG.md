# Changelog

What changed and why, newest first. Dates are Sydney time.

## 2026-11-10

- **Surf mode shows the swell.** Feedback from a surfer: they want to see the swell. Ideas from open-swells (ideas only: it has no licence).
  - **Every train, in the top card:** the Ocean line has a chip per wave train at the middle of the session's best hours: the main swell, a second swell and the wind chop. For example "3ft ENE @ 6s · 1ft SSE @ 9s · Chop 1ft NNE @ 2s". A groundswell hiding under wind swell now shows. Exported as `conditions.trains`.
  - **At each break, on its card:** each train's height once it gets there (that break's exposure to its direction and period, then breaking height), biggest first. For example "Under 1ft ENE @ 6s, under 1ft SSE @ 9s at the break". Several breaks can share the top score, so this sits on every card rather than only the top one. Exported as `here.trains`.
  - **A swell chart for the week** (`swellchart.ts`):
    - each train offshore hour by hour: the main swell as a filled area, the second swell and the chop as lines
    - arrows every six hours for the way the main swell comes from, and the tide underneath in its own sand colour. The legend lists the tide too, and the chop's key is dashed like its line, so the two greys aren't confused
    - night shading and the selected session as a band
    - hover or drag for a readout; tap to jump to that session.
    - open a break's card and the chart adds that break's own line: the wave height at the break, hour by hour, over the offshore swell, so you can see what its shelter does. The legend and readout name the break. Exported as `swell_hours.breaks`, by spot id.
    - Exported as `swell_hours`, every forecast hour, about 50 KB with the breaks. It works on a phone.
    - On desktop, surf mode scrolls the page so the chart doesn't squeeze the map and list. They keep a full-height block under it. Swim mode stays a fixed-height page.
  - The main swell's period is the longer of its own and the whole sea's, as the surf score reads it (R-SU6). Swim mode is unchanged.

- **Each spot's card says what it's like there, not out at sea.** Feedback: are the chips beach-specific? They aren't. Wind, air, rain, swell, water and tides are one value for the whole coast. So every spot's card now has a short line with what is specific to it: the waves at its sand or break, and which way the wind blows there (offshore, cross-shore, onshore, or sheltered, such as Bondi's north end in a nor'easter). For example "Under 1ft at the sand · cross-shore". Exported as `here` on each score.
- **The top card names its top pick, and the bars live in the cards.** Clicking AM, Midday or PM didn't make it obvious the top card's hours were one spot's. Its bars were the typical beach's, so they could disagree with the headline score. Now:
  - the headline's spot name ("Clovelly · 8/10") opens its card and flies the map to it, and its hours sit under it with the best ones highlighted (no caption line, to save space)
  - the top card has no bars. Each spot's own bars are in its card, so they always match its score.
  - tried and dropped: taking the hours out of the top card and auto-opening the top pick's card instead. On a phone the hours ended up a long scroll from the session you tapped.
- **Visit counts with GoatCounter.** One script tag in `index.html` gives daily unique visitors, page views and referrers at beachbot.goatcounter.com. It uses no cookies, needs no consent banner, and doesn't count localhost. The About section says so.

## 2026-11-09

- **Seven more surf breaks in the eastern suburbs, tagged by level.** Ben Buckler and Wedding Cake Island (expert), Clovelly Bombie, Lurline Bay and Malabar (advanced), and Mackenzies and Maroubra (north end) (intermediate).
  - **New per-break fields:** a level, a minimum size at the break, the swell directions it breaks on, and a best tide where known. Reefs want groundswell: short-period swell scores lower on them. Rule R-SU8.
  - **Swell windows:** the bombies and Malabar's point are measured at the pin rather than walked back to the shore (`at_pin`).
  - **Water:** Ben Buckler and Wedding Cake are out past the drains, so rain there is a warning rather than a closure.
  - **Kept out of the call:** advanced and expert breaks are scored and shown on the site with an amber tag, but never make the session's surf call, the event's top 3 or the calendar.
  - **Checked against about 150 dated sessions** (research/eastern-reefs-dated.md, mostly a local's daily filmed surf check):
    - Clovelly Bombie scores 8 on all three of its good days.
    - Malabar was retuned to need a big swell from E to S.
    - Mackenzies was retuned to take S swell and prefer low tide.
    - Maroubra's north point is left out: two rounds of searching found no dated session that names it (research/maroubra-north.md).
    - Maroubra (north end), the Dunny Bowl corner, is scored instead. It's out of the N–NE wind (new `wind_shelter`, which scores that wind at half strength), so in a nor'easter it beats the open beach by 1–3 points.
  - **Backtested 2023 to 2026:** the bombies and Malabar are good 1–3 days a year, Mackenzies about 13 and Maroubra's north corner about 15. The original four breaks are unchanged.

- **Smoother swell animation.**
  - **No more jump once per crest:** each crest now keeps its own pattern the whole way across. Before, the loop wrapped every crest spacing and each crest took on its neighbour's gaps, so the whole field jolted.
  - **Arcs fade in and out:** each arc fades in, travels, fades out and comes round again, out of step with its neighbours, so nothing pops in or out.
  - **A slight trail:** three fainter copies just behind each arc.
  - **Eased changes:** the layer fades in and out when switched, and cross-fades to a new swell when the direction or period changes between sessions. A change in height just brightens or dims the lines in place, so scrubbing hours doesn't flicker.
- **Runs every hour around the clock instead of 4:15am to 9:15pm.** The site no longer says "updated 7h ago" overnight, and the overnight model updates reach the morning calls before the 4:15 run. It still fits Cloud Run's free tier, at about 40% of the free compute.
- **A Swell switch on the map, next to Wind, off by default.** It draws faint swell lines drifting the way the swell is travelling, in the spirit of Windy's and Surfline's swell maps.
  - **Shape:** each crest is a short arc bowing forward in the middle, staggered so it reads as sea rather than a grid.
  - **Period:** long-period groundswell gets wider-spaced, quicker lines; short wind swell gets tight ones.
  - **Size:** bigger swell draws brighter.
  - **Open ocean only:** the lines are clipped to the open ocean using an outline built from the OpenStreetMap coastline (`scripts/build_sea_mask.py` writes `web/src/sea.json`), cut across the heads so they stay off land, the harbour, Botany Bay and Broken Bay/Pittwater.
  - **Switches:** Wind and Swell are now one small pill of icon chips that fill in when on, replacing the full-size toggle. The browser remembers each.
  - **Layering:** both the wind trails and the swell lines now draw under the score pins rather than over them. Each has its own map pane below Leaflet's markers, held in place on screen as the map pans.
  - **Reduced motion:** with reduced motion on, the lines are drawn still.
  - **Data:** scores.json now has the swell direction in degrees (`swell_deg`); older files fall back to the compass point.

- **The surf score is checked against real days, and two fixes make good days score like good days.** I collected 38 dated days since 2023 from Tracks, Weatherzone, ABC, Aquabumps and dated surf checks (in research/surf-history.md), plus a 12 Apr 2026 drone clip of Maroubra at 4–6 ft. Bad and flat days already scored low, but good days had a median of 5/10, and Maroubra on 12 April was a 7.
  - **Period:** surf now reads the longer of the swell period and the whole sea's period. The forecast's swell period runs about 3 s short on groundswell days: 6.8 s against a 9.65 s peak on the morning of Bronte's 6–8 ft barrels, 11 Apr 2024. So nearly every groundswell missed its quality points.
  - **Offshore wind** is now judged against how fast the waves are breaking. Under the old rule anything over 20 km/h was poor and gusts of 40+ cost more; now a 21 km/h westerly is ideal on 1.5 m of groundswell but too much on a 0.6 m wave. The physics behind it is in research/offshore-wind-surf.md.
  - **Unchanged:** cross-shore and onshore wind, and swimming.
  - **Result:**
    - Good days: median 7, with 5 of 18 at 8+ (was 2).
    - Maroubra on 12 April: 9/10.
    - High-confidence storm, East Coast Low and closure days: still 1–4.
    - Days with a break at 8+: about 28 a year, up from 9, so expect more surf calendar events.

- **About explains swell types and refraction, with two new figures.** Before step 1, "First, two kinds of swell" covers wind swell and groundswell and why period matters. Its figure is drawn to scale: a 6 s wind swell (56 m between crests, about 17 km/h) and a 14 s groundswell (306 m, about 39 km/h) over the same 600 m of sea, plus a side-on seabed showing where each starts to feel the bottom (half its wavelength: 28 m deep about 2 km out, against 153 m about 30 km out). Step 2 now opens with a headland: an 8 s and a 14 s swell from the ESE meeting a made-up point. The crests come from solving each period's arrival time over the seabed (wave speed from depth, Dijkstra over 16 directions), and the rays are traced square to them, so the drawing is computed rather than sketched. It shows both swells wrapping, the groundswell turning much further out and lining up with the bay's beach, and the rays bunching on the point and fanning out across the bay. Rick Salmon's *Introduction to Ocean Waves* (Scripps) is cited in the sources for the physics.

- **Settings behind a cog**, top right next to the info button. It has swim or surf, the coast (Eastern suburbs or Northern beaches, moved out of the header) and units: wind in km/h, knots or mph, waves in metres or feet (whole feet, as surfers say it), and °C or °F. Units change only what's shown, including numbers in the bot's notes and the lifeguard reports ("~1.4m at the beach" becomes "~5ft at the beach"); scoring stays in km/h, metres and °C. Settings are saved in the browser, ready to become account preferences later. The line under the title says which coast and mode you're on ("Eastern suburbs · Swim").
- **Swim or surf.** A setting picks which model the whole site follows. Swim is the default and is the site as it was, minus the surf breaks (Surf is gone from the Activity filter). Surf mode changes the whole page:
  - the week grid shows each session's best surf break on the surf scale;
  - the call says "Worth it" when the surf's pumping (8/10 or better);
  - the headline shows that break's bars and hour strip;
  - the list and map show only the surf breaks, with filled badges, since nothing else is on screen to tell them apart from.

  The site remembers your choice, and `?mode=surf` in the link opens surf mode. scores.json now has each session's surf call (break, score, and whether it's in the day's surf event) and the surf threshold, so the site shows what the calendar posted. The About dialog explains the two models.

- **The lifeguards' morning reports count on the day.** Randwick Council's lifeguards post a report each morning for Clovelly, Coogee, Maroubra and Little Bay (RSS feed, usually by 8:30am). The bot reads it on every run and only takes today's reports: an older one, like Clovelly's Sunday report still in the feed on Monday, is ignored. A beach they've closed is out for the rest of the day, with the reason "closed by lifeguards"; its ocean pools aren't. On 9 Nov this closed Coogee and Maroubra in a 2m south swell. Bluebottles sighted cost the beach its usual bluebottle points whatever the wind has done, and "none sighted" drops the wind-based guess. If the feed is down, scoring goes on as before.
- **The site shows the report under a beach's conditions** for today's sessions: status, waves, rips, bluebottles, water temperature and the lifeguards' own words. About has a step for it (11. What the lifeguards say) and credits the feed.
- **Reported vs modelled wave height is logged** in scores.json (`lifeguard_log`, kept 120 days): one row per beach per morning, to tune each beach's swell exposure against. The first morning already shows the model under-reading a big south swell: the lifeguards had 2m at Coogee and Maroubra, and the model had 0.9 m and 1.2 m.

## 2026-11-07

- **Surf bars shrink with the waves.** A surf score starts from 5 and the wave size scales the quality, wind and weather points (tiny waves keep a third of them), but the surf bars showed those points before the scaling: Bondi (south end) this evening read Wind 6, Wave size 6, Wave quality 6 and Weather 10 for a 2/10. Now each bar is what the part actually adds, as a share of the most it could: Wind 1, Wave size 4, Wave quality 2 and Weather 5.
- **Swimming leads; surf is on its own scale.** A session's call, score and "worth it" now come only from the ocean beaches and pools: surf never leads (it led 20 of 405 worth-it sessions since Nov 2024) and doesn't count towards a session's score, since a surf 8 (waves, wind, swell) isn't a swim 8. Surf breaks stay on the site for anyone who surfs, with outlined badges and pins rather than filled ones, sorted after the swims. When the surf's pumping (8/10 or better on its scale, kept until it drops below 7) the calendar gets a separate "🏄 Surf 8/10 Maroubra · Sat morning" event for the day, never mixed into the swim event: about 15 days in two years.
- **Hour by hour.** Under each session's call, and in each spot's card, a strip shows every hour of the session coloured by its own score, with the best two hours (what the score is) ringed, storms marked ⚡, ruled-out hours greyed and hours already gone faded. Underneath it says when the best two hours are and, when storms or a closure end the session after them, that too ("Best 2–4pm · ⚡ storms from 4pm"); the calendar event says the latter. Clovelly this evening was a 7 for 2-4pm and gave no hint of the storms from 4pm. The scores file carries each spot's hours, so it's about twice the size.
- **Every day is three sessions: morning (sunrise to 11am), midday (11am to 2pm) and evening (2pm to sunset)**, the same on weekdays and weekends. Weekdays used to be before work (to 10am) and after work (from 4pm), and weekends skipped 11am to 2pm; not everyone works nine to five. Each is still scored on its best two hours, locked in when it starts and posted like the others ("8/10 Bondi (north end) · Sat midday"). Backtested from Nov 2024 (eastern suburbs): 364 posts instead of 201, mostly new middays (124) and weekday evenings now starting at 2pm (63, up from 36).
- **The calendar holds out for 9/10.** Sessions at 9/10 or better go in the day's event (8/10 is still "worth it" on the site), and one stays in until it drops below 8/10. The 🔥 is now for a 10/10. Backtest from Nov 2024 (eastern): about 42 event days a year, 0.8 a week, two or three a week in January and February and almost none from May to October.
- **No part of the score goes past its top**, so a 10/10 needs every part at full marks. Bondi (north end)'s north-easterly bonus could lift its wind to 25 of 15 and make a 19° water morning a 10/10 (three of the eight 10s since Nov 2024); now the bonus still helps a north-easterly but stops at full marks, and the bars always add up.
- **Every bar is a part of the score.** The bars under a spot (Wind, Calm water, Weather, Water quality; a pool's calm and tide; a surf spot's waves) used to be worked out on their own rules, so Clovelly's midday read 10, 10, 8 and 10 and still scored 7: the Wind bar liked the light breeze, the score didn't. Now the scoring keeps its points for each part, and each bar is those points out of 10: 10 is the most the part can add, and each step down is 5 points the score didn't get. Weather counts warmth where the day's heading, rain, cloud and warm water. The About dialog has a table of what each wind is worth (how the bars work was too much detail for it, so it stays out).
- **A light breeze is good whichever way it blows.** Wind points at a beach go by strength first: under 8 km/h is the full 15 from any direction, 8-15 km/h is 12 offshore, 8 cross-shore and 3 onshore, and direction matters more as it strengthens (stronger winds score as before). Clovelly's midday today, 6-10 km/h across the inlet, goes from 76 to about 85. Backtest from Nov 2024 (eastern): 203 calendar days instead of 189, 9/10s up from 77 to 103, and Clovelly leads 66% of posts (51% before).
- **One calendar event per day.** A day's good sessions are bundled into a single event ("9/10 Clovelly · Sat morning & evening") running from the first to the last, with each session's call, top 3 spots and conditions in the description. A session stays in until it drops below 7/10, and the event goes once none are left; once it's started it's left alone. Old one-per-session events are cleared the first time a day is posted the new way. Backtest: 189 events over two years instead of 274 (1.8 a week, about 3 a week in summer).
- **Weekday middays are on the site but never in the calendar**: most people can't get away at lunch on a workday. A good one still says "Worth it" on the site. That leaves 274 calendar posts in the backtest instead of 364 (201 before the three sessions).
- **The site stacks AM, MID and PM under each date** on phones and desktops alike, and finished sessions can be opened again: greyed in the week, with "Finished" on their card and the call they had before they started. A midday card shows the tides from 9am to 4pm and no sunrise or sunset.
- **No more best-window times** ("best 11am–1pm") on the site or in calendar events. The score still comes from a spot's best two hours; the session's times are the ones that matter.
- **The About dialog has a 24-hour clock of the three sessions**, and the warmth figure shades all three.
- **Where the day's heading is read off the land, not the land/sea blend.** The bot averages an inland and an offshore grid cell to get the temperature at the beach, and on sea-breeze days the sea cell drags that 4-5° under the day's real high. On 7 Nov the land cell said 28°, Observatory Hill measured 29.4° and the blend said 24°, so Freshwater's morning got no warmth points and scored 76 instead of 85. A morning now looks ahead to the land cell's high (an evening keeps the afternoon's land high, and a southerly change is spotted on the land series too), still less 3°, so the full warmth bonus needs a day of about 29° as intended. The hour itself is still scored on the blend, and the temperatures shown are unchanged. Only once the water is 20° or warmer: a hot spring westerly heats the land but an 18° sea is still an 18° swim. Backtested from Nov 2024 (eastern suburbs): 15 more sessions posted (186 to 201), none lost, and 9/10s up from 39 to 66, mostly hot summer mornings.

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
