# beach bot

Checks the weather and ocean forecast and tells me when it's worth going to the beach. Eastern suburbs Sydney only. Clovelly is the favourite, so it wins ties.

## What it does

- Pulls the forecast from Open-Meteo (wind, swell, air and water temp, rain)
- Checks Beachwatch for water quality
- Scores every beach for a morning session (before work) and an evening session (after work), plus weekends
- Anything 8/10 or better goes in a shared Google Calendar, and 9+ gets a 🔥
- If the forecast turns, the event gets removed
- Writes all the scores to a JSON file, which the map site in `docs/` reads

Runs on Cloud Run three times a day: 4am, 3pm and 7pm.

Map: https://lukewjudd.github.io/beach-bot/

## Running it

```bash
pip install -r requirements.txt
python beach_bot.py --all      # show the scores, don't touch the calendar
python beach_bot.py --sync     # update the calendar
python backtest.py             # replay every session since 2023
```

## Deploying

Put `PROJECT_ID` and `CALENDAR_ID` in `.env`, then:

```bash
./deploy.sh
```

Full setup is in `SETUP.md`. The beach rules and where they came from are in `beach-knowledge.md`.

## Tweaking

The thresholds are at the top of `beach_bot.py`. If it posts too much, raise the bar. If it's too quiet, lower it.
