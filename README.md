# beach bot

bot look at weather. bot look at ocean. bot tell me when beach good.

eastern suburbs sydney only. clovelly best beach. clovelly win ties.

## what it do

- grab forecast from open-meteo (wind, swell, temp, rain, water temp)
- grab beachwatch to see if water gross
- score every beach for morning (before work) and evening (after work). weekends too
- score 8/10 or more = goes in google calendar. 9+ gets a 🔥
- forecast get worse = event go away
- dump all scores to json, map site in `docs/` shows them

runs on cloud run 3 times a day. 4am, 3pm, 7pm.

## run it

```bash
pip install -r requirements.txt
python beach_bot.py --all      # look at scores, touch nothing
python beach_bot.py --sync     # actually update calendar
python backtest.py             # how would it have gone since 2023
```

## deploy it

put `PROJECT_ID` and `CALENDAR_ID` in `.env` then

```bash
./deploy.sh
```

full setup in `SETUP.md`. all the beach rules and where they came from in `beach-knowledge.md`.

## change it

numbers at top of `beach_bot.py`. bar too high, make lower. bar too low, make higher.
