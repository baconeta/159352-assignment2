from flightbookingapp import db
from flightbookingapp.models import *
import datetime
from datetime import timedelta

fc = "KA78"
route = Route.query.filter_by(flight_code=fc).first()
fn = route.flight_code
date = datetime.date(2022, 6, 10)
price = 91.75

for x in range(55):
    date = date + timedelta(7)
    new = Departure(flight_number=fn, price=price, depart_date=date, arrival_date=date)
    db.session.add(new)

db.session.commit()

