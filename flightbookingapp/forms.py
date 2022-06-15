from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from flightbookingapp.models import Customer, Airport


def airports():
    return Airport.query.all()


class RegistrationForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired(), Length(min=3, max=20)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=40)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=6, max=40), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        customer = Customer.query.filter_by(email=email.data).first()
        if customer:
            raise ValidationError('Email address is already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=40)])
    remember = BooleanField('Remember me', default=False)
    submit = SubmitField('Login')


class BookingForm(FlaskForm):
    fly_from = QuerySelectField('From', query_factory=airports, allow_blank=True)
    fly_to = QuerySelectField('To', query_factory=airports, allow_blank=True)
    tickets = IntegerField('Tickets', validators=[NumberRange(min=1, max=6, message="Select between 1 and 6 tickets.")])
    submit = SubmitField('Search')

    # TODO add validator for tickets number
    def validate_airports(self, fly_from, fly_to):
        if fly_to == " " or fly_from == " ":
            raise ValidationError('Select an airport')


class FindBookingForm(FlaskForm):
    booking_ref = StringField('Booking Reference', validators=[DataRequired(), Length(min=1, max=6)])
    surname = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Find Booking')

    # TODO add validator to find a booking

