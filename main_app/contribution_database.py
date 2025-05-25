#!/util/python3/bin/python

import uuid

from django.utils import timezone

from main_app.models import InvalidSMSContribution, SMSContribution, Station

"""
Functions to set up a database and save contributions to the database.

@author Arthur De Araujo
@contact adearauj@buffalo.edu
@github github.com/wafflez180

Created: 06/18/2018
"""


def save_contribution(
    is_valid, station_id, water_height, temperature, phone_number, message_body
):
    hashed_phone_number = str(uuid.uuid3(uuid.NAMESPACE_OID, phone_number[-10:]))
    if water_height:
        water_height = float(water_height)

    if is_valid:
        station = Station.objects.get(id=station_id)
        new_contributon = SMSContribution(
            contributor_id=hashed_phone_number,
            station=station,
            water_height=water_height,
            temperature=temperature,
            date_received=timezone.localtime(),
        )
        new_contributon.save()
    else:
        new_invalid_contribution = InvalidSMSContribution(
            contributor_id=hashed_phone_number,
            message_body=message_body,
            date_received=timezone.localtime(),
        )
        new_invalid_contribution.save()

    # ToDo: Consider executing graph generation less because it takes a lot of computation
    # if is_valid:
    # graphs.generate()
    print("Saved new contribution.")
