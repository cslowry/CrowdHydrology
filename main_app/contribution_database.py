#!/util/python3/bin/python

import uuid
from typing import Optional, Union

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
    hashed_phone_number = hash_phone_number(phone_number)
    if water_height:
        water_height = float(water_height)

    if is_valid:
        station = get_station_by_id(station_id)
        save_valid_contribution(hashed_phone_number, station, temperature, water_height)
    else:
        save_invalid_contribution(hashed_phone_number, message_body)

    # ToDo: Consider executing graph generation less because it takes a lot of computation
    # if is_valid:
    # graphs.generate()


def save_invalid_contribution(hashed_phone_number, message_body):
    new_invalid_contribution = InvalidSMSContribution(
        contributor_id=hashed_phone_number,
        message_body=message_body,
        date_received=timezone.localtime(),
    )
    new_invalid_contribution.save()


def save_valid_contribution(
    hashed_phone_number: str,
    station: Station,
    water_height: float,
    temperature: Optional[float] = None,
) -> SMSContribution:
    new_contributon = SMSContribution(
        contributor_id=hashed_phone_number,
        station=station,
        water_height=water_height,
        temperature=temperature,
        date_received=timezone.localtime(),
    )
    new_contributon.save()
    return new_contributon


def get_station_by_id(station_id) -> Union[Station, None]:
    # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#first
    station = Station.objects.filter(id=station_id).first()
    return station


def hash_phone_number(phone_number: str) -> str:
    hashed_phone_number = str(uuid.uuid3(uuid.NAMESPACE_OID, phone_number[-10:]))
    return hashed_phone_number
