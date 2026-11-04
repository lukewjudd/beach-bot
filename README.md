# beach bot

Checks the weather and ocean forecast and tells me when it's worth going to the beach in Sydney: the eastern suburbs (Clovelly is the favourite, so it wins ties) and the northern beaches (Shelly Beach is theirs). Each has its own calendar, and the site switches between them.

## What it does

- Pulls the forecast from Open-Meteo (wind, swell, air and water temp, rain, storms)
- Takes rain that's already fallen from BOM's rain gauges (Observatory Hill and Sydney Airport), since the models under-read storms
- Checks Beachwatch for water quality (only today's forecast; otherwise it goes off recent rain)
- Scores every beach for a morning session (before work) and an evening session (after work), plus weekends
- Anything 8/10 or better is "worth it" and goes in a shared Google Calendar, and 9+ gets a 🔥
- If the forecast turns, the event gets removed once it drops below 7/10, so it doesn't flip-flop
- Thunderstorms rule everything out
- Writes all the scores to a JSON file, which the map site reads

Runs on Cloud Run every hour from 4:15am to 9:15pm. The 6:15 run catches Beachwatch's daily update.

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
