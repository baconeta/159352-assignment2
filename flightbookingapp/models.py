from datetime import datetime
from flightbookingapp import db


class Student(db.Model):
    studId = db.Column(db.CHAR(6), primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(50), nullable=False)
    email = db.Column(db.VARCHAR(50), nullable=False)


db.create_all()
