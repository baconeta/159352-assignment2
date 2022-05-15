from flightbookingapp import db


class Aircraft(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.VARCHAR(50), nullable=False)
    seats = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Aircraft('{self.id}', '{self.name}')"


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    first_name = db.Column(db.VARCHAR(20), nullable=False)
    last_name = db.Column(db.VARCHAR(20), nullable=False)
    email = db.Column(db.VARCHAR(50), nullable=False, unique=True)
    phone_number = db.Column(db.Integer)
    password = db.Column(db.VARCHAR(16), default=None)
    bookings = db.relationship('Booking', backref='booking_ref')

    def __repr__(self):
        return f"Customer('{self.first_name}', '{self.last_name}')"


class FlightNumber(db.Model):
    flight_code = db.Column(db.VARCHAR(10), primary_key=True, nullable=False, unique=True)
    depart_time = db.Column(db.DateTime, nullable=False)
    arrive_time = db.Column(db.DateTime, nullable=False)
    stopover_time = db.Column(db.DateTime)
    depart_airport = db.Column(db.CHAR(4), db.ForeignKey('airport.int_code'), nullable=False)
    arrive_airport = db.Column(db.CHAR(4), db.ForeignKey('airport.int_code'), nullable=False)
    stopover_airport = db.Column(db.CHAR(4), db.ForeignKey('airport.int_code'))

    def __repr__(self):
        return f"Flight('{self.flight_code}', '{self.depart_airport}')"


class Airport(db.Model):
    int_code = db.Column(db.CHAR(4), primary_key=True, unique=True)
    name = db.Column(db.VARCHAR(50), nullable=False)

    def __repr__(self):
        return f"Airport('{self.name}', '{self.int_code}')"


class Booking(db.Model):
    booking_ref = db.Column(db.VARCHAR(6), primary_key=True, nullable=False, unique=True)
    customer = db.Column(db.Integer, db.ForeignKey('customer.id'))
    flight = db.Column(db.Integer, db.ForeignKey('departure.id'))

    def __repr__(self):
        return f"Booking('{self.booking_ref}', '{self.customer.__repr__()}', '{self.flight.__repr__()}')"


class Departure(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    flight_number = db.Column(db.VARCHAR(10), db.ForeignKey('flightnumber.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.00)
