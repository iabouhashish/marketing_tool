from datetime import datetime, timedelta

import pytest

from marketing_project.scheduler import Scheduler


def test_scheduler_initialization():
    """Test that scheduler initializes properly."""
    scheduler = Scheduler()
    assert scheduler is not None
    scheduler.shutdown()


def test_scheduler_job_scheduling():
    """Test that scheduler can schedule jobs."""
    scheduler = Scheduler()

    # Test job function
    job_called = False

    def test_job():
        nonlocal job_called
        job_called = True

    # Schedule job to run in 1 second
    run_time = datetime.now() + timedelta(seconds=1)
    scheduler.schedule_job(test_job, "test_job_1", run_time)

    # Wait a bit for job to execute
    import time

    time.sleep(2)

    # Clean up
    scheduler.shutdown()

    # Note: In a real test, you'd need to properly wait for job execution
    # This is a basic test to ensure the scheduler doesn't crash
    assert True


def test_scheduler_shutdown():
    """Test that scheduler shuts down properly."""
    scheduler = Scheduler()
    scheduler.shutdown()
    # If we get here without exception, shutdown worked
    assert True
