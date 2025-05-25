import csv
import os
import uuid
from datetime import datetime

from main_app.models import SMSContribution, Station

contributions = []

if os.path.exists("sms.csv"):
    totalfile = open("sms.csv", "r")
    totalreader = csv.reader(totalfile, delimiter=",")
    firstrow = True
    for user in totalreader:
        if not firstrow:
            if "IL" in user[2] and "received" in user[3]:
                contributions += [(user[0], user[2], user[4])]
        firstrow = False
    totalfile.close()
else:
    print("Error: Couldn't find MI2022.csv.")

# print(contributions)

for contribution in contributions:
    date_received = datetime.strptime(
        (contribution[1].lstrip() + "-0000"), "%Y-%m-%d %H:%M:%S%z"
    )
    try:
        print(contribution)
        hashed_phone_number = str(uuid.uuid3(uuid.NAMESPACE_OID, "0000000000"))
        station = Station.objects.get(id="MI2026")
        new_contributon = SMSContribution(
            contributor_id=hashed_phone_number,
            station=station,
            water_height=None,
            temperature=contribution[0],
            date_received=date_received,
        )
        new_contributon.save()
    except Exception as e:
        print(e)
        pass
