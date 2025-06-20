"""
Progress.py: Thread-safe progress tracking for dataset generation jobs.
"""
import threading

class ProgressTracker:
    def __init__(self):
        self._progress = {}
        self._lock = threading.Lock()

    def start_job(self, job_id, total_steps):
        with self._lock:
            self._progress[job_id] = {
                "current": 0,
                "total": total_steps,
                "status": "started",
                "message": "Job started"
            }

    def update(self, job_id, current, message=None):
        with self._lock:
            if job_id in self._progress:
                self._progress[job_id]["current"] = current
                if message:
                    self._progress[job_id]["message"] = message  # No emoji, just message

    def complete(self, job_id):
        with self._lock:
            if job_id in self._progress:
                self._progress[job_id]["status"] = "complete"
                self._progress[job_id]["message"] = "Job complete"

    def get(self, job_id):
        with self._lock:
            return self._progress.get(job_id, None)

progress_tracker = ProgressTracker()