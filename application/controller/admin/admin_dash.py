import datetime as dt

from flask import render_template, request, redirect, current_app as app
from ..misc.helper_functions import session_user, only_admins, only_gods
from ...model.db import db
from ...model.models import Category, User, Order, Product

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField, HiddenField, DateField, ValidationError
from wtforms.validators import DataRequired

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from os import path


class AlterAccessForm(FlaskForm):
    username = HiddenField('username')
    access_level = SelectField('access', choices=[('User', 'User'), ('Admin', 'Admin'), ('God', 'God')],
                               validators=[DataRequired()])
    submit = SubmitField('Change')


class WindowForm(FlaskForm):
    window = IntegerField('Display data for the past ', validators=[DataRequired()])
    submit = SubmitField('Change')


def after_validator(fieldname):
    def _check(form, field):
        if form[fieldname].data > field.data:
            raise ValidationError("Start date must be before end date.")
        if field.data > dt.datetime.now().date():
            raise ValidationError("End Date must be before today.")
    return _check


class CoverdaysForm(FlaskForm):
    start = DateField('Start date', validators=[DataRequired()])
    end = DateField('End date', validators=[DataRequired(), after_validator('start')])
    submit = SubmitField('Change')


def stringify(x):
    if len(x) == 0:
        return ''

    strx = ''
    for i in x[:-1]:
        strx += i + ','
    strx += x[-1]
    return strx



@app.route("/admin")
@only_admins
def admin_dashboard():
    e = request.args.get("error")
    user = session_user()
    categories = db.session.query(Category).all()
    return render_template("admin/admin_dash.html", user=user, categories=categories, error=e)


@app.route('/make_admins', methods=['GET', 'POST'])
@only_gods
def make_admins():
    user = session_user()
    form = AlterAccessForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            User.query.filter_by(user_name=form.username.data).update({'user_type': form.access_level.data})
            db.session.commit()

    users = db.session.query(User).filter(User.user_name != user.user_name).all()
    return render_template("admin/make_admins.html", user=user, users=users, form=form)


@app.route('/statistics', methods=['GET', 'POST'])
@only_admins
def stats():
    user = session_user()
    requested = request.args.get("requested")
    window = request.args.get("window")
    start = request.args.get("start")
    end = request.args.get("end")
    allprods = db.session.query(Product).all()

    try:
        start = dt.datetime.strptime(start, "%Y-%m-%d")
    except (ValueError,TypeError):
        start = (dt.datetime.now() - dt.timedelta(days=30))
    start = start.replace(start.year, start.month, start.day, 0, 0, 0, 0)

    try:
        end = dt.datetime.strptime(end, "%Y-%m-%d")
    except (ValueError,TypeError):
        end = dt.datetime.now()
    end = end.replace(end.year, end.month, end.day, 23, 59, 59, 999999)

    try:
        window = int(window)
    except (ValueError, TypeError):
        window = 30

    if requested is None:
        requested = ["Total"]
    else:
        requested = requested.split(",")

    class DelForm(FlaskForm):
        products = SelectField('Remove series from the time series graph:', choices=requested, validators=[DataRequired()])
        submit = SubmitField('Delete')

    class NewForm(FlaskForm):
        choices = ["Total"]
        for i in allprods:
            choices.append(i.product_name)

        for i in requested:
            try:
                choices.remove(i)
            except ValueError:
                pass

        products = SelectField('Add new series to the time series graph:', choices=choices, validators=[DataRequired()])
        submit = SubmitField('Add')

    delform = DelForm()
    newform = NewForm()
    winform = WindowForm()
    coverdays = CoverdaysForm()

    if request.method == 'POST':
        if delform.validate_on_submit():
            requested.remove(delform.products.data)
            return redirect(
                f"/statistics?requested={stringify(requested)}&window={window}&start={start.date()}&end={end.date()}")

        if newform.validate_on_submit():
            requested.append(newform.products.data)
            return redirect(
                f"/statistics?requested={stringify(requested)}&window={window}&start={start.date()}&end={end.date()}")

        if winform.validate_on_submit():
            window = winform.window.data
            return redirect(
                f"/statistics?requested={stringify(requested)}&window={window}&start={start.date()}&end={end.date()}")

        if coverdays.validate_on_submit():
            start = coverdays.start.data
            end = coverdays.end.data
            return redirect(f"/statistics?requested={stringify(requested)}&window={window}&start={start}&end={end}")
        else:
            delform = DelForm()
            newform = NewForm()
            winform = WindowForm()

            start = (dt.datetime.now())
            start = start.replace(start.year, start.month, start.day, 0, 0, 0, 0)
            end = start

    # Sales vs Time
    totals = {"Total": {}}
    for product in allprods:
        totals[product.product_name] = {}

    if window < 0:
        orders = db.session.query(Order).all()
    else:
        orders = db.session.query(Order).filter(dt.datetime.now() - dt.timedelta(int(window)) < Order.order_date).all()

    for order in orders:
        if order.order_date.date() not in totals["Total"]:
            totals["Total"][order.order_date.date()] = (order.product_quantity * order.product.product_price)
        else:
            totals["Total"][order.order_date.date()] += (order.product_quantity * order.product.product_price)

        if order.order_date.date() not in totals[order.product.product_name]:
            totals[order.product.product_name][order.order_date.date()] = (
                    order.product_quantity * order.product.product_price)
        else:
            totals[order.product.product_name][order.order_date.date()] += (
                    order.product_quantity * order.product.product_price)

    for total in totals:
        if total in requested:
            plt.plot(list(totals[total].keys()), list(totals[total].values()), label=f'{total} Sales')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.title("Sales vs Time")
    plt.savefig(path.dirname(__file__).replace("controller\\admin", "view\\static\\plot.png"))
    plt.close()

    avgsales = {}
    for product in allprods:
        avgsales[product.product_name] = 0

    orders = db.session.query(Order).filter(Order.order_date.between(start, end)).all()
    for order in orders:
        avgsales[order.product.product_name] += (order.product_quantity * order.product.product_price)

    tabledata = []
    for product in allprods:
        old = round(avgsales[product.product_name] / (1 + (end - start).days), 2)
        tabledata.append([product.product_name, product.product_stock, old,
                          -1 if old == 0 else round(product.product_stock / old, 2)])

    return render_template("admin/stats.html", user=user, delform=delform, winform=winform, newform=newform,
                           requested=stringify(requested), window=window, tabledata=tabledata, coverdays=coverdays,
                           start=start.date(), end=end.date())
