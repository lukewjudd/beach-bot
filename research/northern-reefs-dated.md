# Northern Beaches: more breaks, with dated surf sessions for backtesting

Compiled 10 Nov 2026. This is the same exercise as `eastern-reefs-dated.md`, for the stretch from Manly/Shelly Beach to Palm Beach.
It covers breaks that are **not** already in `NORTHERN_SURF`. That list already has Manly, Freshwater, Curl Curl, Dee Why Point, Long Reef,
North Narrabeen, Warriewood, Newport, Avalon and Palm Beach.

Dates are to the day. Each one is either stated in the source (title, caption, article) or deduced from a publish date plus
"today", "yesterday" or "last weekend" wording; deduced dates are marked *inferred*. A day where a source names the break but doesn't say
how it was is marked "surfed" or "breaking". Undated material is listed separately as weak leads and should not go into a backtest.
Sessions before 2022 are kept, marked *(pre-2022)*, because they fall outside the forecast archive but still show how the spot behaves.

Verdicts: **GOOD** (working, pumping), **OK** (surfable, mixed), **POOR** (swell present but the spot isn't working: wrong
direction, blown out, closing out, or too small or too big for it), **FLAT**.

## Sources and how they were used

- **No Northern Beaches equivalent of the eastern "Surf Check" YouTube channel turned up.** No local posts a daily, dated, written
  verdict on YouTube. The nearest equivalents are two written sources:
  - **realsurf.com.** Daily dated reports written from Dee Why. Each one gives the MHL Sydney buoy reading (Hs, period, direction) and
    the wind, and often captions photos of named breaks (Surfrider Gardens/South Narrabeen, Collaroy, Mona Vale, Bungan, Little Narra).
    Its Manly coverage stops around 2021. This is the backbone for the middle section.
  - **Sprout Daily** (sproutdaily.com/the-daily/D-mon-YY). A daily Manly photo blog by Murray Fraser, with swell and wind in the text.
    It covers Manly, Queenscliff, Fairy Bower, Deadmans and the Queenscliff Bombie. URLs follow the date, so more days can be checked.
    Many posts are about sunrise or pools and don't mention surf.
  - A "Sydney Surf Report <beach>" YouTube channel posts clips with dates in the titles (Mona Vale, Bilgola). There is no text
    verdict, so the clips would have to be watched; none are scored here.
- **Tracks Magazine** swell recaps (fetchable), Pittwater Online News swell galleries, the WSL, Stab, and the Manly Observer.
- **Spot guides used for conditions:** Wannasurf "Sydney North" (59 spots listed), surf-forecast.com break pages and dated photos,
  mondo.surf, Surfnerd, thesurfatlas.com, waveexplorers. Surfline guide text came from search snippets only.
- **Blocked, skipped:** swellnet.com (403), surfline.com (403; snippets only), theinertia.com (403), gettyimages (403), and
  beachsafe.org.au (JavaScript only; snippets). coastalwatch.com now redirects to Surfline. surfingworld.com.au returned an empty page.
  YouTube through WebFetch gave no metadata. The public watch-page HTML (title, upload date, description) was read with a plain
  request, with no bot check involved. Wayback was not used.

---

## 1. Fairy Bower ("the Bower"), Shelly Beach headland, Manly

**What and where:** A right-hand point/reef break on the north side of the headland between Manly and Shelly Beach. It runs from
the tip through the "Racetrack" section and fades into deep water off Shelly.
- Wannasurf pin: 33°47.955'S 151°17.914'E (**-33.7993, 151.2986**). Mondo gives -33.799, 151.297.
- It breaks off the Shelly Beach headland, but it faces roughly ESE into the open ocean. The `Shelly Beach` Beach entry (facing 290)
  is the wrong exposure for it, so it would need its own facing or `at_pin=True`.

**Level:**
- Wannasurf: experienced.
- Surfnerd: expert.
- Surf Atlas: advanced.
- Mondo: intermediate (the outlier).

**Conditions by source:**
- **Wannasurf:** swell SE or E. Works from 1.0–1.5 m and holds 4 m+. Wind W, SW, S or SE. All tides, best on a rising or falling tide.
  At low tide above about 5 ft it is "very ledgey and shallow".
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/fairy_bower/index.html
- **surf-forecast:** best swell SE, best wind SW, "Good surf at all stages of the tide". A reviewer calls it fickle, working only a
  few times a year. https://www.surf-forecast.com/breaks/Fairy-Bower
- **Surfnerd (Winki Pop / Fairy Bower):** best swell SE, workable from NE round to S. About 1.2–6.1 m. SW offshore. Low to mid tide,
  rising. https://surfnerd.com/surf-forecast/winki-pop-fairy-bower
- **Mondo:** swell E–SE (68–158°), wind 113–293° (SE through W), all tides. https://www.mondo.surf/surf-spot/fairy-bower/guide/9876
- **Disagreements:** the tide (all tides vs. low–mid) and the level (intermediate vs. expert).
- **Pattern in the dated days:** E, ENE and NE swells light it up (even a cyclone swell). A big S or SSE swell mostly runs past the
  point: "a challenging swell direction for us" (Sprout, 3 Jun 2024).

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2025-08-04 | POOR (too big) | "raw 4m east swell", wind "light and offshore"; even Fairy Bower had "too much water moving across the reef" | https://www.sproutdaily.com/the-daily/4-aug-25 |
| 2024-10-01 | OK | "leftover east swell", "a light sou-wester"; opens things up for all-comers "from Fairy Bower to South Steyne" | https://www.sproutdaily.com/the-daily/1-oct-24 |
| 2024-06-03 | POOR (wrong direction) | S swell "maxing out around dawn at 4 metres", "a challenging swell direction for us"; only straight refracted lines got in | https://www.sproutdaily.com/the-daily/3-jun-24 |
| 2023-01-16 | FLAT | "short period ENE wind swell", "very light onshore breeze"; lead photo "Fairy Bower Glass" | https://www.sproutdaily.com/the-daily/16-jan-23 |
| 2022-04-11 | surfed (no verdict) | Video title "FAIRY BOWER RAW FOOTAGE 4K \| April 11th 2022" | https://www.youtube.com/watch?v=u0s6GoJQ4Ho |
| 2020-08-11 *(pre-2022)* | OK | "South Steyne was head and a bit as was the Bower" | https://www.realsurf.com/category/all-surf-reports/manly/ |
| 2020-02-14 *(pre-2022)* | GOOD | Photo "Cyclone Eusi hits the Bower", 08:09, rising tide; surf-forecast model about 2.5–2.8 m NE/ENE at 14–15 s, light SE–SSE | https://www.surf-forecast.com/breaks/Fairy-Bower/photos/22065 |
| 2018-08-20 *(pre-2022)* | POOR | "Not much at the Bower or South Steyne"; Queenscliff chest to head-plus (a south swell) | https://www.realsurf.com/?p=490497 |
| 2017-08-20 *(pre-2022)* | POOR/OK | "Swell mostly pushing past the Bower but there are occasional head plus sets", "Very fat and slow"; model SSE about 4.2 at 12 s | https://www.realsurf.com/?p=487594 |

