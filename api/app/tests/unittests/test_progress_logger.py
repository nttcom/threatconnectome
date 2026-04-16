import logging
import threading
import time

import pytest

from app import models
from app.tests.common.constants import PTEAM1, USER1
from app.tests.common.utils import create_pteam, create_user
from app.utility.progress_logger import TimeBasedProgressLogger


class TestTimeBasedProgressLogger:

    @pytest.fixture(scope="function", name="setup_pteam")
    def setup_pteam(self):
        create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)

    def _refresh_and_get_progress(self, testdb, pteam_id, service_name):
        testdb.expire_all()
        return (
            testdb.query(models.SbomUploadProgress)
            .filter_by(pteam_id=str(pteam_id), service_name=service_name)
            .one_or_none()
        )

    def _create_logger(
        self,
        mocker,
        title,
        pteam_id,
        service_name,
        trigger,
    ):

        mocker.patch.object(TimeBasedProgressLogger, "LOG_TRIGGER_COUNT", trigger)

        logger = TimeBasedProgressLogger(
            title=title,
            pteam_id=pteam_id,
            service_name=service_name,
            logger=logging.getLogger("app.utility.progress_logger"),
        )

        do_update_event = threading.Event()

        def _fake_wait(timeout):
            while True:
                if do_update_event.is_set():
                    do_update_event.clear()
                    return False
                if logger._stop_event.is_set():
                    return True
                time.sleep(0.001)

        mocker.patch.object(logger._stop_event, "wait", side_effect=_fake_wait)
        logger._do_update_event = do_update_event

        return logger

    def test_it_should_output_log_when_add_progress(self, mocker, setup_pteam):
        # Given
        logger = self._create_logger(
            mocker,
            title="Test Task",
            pteam_id=self.pteam1.pteam_id,
            service_name="test_service1",
            trigger=1,
        )

        mock_info = mocker.patch.object(logger.logger, "info")

        try:
            for i in range(5):
                logger.add_progress(20.0)
                logger._do_update_event.set()
                time.sleep(0.02)
        finally:
            logger.stop()

        # Then
        log_messages = [args[0] for args, _ in mock_info.call_args_list]
        assert "[Test Task] Progress: 40.0%" in log_messages

    def test_it_should_return_100_when_progress_overflows(self, mocker, setup_pteam):
        # Given
        logger = self._create_logger(
            mocker,
            title="Test Task",
            pteam_id=self.pteam1.pteam_id,
            service_name="test_service1",
            trigger=1,
        )

        mock_info = mocker.patch.object(logger.logger, "info")

        try:
            logger.add_progress(120.0)
            logger._do_update_event.set()
            time.sleep(0.02)
        finally:
            logger.stop()

        # Then
        log_messages = [args[0] for args, _ in mock_info.call_args_list]
        assert "[Test Task] Progress: 100.0%" in log_messages

    def test_it_should_store_progress_in_db(self, mocker, testdb, setup_pteam):
        # Given
        logger = self._create_logger(
            mocker,
            title="DB Test Task",
            pteam_id=self.pteam1.pteam_id,
            service_name="test_service",
            trigger=10,
        )

        # When
        try:
            time.sleep(0.02)

            initial = (
                testdb.query(models.SbomUploadProgress)
                .filter_by(pteam_id=str(self.pteam1.pteam_id), service_name="test_service")
                .one_or_none()
            )
            assert initial is not None
            assert initial.progress_rate == 0.0
            assert initial.created_at <= initial.updated_at

            logger.add_progress(50.0)
            logger._do_update_event.set()
            time.sleep(0.02)

            updated = self._refresh_and_get_progress(testdb, self.pteam1.pteam_id, "test_service")
            assert updated is not None
            assert updated.progress_rate == 0.5

            assert updated.created_at == initial.created_at
            assert updated.updated_at >= initial.updated_at

        finally:
            logger.stop()

        # Then
        after = self._refresh_and_get_progress(testdb, self.pteam1.pteam_id, "test_service")
        assert after is None
