import re
from datetime import datetime

def verifyEpisodeFormat(episode):
    """
    Checks if the provided episode string matches to the format "SxxExx".

    Args:
        episode (str): The season and episode string to validate.

    Returns:
        bool: Returns 'True' if the string matches the expected format, 'False' otherwise.
    """
    format=r"^S\d{2}E\d{2}$"
    return bool(re.match(format, episode))

def verifyDateFormat(date):
    """
    Validates if the provided date string follows the "YYYY-MM-DD" format.

    Args:
        date (str): The date string to validate.

    Returns:
        bool: Returns 'True' if the string matches the format, 'False' otherwise.
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False