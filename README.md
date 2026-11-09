# beach bot

Checks the weather and ocean forecast and tells me when it's worth going to the beach in Sydney: the eastern suburbs (Clovelly is the favourite, so it wins ties) and the northern beaches (Shelly Beach is theirs). Each has its own calendar, and the site switches between them.

## What it does

- Pulls the forecast from Open-Meteo (wind, swell, air and water temp, rain, storms)
- Takes rain that's already fallen from BOM's rain gauges (Observatory Hill and Sydney Airport), since the models under-read storms
- Checks Beachwatch for water quality (only today's forecast; otherwise it goes off recent rain)
- Scores every beach for three sessions a day, every day: morning (sunrise to 11am), midday (11am to 2pm) and evening (2pm to sunset)
- Anything 8/10 or better is "worth it" on the site; 9/10 or better goes in a shared Google Calendar, one event a day, and a 10/10 (every part at full marks) gets a 🔥
- If the forecast turns, a session comes off its event once it drops below 8/10, so it doesn't flip-flop
- Surf breaks are scored too, on their own scale: they never lead a session, and when it's pumping (8/10) the calendar gets a separate 🏄 Surf event
- Thunderstorms rule everything out
- Writes all the scores to a JSON file, which the map site reads

Runs on Cloud Run every hour, at a quarter past, around the clock. The 6:15 run catches Beachwatch's daily update.

Map: https://lukewjudd.github.io/beach-bot/

## Layout

```
bot/       Python package: forecast, scoring, calendar, export (uv, ruff, pytest)
web/       the map site: Vite + TypeScript + Leaflet, self-hosted Protomaps tiles
deploy.sh  Cloud Run job, schedule and public bucket
beach-knowledge.md  the eastern suburbs rules and where they came from
northern-beaches-knowledge.md  the same for the northern beaches
research/  extra research (harbour beaches, missing pools)
```

## Running it

```bash
cd bot
uv sync
uv run beach-bot --all      # show the scores, don't touch the calendar
uv run beach-bot --sync     # update the calendar and upload scores.json
uv run beach-backtest       # replay every session since 2023
uv run pytest
```

The site:

```bash
cd bot && uv run beach-bot --json ../web/public   # local data for the site: scores-<region>.json
cd web && npm install && npm run dev
```

## Deploying

The bot: put `PROJECT_ID` and `CALENDAR_ID` (and `CALENDAR_ID_NORTH` for the northern beaches calendar) in `.env`, then `./deploy.sh`. Without `CALENDAR_ID_NORTH` the northern beaches are scored for the site but not posted.

The site deploys itself to GitHub Pages on every push to `main` that touches `web/`.

Full setup is in `SETUP.md`. What's changed is in `CHANGELOG.md`.

## Tweaking

The thresholds are in `bot/src/beach_bot/config.py`. If it posts too much, raise the bar. If it's too quiet, lower it.
