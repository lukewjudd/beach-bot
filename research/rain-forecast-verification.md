# Forecasting Sydney's rain: which model, or which blend

Checked 12 Nov 2026, after Saturday's Clovelly call dropped from 9 to 6 on one model's rain.

## What happened

On 12 Nov 2026 the default model (Open-Meteo's "best match", ECMWF-led in Sydney) moved to about 14mm on Friday
night. That's over Clovelly's 10mm "recent rain" limit, so Saturday morning lost 25 points and the calendar event
went. The other models disagreed:

| Model | 9am Fri to 9am Sat |
|---|---|
| Best match | 14.0mm |
| ECMWF IFS | 13.5mm |
| GEM (Canada) | 12.9mm |
| ECMWF AIFS (AI) | 6.0mm |
| Météo-France | 2.4mm |
| ICON (Germany) | 2.1mm |
| GFS (US) | 1.5mm |
| UKMO | 1.5mm |
| JMA (Japan) | 0.6mm |
| BOM ACCESS-G | 0.0mm |

## What forecasters use

- No published verification compares the models' rain for Sydney.
- BOM's own forecasts are a consensus of several models, each bias-corrected (its Operational Consensus
  Forecast), with ECMWF among the inputs. They aren't one model's output.
- Studies of short-range rain agree that a multi-model blend beats single models. Rain loses skill faster with
  lead time than any other surface element.
- BOM's ACCESS-C (1.5km, Sydney domain) isn't on Open-Meteo. ACCESS-G is, but it has gaps in the archive and the
  worst errors here.

## The test

- **Forecasts:** Open-Meteo's previous-runs archive, as each model stood 1 and 2 days before (hourly, summed
  9am to 9am).
- **Gauge:** Sydney Airport, BOM 066037, from NOAA's GHCN-Daily copy. BOM's site turns away scripts.
- **Period:** Aug 2024 to Oct 2026, 797 days, 69 of them with 10mm or more.
- **Question:** the bot's own, will a day have 10mm (or 20mm)?
- **Score:** hits ÷ (hits + misses + false alarms).

Run it again with `bot/scripts/verify_rain_models.py`.

| 10mm days | Caught | False alarms | Score |
|---|---|---|---|
| Best match, 1 day ahead | 42% | 38% | 0.33 |
| Eight-model vote, 1 day ahead | 61% | 41% | 0.43 |
| Best match, 2 days ahead | 42% | 41% | 0.33 |
| Eight-model vote, 2 days ahead | 59% | 39% | 0.43 |

| 20mm days | Caught | False alarms | Score |
|---|---|---|---|
| Best match, 1 day ahead | 37% | 38% | 0.30 |
| Eight-model vote, 1 day ahead | 43% | 35% | 0.35 |
| Best match, 2 days ahead | 31% | 42% | 0.26 |
| Eight-model vote, 2 days ahead | 40% | 50% | 0.29 |

Other blends, from an earlier pass on the days every model covered:

- The **middle** of the models has the fewest false alarms but misses heavy rain.
- The **average** is close to the vote at 10mm but weaker at 20mm.
- The **second wettest** catches the most rain days but doubles the false alarms.

The best single models were ECMWF AIFS (0.44 at 1 day) and GFS (0.45 at 2 days), but neither was best across the
board. The vote was best or close to it everywhere.

## Caveats

- One gauge, with about 70 wet days, so the gaps between the top few methods are within noise. The clear result is
  that a blend beats the one model the bot used.
- The bot counts rain hour by hour, so each rain day's vote total is spread over the hours the way the models'
  average has it. The models agree on how much far better than on which hour.
