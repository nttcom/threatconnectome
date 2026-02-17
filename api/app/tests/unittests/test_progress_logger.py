import time
from logging import INFO

from app.utility.progress_logger import TimeBasedProgressLogger


class TestTimeBasedProgressLogger:
    def test_it_should_output_log_when_add_progress(self, caplog):
        # Given
        caplog.set_level(INFO)

        # When
        logger = TimeBasedProgressLogger(title="Test Task", interval_seconds=0.5)
        try:
            for i in range(5):
                logger.add_progress(20.0)
                time.sleep(1.0)
        finally:
            logger.stop()

        # Then
        assert (
            "app.utility.progress_logger",
            INFO,
            "[Test Task] Progress: 40.0%",
        ) in caplog.record_tuples
        assert len(caplog.record_tuples) > 7
        assert len(caplog.record_tuples) < 11

    def test_it_should_return_100_when_progress_overflows(self, caplog):
        # Given
        caplog.set_level(INFO)

        # When
        logger = TimeBasedProgressLogger(title="Test Task", interval_seconds=0.5)
        try:
            logger.add_progress(120.0)
            time.sleep(1.0)
        finally:
            logger.stop()

        # Then
        assert (
            "app.utility.progress_logger",
            INFO,
            "[Test Task] Progress: 100.0%",
        ) in caplog.record_tuples
