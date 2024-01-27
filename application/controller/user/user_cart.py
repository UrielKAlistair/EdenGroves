from flask import render_template, redirect, current_app as app, request
from ..misc.helper_functions import session_user, only_logged_in
from ...model.db import db
from ...model.models import Cart, Product, Order

from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField
from wtforms.validators import DataRequired
import datetime


class DeleteProduct(FlaskForm):
    product_id = HiddenField('pid', validators=[DataRequired()])
    submit = SubmitField('Delete')


@app.route("/cart", methods=['GET', 'POST'])
@only_logged_in
def user_cart():
    notempty = False
    user = session_user()
    items = db.session.query(Cart).filter(Cart.user_id == user.user_id).all()
    if len(items) != 0:
        notempty = True
    s = 0
    for item in items:
        s += item.product.product_price * item.product_quantity
    del_form = DeleteProduct()

    if del_form.validate_on_submit():
        db.session.query(Cart).filter(Cart.user_id == user.user_id, Cart.product_id == del_form.product_id.data).delete()
        db.session.commit()
        return redirect('/cart')

    error = request.args.get("error")
    return render_template("user/user_cart.html", user=user, items=items, total=s, del_form=del_form, error=error,
                           notempty=notempty)


@app.route("/change_product_count", methods=["POST"])
def change_product_count():
    user = session_user()
    if user is None:
        return {"error": "User not logged in."}

    product_id = int(request.form['product_id'])
    product_count = int(request.form['product_count'])

    if product_count > 100:
        return {"error": "Sorry; Purchase of more than 100 units is not permitted."}

    existing = db.session.query(Cart).filter(Cart.user_id == user.user_id, Cart.product_id == product_id).first()
    if existing is not None:
        prod = db.session.query(Product).filter(Product.product_id == product_id).first()
        stock = prod.product_stock
        if stock - product_count < 0:
            return {"error": f"Not enough stock. Available stock: {stock} {prod.product_unit}."}
        if product_count <= 0:
            return {"error": "Invalid quantity."}
        existing.product_quantity = product_count
        db.session.commit()
        return {"success": "Successfully added to cart."}

    return {"error": "Product not found in cart."}


@app.route("/addcart", methods=['POST'])
def add_to_cart():
    user = session_user()
    if user is None:
        return {"redirect": "/login?not_logged_in=True"}
    product_id = request.form["product_id"]

    existing = db.session.query(Cart).filter(Cart.user_id == user.user_id, Cart.product_id == product_id).first()
    if existing is not None:
        return {"error": True}

    cart = Cart(user.user_id, product_id, 1)
    db.session.add(cart)
    db.session.commit()

    return {"success": True}


@app.route("/checkout", methods=["GET", "POST"])
@only_logged_in
def checkout():
    unconfirmed = True
    user = session_user()
    existing = db.session.query(Cart).filter(Cart.user_id == user.user_id)
    error = []
    orders = []
    total = 0

    if existing.count() == 1:
        return redirect(f'/buy/{existing.first().product_id}?cart_redirect=1')

    for item in existing:

        if (item.product_quantity > item.product.product_stock):
            error.append(item.product.product_name)
        if item.product_quantity <= 0:
            error.append(item.product.product_name)

        elif len(error) == 0:

            item.product.product_stock -= item.product_quantity
            new = Order(datetime.datetime.now(), "Booked", user.user_id, item.product.product_id,
                        item.product_quantity)
            total += item.product_quantity * item.product.product_price

            orders.append(new)
            db.session.add(new)

    if request.method == "POST":
        if len(error) == 0:
            existing.delete()
            db.session.commit()
            unconfirmed = False
        else:
            orders = []
            unconfirmed = False

    print(orders)
    return render_template("user/checkout.html", orders=orders, errors=error, user=user, total=total,
                           unconfirmed=unconfirmed)
