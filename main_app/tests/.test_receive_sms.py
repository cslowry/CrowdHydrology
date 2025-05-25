import datetime

from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from main_app.models import Station
from main_app.receive_sms import incoming_sms
from main_app.survey import Survey, SurveyDistribution, on_survey_received


def create_mock_request(body, _from):
    request = HttpRequest()
    request.method = "POST"
    request.POST["Body"] = body
    request.POST["From"] = _from

    return request


class TestReceiveSMS(TestCase):
    def setUp(self):
        self.phone_number = "+17165552022"
        self.survey_distribution = SurveyDistribution(
            Survey.IMPROVE_CROWDHYDROLOGY, self.phone_number
        )
        self.survey_link = self.survey_distribution.get_link()
        self.response_id = "R_123456"
        self.station_id = "NY9999"
        self.request_body = self.station_id + " 2.05"

        # Create mock station object for contribution
        self.station = Station.objects.create(
            id=self.station_id,
            name=self.station_id,
            loc_latitude=0,
            loc_longitude=0,
            upper_bound=5,
            lower_bound=0,
            date_added=timezone.now(),
        )

    @override_settings(DEBUG=True)
    def test_incoming_sms_first_contribution(self):
        """
        incoming_sms returns a message containing the IMPROVE_CROWDHYDROLOGY survey message if the phone number has not yet made a contribution
        """
        request = create_mock_request(self.request_body, self.phone_number)
        response = incoming_sms(request)
        self.assertContains(response, self.survey_link)

    @override_settings(DEBUG=True)
    def test_incoming_sms_second_recent_contribution(self):
        """
        incoming_sms returns a message without the IMPROVE_CROWDHYDROLOGY survey message if the phone number has recently been sent the survey
        """
        self.survey_distribution.on_sent()

        request = create_mock_request(self.request_body, self.phone_number)
        response = incoming_sms(request)
        self.assertNotContains(response, self.survey_link)

    @override_settings(DEBUG=True)
    def test_incoming_sms_second_unrecent_contribution(self):
        """
        incoming_sms returns a message with the IMPROVE_CROWDHYDROLOGY survey message if the phone number has not recently been sent the survey
        """
        unrecent = timezone.localtime() - datetime.timedelta(days=50)
        self.survey_distribution.on_sent(lambda: unrecent)

        request = create_mock_request(self.request_body, self.phone_number)
        incoming_sms(request)
        response = incoming_sms(request)
        self.assertNotContains(response, self.survey_link)

    @override_settings(DEBUG=True)
    def test_incoming_sms_second_unrecent_contribution_after_received(self):
        """
        incoming_sms returns a message without the IMPROVE_CROWDHYDROLOGY survey message if the phone number has not recently been sent the survey and has sent a response
        """
        unrecent = timezone.localtime() - datetime.timedelta(days=50)
        self.survey_distribution.on_sent(lambda: unrecent)
        on_survey_received(
            self.survey_distribution.get_survey_id(),
            self.response_id,
            self.survey_distribution.get_contributor_id(),
        )

        request = create_mock_request(self.request_body, self.phone_number)
        incoming_sms(request)
        response = incoming_sms(request)
        self.assertNotContains(response, self.survey_link)
