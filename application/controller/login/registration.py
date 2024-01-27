from flask import render_template, redirect, current_app as app
from ...model.db import db
from ...model.models import User
from ..misc.helper_functions import session_user

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from werkzeug.security import generate_password_hash
from base64 import b64decode


def password_validator():

    def _check(form, field):
        length = field.data and len(field.data) or 0
        if length == 0:
            return

        if length < 12 or length > 25:
            # Checking for length
            message = "The entered password is not of the correct length."
            raise ValidationError(message)

        elif not any(c.isupper() for c in field.data):
            # Checking for uppercase
            message = "The entered password does not have an Uppercase letter."
            raise ValidationError(message)

        elif not any(c.islower() for c in field.data):
            # Checking for lowercase
            message = "The entered password does not have a Lowercase letter."
            raise ValidationError(message)

        elif not any(c.isdigit() for c in field.data):
            # Checking for numbers
            message = "The entered password does not have a number."
            raise ValidationError(message)

        elif not any(c in '!@#$%^&*' for c in field.data):
            # Checking for special characters
            message = "The entered password does not have a special character."
            raise ValidationError(message)

        elif ' ' in field.data:
            # Checking for spaces
            message = "Spaces are not allowed in the password."
            raise ValidationError(message)

    return _check


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), password_validator(),
                                         EqualTo('confirm_password', message='Passwords do not match')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


def flush_registration_form(form):
    form.username.data = ""
    form.email.data = ""
    form.password.data = ""
    form.confirm_password.data = ""


@app.route("/register", methods=["GET", "POST"])
def user_registration():
    """
    This function is used to render the registration page.

    If the user is already logged in, they are redirected to the dashboard. Else, the page is rendered.
    Once a POST request is received form the form, the main logic is executed.

    First, the input data is validated. (Sensible email, decent password etc.)
    If the data is valid, the database must be queried for conflicts with existing accounts.

    If an account already exists with that email, the user is redirected to the login page with an error message.
    If the username is already taken, the page reloads and the user is asked to use another name.

    If all is well, the user is registered successfully.
    """

    if session_user():
        return redirect("/", code=302)

    form = RegistrationForm()
    if form.validate_on_submit():

        email = form.email.data
        if db.session.query(User).filter_by(user_email=email).first() is not None:
            return redirect("/login?acc_already_exists=True", code=302)

        uname = form.username.data
        if db.session.query(User).filter_by(user_name=uname).first() is not None:
            return render_template("login/user_registration.html", name_taken_error=True, form=form)

        password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=16)
        _, salt, pwd_hash = password.split("$")
        pwd_hash = b64decode(pwd_hash)  # Convert string hash of password into a binary string for efficient storage
        user = User(uname, pwd_hash, salt, email, "User")

        db.session.add(user)
        db.session.commit()
        flush_registration_form(form)
        return redirect("/login?registration_successful=True", code=302)

    return render_template("login/user_registration.html", name_taken_error=False, form=form)
