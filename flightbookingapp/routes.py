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
    form = BookingForm()
    return render_template('booking.html', title='Book a flight', form=form)


@app.route('/customer')
@login_required
def customer():
    user_bookings = current_user.bookings
    departures = Departure.query.all()
    return render_template('customer.html', title='My Account', bookings=user_bookings, departures=departures)


@app.route('/bookings')
def bookings():
    user_bookings = []
    departures = []
    if current_user.is_authenticated:
        user_bookings = current_user.bookings
        departures = Departure.query.all()

    return render_template('bookings.html', title='Bookings', loggedin=current_user.is_authenticated,
                           user_bookings=user_bookings, departures=departures)
