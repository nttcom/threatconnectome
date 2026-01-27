from datetime import date, datetime, timedelta, timezone

from app.eol_constants import EOL_WARNING_THRESHOLD_DAYS


def is_within_eol_warning(eol_from: date) -> bool:
    """Check if the EOL is within the configured warning threshold.

    Returns True when ``eol_from - now`` is less than or equal to
    ``EOL_WARNING_THRESHOLD_DAYS``.
    """
    time_until_eol = eol_from - datetime.now(timezone.utc).date()
    return time_until_eol <= timedelta(days=EOL_WARNING_THRESHOLD_DAYS)
