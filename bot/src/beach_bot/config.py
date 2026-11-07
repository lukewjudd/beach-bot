"""Tunables: thresholds, session times and forecast points."""

from zoneinfo import ZoneInfo

TZ = ZoneInfo("Australia/Sydney")

# ---------------------------------------------------------------- tunables
DAYS_AHEAD = 2  # calendar events: today + this many days
FORECAST_DAYS = 12  # the site shows this week and next (as far as the swell forecast reaches, ~9 days)
EVENT_THRESHOLD = 80  # session score needed to post an event (8/10)
FIRE_THRESHOLD = 90  # adds a 🔥 to the title (9/10+)
KEEP_THRESHOLD = 70  # a posted event stays until the session drops below this (7/10), so it doesn't flip-flop
SURF_THRESHOLD = EVENT_THRESHOLD
FAVOURITE_TOLERANCE = 5  # R-TB1: a region's favourite (Clovelly in the east) wins if within this many points
WINDOW_HOURS = 2  # sessions are judged on their best stretch this long, not the whole slot
SITE_URL = "https://lukewjudd.github.io/beach-bot/"  # linked at the bottom of every event

WEEKDAY_SESSIONS = {"am": (None, 10), "pm": (16, None)}  # None = sunrise/sunset
WEEKEND_SESSIONS = {"am": (None, 11), "pm": (14, None)}

# Warmth is scored on where the day's heading, not just the hour: a 7am swim on a day going to 30 is a warm-day
# swim. Mornings get credit for the warmth up to 1pm, less WARMTH_DISCOUNT; evenings keep the afternoon's warmth
# (less the same), unless a change has knocked the temperature down by COOL_CHANGE since the afternoon peak.
WARMTH_DISCOUNT = 3  # degrees off the warmth still to come (backtested: the bar for the full warmth bonus)
WARMTH_AHEAD_TO = 13  # a morning looks ahead to this hour
COOL_CHANGE = 4  # degrees below the afternoon peak that means a change has come through
# Where the day's heading is read off the land cell's high (the blend with the sea cell runs 4-5° under it on
# sea-breeze days), but only once the water is this warm: a hot westerly in spring is still an 18° swim
WARMTH_LAND_MIN_SEA = 20

# BOM rain gauges (each region lists its own), from the NSW observations bundle on BOM's public FTP
BOM_OBS_URL = "ftp://ftp.bom.gov.au/anon/gen/fwo/IDN60910.tgz"
# Past rain the gauges don't cover is read across these models (75th percentile); one model alone under-reads storms
RAIN_MODELS = ("best_match", "ecmwf_ifs025", "icon_seamless", "gem_seamless", "jma_seamless", "ukmo_seamless")

# Lightning: thunderstorm weather codes, or lots of storm energy (CAPE) with rain likely
STORM_CODE = 95
STORM_CAPE = 1000  # J/kg
STORM_RAIN_PROB = 60
