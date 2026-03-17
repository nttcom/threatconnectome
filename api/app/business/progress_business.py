from datetime import datetime, timezone


def predict_completion_time(created_at: datetime, progress_rate: float) -> datetime:
    """
    created_at: The start time of the task
    progress_rate: The progress rate (0.0 to 1.0)
    """
    if progress_rate == 0:
        progress_rate = 0.001

    total_duration = (datetime.now(timezone.utc) - created_at) / progress_rate
    return created_at + total_duration