**Weak leads:**
- "Fairy Bower Manly - Australia 04.01.22": ambiguous (4 Jan or 1 Apr 2022). https://www.youtube.com/watch?v=g8Cz47PAvbA
- A "Halloween 2023" swell clip with no exact day. https://www.youtube.com/watch?v=D2ECVPgEB3g
- Getty "big swell at Fairy Bower", March 2022, no day (blocked).
- The Northern Beaches Council "large swells forecast" notice of 26 Mar 2026 is a forecast, not an observation.

## 2. Winki Pop / Winkipop / "Winki"

**What and where:** It is on the same headland as Fairy Bower: a short, hollow, ledgy right on a shelf in front of the cliffs, at the inside
(southern) end of the Bower. Surf Atlas says "Winki Pop" is sometimes used for the Bower itself. On rare days it links through to
the Bower. Don't confuse it with Winki Pop at Torquay, Victoria.

**Conditions:** Wannasurf has two contradictory pages for it:
- **"winkipop"** (33°47.964'S 151°17.888'E): works from 2–2.5 m, holds 5 m+; swell S/SE/E; mid to high tide.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/winkipop/index.html
- **"winki"** (33°47.941'S 151°17.91'E): works from under 1 m, holds 3 m+; swell SE/E/NE. One user says "too much south swell makes the
  sets crumble". Mid to high tide. https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/winki/index.html
- **surf-forecast** "Winkipop": SE swell, SW wind. https://www.surf-forecast.com/breaks/Winkipop
- **waveexplorers:** intermediate to advanced, NE/E swell. https://waveexplorers.com/surf-spot/australia/sydney/winkipop

**Dated sessions:** none from 2022 on. Older surf-forecast photos: 2010-04-29 "solid 5-6 ft" on a rising tide; 2016-05-04 "May 2016
groundswell"; 2017-08-20 (4 stars, SSE). https://www.surf-forecast.com/breaks/Winkipop/photos

**Verdict:** fold it into Fairy Bower. Don't give it its own entry.

## 3. Queenscliff (north end of Manly beach)

**What and where:** A beach break with lefts and rights at the north end of the Manly–North Steyne stretch, by the lagoon mouth and
Queenscliff headland.
- Wannasurf pin: 33°47.014'S 151°17.44'E (**-33.7836, 151.2907**).
- The Queenscliff Bombie offshore refracts the swell into A-frames and feeds a strong rip.

**Level:** all surfers (Wannasurf); "OK for beginners and groms at times" (surf-forecast).

**Conditions by source:**
- **Wannasurf:** 1–1.5 m up to 2.5 m+, NW wind, all tides. It lists "SW" swell, which is almost certainly an entry error.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/queenscliff/index.html
- **surf-forecast:** NE swell, NW wind, all tides. https://www.surf-forecast.com/breaks/Queenscliff
- **What the dated days show:** on S and SE swells the north end is consistently bigger than South Steyne and the Bower. On
  11 May 2023 it was overhead at Queenscliff and waist-high at South Steyne; on 20 Aug 2018, chest to head-plus at Queenscliff
  and "not much" at the Bower. It also handles NW wind better.

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2025-04-10 | OK/POOR early | "south swell is hanging in there", south-facing beaches "nudging head-high on the sets"; high tide blocked the early waves at Queenscliff | https://www.sproutdaily.com/the-daily/10-apr-25 |
| 2024-10-01 | OK | "leftover east swell", "a light sou-wester", peaky and clean "North Steyne to Queenscliff" | https://www.sproutdaily.com/the-daily/1-oct-24 |
| 2024-08-09 | POOR/FLAT | "short-period NE wind swell"; "there wasn't a whole lot on offer on either side" of Queenscliff Headland | https://www.sproutdaily.com/the-daily/9-aug-24 |
| 2023-07-21 | OK | "two, maybe three foot at Queenscliff with a capacity crowd", "swell's eased a touch today" | https://www.sproutdaily.com/the-daily/21-jul-23 |
| 2023-05-11 | GOOD | "overhead sets up at Queensie"; SE about 2.6 m, about 11 s, light westerly, low tide 07:05 | https://www.realsurf.com/2023/05/11/sweet-conditions-early/ |
| 2023-04-11 | GOOD (tricky) | S swell, "closer to 4-6ft", "solid overhead"; the bombie angles the swell into a "hefty rip" | https://www.sproutdaily.com/the-daily/11-apr-23 |
| 2019-05-31 *(pre-2022)* | OK | "sweet shoulder high sections on the occasional bomb sets", "Offshore" | https://www.realsurf.com/?p=492512 |
| 2018-08-20 *(pre-2022)* | OK | "chest to head plus on the bombs at low tide" | https://www.realsurf.com/?p=490497 |

## 4. Queenscliff Bombie ("Queensie Bombie")

**What and where:** A deep-water boulder-reef bombora off Queenscliff headland, breaking left and right. Wannasurf pin: 33°47.352'S 151°17.692'E.

**Level:** "Pros or kamikaze only" (Wannasurf); "expert stuff only" (Surf Atlas).

