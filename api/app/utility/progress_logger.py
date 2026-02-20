import logging
import threading


class TimeBasedProgressLogger:
    def __init__(self, title: str, interval_seconds: float = 600.0, logger=None):
        """
        title: Title of the progress task.
        interval_seconds: Interval (in seconds) at which progress logs should be emitted.
        logger: Optional logger instance. If not provided, the default logger is used.
        """
        self.title = title
        self.interval_seconds = interval_seconds
        self.logger = logger or logging.getLogger(__name__)
        self.current_percent: float = 0.0
        self._stop_event = threading.Event()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while True:
            if self._stop_event.wait(self.interval_seconds):
                break
            percent = min(self.current_percent, 100.0)
            self.logger.info(f"[{self.title}] Progress: {percent:.1f}%")

    def add_progress(self, percent: float):
        self.current_percent += percent

    def stop(self):
        self._stop_event.set()
