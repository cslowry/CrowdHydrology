#!/util/python3/bin/python

import csv
import time

from main_app.models import SMSContribution

contribution_list = SMSContribution.objects.filter(station="NY1000")


with open(
    "../../crowdhydrology_driver/data/" + "NY1000".upper() + ".csv", "w"
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
print("Done! Saved contributions to csv.")
