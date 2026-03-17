import logging
import threading
from datetime import datetime, timezone

from app import models, persistence
from app.database import create_session

SessionLocal = create_session()


class TimeBasedProgressLogger:
    LOG_TRIGGER_COUNT = 10
    INTERVAL_DB_SECONDS = 60

    def __init__(
        self,
        title: str,
        pteam_id: str | None = None,
        service_name: str | None = None,
        logger=None,
        session_factory=None,
    ):
        """
        title: Title of the progress task.
        interval_seconds: Interval (in seconds) at which progress logs should be emitted.
        logger: Optional logger instance. If not provided, the default logger is used.
        """
        self.title = title
        self.pteam_id = pteam_id
        self.service_name = service_name
        self.logger = logger or logging.getLogger(__name__)
        self.current_percent: float = 0.0
        self._stop_event = threading.Event()
        self.count = 0

        self._db_enabled = self.pteam_id is not None and self.service_name is not None
        if self._db_enabled:
            self._SessionLocal = session_factory or SessionLocal
            self.sbom_upload_progress_id: str | None = None
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        else:
            self._SessionLocal = None

    def _run(self):
        db = None
        try:
            with self._SessionLocal() as db:
                # First Insert
                progress = self._create_initial_progress(db)
                # Loop to periodically record progress
                while True:
                    if self._stop_event.wait(self.INTERVAL_DB_SECONDS):
                        break
                    self._update_progress_in_db(db, progress)
        except Exception:
            self.logger.error("Failed uploading SBOM as a service: %s", self.service_name)
            if db is not None:
                try:
                    db.rollback()
                except Exception:
                    self.logger.exception(
                        "[%s] Failed to rollback DB session in TimeBasedProgressLogger",
                        self.title,
                    )
            self._stop_event.set()

    def _create_initial_progress(self, db) -> models.SbomUploadProgress:
        progress = models.SbomUploadProgress(
            pteam_id=self.pteam_id,
            service_name=self.service_name,
            progress_rate=0.0,
            created_at=datetime.now(timezone.utc),
        )
        persistence.create_sbom_upload_progress(db, progress)
        self.sbom_upload_progress_id = progress.sbom_upload_progress_id
        return progress

    def _update_progress_in_db(self, db, progress):
        percent = min(self.current_percent, 100.0)
        persistence.update_sbom_upload_progress(
            db,
            progress,
            percent / 100.0,
        )

        self.count += 1
        if self.count % self.LOG_TRIGGER_COUNT == 0:
            self.logger.info(f"[{self.title}] Progress: {percent:.1f}%")

    def add_progress(self, percent: float):
        self.current_percent += percent

    def stop(self):
        if not getattr(self, "_db_enabled", False):
            return

        self._stop_event.set()

        # Wait for worker thread to finish if it exists
        if hasattr(self, "_thread") and self._thread is not None:
            self._thread.join()

        # After thread finishes, check and delete DB record
        if self.sbom_upload_progress_id is None:
            return

        with self._SessionLocal() as db:
            persistence.delete_sbom_upload_progress_by_id(db, self.sbom_upload_progress_id)
