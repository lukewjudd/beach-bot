"""Tunables: thresholds, session times and forecast points."""

from zoneinfo import ZoneInfo

TZ = ZoneInfo("Australia/Sydney")

# ---------------------------------------------------------------- tunables
DAYS_AHEAD = 2  # today + this many days
EVENT_THRESHOLD = 80  # session score needed to post an event (8/10)
FIRE_THRESHOLD = 90  # adds a 🔥 to the title (9/10+)
KEEP_THRESHOLD = 70  # a posted event stays until the session drops below this (7/10), so it doesn't flip-flop
SURF_THRESHOLD = EVENT_THRESHOLD
CLOVELLY_TOLERANCE = 5  # R-TB1: Clovelly wins if within this many points
WINDOW_HOURS = 2  # sessions are judged on their best stretch this long, not the whole slot
FAVOURITE = "Clovelly"

WEEKDAY_SESSIONS = {"am": (None, 9), "pm": (17, None)}  # None = sunrise/sunset
WEEKEND_SESSIONS = {"am": (None, 11), "pm": (14, None)}

FORECAST_POINT = (-33.914, 151.267)  # Clovelly; weather is a blend of the land and sea cells either side
MARINE_POINT = (-33.92, 151.33)  # one offshore point; beaches differ via k below
# Past rain is read across these models (75th percentile); one model alone under-reads storms
RAIN_MODELS = ("best_match", "ecmwf_ifs025", "icon_seamless", "gem_seamless", "jma_seamless", "ukmo_seamless")

# Lightning: thunderstorm weather codes, or lots of storm energy (CAPE) with rain likely
STORM_CODE = 95
STORM_CAPE = 1000  # J/kg
STORM_RAIN_PROB = 60
