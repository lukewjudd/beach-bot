# beach bot

Checks the weather and ocean forecast and tells me when it's worth going to the beach. Eastern suburbs Sydney only. Clovelly is the favourite, so it wins ties.

## What it does

- Pulls the forecast from Open-Meteo (wind, swell, air and water temp, rain, storms)
- Reads rain that's already fallen across six weather models and leans wet, since one model alone under-reads storms
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
beach-knowledge.md  the beach rules and where they came from
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
cd bot && uv run beach-bot --json ../web/public/scores.json   # local data for the site
cd web && npm install && npm run dev
```

## Deploying

The bot: put `PROJECT_ID` and `CALENDAR_ID` in `.env`, then `./deploy.sh`.

The site deploys itself to GitHub Pages on every push to `main` that touches `web/`.

Full setup is in `SETUP.md`. What's changed is in `CHANGELOG.md`.

## Tweaking

The thresholds are in `bot/src/beach_bot/config.py`. If it posts too much, raise the bar. If it's too quiet, lower it.
