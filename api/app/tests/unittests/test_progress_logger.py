import logging
import time

from app.database import get_db
from app.models import PTeam, SSVCDeployerPriorityEnum
from app.utility.progress_logger import TimeBasedProgressLogger


class TestTimeBasedProgressLogger:

    def test_it_should_output_log_when_add_progress(self, mocker):

        # Given
        db = next(get_db())
        db.add(
            PTeam(
                pteam_id="dummy",
                pteam_name="dummy team",
                contact_info="dummy@example.com",
                alert_ssvc_priority=SSVCDeployerPriorityEnum.IMMEDIATE,
            )
        )
        db.commit()

        original_interval = TimeBasedProgressLogger.INTERVAL_DB_SECONDS
        original_trigger = TimeBasedProgressLogger.LOG_TRIGGER_COUNT
        TimeBasedProgressLogger.INTERVAL_DB_SECONDS = 0.5
        TimeBasedProgressLogger.LOG_TRIGGER_COUNT = 1

        logger = TimeBasedProgressLogger(
            title="Test Task",
            pteam_id="dummy",
            service_name="dummy",
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
        db = next(get_db())
        db.add(
            PTeam(
                pteam_id="dummy",
                pteam_name="dummy team",
                contact_info="dummy@example.com",
                alert_ssvc_priority=SSVCDeployerPriorityEnum.IMMEDIATE,
            )
        )
        db.commit()

        original_interval = TimeBasedProgressLogger.INTERVAL_DB_SECONDS
        original_trigger = TimeBasedProgressLogger.LOG_TRIGGER_COUNT
        TimeBasedProgressLogger.INTERVAL_DB_SECONDS = 0.5
        TimeBasedProgressLogger.LOG_TRIGGER_COUNT = 1

        logger = TimeBasedProgressLogger(
            title="Test Task",
            pteam_id="dummy",
            service_name="dummy",
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
