import logging

from apscheduler.schedulers.background import (
    BackgroundScheduler,
)
from apscheduler.triggers.interval import (
    IntervalTrigger,
)

from app.services.trip_scheduler_service import (
    run_trip_scheduler_cycle,
)


logger = logging.getLogger(__name__)


trip_scheduler = BackgroundScheduler(
    timezone="UTC",
)


def start_trip_scheduler() -> None:
    if trip_scheduler.running:
        return

    trip_scheduler.add_job(
        run_trip_scheduler_cycle,
        trigger=IntervalTrigger(seconds=30),
        id="trip-status-scheduler",
        name="Update trip statuses and create next trips",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    # Run once immediately when the application starts.
    run_trip_scheduler_cycle()

    trip_scheduler.start()

    logger.info("Trip scheduler started.")


def stop_trip_scheduler() -> None:
    if not trip_scheduler.running:
        return

    trip_scheduler.shutdown(wait=False)

    logger.info("Trip scheduler stopped.")