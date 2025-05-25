from django.db import models
from django.utils import timezone
from localflavor.us.us_states import STATE_CHOICES

# Create your models here.


class Sponsor(models.Model):
    name = models.CharField(max_length=200)
    picture = models.ImageField(upload_to="station_sponsor_pics", blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Station(models.Model):
    id = models.CharField(max_length=200, primary_key=True, unique=True)
    name = models.CharField(max_length=200)
    station_pic = models.ImageField(upload_to="station_pics", blank=True)
    state = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default="MI",
    )
    loc_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    loc_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    upper_bound = models.FloatField()
    lower_bound = models.FloatField()

    WATER_BODY_TYPE_CHOICES = (
        ("BR", "Brook"),
        ("CA", "Cave"),
        ("CR", "Creek"),
        ("LA", "Lake"),
        ("PO", "Pond"),
        ("RI", "River"),
    )
    water_body_type = models.CharField(
        max_length=2,
        choices=WATER_BODY_TYPE_CHOICES,
        default="RI",  # River
    )

    # CHECK
    STATUS_CHOICES = (
        ("OP", "Open"),
        ("CS", "Coming Soon"),
        ("UM", "Under Maintenance"),
        ("CD", "Closed"),
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default="OP",  # River
    )
    # status = models.CharField(max_length=200)

    date_added = models.DateField()
    sponsor_1 = models.ForeignKey(
        Sponsor,
        related_name="sponsorone",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    sponsor_2 = models.ForeignKey(
        Sponsor,
        related_name="sponsortwo",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{} : {}".format(self.id, self.name)


class SMSContribution(models.Model):
    contributor_id = models.UUIDField()
    station = models.ForeignKey(Station, on_delete=models.PROTECT)
    water_height = models.FloatField(null=True)
    temperature = models.FloatField(null=True, blank=True, default=None)
    date_received = models.DateTimeField(unique=True)

    def __str__(self):
        return "{} : w={} t={} ({})".format(
            self.station_id,
            self.water_height,
            self.temperature,
            timezone.localtime(self.date_received).strftime("%D %H:%M:%S"),
        )


class InvalidSMSContribution(models.Model):
    contributor_id = models.UUIDField()
    message_body = models.CharField(max_length=300)
    date_received = models.DateTimeField(unique=True)

    def __str__(self):
        return "{} ({})".format(
            self.message_body,
            timezone.localtime(self.date_received).strftime("%D %H:%M:%S"),
        )


class SurveySent(models.Model):
    survey_id = models.CharField(max_length=20)
    contributor_id = models.UUIDField()
    date_sent = models.DateTimeField()

    def __str__(self):
        return "sid={} cid={} ({})".format(
            self.survey_id, self.contributor_id, timezone.localtime(self.date_sent)
        )


class SurveyReceived(models.Model):
    survey_id = models.CharField(max_length=20)
    response_id = models.CharField(max_length=20, unique=True)
    contributor_id = models.UUIDField(null=True, blank=True)
    date_received = models.DateTimeField()

    def __str__(self):
        return "sid={} rid={} cid={} ({})".format(
            self.survey_id,
            self.response_id,
            self.contributor_id,
            timezone.localtime(self.date_received),
        )
