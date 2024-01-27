from flask import render_template, redirect, current_app as app, request
from ..misc.helper_functions import session_user, only_logged_in
from ...model.db import db
from ...model.models import Category, Order, Cart, ProductSearch, CatSearch, Product
from ..admin.admin_dash import stringify

from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, HiddenField, SelectField
from wtforms.validators import DataRequired
import datetime
import requests



class SortForm(FlaskForm):
    sorting = SelectField('Sort by: ', choices=["Prices Low to High","Prices High to Low","Ratings","Featured"])
    submit = SubmitField('Sort')
class PriceForm(FlaskForm):
    minprice = IntegerField('Min Price', validators=[DataRequired()])
    maxprice = IntegerField('Max Price', validators=[DataRequired()])
    submit = SubmitField('Filter')

def reduced_ask(asked, category):
    askclone = asked.copy()
    askclone.remove(category.category_name)
    return stringify(askclone)

class CancelOrderForm(FlaskForm):
    order_id = HiddenField('Order ID', validators=[DataRequired()])
    submit = SubmitField('Cancel Order')


class BuyNowForm(FlaskForm):
    product_quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Buy Now')


@app.route("/")
def user_dashboard():
    user = session_user()
    if user is not None:
        if user.user_type == 'Admin' or user.user_type == 'God':
            return redirect('/admin')
    categories = db.session.query(Category).all()
    success = request.args.get("success")
    return render_template("user/user_dash.html", user=user, categories=categories, success=success)


@app.route("/orders", methods=["GET", "POST"])
@only_logged_in
def my_orders():
    user = session_user()
    orders = db.session.query(Order).filter(Order.user_id == user.user_id).order_by(Order.order_date.desc()).all()
    success = request.args.get("success")
    form = CancelOrderForm()

    if form.validate_on_submit():
        order = db.session.query(Order).filter(Order.order_id == form.order_id.data)
        order.first().product.product_stock += order.first().product_quantity
        order.delete()
        db.session.commit()

        orders = db.session.query(Order).filter(Order.user_id == user.user_id).all()

    return render_template("user/myorders.html", orders=orders, user=user, success=success, form=form)


@app.route("/buy/<int:product_id>", methods=["GET", "POST"])
@only_logged_in
def buy_now(product_id):
    user = session_user()
    form = BuyNowForm()
    error = None
    product = requests.get(f'http://127.0.0.1:5050/api/product/{product_id}').json()
    cart_redirect = request.args.get("cart_redirect")

    if form.validate_on_submit():

        product_quantity = request.form.get("product_quantity")

        if int(product_quantity) > int(product["product_stock"]):
            error = f'Not enough stock. Available stock: {product["product_stock"]} {product["product_unit"]}.'
        if int(product_quantity) > 100:
            error = "Sorry; Purchase of more than 100 units is not permitted."
        if int(product_quantity) <= 0:
            error = "Invalid quantity."

        if error is None:
            new = Order(datetime.datetime.now(), "Booked", user.user_id, product_id, product_quantity)
            Product.query.filter(Product.product_id == product_id).update(
                {Product.product_stock: Product.product_stock - int(product_quantity)})
            db.session.add(new)
            if cart_redirect:
                db.session.query(Cart).filter(Cart.user_id == user.user_id, Cart.product_id == product_id).delete()
            db.session.commit()
            return redirect('/orders?success=1')

    return render_template("user/buynow.html", user=user, error=error, form=form, product=product,
                           cart_redirect=cart_redirect)


@app.route("/search", methods=["GET", "POST"])
def search():
    user = session_user()
    q = request.args.get("q")
    asked = request.args.get("category")
    minprice = request.args.get("minprice")
    maxprice = request.args.get("maxprice")
    rating = request.args.get("rating")
    price_filtered = True
    rating_filtered = True

    sortform= SortForm()

    if minprice is None or maxprice is None:
        minprice = 0
        maxprice = 10000
        price_filtered = False
    else:
        minprice=int(minprice)
        maxprice=int(maxprice)

    if rating is None:
        rating = 0
        rating_filtered = False
    else:
        rating = int(rating)

    priceform = PriceForm()

    if asked is None or len(asked) == 0 :
        asked = []
    else:
        asked = asked.split(",")
        for i in asked:
            if i=="":
                asked.remove(i)

    if priceform.validate_on_submit():
        minprice = priceform.minprice.data
        maxprice = priceform.maxprice.data
        if rating_filtered:
            return redirect(f'/search?q={q}&category={stringify(asked)}&minprice={minprice}&maxprice={maxprice}&rating={rating}')
        else:
            return redirect(f'/search?q={q}&category={stringify(asked)}&minprice={minprice}&maxprice={maxprice}')

    categories = db.session.query(Category).all()
    results = []
    try:
        for prod in ProductSearch.query.filter(ProductSearch.product_name.op("MATCH")(q)).all():
            results.append(prod.product)

        for cat in CatSearch.query.filter(CatSearch.category_name.op("MATCH")(q)).all():
            for prod in cat.category.products:
                if prod not in results:
                    results.append(prod)

        if len(asked) > 0 :
            for result in results:
                if result.category.category_name not in asked:
                    results.remove(result)

        if price_filtered:
            for result in results:
                if result.product_price < minprice or result.product_price > maxprice:
                    results.remove(result)

        if rating_filtered:
            for result in results:
                if result.product_rating < rating:
                    results.remove(result)

    except Exception as e:
        results = []

    suffix = ""
    ratingsuffix = ""
    if price_filtered:
        suffix+=f"&minprice={minprice}&maxprice={maxprice}"
        ratingsuffix = suffix
        suffix += f"&rating={rating}"

    if sortform.validate_on_submit():
        if sortform.sorting == "Prices Low to High":
            results.sort(key=lambda x: x.product_price)
        if sortform.sorting == "Prices High to Low":
            results.sort(key=lambda x: x.product_price, reverse=True)
        if sortform.sorting == "Ratings":
            results.sort(key=lambda x: x.product_rating, reverse=True)
        if sortform.sorting == "Featured":
            orders = db.session.query(Order).all()
            avgsales = {}
            for order in orders:
                avgsales[order.product.product_name] += (order.product_quantity * order.product.product_price)
            results.sort(key=lambda x: avgsales[x.product_name], reverse=True)

    return render_template("common/search.html", results=results, q=q, user=user,
                           categories=categories, asked=asked, askedstr="" if len(asked) is 0 else stringify(asked)+",",
                           reduced_ask=reduced_ask, suffix=suffix, priceform=priceform, ratingsuffix=ratingsuffix, minprice=minprice, maxprice=maxprice, sortform=sortform)
