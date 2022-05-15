from flightbookingapp import app
from flightbookingapp.models import Aircraft, Customer, FlightNumber, Airport
from flask import render_template, jsonify, request, redirect, url_for


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')
