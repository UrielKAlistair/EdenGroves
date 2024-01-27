from flask import render_template, redirect, current_app as app, request
from flask_wtf import FlaskForm

from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
import requests

from ..misc.helper_functions import only_admins, session_user


class AddCategory(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')


class EditCategory(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Edit Category')


@app.route("/editcat/<int:cat_id>", methods=['GET', 'POST'])
@only_admins
def edit_category(cat_id):
    user = session_user()
    form = EditCategory()

    if form.validate_on_submit():
        response = requests.put(f'http://127.0.0.1:5050/api/category/{cat_id}',
                                json={"category_name": form.category_name.data})

        if response.status_code == 200:
            return redirect('/admin')
        else:
            return redirect(f'/editcat/{cat_id}?error={response.status_code}')

    error = request.args.get("error")
    return render_template("admin/editcat.html", user=user, form=form, cat_id=cat_id, error=error)


@app.route("/addcat", methods=['GET', 'POST'])
@only_admins
def add_category():
    user = session_user()
    form = AddCategory()

    if form.validate_on_submit():
        response = requests.post('http://127.0.0.1:5050/api/category', json={"category_name": form.category_name.data})
        if response.status_code == 201:
            return redirect('/admin')
        else:
            return redirect(f'/addcat?error={response.status_code}')

    error = request.args.get("error")
    return render_template("admin/addcat.html", user=user, form=form, error=error)

@app.route("/delcat/<int:cat_id>", methods=['GET'])
@only_admins
def delete_cat(cat_id):
    response = requests.delete(f'http://127.0.0.1:5050/api/category/{cat_id}')
    if response.status_code!=200:
        return redirect(f'/admin?error=0')
    return redirect("/admin")