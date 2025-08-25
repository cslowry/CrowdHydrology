#!/util/python3/bin/python
import random
import uuid
from typing import Optional, Union

from django.utils import timezone

from crowd_hydrology.settings import redis_conn
from main_app.exceptions import OTPExpiredException
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
) -> Union[SMSContribution, InvalidSMSContribution]:
    hashed_phone_number = hash_phone_number(phone_number)
    if water_height:
        water_height = float(water_height)

    if is_valid:
        station = get_station_by_id(station_id)
        return save_valid_contribution(
            hashed_phone_number=hashed_phone_number,
            station=station,
            water_height=water_height,
            temperature=temperature,
        )
        # return save_valid_contribution(hashed_phone_number, station, temperature, water_height)
    else:
        return save_invalid_contribution(hashed_phone_number, message_body)

    # ToDo: Consider executing graph generation less because it takes a lot of computation
    # if is_valid:
    # graphs.generate()


def save_invalid_contribution(
    hashed_phone_number, message_body
) -> InvalidSMSContribution:
    new_invalid_contribution = InvalidSMSContribution(
        contributor_id=hashed_phone_number,
        message_body=message_body,
        date_received=timezone.localtime(),
    )
    new_invalid_contribution.save()
    return new_invalid_contribution


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


def update_sms_contribution(
    _id: int,
    station: Station,
    water_height: float,
    temperature: float = None,
):
    contribution = SMSContribution.objects.filter(id=_id).first()
    contribution.station = station
    contribution.water_height = water_height
    contribution.temperature = temperature
    return contribution


def get_station_by_id(station_id) -> Union[Station, None]:
    # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#first
    station = Station.objects.filter(id=station_id).first()
    return station


def hash_phone_number(phone_number: str) -> str:
    hashed_phone_number = str(uuid.uuid3(uuid.NAMESPACE_OID, phone_number[-10:]))
    return hashed_phone_number


def get_success_contribution_message(contribution: SMSContribution, otp: int):
    return (
        f"Thanks for contributing to CrowdHydrology research and being a citizen scientist! "
        f"Your contribution was saved with the following details: \n"
        f"Station ID: {contribution.station.id}\n"
        f"Water Height: {contribution.water_height} ft\n\n"
        f"If the values seem incorrect, please send another message in format: \n"
        f"`update OTP STATION ID WATER_HEIGHT`\n"
        f"Your OTP is {otp}. NOTE: OTP is valid for 24 hours."
    )


def get_update_contribution_message(contribution, otp):
    return (
        f"Thanks for contributing to CrowdHydrology research and being a citizen scientist! \n\n"
        f"Your contribution was update with the following details: \n"
        f"Station ID: {contribution.station.id}\n"
        f"Water Height: {contribution.water_height} ft\n\n"
        f"If the values seem incorrect, please send another message in format: \n"
        f"`update OTP STATION ID WATER_HEIGHT`\n"
        f"Your OTP is {otp}. NOTE: OTP is valid for 24 hours after you first submitted your contribution."
    )


def generate_contribution_otp():
    otp = random.randint(1000, 9999)
    while redis_conn.get(otp):
        otp = random.randint(1000, 9999)
    return otp


def map_otp_to_contribution(otp: int, contribution_id: int, ttl=86400) -> None:
    """Map OTP to contribution ID with expiration time."""

    # TODO: set expire time in environment variable.
    redis_conn.setex(name=otp, time=ttl, value=contribution_id)


def get_contribution_by_otp(otp: int):
    contribution = redis_conn.get(otp)
    if not contribution:
        raise OTPExpiredException()
