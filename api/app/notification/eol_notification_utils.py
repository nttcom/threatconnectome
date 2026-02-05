from datetime import date, datetime, timedelta, timezone

"""EOL feature-specific constants.

Modify `EOL_WARNING_THRESHOLD_DAYS` here to change the 6-month threshold
across immediate and scheduled notifications.
"""

EOL_WARNING_THRESHOLD_DAYS: int = 180


def is_within_eol_warning(eol_from: date) -> bool:
    """Check if the EOL is within the configured warning threshold.

    Returns True when ``eol_from - now`` is less than or equal to
    ``EOL_WARNING_THRESHOLD_DAYS``.
    """
    time_until_eol = eol_from - datetime.now(timezone.utc).date()
    return time_until_eol <= timedelta(days=EOL_WARNING_THRESHOLD_DAYS)