**Conditions:**
- Wannasurf: starts at 2.5–3 m and holds 5 m+, all tides.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/queensie_bombie/index.html
- Tracks: it needs "the perfect combination of East swell and offshore winds", and before 2025 it had last broken properly in 2016.
  https://tracksmag.com.au/watch-sydneys-queenscliff-bombie-comes-to-life

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2025-08-06 | breaking, unridden | "Out at The Bombie there were some big perfect waves breaking with no takers" | https://www.sproutdaily.com/the-daily/6-aug-25 |
| 2025-08-05 *(inferred)* | GOOD (XXL) | Tom Myers' "XXL drainer". Tracks (Fri 8 Aug) says "earlier this week", and another write-up says Tuesday morning. Sprout on 4 Aug: "raw 4m east swell", light offshore | https://tracksmag.com.au/watch-sydneys-queenscliff-bombie-comes-to-life |
| 2025-04-18 | GOOD (XXL) | "Perfectly groomed Bombie", "The right starting to bowl around 8ish"; photos dated 20250418; big E swell from ex-TC Tam | https://www.sproutdaily.com/the-daily/30-apr-25 ; https://tracksmag.com.au/tom-myers-on-the-wave-of-his-life-at-sydneys-queenscliff-bombie |
| 2025-04-01 | POOR (too windy) | Buoy "over 5.5 metres" Hs; the bombies "maybe too windy", and the crew went to Freshie | https://www.sproutdaily.com/the-daily/1-apr-25 |
| 2022-04-02 | breaking, unridden | Surfline (snippet): "Queenscliff Bombie, no takers"; the bombies "began to cap, then to break properly" | https://www.surfline.com/surf-news/april-2-2022-sydney-bombies/148168 |

## 5. Long Reef Bombie

**What and where:** It is real and publicly named: an offshore reef bombora off Long Reef point, with a long paddle.
- Wannasurf pin: 33°44.754'S 151°18.502'E.
- Wannasurf says it breaks right and left; surf-forecast says left.

**Level:** "Pros or kamikaze only"; you need a big-wave gun.

**Conditions:**
- Wannasurf: swell S/SE/E, 1–1.5 m up to 5 m+ (the 1–1.5 m start looks too low), N/NW/W/NE wind, low to mid tide.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/long_reef_bombie/index.html
- surf-forecast: SE swell, NW wind, mid tide rising, "rarely breaks". https://www.surf-forecast.com/breaks/Long-Reef-Bombie

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2022-04-02 | breaking, unridden | waves "poured unridden around the back of Long Reef" (Surfline snippet) | https://www.surfline.com/surf-news/april-2-2022-sydney-bombies/148168 |
| 2016-03-11 *(pre-2022)* | breaking (sometimes) | "Swell was coming from the SE at up 1.8 metres and 13 seconds"; "outside bombies were picking up the occasional set" | https://www.realsurf.com/tag/long-reef-bombies/ |
| 2011-05-19 *(pre-2022)* | surfed | "people towing and paddling in to the bombies" | https://www.realsurf.com/tag/long-reef-bombies/ |

## 6. Deadmans ("Deadies"), and "Deeps"

**Deadmans, what and where:** A right-hand reef slab about 30 m off the cliffs on the ocean side of the Shelly/North Head headland, past
Winki toward Bluefish Point.
- Wannasurf pin: 33°48.018'S 151°18.028'E.
- It is surfed by paddling, not tow-only.

**Level:** experienced or expert only. Wannasurf says it breaks "about 5 days a year".

**Conditions:**
- Wannasurf: swell S/SE/E, starts at 2.5–3 m and holds 5 m+, wind W/SW/S/SE/E, mid to high tide.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/deadmans/index.html
- Surf Atlas: it needs "a hefty SE or NE element".

**"Deeps":** no public source names a break called Deeps on the Northern Beaches.

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2025-08-05 / 06 | breaking | 5 Aug caption "Deadman's Line", swell "too big for just about everywhere"; 6 Aug "Deadman's starting to wake" | https://www.sproutdaily.com/the-daily/5-aug-25 ; https://www.sproutdaily.com/the-daily/6-aug-25 |
| 2025-07-02 *(inferred)* | OK/GOOD | "Deadman's had a few yesterday" (post dated 3 Jul) | https://www.sproutdaily.com/the-daily/3-jul-25 |
| 2025-04-02 | GOOD | "Deadman's was flexing again this morning"; "four and a half metres out of the south-east", wind "straight offshore out of the west" (checked directly) | https://www.sproutdaily.com/the-daily/2-apr-25 |
| 2025-04-01 | GOOD (heavy) | "Deadmans wipeouts, RAW surf footage, 1st April 2025"; buoy Hs over 5.5 m | https://www.youtube.com/watch?v=TAVEyxSllGw |
| 2024-07-31 / 08-01 | GOOD (big) | Swell Diary "Big Solid Deadmans"; Sprout: "4 and 5 metres with outlier sets over 10metres" | https://swelldiary.com/break/deadmans/ ; https://www.sproutdaily.com/the-daily/31-jul-24 |
| 2024-06-17 | surfed | Swell Diary "Raw Footage Deadmans" | https://swelldiary.com/break/deadmans/ |
| 2022-01-02 | surfed | Swell Diary "Raw Footage Deadmans" | https://swelldiary.com/break/deadmans/ |

---

## 7. Collaroy (south end of the Collaroy–Narrabeen beach)

**What and where:** A beach break with lefts and rights in the south corner of the 3.6 km Collaroy–Narrabeen beach, sheltered by Long Reef.
- surf-forecast puts it at about -33.74, 151.32.
- Wannasurf's "Collaroy (The pipe)" page actually describes the left at the stormwater pipe, at the Collaroy/South Narrabeen boundary.

**Level:**
- Surfline (snippet): the south end "is protected from swell and suits a wide range of surfers"; shoulder-high to overhead, mid tide.
- surf-forecast: small days suit beginners.
- Wannasurf (the pipe): experienced.

**Conditions by source:**
- **Wannasurf (the pipe):** swell SW/S/SE/E; wind W/SW/S/SE; all tides; under 1 m up to 2.5 m+; "works once or twice a month".
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/collaroy/index.html
- **surf-forecast:** NE swell is ideal, SW wind. https://www.surf-forecast.com/breaks/Collaroy
- **realsurf:** this disagrees with surf-forecast. The south corner is where people go to hide from big E–SSE swell with a southerly
  wind. On ordinary swells it is flat or tiny.

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2026-05-25 | POOR–OK | protected spots "like Collaroy… lightly populated thanks to the wobbly looking and section-y conditions"; 3.2 m 12 s E, light offshore | https://www.realsurf.com/2026/05/25/big-and-messy-on-monday-morning/ |
| 2025-04-18 | GOOD (the only real option) | "Everybody's at Collaroy"; buoy "4-7 metres of 15 second interval E by ENE swell"; S–SW wind | https://www.realsurf.com/2025/04/18/its-on-7/ |
| 2025-03-08 | OK–GOOD | "When the big southerly swell comes, and a southerly wind is pumping, Collaroy beach is the best place to hide away… What a great day." (session date in the description). realsurf that morning: 2 m 10 s E, ESE wind | https://www.youtube.com/watch?v=V12lx5tVpg0 ; https://www.realsurf.com/2025/03/08/still-scrappy-and-blergh-this-morning/ |
| 2024-12-24 | POOR | "There were infrequent little sets at Collaroy"; 2.7 m S 9–10 s; SW 8–13 kt | https://www.realsurf.com/2024/12/24/south-corners-the-go/ |
| 2019-06-01 *(pre-2022)* | POOR–OK | bomb sets "around half the size and frequency compared to Dee Why"; 4.5 m 13 s from 150°, SSW 12–20 kt | https://www.realsurf.com/?p=492532 |
| 2019-05-28 *(pre-2022)* | FLAT | "Collaroy flat but sunny, 2 out" | https://www.realsurf.com/?p=492473 |
| 2018-03-12 *(pre-2022)* | FLAT | North Collaroy "pretty much zip"; 1 m 9 s from 97° | https://www.realsurf.com/?p=489145 |
| 2014-08-19 *(pre-2022)* | OK | Dee Why unsurfable; at Collaroy "surface conditions were considerably smoother… fat and full looking waves"; 4.7 m SSE 11 s, S 20–30 kt | https://www.realsurf.com/2014/08/19/few-options/ |

