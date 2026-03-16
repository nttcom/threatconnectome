import logging
import threading
from datetime import datetime, timezone

from app import models
from app.database import create_session


class TimeBasedProgressLogger:
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
        self.log_rate = 10
        self.interval_db_seconds = 60
        self.logger = logger or logging.getLogger(__name__)
        self.current_percent: float = 0.0
        self._stop_event = threading.Event()
        self.count = 0
        self.SessionLocal = create_session()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        # First Insert
        db = self.SessionLocal()
        try:
            progress = models.SbomUploadProgress(
                pteam_id=self.pteam_id,
                service_name=self.service_name,
                progress_rate=0.0,
                created_at=datetime.now(timezone.utc),
            )
            db.add(progress)
            db.commit()
        finally:
            db.close()

        while True:
            if self._stop_event.wait(self.interval_db_seconds):
                break

            db = self.SessionLocal()
            try:
                progress = (
                    db.query(models.SbomUploadProgress)
                    .filter_by(
                        pteam_id=self.pteam_id,
                        service_name=self.service_name,
                    )
                    .first()
                )
                if not progress:
                    continue

                percent = min(self.current_percent, 100.0)

                # Update DB
                progress.progress_rate = percent / 100.0
                progress.updated_at = datetime.now(timezone.utc)
                db.commit()

                # Log (throttled)
                self.count += 1
                if self.count % self.log_rate == 0:
                    self.logger.info(f"[{self.title}] Progress: {percent:.1f}%")

            finally:
                db.close()

    def add_progress(self, percent: float):
        self.current_percent += percent

    def stop(self):
        self._stop_event.set()

        db = self.SessionLocal()
        try:
            progress = (
                db.query(models.SbomUploadProgress)
                .filter_by(
                    pteam_id=self.pteam_id,
                    service_name=self.service_name,
                )
                .first()
            )
            if progress:
                db.delete(progress)
                db.commit()
        finally:
            db.close()
