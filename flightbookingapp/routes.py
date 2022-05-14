import sqlite3

from flightbookingapp import app
from flightbookingapp.models import Student
from flask import render_template, jsonify, request, redirect, url_for


@app.route('/')
def index():
    return '<h1>Index Page</h1>'


@app.route('/hello')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/hello/<name>/<int:idnum>')
def hello_you(name, idnum):
    return '<h1>Hello</h1><h3>' + name + ' ' + str(idnum)


@app.route('/puppies')
def puppies():
    return render_template('puppies.html')


# Helper function needed to get SQLite3 rows as dictionaries
def dict_factory(curs, row):
    d = {}
    for idx, col in enumerate(curs.description):
        d[col[0]] = row[idx]
    return d


@app.route('/dblook', methods=['POST', 'GET'])
def dblook():
    conn = sqlite3.connect('flightbookingapp/college.db')
    conn.row_factory = dict_factory
    curs = conn.cursor()
    curs.execute(f'SELECT * FROM {Student}')
    rows = []
    for row in curs:
        rows.append(row)
    return jsonify(rows)


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/showit', methods=['POST', 'GET'])
def showit():
    sid = request.form['studid']
    conn = sqlite3.connect('flightbookingapp/college.db')

    return render_template('show.html')


@app.route('/formjs')
def formjs():
    return render_template('formjs.html')
