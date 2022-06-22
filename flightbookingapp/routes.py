from dateutil import parser
from datetime import timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from flightbookingapp import app, db, bcrypt
from flightbookingapp.forms import *
from flightbookingapp.models import Aircraft, Customer, Route, Airport, Booking, Departure
import flightbookingapp.route_funcs as funcs


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@app.route('/booking', methods=['GET', 'POST'])
def home():
    form = BookingForm()
    if form.validate_on_submit():
        fly_from = form.fly_from.data.int_code
        fly_to = form.fly_to.data.int_code
        tickets = form.tickets.data
        calendar = form.calendar.data
        return redirect(url_for('search_results', fly_from=fly_from, fly_to=fly_to, tickets=tickets, date=calendar))
    return render_template('index.html', title='Book a flight', form=form)


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
        if Customer.query.filter_by(email=form.email.data).first() is not None:
            # Customer already has an account
            flash(f"A user already exists with that email address. Login to your account below.", 'info')
        else:
            try:
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                new_customer = Customer()
                new_customer.first_name = form.firstname.data
                new_customer.last_name = form.lastname.data
                new_customer.email = form.email.data
                new_customer.dob = form.dob.data
                new_customer.password = hashed_password
                db.session.add(new_customer)
                db.session.commit()
                flash(f"Welcome to Kulta Air, {form.firstname.data}. You can now login.", 'success')
            except SQLAlchemyError:
                flash("Something went wrong. See administrator for details", "danger")
                return render_template('register.html', title='Register', form=form)
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out. See you next time!', "success")
    return redirect(url_for('login'))


@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    # Customer Details
    form = UpdateDetailsForm()
    funcs.handle_customer_details(form)

    # Bookings
    if request.method == "POST":
        if request.form.get('cancel') == 'Cancel booking':
            funcs.cancel_booking(request.form.get('booking'))
            return redirect(url_for('customer'))
        if request.form.get('view') == 'View invoice':
            return redirect(url_for('invoice', booking_ref=request.form.get('booking'), surname=current_user.last_name))

    flight_info = funcs.collect_user_bookings()
    return render_template('customer.html', title='My Account', bookings=flight_info, form=form)


@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    if request.method == "POST":
        if request.form.get('cancel') == 'Cancel booking':
            funcs.cancel_booking(request.form.get('booking'))
            return redirect(url_for('bookings'))
        if request.form.get('view') == 'View invoice':
            return redirect(url_for('invoice', booking_ref=request.form.get('booking'), surname=current_user.last_name))

    # Find a booking functions
    form = FindBookingForm()
    if form.validate_on_submit():
        find_booking = Booking.query.filter_by(booking_ref=form.booking_ref.data.upper()).first()
        if find_booking:
            booking_customer = Customer.query.filter_by(id=find_booking.customer).first()
            if form.surname.data.upper() == booking_customer.last_name.upper():
                return redirect(url_for('invoice', booking_ref=find_booking.booking_ref,
                                        surname=booking_customer.last_name.upper()))
        else:
            flash("No matching booking found.", "info")
        if find_booking:
            return redirect(url_for('home'))

    # Prepare to show user bookings
    flight_info = {}
    if current_user.is_authenticated:
        flight_info = funcs.collect_user_bookings()

    return render_template('bookings.html', title='Bookings', loggedin=current_user.is_authenticated,
                           user_bookings=flight_info, form=form)


@app.route('/search_results/<fly_from>&<fly_to>&<tickets>&<date>', methods=['GET', 'POST'])
def search_results(fly_from, fly_to, tickets, date):
    matches = funcs.find_matching_flights(date, fly_from, fly_to, tickets)

    today = parser.parse(date)

    # Check for matching flights on 3 days either side of the request
    dates = {}
    for i in range(-3, 4):
        check_date = today + timedelta(i)
        dates[check_date] = len(funcs.find_matching_flights(check_date.strftime("%Y-%m-%d"), fly_from, fly_to, tickets))

    if request.method == 'POST':
        if request.form.get('book') == 'Book this flight':
            return redirect(
                url_for('book', tickets=request.form.get('tickets'), departure=request.form.get('departure')))

        # Links from within the date_cards in the search result page
        if request.form.get('date'):
            return redirect(
                url_for('search_results', fly_from=fly_from, fly_to=fly_to, tickets=tickets,
                        date=request.form.get('date'), dates=dates))

    form = BookingForm()
    if form.validate_on_submit():
        calendar, fly_from, fly_to, tickets = funcs.grab_search_data(form)

        return redirect(
            url_for('search_results', fly_from=fly_from, fly_to=fly_to, tickets=tickets, date=calendar, dates=dates))
    else:
        funcs.fill_booking_form_fields(date, fly_from, fly_to, form, tickets)

    return render_template('search_results.html', title='Find a Flight', bookable=matches, form=form, dates=dates)


@app.route('/book/<tickets>&<departure>', methods=['GET', 'POST'])
@login_required
def book(tickets, departure):
    flight = Departure.query.filter_by(id=departure).first()
    route = Route.query.filter_by(flight_code=flight.flight_number).first()
    dep_airport = Airport.query.filter_by(int_code=route.depart_airport).first()
    arr_airport = Airport.query.filter_by(int_code=route.arrive_airport).first()

    if request.method == "POST":
        if 'Confirm booking' in request.form.get('confirm') and current_user.is_authenticated:
            booking_ref, success = funcs.save_booking(flight, tickets, current_user.id)
            if success:
                return redirect(url_for('confirmation', booking_ref=booking_ref.upper()))
            else:
                flash("Those tickets were sold while you were waiting! Try finding another flight.", "danger")
                redirect(url_for('home'))

    return render_template('book.html', flight=flight, route=route, tickets=tickets, dep=dep_airport, arr=arr_airport)


@app.route('/confirmation/<booking_ref>', methods=['GET', 'POST'])
def confirmation(booking_ref):
    if request.method == "POST" and request.form.get('view') == "View invoice":
        return redirect(url_for('invoice', booking_ref=booking_ref, surname=current_user.last_name.upper()))

    return render_template('confirmation.html', booking_ref=booking_ref)


@app.route('/invoice/<booking_ref>/<surname>')
def invoice(booking_ref, surname):
    try:
        booking = Booking.query.filter_by(booking_ref=booking_ref).first()
        booker = Customer.query.filter_by(id=booking.customer).first()
        if booker.last_name.upper() != surname.upper():
            return render_template('404.html')
        departure = Departure.query.filter_by(id=booking.flight).first()
        route = Route.query.filter_by(flight_code=departure.flight_number).first()
        date = departure.depart_date
        aircraft = Aircraft.query.filter_by(id=route.plane).first()
        return render_template('invoice.html', booking=booking, date=date, customer=booker, departure=departure,
                               route=route, aircraft=aircraft)
    except SQLAlchemyError:
        flash(
            "Something went wrong getting your invoice. Please call our helpdesk on 07-555-1010 during business hours for support.",
            "danger")
        return render_template(url_for('home'))


@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if funcs.reset_customer_password(form):
            return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
