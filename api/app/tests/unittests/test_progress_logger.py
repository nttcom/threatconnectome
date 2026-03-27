import logging
import time

from app.tests.medium.constants import PTEAM1, USER1
from app.tests.medium.utils import create_pteam, create_user
from app.utility.progress_logger import TimeBasedProgressLogger


class TestTimeBasedProgressLogger:

    def test_it_should_output_log_when_add_progress(self, mocker):
        # Given
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)

        original_interval = TimeBasedProgressLogger.INTERVAL_DB_SECONDS
        original_trigger = TimeBasedProgressLogger.LOG_TRIGGER_COUNT
        TimeBasedProgressLogger.INTERVAL_DB_SECONDS = 0.5
        TimeBasedProgressLogger.LOG_TRIGGER_COUNT = 1

        logger = TimeBasedProgressLogger(
            title="Test Task",
            pteam_id=pteam1.pteam_id,
            service_name="test_service1",
            logger=logging.getLogger("app.utility.progress_logger"),
        )

        mock_info = mocker.patch.object(logger.logger, "info")

        try:
            for i in range(5):
                logger.add_progress(20.0)
                time.sleep(1.0)
        finally:
            logger.stop()
            TimeBasedProgressLogger.INTERVAL_DB_SECONDS = original_interval
            TimeBasedProgressLogger.LOG_TRIGGER_COUNT = original_trigger

        # Then
        log_messages = [args[0] for args, _ in mock_info.call_args_list]
        assert "[Test Task] Progress: 40.0%" in log_messages
        assert 7 < mock_info.call_count < 11

    def test_it_should_return_100_when_progress_overflows(self, mocker):
        # Given
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)

        original_interval = TimeBasedProgressLogger.INTERVAL_DB_SECONDS
        original_trigger = TimeBasedProgressLogger.LOG_TRIGGER_COUNT
        TimeBasedProgressLogger.INTERVAL_DB_SECONDS = 0.5
        TimeBasedProgressLogger.LOG_TRIGGER_COUNT = 1

        logger = TimeBasedProgressLogger(
            title="Test Task",
            pteam_id=pteam1.pteam_id,
            service_name="test_service1",
            logger=logging.getLogger("app.utility.progress_logger"),
        )

        mock_info = mocker.patch.object(logger.logger, "info")

        try:
            logger.add_progress(120.0)
            time.sleep(1.0)
        finally:
            logger.stop()
            TimeBasedProgressLogger.INTERVAL_DB_SECONDS = original_interval
            TimeBasedProgressLogger.LOG_TRIGGER_COUNT = original_trigger

        # Then
        log_messages = [args[0] for args, _ in mock_info.call_args_list]
        assert "[Test Task] Progress: 100.0%" in log_messages
