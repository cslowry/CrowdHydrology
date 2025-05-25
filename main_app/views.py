import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# from main_app import data_migrate_csv
# from main_app import twilio_csv_data_migration
# from main_app import send_CUAHSI_data
from main_app.models import SMSContribution, Station


# Create your views here.
@login_required
def index(request):
    return render(request, "main_app/index.html")


@login_required
def download(request):
    path = request.GET["path"]
    file_path = os.path.join(settings.STATIC_DIR, path)
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response[
                "Content-Disposition"
            ] = "attachment; filename=" + os.path.basename(file_path)
            return response
    raise Http404


@csrf_exempt
def get_data(request):
    station_id = request.GET["station"]
    try:
        station = Station.objects.get(id=station_id)
        contributions = SMSContribution.objects.filter(station=station)
        contributions_json = []
        for contribution in contributions:
            print("hey")
            contributions_json += [
                (
                    {
                        "contributor_id": contribution.contributor_id,
                        "gage_height": contribution.water_height,
                        "temperature": contribution.temperature,
                        "date_received": contribution.date_received,
                    }
                )
            ]
        print(contributions_json)
        return JsonResponse({"contributions": contributions_json})
    except Exception:
        return HttpResponseBadRequest(
            content="Error: Couldn't find a station with that ID."
        )
