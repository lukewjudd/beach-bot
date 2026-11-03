# Beach bot setup

The bot runs on Google Cloud every hour from 4:15am to 9:15pm Sydney time. Each run scores every morning and evening session for the next 2 days, picks the best eastern suburbs beach for each, and adds, updates or removes events in a shared "Beach 🌊" Google Calendar. Only sessions that score **8/10 or better** get an event, so the calendar stays quiet apart from the best days. An event stays until the session drops below 7/10, so it doesn't come and go with every run. A 9/10 or 10/10 session gets a 🔥.

## 1. Create the calendar (2 min)
1. In Google Calendar on the web, go to **Settings → Add calendar → Create new calendar** and name it `Beach 🌊`.
2. Open its settings. Under **Integrate calendar**, copy the **Calendar ID**. It looks like `abc123@group.calendar.google.com`.

## 2. Make a personal Google Cloud project (3 min)
1. Go to https://console.cloud.google.com with your **personal** Google account.
2. Create a project, e.g. `beach-bot-luke`, and attach a billing account. Google requires one even within the free tier.
3. Optional: set a $1 budget alert under **Billing → Budgets & alerts**.

## 3. Point gcloud at your personal account
Create a separate gcloud profile for this project so it never touches any other account:

```bash
gcloud config configurations create beach
gcloud auth login
gcloud config set project beach-bot-luke
```

Switch back to your usual profile later with `gcloud config configurations activate default`.

## 4. Deploy
In this folder, run:

```bash
PROJECT=beach-bot-luke CALENDAR_ID=abc123@group.calendar.google.com ./deploy.sh
```

The script:
- enables the APIs
- creates a `beach-bot` service account
- builds and deploys the Cloud Run Job
- creates the schedule

It always uses the `beach` gcloud profile, whichever profile is active in your shell. It's safe to re-run after you change the code.

## 5. Share the calendar
In the Beach calendar's settings, under **Share with specific people**:
- Add `beach-bot@<PROJECT>.iam.gserviceaccount.com` with **Make changes to events**.
- Add each friend's Gmail address with **See all event details**.

Each person (including you) then opens the Beach calendar's settings:
- Under **Other notifications**, turn on **New events**.
- Optionally, add an event notification.

## 6. Test it
```bash
gcloud --project beach-bot-luke run jobs execute beach-bot --region us-central1 --wait
```

## Tuning
The thresholds are in `bot/src/beach_bot/config.py`:
- `EVENT_THRESHOLD`: how good a session has to be before it's posted.
- `FIRE_THRESHOLD`: when a session gets a 🔥.
- `CLOVELLY_TOLERANCE`: how close another beach's score has to be for Clovelly to still win.

The beaches themselves are in `bot/src/beach_bot/beaches.py`. The rule ids in the code (R-W1 and so on) match `beach-knowledge.md`.

To preview without touching the calendar, from `bot/`:
- `uv run beach-bot` shows the sessions that would be posted.
- `uv run beach-bot --all` shows the full report for every session.

Re-run `./deploy.sh` after any change to the bot.

## Map site
Every run also uploads `scores.json` to the public bucket `<PROJECT>-beach-scores`. The site in `web/` reads that file. It's built and published to GitHub Pages by `.github/workflows/pages.yml` on every push to `main` that touches `web/`. In the repo's **Settings → Pages**, the source must be **GitHub Actions**.

To work on the site locally:
```bash
cd bot && uv run beach-bot --json ../web/public/scores.json
cd web && npm install && npm run dev
```

The map is a [Protomaps](https://protomaps.com) extract in `map/`, drawn with Leaflet + protomaps-leaflet, so there's no map provider or key. `deploy.sh` uploads it to the public bucket, and the site reads tiles out of the one `.pmtiles` file with byte-range requests. (Not from GitHub Pages: its CDN fetches the whole file on a cache miss, which made the first tiles slow.) To rebuild it (the coastline doesn't change much, so roughly once a year):
```bash
pmtiles extract https://build.protomaps.com/<YYYYMMDD>.pmtiles map/eastern-suburbs.pmtiles --bbox=151.17,-34.01,151.32,-33.83 --maxzoom=14
```
