import re
from datetime import datetime

def verifyEpisodeFormat(episode):
    format=r"^S\d{2}E\d{2}$"
    return bool(re.match(format, episode))

def verifyDateFormat(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

