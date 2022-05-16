from flightbookingapp import app
from flightbookingapp.forms import *
from flightbookingapp.models import Aircraft, Customer, Route, Airport, Booking, Departure
from flask import render_template, jsonify, request, redirect, url_for, flash


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@kulta.com" and form.password.data == "password":
            flash(f"Welcome back to Kulta Air, {form.email.data}.", 'success')
            return redirect(url_for('home'))
        else:
            flash(f"Username or password invalid. Check your information and try again.", 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Welcome to Kulta Air, {form.firstname.data}.", 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/booking')
def booking():
    return render_template('booking.html', title='Book a flight')
