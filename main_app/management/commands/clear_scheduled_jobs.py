import django_rq
from django.core.management.base import BaseCommand
from django_rq.queues import DjangoScheduler
from loguru import logger
from rq.job import Job


class Command(BaseCommand):
    help = "Sets up periodic tasks using RQ Scheduler"

    # clear with all option or id option.
    def add_arguments(self, parser):
        parser.add_argument("--id", type=str, help="ID of the scheduled job to clear.")
        parser.add_argument(
            "--all", action="store_true", help="Clear all scheduled jobs."
        )

    def handle(self, *args, **options):
        # scheduler: DjangoScheduler = django_rq.get_scheduler()
        # # empty scheduler quuee
        # for job in scheduler.get_jobs():
        #     scheduler.cancel(job)
        # logger.info("Cleared all scheduled jobs.")
        job_id = options.get("id")
        clear_all = options.get("all", False)
        scheduler: DjangoScheduler = django_rq.get_scheduler()
        if clear_all:
            for job in scheduler.get_jobs():
                scheduler.cancel(job)
            logger.info("Cleared all scheduled jobs.")
        elif job_id:
            # iterate and find job
            job = Job.fetch(job_id, connection=scheduler.connection)
            if job:
                scheduler.cancel(job)
                logger.info(f"Cleared scheduled job with ID: {job_id}")
            else:
                logger.warning(f"No scheduled job found with ID: {job_id}")
        else:
            logger.error(
                "Please provide either --id to clear a specific job or --all to clear all jobs."
            )
