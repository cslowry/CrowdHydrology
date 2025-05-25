#!/util/python3/bin/python

import csv
import os

from django.db.models import Count

from main_app.models import SMSContribution

sms_csv = []

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
counter2 = 0
if os.path.exists(
    "/Users/arthurdearaujo/Desktop/Hydrogeology Research/crowd_hydrology/main_app/sms.csv"
):
    totalfile = open(
        "/Users/arthurdearaujo/Desktop/Hydrogeology Research/crowd_hydrology/main_app/sms.csv",
        "r",
    )
    totalreader = csv.reader(totalfile, delimiter=",")
    firstrow = True
    for user in totalreader:
        if not firstrow:
            # print(len(user))
            # print(user)
            if "1023" in user[2].upper() and "received" in user[3]:
                print(user[2])
                sms_csv += [(user[0], user[2], user[4])]
                counter2 += 1
                print("entered")
            elif int(user[0]) != 8457091170 and "received" in user[3]:
                sms_csv += [(user[0], user[2], user[4])]
        firstrow = False
    totalfile.close()
else:
    print("Error: Couldn't find twilio_sms.csv.")

# print(sms_csv_dict)
print("-")
print("-")
print("-")

print()


duplicates = (
    SMSContribution.objects.values("date_received")
    .order_by()
    .annotate(count_id=Count("id"))
    .filter(count_id__gt=1)
)
print(duplicates)
counter = 0
for duplicate in duplicates:
    print(duplicate)
    duplicate_objs = SMSContribution.objects.filter(
        date_received=duplicate["date_received"]
    )
    for obj in range(len(duplicate_objs) - 1):
        print(duplicate_objs)
        print(duplicate_objs[obj])
        duplicate_objs[obj].delete()
        counter += 1
print("deleted: " + str(counter))
print(counter2)
