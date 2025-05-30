# Generated by Django 2.0.5 on 2019-01-08 17:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main_app", "0014_auto_20180716_1151"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="invalidsmscontribution",
            unique_together={("contributor_id", "message_body", "date_received")},
        ),
        migrations.AlterUniqueTogether(
            name="smscontribution",
            unique_together={
                (
                    "contributor_id",
                    "station",
                    "water_height",
                    "temperature",
                    "date_received",
                )
            },
        ),
    ]
