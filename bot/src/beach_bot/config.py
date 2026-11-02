"""Tunables: thresholds, session times and forecast points."""

from zoneinfo import ZoneInfo

TZ = ZoneInfo("Australia/Sydney")

# ---------------------------------------------------------------- tunables
DAYS_AHEAD = 2            # today + this many days
EVENT_THRESHOLD = 80      # session score needed to post an event (8/10)
FIRE_THRESHOLD = 90       # adds a 🔥 to the title (9/10+)
SURF_THRESHOLD = EVENT_THRESHOLD
CLOVELLY_TOLERANCE = 5    # R-TB1: Clovelly wins if within this many points
WINDOW_HOURS = 2          # sessions are judged on their best stretch this long, not the whole slot
FAVOURITE = "Clovelly"

WEEKDAY_SESSIONS = {"am": (None, 9), "pm": (17, None)}    # None = sunrise/sunset
WEEKEND_SESSIONS = {"am": (None, 11), "pm": (14, None)}

FORECAST_POINT = (-33.914, 151.267)  # Clovelly; weather is a blend of the land and sea cells either side
MARINE_POINT = (-33.92, 151.33)      # one offshore point; beaches differ via k below
