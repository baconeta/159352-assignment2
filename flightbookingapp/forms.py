from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerRangeField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flightbookingapp.models import Customer


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
    # TODO fix this default field option
    fly_from = SelectField('From', validators=[DataRequired()], choices=[" "])
    fly_to = SelectField('To', validators=[DataRequired()], choices=[" "])
    tickets = IntegerField('Tickets', validators=[NumberRange(min=1, max=6, message="Select between 1 and 6 tickets.")])
    submit = SubmitField('Search')

    # TODO add validator for tickets number


class FindBookingForm(FlaskForm):
    booking_ref = StringField('Booking Reference', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Login')
