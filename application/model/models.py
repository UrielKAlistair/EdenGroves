from .db import db


class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # TODO: What if it overflows?
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_password = db.Column(db.BINARY(32), nullable=False)
    password_salt = db.Column(db.String(16), nullable=False)
    user_email = db.Column(db.String(256), unique=True, nullable=False)  # TODO: Send an email confirmation?
    user_type = db.Column(db.String(10), nullable=False)

    cart = db.relationship('Cart', back_populates='user')
    orders = db.relationship('Order', back_populates='user')

    def __init__(self, user_name, user_password, password_salt, user_email, user_type):
        self.user_name = user_name
        self.user_password = user_password
        self.password_salt = password_salt
        self.user_email = user_email
        self.user_type = user_type


class Category(db.Model):
    __tablename__ = "category"

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='category', cascade='all, delete')
    cat_search = db.relationship('CatSearch', back_populates='category')

    def __init__(self, category_name):
        self.category_name = category_name


class Product(db.Model):
    __tablename__ = "product"

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(50), unique=True, nullable=False)

    product_price = db.Column(db.Float, nullable=False)
    product_unit = db.Column(db.String(10), nullable=False)

    product_stock = db.Column(db.Integer, nullable=False)
    product_image = db.Column(db.VARBINARY(256), nullable=False)

    product_rating = db.Column(db.Float, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)

    category = db.relationship('Category', back_populates='products')
    orders = db.relationship('Order', back_populates='product')
    product_search = db.relationship('ProductSearch', back_populates='product')

    def __init__(self, product_name, product_price, product_unit, product_stock, product_image, category_id, product_rating=0):
        self.product_name = product_name
        self.product_price = product_price
        self.product_unit = product_unit
        self.product_stock = product_stock
        self.product_image = product_image
        self.category_id = category_id
        self.product_rating = product_rating


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, index=True)

    order_date = db.Column(db.DateTime, nullable=False)
    order_status = db.Column(db.String(50), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='orders')
    product = db.relationship('Product', back_populates='orders')

    def __init__(self, order_date, order_status, user_id, product_id, product_quantity):
        self.order_date = order_date
        self.order_status = order_status
        self.user_id = user_id
        self.product_id = product_id
        self.product_quantity = product_quantity


class Cart(db.Model):
    __tablename__ = "cart"

    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product')
    user = db.relationship('User', back_populates='cart')

    def __init__(self, user_id, product_id, product_quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.product_quantity = product_quantity


class ProductSearch(db.Model):
    __tablename__ = "product_search"

    rowid = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key=True)
    product_name = db.Column(db.String(50))
    product = db.relationship('Product')

class CatSearch(db.Model):
    __tablename__ = "cat_search"

    rowid = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)
    category_name = db.Column(db.String(50))
    category = db.relationship('Category')



# db.create_all()

# x=db.session.query(User).filter(User.user_name == 'morgan freeman')
# print(f"Updating {x} in models.py", x.first().user_type)
# x.update({'user_type': 'God'})
# print(x.first().user_type)
# db.session.commit()

# CREATE VIRTUAL TABLE
# product_search
# USING fts5(product_name, content=product,content_rowid=product_id, tokenize="porter unicode61")

# CREATE TRIGGER product_add_trigger
# AFTER INSERT ON product
# BEGIN
# insert into product_search(product_name,rowid) values (new.product_name, new.rowid);
# END
#
# CREATE TRIGGER product_delete_trigger
# AFTER DELETE ON product
# BEGIN
# insert into product_search(product_search, product_name, rowid) values ('delete', old.product_name, old.rowid);
# END
#
# CREATE TRIGGER product_update_trigger
# AFTER UPDATE ON product
# BEGIN
# insert into product_search(product_search, product_name, rowid) values ('delete', old.product_name, old.rowid);
# insert into product_search(product_name, rowid) values (new.product_name, new.rowid);
# END

# CREATE VIRTUAL TABLE
# cat_search
# USING fts5(category_name, content=category,content_rowid=category_id, tokenize="porter unicode61")

# CREATE TRIGGER category_add_trigger
# AFTER INSERT ON category
# BEGIN
# insert into cat_search(category_name, rowid) values (new.category_name, new.rowid);
# END;
#
# CREATE TRIGGER category_delete_trigger
# AFTER DELETE ON category
# BEGIN
# insert into cat_search(cat_search, category_name, rowid) values ('delete', old.category_name, old.rowid);
# END;
#
# CREATE TRIGGER category_update_trigger
# AFTER UPDATE ON category
# BEGIN
# insert into cat_search(cat_search, category_name, rowid) values ('delete', old.category_name, old.rowid);
# insert into cat_search(category_name, rowid) values (new.category_name, new.rowid);
# END;