**Weak leads:** "Solid Swell Hits Collaroy" (uploaded 2026-03-31, no date) https://www.youtube.com/watch?v=Bq8xL285yzI ;
"Surfing on 7ft waves at Collaroy" (uploaded 2024-09-28) https://www.youtube.com/watch?v=gZc2YBBQeAM

**Collaroy End ("The Kick"):**
- A right over flat rock and sand next to Collaroy pool. Wannasurf pin: 33°44.039'S 151°18.362'E.
- Wannasurf: E/NE swell, low tide only, breaks "sometimes".
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/Collaroy_End/index.html
- realsurf shows it working on big S swells instead: OK on 2011-05-18 at 3 m 13 s S, and "Pretty fat looking bomb" on 2014-08-19 at 4.7 m SSE.
  https://www.realsurf.com/2011/05/19/pics-by-don-the-kick-and-collaroy-wed-18-may/
- No sessions from 2022 on.

## 8. South Narrabeen ("Southy"; "Surfrider Gardens" in realsurf's wording)

**What and where:** An exposed beach break on sandbars, lefts and rights, from the Collaroy pipe north to about Surfrider Gardens (Ocean St).
surf-forecast puts it at about -33.72, 151.31.

**Level:** experienced.
- Wannasurf: a "regional classic"; the right "punishes poor takeoffs", and beginners should stay at the Collaroy end.
- realsurf: the ratio of close-outs to makeable waves is "the usual 10:1 for the place".
- Tracks (13 Aug 2025): "Sydney's answer to Pipeline".

**Conditions by source:**
- **Wannasurf:** swell SE/E/NE; wind W/SW/S/SE; all tides; under 1 m to 2 m+. A 2007 commenter says it "doesn't hold much size over
  6 ft". About 150 days a year. https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/south_narrabeen/index.html
- **surf-forecast:** SE best, SW offshore, all tides, "very consistent". https://www.surf-forecast.com/breaks/Narrabeen_South
- **realsurf:** short-period S swell gives it nothing (2022-01-19), and 3.8 m 13 s E swell overwhelms it (2025-08-05).

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2025-08-23 | OK–GOOD (experienced) | "close-outs to makeable ones ratio was the usual 10:1 for the place"; 2.4 m 9–10 s mainly NE, SW wind | https://www.realsurf.com/2025/08/23/south-narrabeen-session/ ; https://www.realsurf.com/2025/08/23/sunny-start-with-waves-too/ |
| 2025-08-06 | GOOD (experts, XXL) | "XXL South Narrabeen RAW (4K) \| Heavy Beachbreak Barrels – August 6th, 2025"; "Massive east swell"; realsurf "Insane this morning" | https://www.youtube.com/watch?v=HAO9KJ0Ltd4 ; https://www.youtube.com/watch?v=14OhH7vt5t0 ; https://www.realsurf.com/2025/08/06/insane-this-morning/ |
| 2025-08-05 | POOR (too big) | "The open stretches are completely overwhelmed"; 3.8 m 13 s E | https://www.realsurf.com/2025/08/05/open-beaches-closed/ |
| 2025-04-19 | GOOD–OK (experts) | "South Narrabeen Saturday 19th April", "Early morning at Southy"; realsurf "Still big early but dropping fast… only experienced riders" | https://www.youtube.com/watch?v=SSsp6j3CTxo ; https://www.realsurf.com/2025/04/19/still-big-early-but-dropping-fast/ |
| 2024-04-07 | GOOD–OK | "Surfrider Gardens doing its thing"; E "2+ range with a useful 11 second periods… head high plus"; light NW; tide falling | https://www.realsurf.com/2024/04/07/lotsa-waves-but-that-water/ |
| 2022-02-27 | OK (polluted water) | "Biggest sets were into the shoulder high range at better exposures"; 1.7 m 13 s SSE, light WSW | https://www.realsurf.com/2022/02/27/break-in-the-rain-and-waves-too-but-the-water-looks-bad/ |
| 2022-01-30 | POOR | "from Surfrider Gardens to Northy it's knee to maybe waist"; 0.85 m E 7 s | https://www.realsurf.com/2022/01/30/small-to-near-flat-depending-on-where-you-look/ |
| 2022-01-28 | FLAT | "very weak knee to waist high dribble"; E about 1 m at 5 s; NNE 7–11 kt | https://www.realsurf.com/2022/01/28/just-barely-there-for-friday-morning/ |
| 2022-01-27 | POOR | "South Narra slopfest 0800"; 1.1 m 9 s E; ENE 7–11 kt | https://www.realsurf.com/2022/01/27/weak-and-puny-thursday-morning/ |
| 2022-01-19 | POOR | "knee to waist high at best"; 2.7 m 7 s from S by SSW | https://www.realsurf.com/2022/01/19/missable-wednesday-morning/ |
| 2022-01-17 | POOR (closing out) | Surfrider Gardens "comfortably into the 2x overhead range… shutdown to makeable ratio 50:1"; 2 m 14 s from 81° | https://www.realsurf.com/?p=504139 |

**Weak leads:**
- Tracks, 13 Aug 2025: Southy "going off" "last week" (no day given). https://tracksmag.com.au/watch-sydneys-answer-to-pipeline
- 2016-10-24 *(pre-2022)*: "Big along south Narrabeen". https://www.realsurf.com/?p=484957

## 9. Narrabeen Alley ("Alley Rights")

