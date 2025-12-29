import os
from zoneinfo import ZoneInfo

API_SPORTS_KEY = os.getenv("API_SPORTS_KEY", "db298b866891a40645b145c9dd202cfe")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyBaYsXvFLHytr2hHHECF1bI4wvVXTHrMcw")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7986237119:AAGE2J03qPLAWQFzc5KarNSbCSZwH1o0qIU")

API_SPORTS_BASE = "https://v3.football.api-sports.io"

GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1002016840854"))  # set -100... to enable group pushes
GROUP_TOPIC_ID = int(os.getenv("GROUP_TOPIC_ID", '9'))

# ✅ СПИСОК КАНАЛІВ ДЛЯ РОЗСИЛКИ
# thread_id = None → звичайна група
# thread_id = число → топік

PUSH_TARGETS = [
    {
        "chat_id": -5059955185,
        "thread_id": None,  # ✅ звичайна група
    },
    {
        "chat_id": -1002016840854,
        "thread_id": 9,    # ✅ топік
    }
]

TZ_UTC = ZoneInfo("UTC")
TZ_ITALY = ZoneInfo("Europe/Rome")
TZ_UKRAINE = ZoneInfo("Europe/Kyiv")

DATA_DIR = "data"
REMINDERS_FILE = "reminders.json"

MORNING_UPDATE_HOUR = int(os.getenv("MORNING_UPDATE_HOUR", "8"))
EVENING_UPDATE_HOUR = int(os.getenv("EVENING_UPDATE_HOUR", "22"))
CACHE_RETENTION_DAYS = int(os.getenv("CACHE_RETENTION_DAYS", "4"))
MIN_REQUESTS_TO_ALLOW_MANUAL = int(os.getenv("MIN_REQUESTS_TO_ALLOW_MANUAL", "10"))

HEADERS = {"x-apisports-key": API_SPORTS_KEY}

USE_REDIS=True          # false — JSON, true — Redis
REDIS_URL="redis://localhost:6379/0"  # або твій Redis URL

# Нагадування перед матчем (в хвилинах до початку)
REMINDER_MINUTES_BEFORE = 15

# Діапазон для надійного спрацювання (через сканування кожну хвилину)
REMINDER_TOLERANCE_MINUTES = 2  # тобто від 13 до 17 хв