#!/util/python3/bin/python

import csv

from main_app.models import SMSContribution, Station

station = Station.objects.get(id="NY1000")

contribution_list = SMSContribution.objects.filter(station=station)

with open(
    "/Users/arthurdearaujo/Desktop/Hydrogeology Research/crowd_hydrology/CUAHSI-CSVs/bulkUpload.csv",
    "w",
) as csv_file:
    writer = csv.writer(csv_file, delimiter=",")
    writer.writerow(
        [
            "SourceCode",
            "DataValue",
            "SiteCode",
            "SiteName",
            "Latitude",
            "Longitude",
            "State",
            "SiteType",
            "QualityControlLevelCode",
            "CensorCode",
            "UTCOffset",
            "LocalDateTime",
            "DateTimeUTC",
            "MethodDescription",
            "MethodCode",
            "GeneralCategory",
            "DataType",
            "IsRegular",
            "ValueType",
            "SampleMedium",
            "Units",
            "VariableName",
            "VariableCode",
        ]
    )
    for contribution in contribution_list:
        # contribution.date_received.strftime('%m/%d/%Y')
        row = []
        row += [
            str(contribution.contributor_id),
            float(contribution.water_height),
            str(contribution.station.id),
        ]
        row += [
            str(contribution.station.name),
            float(contribution.station.loc_latitude),
            float(contribution.station.loc_longitude),
        ]
        row += [
            str(contribution.station.state),
            str(contribution.station.water_body_type),
            "1",
        ]
        row += [
            "NC",
            "0",
            contribution.date_received.strftime("%m/%d/%Y"),
            contribution.date_received.strftime("%m/%d/%Y"),
        ]
        row += [
            "SMS from Citizen Scientist",
            "1",
            "Hydrology",
            "Sporadic",
            "False",
            "Field Observation",
            "Surface Water",
        ]
        row += ["Feet", "Gage Height", "1"]
        writer.writerow(row)
print("Done! Saved " + station.id + " contributions to csv.")