**What and where:** Rights in the lagoon-entrance channel at North Narrabeen.
- surf-forecast lists it as "Narrabeen-Alley Rights": about -33.71, 151.31, ENE swell best, NW wind, all tides.
  https://www.surf-forecast.com/breaks/Narrabeen_Alley-Rights
- It has no Wannasurf or Surfline page of its own.
- Tracks (2012) calls it the "Alley channel rights", with sand that depends on the lagoon and dune works. https://tracksmag.com.au/?p=29872
- A 2019 YouTube description calls it "a magical surf spot only for locals of North Narrabeen".
  https://www.youtube.com/watch?v=3_WbuNYCKhc

**Dated sessions:** none found. It is part of North Narrabeen, which the bot already scores.

## 10. Turimetta ("Turrimetta"; also "Little Narrabeen"/"Little Narra"; Surfline "Turimetta Head")

**What and where:** A beach between Narrabeen Head and Turimetta Head, reached by a 5–15 minute walk.
- Wannasurf pin: 33°41.984'S 151°18.604'E (**-33.700, 151.310**).
- The left over rocks is usually the best wave and "for experts only". The middle is the most crowded; the far right is sand over
  many submerged rocks.
- surf-forecast adds a left-hand reef.

**Level:** experienced (rocks, localism, sharks).

**Conditions by source:**
- **Wannasurf:** swell S/SE/E/NE; wind NW/W/SW; mid tide; under 1 m up to 2.5 m+.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/turrametta/index.html
- **surf-forecast:** ESE best, WNW wind, "no shelter from cross-shore breezes", "fairly consistent".
  https://www.surf-forecast.com/breaks/Turimetta-beach
- **realsurf:** it is a semi-sheltered option in NE windswell with NNE wind (2014). Whether the north or south end works depends on swell
  direction (2009).

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2021-01-04 *(pre-2022)* | OK (surfed) | "After a brief but powerful storm, it cleared up for both surfers and sharks" | https://www.youtube.com/watch?v=qa2fda5rjiw |
| 2018-06-24 *(pre-2022)* | POOR | "Size about knee to waist… single punter at little Narra" | https://www.realsurf.com/?p=490259 |
| 2014-01-29 *(pre-2022)* | OK | NNE wind, 1.5 m 7 s NE windswell; Little Narra and Northy "Set wave faces were into the chest plus range" | https://www.realsurf.com/2014/01/29/arvo-seshes-to-be-had/ |
| 2014-01-18 *(pre-2022)* | POOR–OK | Little Narra "Waist high sets provide diversion" | https://www.realsurf.com/2014/01/18/little-windswelly-saturday-morning/ |
| 2009-02-28 *(pre-2022)* | POOR | "shutdowns were the order of the day with only the occasional makeable section" | https://www.realsurf.com/2009/02/28/wozzawood-turimetta/ |

**Weak leads (upload date only):**
- 2024-01-08 bodyboard clip "dumping waves close to shore". https://www.youtube.com/watch?v=U5GIAQWTRSY
- "TEETERING TURIMETTA", uploaded 2025-08-12. https://www.youtube.com/watch?v=A4-ahPdOAak
- "Turimetta Beach Sunday 27th April 2025": big seas, but no surf verdict. https://www.youtube.com/watch?v=SIHgQOWQwn8

## 11. Warriewood "Blackies"

**No such break.** No source puts a break called Blackies at Warriewood; the well-known Blackies is at Cronulla.

The public names at Warriewood are:
- "Warriewood"
- "the corner": Wannasurf's alternative name for a right off the south-end point; experienced, SE/E swell, W/SW/S wind, low to mid falling tide.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/warriewood/index.html
- "the point" and "the middle"
- realsurf's slang "Wozzawood"
- "Cooks Terrace", the stretch north toward Mona Vale

None of these needs a new entry.

## 12. Mona Vale

**What and where:** A beach break with rights and lefts. The main wave is a very fast, hollow right at the "Rip Bowl".
Wannasurf pin: 33°40.924'S 151°18.825'E (**-33.682, 151.314**).

**Level:** experienced. Crowded, with localism.

**Conditions by source:**
- **Wannasurf:** swell N/NE ("needs right-hand banks, a good NE swell"); NW/W wind; all tides; under 1 m to 2 m+.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/mona_watu/index.html
- **surf-forecast:** NE swell, NW wind, "inconsistent", rated 2/10, too small about 65% of the time in January.
  https://www.surf-forecast.com/breaks/Mona-Vale-Beach
- **Surfline (snippet):** NE, E or SE swell; W/NW/SW wind; mid tide; waist-high to double overhead.
- **Surfnerd (snippet):** usually flat "until a solid SE-S swell breaks outside".
- **Disagreement:** NE swell (Wannasurf, surf-forecast) vs SE–S (Surfnerd). Every dated GOOD day was NE.

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2024-08-30 | POOR | "Top picture Mona Vale"; "tiny waves… mostly in the knee high range… odd waist-ish set"; 1.5 m SSE 10 s; NNW | https://www.realsurf.com/2024/08/30/hit-the-south-magnets-for-a-chance/ |
| 2024-05-11 | OK? *(inferred, weak)* | Mona Vale Boardriders Open final held that day. Sydney-wide: about 2 m of 18 s S, light NE, "beach break options will be minimal" | https://www.youtube.com/watch?v=ZjuVCTVOJ1w ; https://www.realsurf.com/2024/05/11/shoulder-to-head-high/ |
| 2024-04-07 | OK–GOOD *(inferred)* | Open final held that day. Sydney-wide: E "2+ range… 11 second periods… head high plus", light NW | https://www.youtube.com/watch?v=tEPlB0cLJsU ; https://www.realsurf.com/2024/04/07/lotsa-waves-but-that-water/ |
| 2014-09-10 *(pre-2022)* | GOOD (7/10) | "surprisingly energetic NE swell"; NE 1.5 m 10 s | https://www.realsurf.com/2014/09/11/mona-vale-midday-weds-10-sept-2014/ |
| 2013-09-23 *(pre-2022)* | FLAT | "grabbed a few views of the flatness" | https://www.realsurf.com/2013/09/23/newport-mona-northy-microness/ |
| 2010-08-11 *(pre-2022)* | GOOD (9/10) | "about as good as I've ever seen it… thunderous barrels"; NE 2 m 10 s | https://www.realsurf.com/2010/08/12/pics-mona-vale-as-good-as-it-gets-wed-11-aug/ |

