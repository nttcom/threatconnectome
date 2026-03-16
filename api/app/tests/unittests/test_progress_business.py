from datetime import datetime, timezone

import pytest

from app.business import progress_business


class TestProgressBusiness:
    @pytest.mark.parametrize(
        "created_at, progress_rate",
        [
            (
                datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                0.0,
            ),
            (
                datetime(2026, 3, 12, 12, 0, 0, tzinfo=timezone.utc),
                0.5,
            ),
            (
                datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
                1.0,
            ),
        ],
    )
    def test_predict_completion_time(self, created_at: datetime, progress_rate: float):
        # Given
        adjusted_progress_rate = progress_rate if progress_rate != 0 else 0.001

        # When
        before = datetime.now(timezone.utc)
        result = progress_business.predict_completion_time(created_at, adjusted_progress_rate)
        after = datetime.now(timezone.utc)

        # Then
        expected_min = created_at + (before - created_at) / adjusted_progress_rate
        expected_max = created_at + (after - created_at) / adjusted_progress_rate
        assert expected_min <= result <= expected_max
