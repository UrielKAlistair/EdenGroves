from flask import render_template, request, redirect, session, current_app as app
from ..misc.helper_functions import session_user
from ...model.db import db
from ...model.models import User

from flask_restful import reqparse, fields

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from werkzeug.security import check_password_hash
from base64 import b64encode


# MAKE A FORGOT PASSWORD THING
# VALIDATE AGAINST SQL INJECTIONS
# MAKE A TOO MANY FAILED ATTEMPTS

def authenticate_login(username, password):
    user = db.session.query(User).filter_by(user_name=username).first()
    if user is None:
        return None
    elif check_password_hash(
            "pbkdf2:sha256$" + user.password_salt + "$" + str(b64encode(user.user_password))[2:-1], password):
        return user.user_id
    else:
        return False


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


def flush_login_form(form):
    form.username.data = ""
    form.password.data = ""


venue_json = {"username": fields.String,
              "password": fields.String}

venues_req_parser = reqparse.RequestParser()
venues_req_parser.add_argument("username", type=str, required=True)
venues_req_parser.add_argument("password", type=str, required=True)


@app.route("/validate_login", methods=["POST"])
def validate_login():
    uname = request.form["username"]
    password = request.form["password"]
    auth = authenticate_login(uname, password)
    if auth is None:
        return {"error": 'User not Found.'}
    elif not auth:
        return {"error": 'Password incorrect.'}
    else:
        session['user'] = auth
        return {}


@app.route("/login", methods=["GET"])
def user_login():
    """
    This function is used to render the login page.

    If the user is already logged in, they are redirected to the dashboard. Else, the page is rendered.

    There are a bunch of situations where the user encounters a special state and is directed here, and needs to be told
    a message specifically tailored for this case. These cases are:
    1. The user has tried to create an account for an email that already has an account.
    2. The user successfully created an account.
    3. The user has tried to perform an action that requires them to be logged in when they were not.

    The page is rendered with any message if needed, and the blank form.

    The core logic executes if a POST request delivers the form data.
    First the input data is length validated. If it is invalid, the core logic won't execute and the page will re render,
    but with an error message thrown by the form validator. This is handled within the templates.

    If the data is valid, the database is queried for the given username.
    If the username is not found, the page reloads with an error message.
    If the username is found, the password is checked. If the password is correct, the user is redirected to the
    dashboard. Else, the page reloads with an error message.

    """

    if session_user():
        return redirect("/", code=302)

    acc_already_exists = request.args.get("acc_already_exists")
    registration_successful = request.args.get("registration_successful")
    not_logged_in = request.args.get("not_logged_in")

    message = False
    if not_logged_in:
        message = "You must be logged in to perform that action. <br> Please Log in. <br>"
    elif acc_already_exists:
        message = "Account already exists. Please Login. <br>"
    elif registration_successful:
        message = '<span class="text-emerald-500"> Registration Successful.</span> <br>'

    form = LoginForm()
    flush_login_form(form)
    # If the form is invalid, or if a GET request is made, the basic login page is rendered again.
    return render_template("login/login.html", error=message, form=form)


@app.route("/logout")
def logout():
    try:
        del session['user']
    except KeyError:
        pass
    return redirect("/", code=302)
