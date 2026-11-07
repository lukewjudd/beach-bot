"""Tunables: thresholds, session times and forecast points."""

from zoneinfo import ZoneInfo

TZ = ZoneInfo("Australia/Sydney")

# ---------------------------------------------------------------- tunables
DAYS_AHEAD = 2  # calendar events: today + this many days
FORECAST_DAYS = 12  # the site shows this week and next (as far as the swell forecast reaches, ~9 days)
EVENT_THRESHOLD = 80  # "worth it" on the site (8/10)
CALENDAR_THRESHOLD = 90  # a session goes in the calendar at 9/10: an event should mean drop everything and go
KEEP_THRESHOLD = 80  # a session in an event stays until it drops below this (8/10), so it doesn't flip-flop
FIRE_THRESHOLD = 100  # a 🔥 in the title: 10/10, every part of the score at full marks
# Surf is scored on its own scale (waves, not calm water), so it never leads a session or counts towards its
# score: it's a swimming app. Surfers get their own calendar event, clearly labelled, when it's pumping.
SURF_THRESHOLD = 80  # a surf break's 8/10: pumping, worth a surf event (about 8 days a year in the east)
SURF_KEEP_THRESHOLD = 70  # a surf event stays until the surf drops below 7/10
FAVOURITE_TOLERANCE = 5  # R-TB1: a region's favourite (Clovelly in the east) wins if within this many points
WINDOW_HOURS = 2  # sessions are judged on their best stretch this long, not the whole slot
SITE_URL = "https://lukewjudd.github.io/beach-bot/"  # linked at the bottom of every event

# Every day is cut into three sessions that cover it end to end (None = sunrise/sunset), the same every day of the
# week: not everyone works nine to five, and a lunchtime swim is as real as a before-work one
SESSIONS = {"am": (None, 11), "md": (11, 14), "pm": (14, None)}
# Slot codes end each session key, so they must stay base32hex (letters a-v) for Google event ids
SLOT_NAMES = {"am": ("AM", "morning"), "md": ("Midday", "midday"), "pm": ("PM", "evening")}

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
