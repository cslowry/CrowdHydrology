import django_rq
from django.conf import settings
from django.core.management.base import BaseCommand

# from django.utils import timezone
from loguru import logger

from workers.tasks import generate_all_stations_csv


class Command(BaseCommand):
    help = "Sets up periodic tasks using RQ Scheduler"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            type=str,
            help="Directory to save CSV files.",
            default=settings.STATION_DATA_DIR,
        )

    def handle(self, *args, **options):
        queue = django_rq.get_queue("default")
        save_directory = options["dir"]

        logger.info("Enqueuing batch CSV generation job.")
        queue.enqueue(generate_all_stations_csv, save_directory)
        logger.info("Job enqueued.")
