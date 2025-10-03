import logging
from datetime import datetime, timedelta
from threading import Event

from apscheduler.schedulers.background import BackgroundScheduler

log = logging.getLogger("marketing_project.core")


class Scheduler:
    def __init__(self):
        log.info("Initializing Scheduler.")
        self._sched = BackgroundScheduler()
        self._sched.start()
        # keep the process alive if you run in "serve" mode
        self._stop_event = Event()
        log.debug("Scheduler started and stop event created.")

    def schedule_job(self, job_func, job_id: str, run_date: datetime = None):
        """
        Schedule a job to run at a specific time or immediately.

        Args:
            job_func: Function to execute
            job_id: Unique identifier for the job
            run_date: When to run the job (if None, runs immediately)
        """
        if run_date is None:
            run_date = datetime.now() + timedelta(minutes=1)

        log.info(f"Scheduling job '{job_id}' at {run_date}")
        try:
            self._sched.add_job(
                job_func,
                trigger="date",
                run_date=run_date,
                id=job_id,
                replace_existing=True,
            )
            log.debug(f"Job '{job_id}' scheduled successfully.")
        except Exception as e:
            log.error(f"Failed to schedule job '{job_id}': {e}")
            raise

    def shutdown(self):
        log.info("Shutting down Scheduler.")
        self._sched.shutdown()
        self._stop_event.set()
        log.debug("Scheduler shutdown complete and stop event set.")

    def wait_forever(self):
        log.info("Scheduler entering wait_forever mode (container will stay alive).")
        # call this if you want your container to stay alive
        self._stop_event.wait()
        log.info("Scheduler wait_forever event released.")
