from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_rq import get_queue

from main_app.models import SMSContribution
from workers.tasks import generate_station_csv


@receiver(pre_save, sender=SMSContribution)
def capture_old_station(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = SMSContribution.objects.get(pk=instance.pk)
            if old_instance.station_id != instance.station_id:
                instance._old_station_id = old_instance.station_id
        except SMSContribution.DoesNotExist:
            pass


@receiver(post_save, sender=SMSContribution)
def trigger_csv_generation(sender, instance, created, **kwargs):
    queue = get_queue("default")
    queue.enqueue(generate_station_csv, instance.station.id)

    # If station changed, update the old station's CSV as well
    if hasattr(instance, "_old_station_id"):
        queue.enqueue(generate_station_csv, instance._old_station_id)
