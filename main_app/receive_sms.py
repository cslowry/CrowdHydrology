#!/util/python3/bin/python

from django_twilio.decorators import twilio_view
from twilio.twiml.messaging_response import MessagingResponse

from main_app import contribution_database as database
from main_app import crowdhydrology_website_database as website_database
from main_app.models import Station

"""
Functions to receive and parse sms.

@author Arthur De Araujo
@contact adearauj@buffalo.edu
@github github.com/wafflez180

Created: 06/18/2018
"""


@twilio_view  # Visit link for more info https://www.twilio.com/blog/2014/04/building-a-simple-sms-message-application-with-twilio-and-django-2.html
def incoming_sms(request):
    # Get the text message the user sent to our Twilio number
    message_body = request.POST.get("Body", None)
    phone_number = request.POST.get("From", None)

    is_valid, station_id, water_height, temperature, error_msg = parse_sms(message_body)

    # Start our TwiML response
    resp = MessagingResponse()

    if is_valid:
        reply_msg = "Thanks for contributing to CrowdHydrology research and being a citizen scientist!"
        reply_msg += (
            "\n\nCheck out the contributions at your station: http://crowdhydrology.com/charts/"
            + str(station_id)
            + "_dygraph.html"
        )

        # To reenable survey distribution, uncomment this block
        """
        survey_distribution = SurveyDistribution(Survey.IMPROVE_CROWDHYDROLOGY, phone_number)
        if survey_distribution.should_send():
            link = survey_distribution.get_link()
            reply_msg += "\n\n" + "You can help us improve CrowdHydrology by completing this survey: " + link

            # TODO: verify that survey is actually sent using callback URL before updating DB
            survey_distribution.on_sent()
        """

        resp.message(reply_msg)
        # TODO: Maybe randomize a funny science joke after

        print("Recieved a valid sms")
        print(
            "\tSMS data:\n\t\tStation: ",
            station_id,
            "\n\t\tWater height: ",
            water_height,
        )
    else:
        resp.message(error_msg)

    # print('STATION: '+station_id)
    # Asynchronously call to save the data to allow the reply text message to be sent immediately
    # mp.Pool().apply_async(database.save_contribution, (is_valid, station_id, water_height, temperature, phone_number, message_body))

    database.save_contribution(
        is_valid, station_id, water_height, temperature, phone_number, message_body
    )
    if is_valid:
        website_database.save_contributions_to_csv(station_id)

    return str(resp)


def parse_sms(message):
    US_STATES = [
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]

    temperature = None
    error_msg = (
        "Whoopsies! We couldn't read your measurement properly.\n Format: NY1000 2.5"
    )

    message = message.upper()

    message_list = message.strip().split(" ")

    # Check if the message has at least a station and one measurement
    if len(message_list) < 2:
        return False, None, None, None, error_msg

    # Check if the station string does not contain a state abbreviation
    if not any(state in message for state in US_STATES):
        return False, None, None, None, error_msg

    # Get the station_id, remove it from the message and then parse the rest
    try:
        station_id = ""
        for state in US_STATES:
            state_abreviation_loc = message.find(state)
            if state_abreviation_loc != -1:
                station_id = message[state_abreviation_loc : state_abreviation_loc + 6]
                # Handle case when message has a space in between the state and id = "NY 1000"
                if hasWhiteSpace(station_id):
                    station_id = message[
                        state_abreviation_loc : state_abreviation_loc + 7
                    ]
                message = message.replace(station_id, "").strip()
                station_id = station_id.replace(" ", "")
    except Exception:
        return False, None, None, None, error_msg

    # Check if the station exists
    try:
        # print(station_id)
        station = Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        return (
            False,
            None,
            None,
            None,
            "Whoopsies! We couldn't find a station with that ID.\n Format: NY1000 2.5",
        )

    # print("THIS IS THE STATION: "+station_id)
    # Parse the measurements, if there are 2 then figure out which is temperature and water height
    try:
        message_measurements_list = message.split()
        # Only one measurement sent
        if len(message_measurements_list) == 1:
            if float(message) <= station.upper_bound:
                water_height = float(message)
                temperature = None
            else:
                water_height = None
                temperature = float(message)
        else:
            # Check which of the 2 measurements is below 32.0, temperature doesn't go below 32.0
            if float(message_measurements_list[0]) <= 32.0:
                water_height = float(message_measurements_list[0])
                temperature = float(message_measurements_list[1])
            else:
                water_height = float(message_measurements_list[1])
                temperature = float(message_measurements_list[0])
    except Exception:
        return False, None, None, None, error_msg

    if temperature and (temperature >= 150.0 or temperature <= 32.0):
        return (
            False,
            None,
            None,
            None,
            "Whoopsies! That temperature measurement is out of bounds!\n\n Please re-submit with a valid temperature measurement. \n Format: NY1000 2.5 80.0",
        )

    if water_height and (
        water_height > station.upper_bound or water_height < station.lower_bound
    ):
        return (
            False,
            None,
            None,
            None,
            "Whoopsies! That water height measurement is out of bounds!\n\n Please re-submit with a valid water height measurement. \n Format: NY1000 2.5",
        )

    return True, station_id, water_height, temperature, error_msg


def hasWhiteSpace(s):
    return s.find(" ") >= 0
