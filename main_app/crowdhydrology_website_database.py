#!/util/python3/bin/python

import csv
import os
import time
from pathlib import Path

from main_app.models import SMSContribution, Station


def save_contributions_to_csv(station_id):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    station = Station.objects.get(id=station_id)

    contribution_list = SMSContribution.objects.filter(station=station)

    print(("/htdocs/www/crowdhydrology_driver/data/" + station.id.upper() + ".csv"))
    my_file = Path(
        ("/htdocs/www/crowdhydrology_driver/data/" + station.id.upper() + ".csv")
    )

    if my_file.is_file():
        print("FILE EXISTS!")

        with open(
            "/htdocs/www/crowdhydrology_driver/data/" + station.id.upper() + ".csv", "w"
        ) as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow(["Date and Time", "Gage Height (ft)", "POSIX Stamp"])
            for contribution in contribution_list:
                writer.writerow(
                    [
                        contribution.date_received.strftime("%m/%d/%Y %X"),
                        str(contribution.water_height),
                        str(time.mktime(contribution.date_received.timetuple())),
                    ]
                )
        print("Done! Saved " + station_id + " contributions to csv.")
    else:
        print("FILE DOESNT EXIST")
