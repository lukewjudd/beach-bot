# Beach bot setup

The bot runs on Google Cloud at 4am, 3pm and 7pm Sydney time. Each run scores every morning and evening session for the next 2 days, picks the best eastern suburbs beach for each, and adds, updates or removes events in a shared "Beach 🌊" Google Calendar. Only sessions that score **8/10 or better** get an event, so the calendar stays quiet apart from the best days. A 9/10 or 10/10 session gets a 🔥.

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
The thresholds are at the top of `beach_bot.py`:
- `EVENT_THRESHOLD`: how good a session has to be before it's posted.
- `FIRE_THRESHOLD`: when a session gets a 🔥.
- `CLOVELLY_TOLERANCE`: how close another beach's score has to be for Clovelly to still win.

The rule ids in the code (R-W1 and so on) match `beach-knowledge.md`.

To preview without touching the calendar:
- `python beach_bot.py` shows the sessions that would be posted.
- `python beach_bot.py --all` shows the full report for every session.

Re-run `./deploy.sh` after any change.

## Map site
Every run also uploads `scores.json` to the public bucket `<PROJECT>-beach-scores`. The site in `docs/` reads that file and is published with GitHub Pages: go to **Settings → Pages → Deploy from a branch → `main` / `/docs`**.

To preview the site locally:
```bash
python beach_bot.py --json docs/scores.json
python3 -m http.server 8765 --directory docs
```
Then open http://localhost:8765. The map tiles come from Stadia Maps, which authorises the live site by its domain.
