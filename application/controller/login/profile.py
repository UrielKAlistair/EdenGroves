from flask import render_template, redirect, current_app as app, request
from ...model.db import db
from ...model.models import User
from ..misc.helper_functions import session_user, only_logged_in
from .registration import password_validator
from .login import authenticate_login

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from werkzeug.security import generate_password_hash
from base64 import b64decode


class UpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    old_password = PasswordField('Password', validators=[DataRequired()])

    password = PasswordField('Password',
                             validators=[password_validator(),
                                         EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password')

    submit = SubmitField('Update Details')


def flush_update_form(form):
    form.username.data = ""
    form.email.data = ""
    form.password.data = ""
    form.confirm_password.data = ""
    form.old_password.data = ""


@app.route("/profile", methods=["GET", "POST"])
@only_logged_in
def profile():
    user = session_user()
    form = UpdateForm()

    if form.validate_on_submit():

        error = False
        x = db.session.query(User).filter(User.user_email == form.email.data).first()
        if x is not None:
            if x.user_id != user.user_id:
                error = "There exists another account associated with that email"

        x = db.session.query(User).filter(User.user_name == form.username.data).first()
        if x is not None:
            if x.user_id != user.user_id:
                error = "That username is already taken"

        if not authenticate_login(user.user_name, form.old_password.data):
            error = "Incorrect password"

        if error:
            return render_template("common/profile.html", user=user, form=form, error=error)

        if len(form.password.data) != 0:
            password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=16)
            _, salt, pwd_hash = password.split("$")
            pwd_hash = b64decode(pwd_hash)  # Convert string hash of password into a binary string for efficient storage

        else:
            pwd_hash = user.user_password
            salt = user.password_salt

        db.session.query(User).filter(User.user_id == user.user_id).update(
            {"user_name": form.username.data, "user_password": pwd_hash, "password_salt": salt,
             "user_email": form.email.data,
             "user_type": user.user_type})
        db.session.commit()

        flush_update_form(form)
        return redirect("/profile?successful=True", code=302)

    success = request.args.get("successful")
    return render_template("common/profile.html", user=user, form=form, success=success)


@app.route("/validate_profile", methods=["POST"])
def validate_profile():
    email = request.form["email"]
    uname = request.form["username"]
    user = session_user()
    if user is None:
        return {"error: not logged in"}

    x = db.session.query(User).filter_by(user_email=email).first()
    if x is not None:
        if x.user_id != user.user_id:
            return {"error": "There exists another account associated with that email"}
    x = db.session.query(User).filter_by(user_name=uname).first()
    if x is not None:
        if x.user_id != user.user_id:
            return {"error": "That username is already taken"}

    return {"success": True}
