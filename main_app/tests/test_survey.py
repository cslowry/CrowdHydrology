import datetime
import random
import string

from django.http import HttpRequest, QueryDict
from django.test import TestCase
from django.utils import timezone

from main_app.models import SurveyReceived, SurveySent
from main_app.survey import (
    Survey,
    SurveyDistribution,
    incoming_survey,
    on_survey_received,
)


def create_mock_request(survey_id, response_id, contributor_id):
    request = HttpRequest()
    request.method = "POST"
    request.POST = QueryDict(
        "SurveyID={}&ResponseID={}&ResponseEventContext={}&Status={}".format(
            survey_id, response_id, contributor_id, "Complete"
        )
    )
    request.META = {"REMOTE_ADDR": "162.247.216.1"}

    return request


class TestSurvey(TestCase):
    def setUp(self):
        self.survey_distribution = SurveyDistribution(
            Survey.IMPROVE_CROWDHYDROLOGY, "+17165552022"
        )
        self.survey_id = self.survey_distribution.get_survey_id()
        self.contributor_id = self.survey_distribution.get_contributor_id()
        self.phone_number = "+17165552022"
        self.response_id = "R_123456789012345"
        self.survey_url = "https://qualtrics.uvm.edu/jfe/form/SV_1ImGl1K50tzcEg6"

    def test_on_survey_received(self):
        """
        on_survey_received updates the contents of the database to add a new SurveyReceived item
        """
        on_survey_received(self.survey_id, self.response_id, self.contributor_id)
        exists = SurveyReceived.objects.filter(
            survey_id=self.survey_id,
            response_id=self.response_id,
            contributor_id=self.contributor_id,
        ).exists()
        self.assertTrue(exists)

    def test_on_survey_received_no_ssid(self):
        """
        on_survey_received updates the contents of the database to add a new SurveyReceived item even if no cid is supplied
        """
        on_survey_received(self.survey_id, self.response_id, None)
        exists = SurveyReceived.objects.filter(
            survey_id=self.survey_id, response_id=self.response_id
        ).exists()
        self.assertTrue(exists)

    def test_on_survey_received_duplicate_response(self):
        """
        on_survey_received does not update the contents of the database to add a duplicate SurveyReceived item
        """
        on_survey_received(self.survey_id, self.response_id, self.contributor_id)
        on_survey_received(self.survey_id, self.response_id, None)
        on_survey_received(self.survey_id, self.response_id, self.contributor_id)
        on_survey_received(self.survey_id, self.response_id, None)
        received_set = SurveyReceived.objects.filter(
            survey_id=self.survey_id, response_id=self.response_id
        )
        self.assertEqual(len(received_set), 1)

    def test_survey_distribution_on_sent(self):
        """
        on_sent updates the contents of the database to add a new SurveySent item
        """
        self.survey_distribution.on_sent()
        exists = SurveySent.objects.filter(
            survey_id=self.survey_id, contributor_id=self.contributor_id
        ).exists()
        self.assertTrue(exists)

    def test_survey_distribution_get_link(self):
        """
        get_link returns a string containing the appropriate survey URL
        """
        link = self.survey_distribution.get_link()
        self.assertIn(self.survey_url, link)
        self.assertIn(str(self.contributor_id), link)

    def test_survey_distribution_should_send(self):
        """
        should_send returns True if the phone number has never been sent the survey
        """
        should = self.survey_distribution.should_send()
        self.assertTrue(should)

    def test_survey_distribution_should_send_sent_recently(self):
        """
        should_send returns False if the phone number has recently been sent the survey
        """
        self.survey_distribution.on_sent()
        should = self.survey_distribution.should_send()
        self.assertFalse(should)

    def test_survey_distribution_should_send_sent_unrecently(self):
        """
        should_send returns True if the phone number has unrecently been sent the survey
        """
        unrecently = timezone.localtime() - datetime.timedelta(days=50)
        self.survey_distribution.on_sent(lambda: unrecently)
        should = self.survey_distribution.should_send()
        self.assertTrue(should)

    def test_survey_distrubtion_should_send_sent_recently_and_received(self):
        """
        should_send returns False if the phone number has recently been sent the survey and has responded
        """
        self.survey_distribution.on_sent()
        on_survey_received(self.survey_id, self.response_id, self.contributor_id)
        should = self.survey_distribution.should_send()
        self.assertFalse(should)

    def test_survey_distribution_should_send_sent_unrecently_and_received(self):
        """
        should_send_survey returns False if the phone number has unrecently been sent the survey and has responded
        """
        unrecently = timezone.localtime() - datetime.timedelta(days=50)
        self.survey_distribution.on_sent(lambda: unrecently)
        on_survey_received(self.survey_id, self.response_id, self.contributor_id)
        should = self.survey_distribution.should_send()
        self.assertFalse(should)

    def test_incoming_survey(self):
        """
        incoming_survey returns HTTP response with status code 200 and updates database with survey data
        """
        request = create_mock_request(
            self.survey_id, self.response_id, self.contributor_id
        )
        response = incoming_survey(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.survey_distribution.should_send())

    def test_survey_under_stress(self):
        """
        survey.py should handle stressful sequence of requests
        """
        N = 100
        phone_numbers = [
            "+1" + str(random.randint(1000000000, 9999999999)) for _ in range(N)
        ]
        distributions = [
            SurveyDistribution(Survey.IMPROVE_CROWDHYDROLOGY, n) for n in phone_numbers
        ]

        for dist in distributions:
            self.assertTrue(dist.should_send())

        for dist in distributions[: N // 2]:
            dist.on_sent()

        for dist in distributions[N // 4 : 3 * N // 4]:
            response_id = "R_" + "".join(random.choices(string.ascii_lowercase, k=15))
            on_survey_received(
                dist.get_survey_id(), response_id, dist.get_contributor_id()
            )

        for i, dist in enumerate(distributions):
            self.assertEqual(dist.should_send(), i >= 3 * N // 4)
