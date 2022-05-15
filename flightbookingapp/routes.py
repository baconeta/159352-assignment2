from flightbookingapp import app
from flightbookingapp.forms import *
from flightbookingapp.models import Aircraft, Customer, FlightNumber, Airport
from flask import render_template, jsonify, request, redirect, url_for


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)


@app.route('/booking')
def booking():
    return render_template('booking.html', title='Book a flight')
