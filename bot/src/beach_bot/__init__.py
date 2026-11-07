"""Beach bot: picks the best Sydney eastern suburbs beach for each morning/midday/evening
session over the next couple of days and keeps a shared Google Calendar in sync.

Rules come from beach-knowledge.md (rule ids like R-W1 refer to that file).

Usage:
  beach-bot                      # dry run: print the scored sessions
  beach-bot --sync               # also write/update/delete Google Calendar events

--sync needs env vars:
  GOOGLE_SERVICE_ACCOUNT_JSON  service account key (the JSON text)
  BEACH_CALENDAR_ID            id of the shared "Beach" calendar
"""
