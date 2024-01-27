from flask import render_template, redirect, current_app as app, request, jsonify
from flask_wtf import FlaskForm

from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired, InputRequired
import requests

from ..misc.helper_functions import only_admins, session_user
from base64 import b64encode


class AddProduct(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    product_image = FileField('Product Image', validators=[FileRequired()])

    product_price = IntegerField('Product Price', validators=[DataRequired()])
    product_unit = StringField('Product Unit', validators=[DataRequired()])
    product_stock = IntegerField('Product Stock', validators=[InputRequired()])

    submit = SubmitField('Add Product')

class EditProduct(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    product_image = FileField('Product Image (Leave this empty to retain the current image)')

    product_price = IntegerField('Product Price', validators=[DataRequired()])
    product_unit = StringField('Product Unit', validators=[DataRequired()])
    product_stock = IntegerField('Product Stock', validators=[InputRequired()])

    submit = SubmitField('Edit Product')


@app.route("/addproduct/<int:cat_id>", methods=['GET', 'POST'])
@only_admins
def add_product(cat_id):
    user = session_user()
    form = AddProduct()


    if form.validate_on_submit():

        packed_data = {"product_name": form.product_name.data,
                       "product_price": form.product_price.data,
                       "product_unit": form.product_unit.data,
                       "product_stock": form.product_stock.data,
                       "product_image": b64encode(request.files[form.product_image.name].read()).decode('utf-8')}
        jsonify(packed_data)
        response = requests.post(f'http://127.0.0.1:5050/api/addproduct/{cat_id}', json=packed_data)

        if response.status_code == 201:
            return redirect('/admin')
        else:
            return redirect(f'/editproduct/{cat_id}?error={response.status_code}')

    error = request.args.get("error")
    return render_template("admin/addproduct.html", user=user, form=form, cat_id=cat_id, error=error)


@app.route("/delproduct/<int:cat_id>/<int:product_id>", methods=['GET'])
@only_admins
def delete_product(cat_id, product_id):
    response = requests.delete(f'http://127.0.0.1:5050/api/product/{product_id}')
    source = request.args.get("source")
    if response.status_code != 200:
        return redirect(f'/admin?error={cat_id}')
    if source:
        return redirect(f'/search?q={source}')
    return redirect("/admin")


@app.route("/editproduct/<int:product_id>", methods=['GET', 'POST'])
@only_admins
def edit_product(product_id):
    user = session_user()
    form = EditProduct()
    details = requests.get(f'http://127.0.0.1:5050/api/product/{product_id}')
    source = request.args.get("source")

    if form.validate_on_submit():

        packed_data = {"product_name": form.product_name.data,
                       "product_price": form.product_price.data,
                       "product_unit": form.product_unit.data,
                       "product_stock": form.product_stock.data,
                       "product_image": b64encode(request.files[form.product_image.name].read()).decode('utf-8')}

        if packed_data["product_image"] == "":
            packed_data["product_image"] = details.json()["product_image"]

        jsonify(packed_data)
        response = requests.put(f'http://127.0.0.1:5050/api/product/{product_id}', json=packed_data)

        if response.status_code == 200:
            if source:
                return redirect(f'/search?q={source}')
            return redirect('/admin')
        else:
            return redirect(f'/editproduct/{product_id}?error={response.status_code}')

    error = request.args.get("error")
    return render_template("admin/editproduct.html", user=user, form=form, error=error, product_id=product_id, details=details.json())
