import datetime
import random
from zoneinfo import ZoneInfo

from dateutil import parser
from flask import flash
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from flightbookingapp import db, bcrypt
from flightbookingapp.models import Booking, Route, Departure, Aircraft, Airport, Customer


def save_booking(flight, tickets, customer_number):
    try:
        booking_ref = generate_booking_ref()
        new_booking = Booking(booking_ref=booking_ref, customer=customer_number, flight=flight.id, tickets=tickets)
        db.session.add(new_booking)
        route = Route.query.filter_by(flight_code=flight.flight_number).first()
        total_seats = Aircraft.query.filter_by(id=route.plane).first().seats
        if flight.booked_seats + int(tickets) <= total_seats:
            flight.booked_seats += int(tickets)
        else:
            db.session.rollback()
            return "", False
        if handle_stopover_pathings(flight, tickets):
            db.session.commit()
        else:
            db.session.rollback()
            return "", False
        flash("Your booking has been confirmed.", "success")
        return booking_ref, True
    except SQLAlchemyError:
        flash(
            "Something went wrong making your booking. Please call our helpdesk on 07-555-1010 during business hours for support.",
            "danger")
        db.session.rollback()
        return "", False


def handle_stopover_pathings(flight, tickets, cancel=False):
    route = Route.query.filter_by(flight_code=flight.flight_number).first()
    if route.stopover_airport is not None:
        stopover_route = Route.query.filter_by(flight_code=route.flight_code + "-R").first()
        return check_and_update_stopover_flights(flight, stopover_route, cancel, tickets)

    if "-R" in flight.flight_number:
        origin_route = Route.query.filter_by(flight_code=route.flight_code[:-2]).first()
        return check_and_update_stopover_flights(flight, origin_route, cancel, tickets)
    return True


def check_and_update_stopover_flights(flight, route, cancel, tickets):
    stopover_flight = Departure.query.filter_by(flight_number=route.flight_code, depart_date=flight.depart_date).first()
    max_seats = Aircraft.query.filter_by(id=route.plane).first().seats
    if cancel:
        stopover_flight.booked_seats -= int(tickets)
    else:
        if stopover_flight.booked_seats + int(tickets) <= max_seats:
            stopover_flight.booked_seats += int(tickets)
        else:
            return False
    return True


def find_matching_flights(date, fly_from, fly_to, tickets):
    matches = {}
    for flight in Departure.query.filter_by(depart_date=date).all():
        route = Route.query.filter_by(flight_code=flight.flight_number).first()
        avail_tickets = Aircraft.query.filter_by(id=route.plane).first().seats - flight.booked_seats
        depart_airport = Airport.query.filter_by(int_code=route.depart_airport).first()
        arrive_airport = Airport.query.filter_by(int_code=route.arrive_airport).first()
        if route.depart_airport == fly_from and route.arrive_airport == fly_to and avail_tickets >= int(tickets):
            date = flight.depart_date
            time = route.depart_time
            if not date_in_past(datetime.datetime.combine(date, time), depart_airport.timezone):
                matches[flight] = [route, avail_tickets, depart_airport, arrive_airport]
    return matches


def grab_search_data(form):
    fly_from = form.fly_from.data.int_code
    fly_to = form.fly_to.data.int_code
    tickets = form.tickets.data
    calendar = form.calendar.data
    return calendar, fly_from, fly_to, tickets


def fill_booking_form_fields(date, fly_from, fly_to, form, tickets):
    form.tickets.data = tickets
    form.fly_from.data = Airport.query.filter_by(int_code=fly_from).first()
    form.fly_to.data = Airport.query.filter_by(int_code=fly_to).first()
    form.calendar.data = parser.parse(date)


def generate_booking_ref():
    new_booking_ref = new_code()

    while Booking.query.filter_by(booking_ref=new_booking_ref).first() is not None:
        new_booking_ref = new_code()

    return new_booking_ref


def new_code():
    new_booking_ref = ""
    for x in range(3):
        new_booking_ref += chr(random.randint(ord('A'), ord('Z')))
    for x in range(3):
        new_booking_ref += str(random.randint(0, 9))
    return new_booking_ref


def date_in_past(date_and_time, timezone) -> bool:
    return datetime.datetime.now(ZoneInfo(timezone)) > date_and_time.replace(tzinfo=ZoneInfo(timezone))


def cancel_booking(booking_ref):
    booking_to_cancel = Booking.query.filter_by(booking_ref=booking_ref).first()
    try:
        tickets = booking_to_cancel.tickets
        departure = Departure.query.filter_by(id=booking_to_cancel.flight).first()
        route = Route.query.filter_by(flight_code=departure.flight_number).first()
        departure_airport = Airport.query.filter_by(int_code=route.depart_airport).first()
        date = departure.depart_date
        time = route.depart_time
        if date_in_past(datetime.datetime.combine(date, time), departure_airport.timezone):
            flash("You can't cancel a flight in the past!", "info")
            return

        departure.booked_seats = departure.booked_seats - tickets
        handle_stopover_pathings(departure, tickets, True)

        db.session.delete(booking_to_cancel)
        db.session.commit()
        flash("Booking " + booking_ref + " cancelled successfully.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Something went wrong cancelling this booking.", "danger")


def handle_customer_details(form):
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            update_customer_details(form)
        else:
            flash('Current password was not correct. Account details not updated.', "warning")
    else:
        form.email.data = current_user.email
        form.firstname.data = current_user.first_name
        form.lastname.data = current_user.last_name
        form.dob.data = current_user.dob


def reset_customer_password(form):
    try:
        cust = Customer.query.filter_by(email=form.email.data).first()
        if cust is None:
            flash('No account exists with email address' + form.email.data, "warning")
            return False
        if form.dob.data == cust.dob:
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            cust.password = hashed_password
            db.session.commit()
            flash("Password reset successfully", "success")
            return True
        else:
            flash('Email and date of birth don\'t match.', "warning")
            return False
    except SQLAlchemyError:
        db.session.rollback()
        flash('Something went wrong with your request. Contact our call centre if the problem persists', "danger")
        return False


def update_customer_details(form):
    try:
        cust = Customer.query.filter_by(email=current_user.email).first()
        new_cust_email = Customer.query.filter_by(email=form.email.data).first()
        if new_cust_email is not None and cust is not new_cust_email:
            flash("The email address " + form.email.data + " is already in use. No details were updated.", "danger")
            form.email.data = cust.email
            return
        cust.email = form.email.data
        cust.dob = form.dob.data
        cust.first_name = form.firstname.data
        cust.last_name = form.lastname.data
        if form.new_password.data is not None and form.new_password.data != "":
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            cust.password = hashed_password
        db.session.commit()
        flash('Successfully updated account details.', "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Something went wrong updating your details. Please contact customer service to update manually.")


def collect_user_bookings():
    flight_info = []
    for booking in current_user.bookings:
        departure = Departure.query.filter_by(id=booking.flight).first()
        route = Route.query.filter_by(flight_code=departure.flight_number).first()
        dep_airport = Airport.query.filter_by(int_code=route.depart_airport).first()
        arr_airport = Airport.query.filter_by(int_code=route.arrive_airport).first()
        stopover_airport = Airport.query.filter_by(int_code=route.stopover_airport).first()
        booking_past = date_in_past(datetime.datetime.combine(departure.depart_date, route.depart_time),
                                    dep_airport.timezone)
        flight_info.append([booking, departure, route, dep_airport, arr_airport, booking_past, stopover_airport])
    return sorted(flight_info, key=lambda flight: flight[1].depart_date)
