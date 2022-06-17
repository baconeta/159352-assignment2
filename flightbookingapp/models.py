from flightbookingapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_customer(user_id):
    return Customer.query.get(int(user_id))


class Aircraft(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.VARCHAR(50), nullable=False)
    seats = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Aircraft('{self.id}', '{self.name}')"


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.VARCHAR(20), nullable=False)
    last_name = db.Column(db.VARCHAR(20), nullable=False)
    email = db.Column(db.VARCHAR(50), nullable=False, unique=True)
    phone_number = db.Column(db.Integer)
    password = db.Column(db.VARCHAR(60), default=None)
    bookings = db.relationship('Booking', backref='booked_customer', lazy=True)

    def __repr__(self):
        return f"Customer('{self.first_name}', '{self.last_name}')"


class Route(db.Model):
    flight_code = db.Column(db.VARCHAR(10), primary_key=True, nullable=False, unique=True)
    depart_time = db.Column(db.Time, nullable=False)
    arrive_time = db.Column(db.Time, nullable=False)
    stopover_time = db.Column(db.Time)
    depart_airport = db.Column(db.CHAR(4), db.ForeignKey('airport.int_code'), nullable=False)
    arrive_airport = db.Column(db.CHAR(4), db.ForeignKey('airport.int_code'), nullable=False)
    stopover_airport = db.Column(db.CHAR(4), db.ForeignKey('airport.int_code'))
    plane = db.Column(db.Integer, db.ForeignKey('aircraft.id'), nullable=False)

    def __repr__(self):
        return f"Flight('{self.flight_code}', '{self.depart_airport}')"


class Airport(db.Model):
    int_code = db.Column(db.CHAR(4), primary_key=True, unique=True)
    name = db.Column(db.VARCHAR(50), nullable=False)
    timezone = db.Column(db.String(50))

    def __repr__(self):
        return f"{self.name}: {self.int_code}"


class Booking(db.Model):
    booking_ref = db.Column(db.VARCHAR(6), primary_key=True, nullable=False, unique=True)
    customer = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    flight = db.Column(db.Integer, db.ForeignKey('departure.id'), nullable=False)
    tickets = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"'{self.tickets}' for booking('{self.booking_ref}', '{self.customer.__repr__()}', '{self.flight.__repr__()}')"


class Departure(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    flight_number = db.Column(db.VARCHAR(10), db.ForeignKey('route.flight_code'), nullable=False)
    depart_date = db.Column(db.Date, nullable=False)
    stopover_date = db.Column(db.Date)
    arrival_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.00)
    booked_seats = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Departure('{self.flight_number}', '{self.depart_date}', '{self.price}')"
