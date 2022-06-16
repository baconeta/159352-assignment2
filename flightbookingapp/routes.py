from flightbookingapp import app, db, bcrypt
from flightbookingapp.forms import *
from flightbookingapp.models import Aircraft, Customer, Route, Airport, Booking, Departure
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required


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
    # airports = Airport.query.all()
    form = BookingForm()
    if form.validate_on_submit():
        fly_from = form.fly_from.data.int_code
        fly_to = form.fly_to.data.int_code
        tickets = form.tickets.data
        print("You are searching for bookings from " + fly_from + " to " + fly_to)
        return redirect(url_for('search_results', fly_from=fly_from, fly_to=fly_to, tickets=tickets))
    # for airport in airports:
    #     form.fly_from.choices.append(airport.name + ": " + airport.int_code)
    #     form.fly_to.choices.append(airport.name + ": " + airport.int_code)
    return render_template('booking.html', title='Book a flight', form=form)  # , airports=airports)


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


@app.route('/search_results/<fly_from>&<fly_to>&<tickets>')
def search_results(fly_from, fly_to, tickets):
    # TODO handle finding correct flights
    return render_template('search_results.html', title='Find a Flight')
