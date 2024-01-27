from flask import Flask
from application.model.db import db
from os import path

host_ip = '0.0.0.0'
port = 5050
pwd = path.abspath(path.dirname(__file__))

app = Flask(__name__, template_folder=pwd + '/application/view/templates',
            static_folder=pwd + '/application/view/static')
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + pwd + '/application/model/database.sqlite3'
app.config["SECRET_KEY"] = "replacethislaterplease"
db.init_app(app)

from application.model.api import api_helpers, category_api, product_api
api_helpers.api.add_resource(category_api.CategoryApi, '/api/category', '/api/category/<int:cat_id>')
api_helpers.api.add_resource(product_api.ProductApi, '/api/addproduct/<int:cat_id>', '/api/product/<int:product_id>')

from application.controller.login import login, registration, profile
from application.controller.misc import controllers_misc
from application.controller.user import user_dash, user_cart
from application.controller.admin import admin_dash, category, product

app.register_error_handler(404, controllers_misc.error_404)

if __name__ == '__main__':
    app.run(host=host_ip, port=port)



