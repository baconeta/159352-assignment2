from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.fields import DateField
from flightbookingapp.models import Customer, Airport


def airports():
    return Airport.query.all()


def validate_email(email):
    customer = Customer.query.filter_by(email=email.data).first()
    if customer:
        raise ValidationError('Email address is already registered.')


class RegistrationForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired(), Length(min=3, max=25)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of birth', validators=[DataRequired()])
    password = PasswordField('Password [at least 6 characters]', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=6), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=40)])
    remember = BooleanField('Remember me', default=False)
    submit = SubmitField('Login')


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('New Password [at least 6 characters]', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=6), EqualTo('new_password')])
    dob = DateField('Date of birth', default=False, validators=[DataRequired()])
    submit = SubmitField('Set New Password')


class BookingForm(FlaskForm):
    fly_from = QuerySelectField('From', query_factory=airports, allow_blank=False)
    fly_to = QuerySelectField('To', query_factory=airports, allow_blank=False)
    tickets = IntegerField('Tickets', validators=[NumberRange(min=1, max=6, message="Select between 1 and 6 tickets.")],
                           default=1)
    calendar = DateField('Flight date', validators=[DataRequired(message="Choose a date to fly")])
    submit = SubmitField('Search')

    def validate_fly_to(self, fly_to):
        if fly_to.data == self.fly_from.data:
            raise ValidationError('You can\'t fly to and from the same airport.')


class FindBookingForm(FlaskForm):
    booking_ref = StringField('Booking Reference', validators=[DataRequired(), Length(min=1, max=6)])
    surname = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Find Booking')


class UpdateDetailsForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired(), Length(min=3, max=20)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password (required)', validators=[DataRequired(), Length(min=6)])
    dob = DateField('Date of birth', validators=[DataRequired()])
    new_password = PasswordField('New Password (optional) [at least 6 characters]')
    submit = SubmitField('Update Details')

    def validate_new_password(self, new_password):
        if new_password.data != "" and new_password.data is not None:
            if len(new_password.data) < 6:
                raise ValidationError('New password must be at least 6 characters long.')
