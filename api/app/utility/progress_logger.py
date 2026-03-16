import logging
import threading
from datetime import datetime, timezone

from app import models, persistence
from app.database import create_session


class TimeBasedProgressLogger:
    LOG_TRIGGER_COUNT = 10
    INTERVAL_DB_SECONDS = 60

    def __init__(
        self,
        title: str,
        pteam_id: str | None = None,
        service_name: str | None = None,
        logger=None,
    ):
        self.title = title
        self.pteam_id = pteam_id
        self.service_name = service_name
        self.logger = logger or logging.getLogger(__name__)
        self.current_percent: float = 0.0
        self._stop_event = threading.Event()
        self.count = 0
        self.SessionLocal = create_session()

        # First Insert
        with self.SessionLocal() as db:
            progress = models.SbomUploadProgress(
                pteam_id=self.pteam_id,
                service_name=self.service_name,
                progress_rate=0.0,
                created_at=datetime.now(timezone.utc),
            )
            db.add(progress)
            db.commit()
            self.sbom_upload_progress_id = progress.sbom_upload_progress_id
            self._progress = progress

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(self.INTERVAL_DB_SECONDS)
            self._update_progress_in_db()

    def _update_progress_in_db(self):
        percent = min(self.current_percent, 100.0)

        with self.SessionLocal() as db:
            progress = db.merge(self._progress)
            progress.progress_rate = percent / 100.0
            progress.updated_at = datetime.now(timezone.utc)
            db.commit()

        self.count += 1
        if self.count % self.LOG_TRIGGER_COUNT == 0:
            self.logger.info(f"[{self.title}] Progress: {percent:.1f}%")

    def add_progress(self, percent: float):
        self.current_percent += percent

    def stop(self):
        self._stop_event.set()

        with self.SessionLocal() as db:
            progress = persistence.get_sbom_upload_progress_by_id(db, self.sbom_upload_progress_id)
            if progress:
                db.delete(progress)
                db.commit()
