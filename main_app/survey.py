import datetime
import re
import uuid
from enum import IntEnum
from ipaddress import ip_address, ip_network

from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from main_app.models import SurveyReceived, SurveySent


class Survey(IntEnum):
    IMPROVE_CROWDHYDROLOGY = 1


class SurveyDistribution:
    def __init__(self, survey, phone_number):
        self.survey_id = {Survey.IMPROVE_CROWDHYDROLOGY: "SV_1ImGl1K50tzcEg6"}[survey]
        self.phone_number = phone_number
        self.contributor_id = uuid.uuid3(uuid.NAMESPACE_OID, phone_number[-10:])
        self.link = {
            Survey.IMPROVE_CROWDHYDROLOGY: "https://qualtrics.uvm.edu/jfe/form/SV_1ImGl1K50tzcEg6?ResponseEventContext={}"
        }[survey].format(str(self.contributor_id))

    def should_send(self):
        recent_lower_bound = timezone.localtime() - datetime.timedelta(days=30)

        sent_survey_recently = SurveySent.objects.filter(
            survey_id=self.survey_id,
            contributor_id=self.contributor_id,
            date_sent__gte=recent_lower_bound,
        ).exists()
        received_survey = SurveyReceived.objects.filter(
            survey_id=self.survey_id, contributor_id=self.contributor_id
        ).exists()

        return not sent_survey_recently and not received_survey

    def get_survey_id(self):
        return self.survey_id

    def get_link(self):
        return self.link

    def get_contributor_id(self):
        return self.contributor_id

    def on_sent(self, time_func=timezone.localtime):
        SurveySent.objects.create(
            survey_id=self.survey_id,
            contributor_id=self.contributor_id,
            date_sent=time_func(),
        )


# Qualtrics network addresses based on https://www.qualtrics.com/support/integrations/api-integration/using-qualtrics-api-documentation
def in_qualtrics_network(addr):
    ip_addr = ip_address(addr)
    qualtrics_networks = [
        ip_network("139.60.152.0/22"),
        ip_network("64.69.212.0/24"),
        ip_network("162.247.216.0/22"),
        ip_network("98.97.248.0/21"),
    ]

    return any(ip_addr in network for network in qualtrics_networks)


def on_survey_received(
    survey_id, response_id, contributor_id, time_func=timezone.localtime
):
    try:
        with transaction.atomic():
            SurveyReceived.objects.create(
                survey_id=survey_id,
                response_id=response_id,
                contributor_id=contributor_id,
                date_received=time_func(),
            )
    except IntegrityError:
        return


@csrf_exempt
def incoming_survey(request):
    response = HttpResponse()

    # Endpoint only accepts posted form data
    if request.method != "POST":
        response.status_code = 405
        return response

    formData = request.POST
    survey_id = formData.get("SurveyID")
    response_id = formData.get("ResponseID")
    contributor_id = formData.get("ResponseEventContext")
    status = formData.get("Status")

    r = re.compile(r"^SV_\w{15}$")
    if not survey_id or not r.match(survey_id):
        response.status_code = 400
        return response

    r = re.compile(r"^R_\w{15}$")
    if not response_id or not r.match(response_id):
        response.status_code = 400
        return response

    # Limit requests to those from Qualtrics network
    # to reduce possibility of request forgery
    remote_addr = request.META.get("REMOTE_ADDR")
    if remote_addr is None or not in_qualtrics_network(remote_addr):
        # TODO: log this w/ the IP address, survey ID, response ID, and status
        response.status_code = 403
        return response

    try:
        contributor_id = uuid.UUID(contributor_id)
    except Exception:
        contributor_id = None

    if status == "Complete":
        on_survey_received(survey_id, response_id, contributor_id)

    return response
