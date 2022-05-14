import os
import sqlite3

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'college.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    curs = conn.cursor()
    curs.execute('SELECT * FROM Student')
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
    conn = sqlite3.connect('college.db')
    sql = '''
    SELECT
      studId,course,name,email
    FROM
      Enrolment INNER JOIN Student
    WHERE
      Enrolment.student=Student.studid and studid=\'{:s}\'
    '''.format(sid)
    curs = conn.execute(sql)

    return render_template('show.html', rows=curs)


@app.route('/formjs')
def formjs():
    return render_template('formjs.html')


if __name__ == '__main__':
    Flask.run(app)
