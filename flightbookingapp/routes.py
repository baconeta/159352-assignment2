from dateutil import parser
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required

from flightbookingapp import app, db, bcrypt
from flightbookingapp.forms import *
from flightbookingapp.models import Aircraft, Customer, Route, Airport, Booking, Departure


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        customer_to_login = Customer.query.filter_by(email=form.email.data).first()
        if customer_to_login and bcrypt.check_password_hash(customer_to_login.password, form.password.data):
            login_user(customer_to_login, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Welcome back to Kulta Air, {customer_to_login.first_name}.", 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f"Username or password invalid. Check your information and try again.", 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_customer = Customer(first_name=form.firstname.data,
                                last_name=form.lastname.data,
                                email=form.email.data,
                                password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        flash(f"Welcome to Kulta Air, {form.firstname.data}. You can now login.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    form = BookingForm()
    if form.validate_on_submit():
        fly_from = form.fly_from.data.int_code
        fly_to = form.fly_to.data.int_code
        tickets = form.tickets.data
        calendar = form.calendar.data
        return redirect(url_for('search_results', fly_from=fly_from, fly_to=fly_to, tickets=tickets, date=calendar))
    return render_template('booking.html', title='Book a flight', form=form)


@app.route('/customer')
@login_required
def customer():
    user_bookings = current_user.bookings
    departures = Departure.query.all()
    return render_template('customer.html', title='My Account', bookings=user_bookings, departures=departures)


@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    form = FindBookingForm()
    if form.validate_on_submit():
        find_booking = Booking.query.filter_by(booking_ref=form.booking_ref.data).first()
        if find_booking:
            booking_customer = Customer.query.filter_by(id=find_booking.customer).first()
            if form.surname.data.upper() == booking_customer.last_name.upper():
                print("Booking Found")
                # TODO open to the invoice page ?
                pass
        else:
            print("No Booking Found")
            # TODO Warn customer that no booking was found with those details
            pass
        if find_booking:
            return redirect(url_for('home'))
    user_bookings = []
    departures = []
    if current_user.is_authenticated:
        user_bookings = current_user.bookings
        departures = Departure.query.all()

    return render_template('bookings.html', title='Bookings', loggedin=current_user.is_authenticated,
                           user_bookings=user_bookings, departures=departures, form=form)


@app.route('/search_results/<fly_from>&<fly_to>&<tickets>&<date>', methods=['GET', 'POST'])
def search_results(fly_from, fly_to, tickets, date):
    matches = find_matching_flights(date, fly_from, fly_to, tickets)

    form = BookingForm()
    if form.validate_on_submit():
        calendar, fly_from, fly_to, tickets = grab_search_data(form)
        return redirect(url_for('search_results', fly_from=fly_from, fly_to=fly_to, tickets=tickets, date=calendar))
    else:
        fill_booking_form_fields(date, fly_from, fly_to, form, tickets)

    search_result_flashes(matches)
    return render_template('search_results.html', title='Find a Flight', bookable=matches, form=form)


def find_matching_flights(date, fly_from, fly_to, tickets):
    matches = {}
    for flight in Departure.query.filter_by(depart_date=date).all():
        route = Route.query.filter_by(flight_code=flight.flight_number).first()
        avail_tickets = Aircraft.query.filter_by(id=route.plane).first().seats
        if route.depart_airport == fly_from and route.arrive_airport == fly_to and avail_tickets >= int(tickets):
            matches[flight] = route
    return matches


def search_result_flashes(matches):
    print("hi")
    if len(matches) > 1:
        flash(f"You found {len(matches)} matching flights.", 'success')
    elif len(matches) == 1:
        flash(f"You found 1 matching flight.", 'success')
    else:
        flash("No matching flights, search again.", 'danger')


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