**Weak leads:**
- "Mona Vale Grom Surf Session - 8th Jan 2024" (realsurf that day: choppy 1.9 m 7 s NE windswell). https://www.youtube.com/watch?v=IYWO43yxvtM
- "Sydney Surf Report Mona Vale Beach" clips dated 28.12.2025, 01.05.2026, 12.06.2026 and 25.07.2026, with no text verdict. realsurf on
  those days, in order: wind "demolishing surface conditions"; knee to waist; "no sign of a surfable wave" at Dee Why; 2.3 m 12.5 s from 162° with WNW wind.

**Mona Vale Basin / "Wamp":**
- A heavy bodyboard shorebreak and slab in Bongin Bongin Bay. Wannasurf pin: 33°40.579'S 151°18.96'E.
- Wannasurf: starts at 1.5–2 m and "often closes out", "pretty much one for the bodyboarders".
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/Wamp_/index.html
- Lead: "Huge slabs at Mona Vale Womp", uploaded 2022-01-18. https://www.youtube.com/watch?v=l7L-BXS69oY

## 13. Bungan

**What and where:** A small (0.6 km) beach between Bungan Head and Mona Vale Head, with sand over some rock.
- Wannasurf pin: 33°39.968'S 151°19.232'E (**-33.666, 151.321**).
- Lefts and rights at the north end in front of the club; "right-hand barrels and steep take-offs" at the south end.
- Access is a steep walk.

**Level:** experienced (Wannasurf). Beachsafe hazard rating 7/10 (snippet).

**Conditions by source:**
- **Wannasurf:** low to mid falling tide; under 1 m up to 2.5 m+; no swell or wind direction given.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/bungan/index.html
- **surf-forecast:** NE swell ideal, NW wind, "consistent", rated 4/10. https://www.surf-forecast.com/breaks/Bungan-Beach
- **Rain:** realsurf repeatedly warns of runoff pollution "Bungan to Manly" after rain.

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2024-08-30 | POOR | "Below: Bungan"; "tiny waves… knee high… odd waist-ish set"; 1.5 m SSE 10 s; NNW | https://www.realsurf.com/2024/08/30/hit-the-south-magnets-for-a-chance/ |
| 2024-04-07 | OK *(conditions inferred)* | "Bungan beach surfing", description "07/04/2024". Sydney-wide: 2+ m E 11 s, light NW | https://www.youtube.com/watch?v=yQOQ_dKaECY ; https://www.realsurf.com/2024/04/07/lotsa-waves-but-that-water/ |
| 2010-08-11 *(pre-2022)* | GOOD (8/10) | "overhead sets and clean offshore conditions"; NE 2 m 10 s | https://www.realsurf.com/2010/08/12/pics-bungan-midday-wed-11-aug-going-orf/ |

## 14. Newport reefs (status only)

**Crosswaves:** a right reef ledge about 150 m off the south-end rock platform; Wannasurf pin 33°39.603'S 151°19.654'E.

**Plungers:** a right ledge about 70 m past Crosswaves around the corner; high tide; SE swell.

**Newport Reef (surf-forecast):** a right reef, SE swell, "inconsistent".

All three are publicly listed, but they are heavy ledges for experienced surfers only, and no dated sessions were found.
Wannasurf's "secrets" and "deadies" pages at Newport are local spots and are left alone.

## 15. Bilgola (beach; "Bilgola Bank"; "Bowles")

**Bilgola Bank** (Wannasurf; alternative name "Oiy-Mac's Bank"):
- Pin 33°38.633'S 151°19.846'E, sand over rock at the north end.
- Experienced surfers; low to mid falling tide.
- Users say the locals are protective.

**Bowles:**
- Pin 33°38.86'S 151°19.755'E, a flat-rock ledge behind the pool, mostly for bodyboarders.
- "very shallow and sucky at dead low".

**surf-forecast "Bilgola Beach":**
- Lefts and rights over reef; best NE swell; NNW wind; all tides; "very consistent".
- Reviewers call it fickle, working a few times a year.
- https://www.surf-forecast.com/breaks/Bilgola-Beach

**Disagreement:** the guides say "very consistent". A 2010 local says it "doesnt fire all that often", and Pittwater Online News says it is "not a renowned spot".

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2010-08-11 *(pre-2022)* | GOOD | "Bilgola doesnt fire all that often,but when she does … the best ive seen it for a long time" | https://www.youtube.com/watch?v=YQNaE1v5RS4 |

**Weak leads:**
- Manly Observer gallery (published 5 Jan 2022): Bilgola in the NE cyclone swell from ex-TC Seth, 3 or 4 Jan 2022 (day not pinned).
  https://manlyobserver.com.au/wild-waves-lash-northern-beaches-gallery/
- "22.02.2026 Sydney Surf Report Bilgola Beach" (no text). https://www.youtube.com/watch?v=RZTmIUiCoII

## 16. Little Avalon ("Little Av"), off Avalon's south headland and pool

**What and where:** A right-hand reef, hollow and powerful, short (under 50 m).
- Wannasurf pin: 33°38.389'S 151°20.023'E, about 400 m off the pool. Mondo: -33.63982, 151.33372.
- Publicly named: Wannasurf, surf-forecast, mondo, Surfnerd, the Council, the press.

**Level:**
- Wannasurf: experienced. Surfnerd: expert. Mondo: intermediate.
- Localism.

**Conditions by source:**
- **Wannasurf:** swell S/SE/E/NE; under 1 m up to 2 m+; NW/W/SW wind; mid to high tide; "Fun in 2-4ft"; very consistent.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/little_avalon/index.html
- **Mondo:** NE to S (22.5–202.5°); SW/W/NW; medium to high tide. https://mondo.surf/surf-spot/little-avalon/guide/9939
- **surf-forecast:** best NE groundswell, SW wind. https://www.surf-forecast.com/breaks/Little-Avalon

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2020-05-22 *(pre-2022)* | GOOD (big) | Kelly Slater caught "10 foot - 3 metre waves at Little Avalon" | https://www.pittwateronlinenews.com/Storm-Swell-May-2020-Surfing-Photos-Avalon-Beach.php |
| 2020-05-23 *(pre-2022)* | OK (still big) | the "only one still out at Little Avalon" | same |
| 2020-09-27 *(pre-2022)* | surfed | "Short edit of Little Avalon on Sun 27th September 2020" | https://www.youtube.com/watch?v=HhR97ZCZYws |
| 2018-08-21 *(pre-2022)* | OK/GOOD (fatal drowning, low tide) | "the first solid swell the East Coast has seen in a month"; Little Avalon was one of the spots "alight" | https://stabmag.com/news/man-drowns-surfing-sydneys-northern-beaches/ |

