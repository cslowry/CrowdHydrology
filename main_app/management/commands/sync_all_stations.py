import django_rq
from django.core.management.base import BaseCommand

# from django.utils import timezone
from loguru import logger

from workers.tasks import generate_all_stations_csv


class Command(BaseCommand):
    help = "Generates CSV files for all stations using the configured storage backend"

    def add_arguments(self, parser):
        # No arguments needed - storage backend is configured in secrets.yaml
        pass

    def handle(self, *args, **options):
        queue = django_rq.get_queue("default")

        logger.info("Enqueuing batch CSV generation job.")
        queue.enqueue(generate_all_stations_csv)
        logger.info("Job enqueued.")
