#!/util/python3/bin/python

import sqlite3
from datetime import datetime

from main_app.models import InvalidSMSContribution, SMSContribution, Station

"""
Function to transfer from the old_sqlite3 database to the django sqlite3 database.

@author Arthur De Araujo
@contact adearauj@buffalo.edu
@github github.com/wafflez180

Created: 01/8/2019
"""

# Connect to database
conn = sqlite3.connect(
    "/Users/arthurdearaujo/Desktop/Hydrogeology Research/crowd_hydrology/main_app/old_crowdhydrology_db.sqlite"
)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cur.fetchall())

cur.execute("SELECT * FROM InvalidSMSContributions")

rows = cur.fetchall()

for row in rows:
    break
    hashed_phone_number = row[0]
    message_body = row[1]
    date_received = datetime.strptime((row[2] + "-0000"), "%Y-%m-%d %H:%M:%S%z")
    new_invalid_contribution = InvalidSMSContribution(
        contributor_id=hashed_phone_number,
        message_body=message_body,
        date_received=date_received,
    )
    new_invalid_contribution.save()

cur.execute("SELECT * FROM SMSContributions")

rows = cur.fetchall()

for row in rows:
    hashed_phone_number = row[0]
    station_id = str(row[1]).replace(",", "")
    water_height = str(row[3]).replace(",", "")
    temperature = None
    date_received = datetime.strptime((row[5] + "-0000"), "%Y-%m-%d %H:%M:%S%z")
    try:
        # print(row)
        station = Station.objects.get(id=station_id)
        new_contributon = SMSContribution(
            contributor_id=hashed_phone_number,
            station=station,
            water_height=float(water_height),
            temperature=temperature,
            date_received=date_received,
        )
        new_contributon.save()
    except Exception:
        message_body = water_height
        new_invalid_contribution = InvalidSMSContribution(
            contributor_id=hashed_phone_number,
            message_body=message_body,
            date_received=date_received,
        )
        new_invalid_contribution.save()
    # break


# Close database connection
conn.commit()
conn.close()