**Weak lead:** Surf Circus, "Tricky take off at Little Avalon" (uploaded 2024-11-07, undated): "wasn't an A plus day… the wind was nice".
https://www.youtube.com/watch?v=O-UWKhg9MGA

## 17. North Avalon

**What and where:** A beach break with lefts and rights at the north end of Avalon, by the headland. It is faster and hollower near the headland.
- Wannasurf pin: 33°38.049'S 151°20.113'E. Mondo: -33.63415, 151.33522.

**Level:** all levels when small (Wannasurf: "regional classic", crowded); intermediate to advanced on big days.

**Conditions by source:**
- **Wannasurf:** swell SE/E; under 1 m up to 5 m+; NW/W/SW/NE wind; low to mid tide.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/north_avalon/index.html
- **Mondo:** E to SE (67.5–157.5°), ENE ideal; W–NW wind; low to mid tide. https://www.mondo.surf/surf-spot/north-avalon/guide/10008
- **surf-forecast "Avalon-North":** a consistent left, best ENE swell, W wind. https://www.surf-forecast.com/breaks/Avalon_North
- **Snippets (World Beach Guide, yeeew):** it handles big swell, with "big lefts cranking down the beach".
- **Disagreement:** SE–E vs ENE/NE. Tracks shows it also handled a large SSE swell (April 2025).

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2025-04-02 *(inferred)* | GOOD (big) | "Tom Carroll and Ace Buchan swooped into some big walls at North Avalon"; large SSE swell, wind swung offshore and dropped | https://tracksmag.com.au/sydney-summer-slop-is-over-as-xl-south-swell-lights-up-parts-of-the-east-coast |
| 2024-07-14 *(inferred)* | GOOD | "a big crew out at North Av again … plenty of barrels"; slightly smaller, lighter offshore (published 18 Jul, "last weekend") | https://tracksmag.com.au/a-weekend-of-pumping-waves-on-australias-east-coast |
| 2024-07-13 *(inferred)* | GOOD (solid) | "big crew out at North Avalon … big wave hopefuls on slightly longer boards"; building E swell, offshore | same |
| 2021-07-11 *(pre-2022)* | surfed | YouTube "North Avalon 11 July 2021" (no description) | https://www.youtube.com/watch?v=T1J8Tbn2g5c |
| 2021-06-01 *(pre-2022)* | GOOD | "North Avalon barrel 1st June" (uploaded 1 Jun 2021) | https://www.youtube.com/watch?v=OWOb4pV0Bbw |
| 2017-03-10 / 11 *(pre-2022)* | GOOD (big) | "Pumping North Avalon Surf - 6-10ft (10-11 March 2017)" | https://www.youtube.com/watch?v=GvAm7q0YtxM |
| 2010-08-11 *(pre-2022)* | GOOD | "whale beacn & Nth Avalon 11/08/2010 … both pumping on the east nor east swell" | https://www.youtube.com/watch?v=V2_n3VNtDFg |

**Avalon days that may include North Av:**
- Good Friday 2025-04-18: "absolutely monster sets", "a perfect offshore breeze".
  https://northernbeachesliving.com.au/is-this-good-fridays-most-epic-surf-photo/
- 2025-07-13: "incredible surfing waves at Avalon Beach". https://www.youtube.com/watch?v=n17QQds0sN4
- 2026-05-24: "Big waves, powerful ocean". https://www.youtube.com/watch?v=vkn56GNU4uE

## 18. The Wedge (Whale Beach) and Whale Beach

**Where:** every source puts the Wedge at the **north** end of Whale Beach, off the northern rocks, not the south end. That includes
Wannasurf ("look for the north corner"), Wikipedia, Surfnerd and Broadsheet. Check an aerial photo before setting a pin.
surf-forecast "The-Wedge" is at about 33.61S 151.34E.

**What it is:** a left over reef, rock and some sand; hollow and powerful.

**Level:**
- Wannasurf: "all surfers". The Council, Sydney.com and Surfnerd: experienced.
- Crowded at weekends; tight local crew.

**Conditions by source:**
- **Wannasurf** (alternative names "Whale Beach Lefts", "Whaley corner"): swell N/NE/E; starts at 1.0–1.5 m and holds 3 m+;
  NW/W/SW wind; low to mid tide; "breaks sometimes".
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/whale_beach_lefts/index.html
- **surf-forecast:** NE swell, WNW wind, "inconsistent". https://www.surf-forecast.com/breaks/The-Wedge
- **Surfline (snippet):** NE, E or SE swell; NW to NE wind; waist-high to double overhead.
- **Swellnet (2018 reader comment):** "needs a north swell".

| Date | Verdict | Conditions (quoted) | Source |
|---|---|---|---|
| 2017-06-17 *(pre-2022)* | GOOD (beach, maybe not the Wedge) | "Whale beach sat 17/6/2017. A few good ones. No-one out." | https://www.youtube.com/watch?v=YCcoYKsY8Po |
| 2013-12-23 *(pre-2022)* | OK (small) | "My daughter Hunter surfing the Wedge at Whale Beach aged 10....23 Dec 2013" | https://www.youtube.com/watch?v=wUqWYFELrN4 |
| 2010-08-11 *(pre-2022)* | GOOD | Whale Beach "pumping on the east nor east swell" | https://www.youtube.com/watch?v=V2_n3VNtDFg |

surf-forecast also has dated photos with no conditions: 2019-05-13 and 2016-06-16. https://www.surf-forecast.com/breaks/The-Wedge/photos

## 19. North Palm Beach and Lighthouse Rights (Barrenjoey)

**North Palm Beach:**
- Wannasurf pin: 33°35.419'S 151°19.69'E, off two black rocks; a 15–30 minute walk.
- Sand over rock; experienced surfers.
- Swell SE/E/NE; under 1 m up to 3 m+; NW/W/SW wind under about 10 kn; low to mid falling tide.
  https://www.wannasurf.com/spot/Australia_Pacific/Australia/NSW/Sydney_North/north_palm_beach/index.html
- No dated sessions. It is the north end of the Palm Beach the bot already has.

**Lighthouse Rights:**
- Wannasurf: "Rarely surfed", "good tow-in break" above about 8 ft. A local says "tow-ins only".

---

## Summary: recommended additions

Sizes are Hs **at the break**, in the same sense as R-SU8 `min_hs`. Directions are swell direction FROM, in degrees.
"Dated" counts the sessions in this file from 2022 on, with older ones in brackets.

