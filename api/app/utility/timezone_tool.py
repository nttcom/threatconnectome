from datetime import datetime, timezone


def convert_to_utc_timezone(dt: datetime):
    if dt.tzinfo == timezone.utc:
        return dt
    else:
        return dt.astimezone(timezone.utc)