| Break | Type | Suggested level | Min size at break | Works on (swell from) | Best tide | Wind (offshore) | Dated 2022+ (older) | Confidence |
|---|---|---|---|---|---|---|---|---|
| **South Narrabeen** | beach, A-frames | intermediate (advanced over about 2 m) | about 0.8 m; overwhelmed above about 3–3.5 m open-ocean | 45–150° (E–SE best); short-period S gives nothing | all, mid best | W, SW (NW OK) | 11 (2) | medium-high |
| **Queenscliff** (Manly north end) | beach, lefts and rights | all | about 0.8 m | 60–180°; S/SE are bigger here than at South Steyne | mid (high tide too full) | NW, W, light SW | 6 (2) | medium |
| **Fairy Bower** (incl. Winki) | right point/reef | advanced | about 1.2 m; holds 4 m+ | 60–150° (E–SE; NE cyclone swell works); big S/SSE runs past | mid, rising; avoid dead low above 1.5 m | SW, S, W, SE | 4 + 1 surfed (4) | medium |
| **Collaroy** (south corner) | sheltered beach corner | all | needs open-ocean ≥ about 2.5 m to get about 0.6–1 m in the corner | 60–165° (big E to SSE); due S at 9–10 s barely gets in | mid | S, SW, W: a southerly hideout (`wind_shelter` about 160–220°) | 4 (4) | medium |
| **North Avalon** | beach, heavy left by the headland | intermediate | about 0.8 m; holds big swell | 45–165° (ENE best; big SSE works) | low to mid | W, NW, SW | 3, all inferred from "last weekend" or sequence (4) | medium |
| **Mona Vale** | beach, fast right (Rip Bowl) | intermediate | about 1 m | 20–135° (NE best; SSE 1.5 m gave knee-high) | mid (all OK) | NW, W | 1 + 2 inferred contest days (3) | medium-low |
| **Bungan** | beach over sand and rock | intermediate (steep south-end take-offs) | about 1 m | 30–120° (NE–E; SSE 1.5 m was tiny) | low to mid, falling | NW, W | 1 + 1 inferred (1) | low-medium |
| **Little Avalon** | right reef ledge | advanced | about 0.8 m; best 2–4 ft faces | 45–180° | mid to high (avoid low) | W, SW, NW | 0 (4) | medium on spec, low on evidence |
| **Turimetta** | beach + left reef over rocks | advanced | about 0.8 m | 45–150° (ESE best) | mid | W, NW (SW OK) | 0 (5) | low |
| **The Wedge** (Whale Beach, **north** end) | left over reef and sand | advanced | about 1.0 m | 20–120° (N/NE/E; NE favoured) | low to mid | W, NW, SW (light) | 0 (3) | low |

**Optional, low value:**
- Whale Beach (beach; intermediate; about 45–110°; low to mid tide; NW–W). It shares a pin with the Wedge.
- Bilgola Beach (intermediate; about 30–120°; NNW–W; fickle; 0 dated from 2022).

## Breaks to leave out, and why

- **Winki Pop / Winkipop:** the inside shelf of Fairy Bower, on the same headland. Wannasurf's two pages contradict each other. Fold it into Fairy Bower.
- **Queenscliff Bombie:** "pros or kamikaze only". It breaks properly maybe once a year (2016, then April and August 2025). XXL E swell only.
- **Long Reef Bombie:** pros only, with a long paddle and a big-wave gun. It "rarely breaks".
- **Deadmans:** an expert slab off the North Head cliffs that works about 5 days a year (needs 2.5–3 m+). It has plenty of dated sessions, but it fits the pros-only slab rule.
- **"Deeps":** no public source names a Northern Beaches break by that name.
- **Collaroy End / "The Kick":** a small rock-ledge right beside the pool, and sources conflict on direction. Fold it into Collaroy.
- **Narrabeen Alley:** part of North Narrabeen (lagoon-channel rights), described as a locals' spot. No dated sessions.
- **Warriewood "Blackies":** there is no such break. Blackies is at Cronulla.
- **Mona Vale Basin / "Wamp":** a bodyboard shorebreak slab that "often closes out".
- **Bilgola Bank ("Oiy-Mac's") and Bowles:** a local nickname with protective locals, and a shallow bodyboard ledge.
- **Newport: Crosswaves, Plungers, Newport Reef:** expert ledges with no dated evidence. "Secrets" and "Deadies" are local names.
- **North Palm Beach:** already covered by Palm Beach (it is the north end; R-NSU5 already notes the pin can't express the ends).
- **Lighthouse Rights (Barrenjoey):** tow-in only, rarely surfed.

## Where this conflicts with the existing northern setup

1. **R-NSU3 says Warriewood and Dee Why Point are the only sheltered breaks in a southerly.** The Collaroy south corner is a third, and
   realsurf treats it as the default hideout. On 2025-04-18, with 4–7 m E/ENE swell and S–SW wind: "Everybody's at Collaroy".
   The 2025-03-08 clip and the 2014-08-19 report back this up.
2. **Manly is pinned at South Steyne** (`Beachwatch "South Steyne Beach"`, k S 0.5). The dated days agree that S swell mostly misses the
   south end. They also show the north end (Queenscliff) running a size bigger on S/SE swells: 2023-05-11, 2023-04-11 and 2018-08-20.
   One Manly pin under-calls Queenscliff on south swells. That is the case for adding Queenscliff.
3. **Fairy Bower can't borrow the Shelly Beach entry's exposure.** Shelly Beach is set to face 290°, inside Cabbage Tree Bay, while the
   Bower faces the open ESE. It needs its own facing (about 110–120°) or `at_pin=True`.
4. **The Wedge is at the north end of Whale Beach,** not the south end as the brief said.
5. **North Narrabeen `max_hs=3.0`** fits South Narrabeen's behaviour: open beaches were "completely overwhelmed" at 3.8 m 13 s E on
   2025-08-05, and the XXL session was the next day as it dropped. No change suggested.
6. **Avalon's k favours SE/S (1.0/0.9)** and the guides favour ENE. North Avalon still worked in the big SSE swell of 2 Apr 2025, so this
   is not a contradiction, just a note.
7. **Rain:** realsurf repeatedly flags runoff pollution from Bungan to Manly after rain (2022-02-27, 2023-01-31, 2026-01-19). This is
   consistent with the beach Beachwatch links. None of the recommended additions is out to sea, so no `out_to_sea` flag applies.
