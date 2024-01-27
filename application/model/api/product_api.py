from flask_restful import Resource, marshal_with, fields, reqparse
from flask_sqlalchemy import query
from flask import make_response
from ...model.models import Product
from ...model.db import db
from .api_helpers import NotFoundError, InternalError, BadRequestError, ConflictError
from base64 import b64encode, b64decode

product_json = {"product_id": fields.Integer,
                "product_name": fields.String,
                "product_price": fields.Integer,
                "product_unit": fields.String,
                "product_stock": fields.Integer,
                "product_image": fields.String}

product_req_parser = reqparse.RequestParser()
product_req_parser.add_argument("product_name", type=str, required=True)
product_req_parser.add_argument("product_price", type=int, required=True)
product_req_parser.add_argument("product_unit", type=str, required=True)
product_req_parser.add_argument("product_stock", type=int, required=True)
product_req_parser.add_argument("product_image", type=str)


class ProductApi(Resource):

    # Get details about a product with a given cat_id, product_id
    @marshal_with(product_json)
    def get(self, product_id):
        try:
            cat_info = db.session.query(Product).filter(Product.product_id == product_id).first()
        except:
            raise InternalError()

        # Since the first() call is made, an empty Query results in a None object.
        if cat_info is None:
            raise NotFoundError()
        else:
            cat_info.product_image = b64encode(b64decode(cat_info.product_image)).decode('utf-8')
            return cat_info, 200

    # Update the details of a cat with a given cat_id
    @marshal_with(product_json)
    def put(self, product_id):
        args = product_req_parser.parse_args()

        if args["product_image"] is not None:
            args["product_image"] = b64encode(b64decode(args["product_image"]))

        if args["product_name"] is None:
            raise BadRequestError('PDT001', 'Product Name is required')
        elif args["product_price"] is None:
            raise BadRequestError('PDT002', 'Product Price is required')
        elif args["product_unit"] is None:
            raise BadRequestError('PDT003', 'Product Unit is required')
        elif args["product_stock"] is None:
            raise BadRequestError('PDT004', 'Product Stock is required')
        else:
            try:
                prod_to_update: query.Query = db.session.query(Product).filter(Product.product_id == product_id)
            except:
                raise InternalError()

            if prod_to_update.count() == 0:
                raise NotFoundError()
            else:

                try:
                    prod_to_update.update(args)
                    db.session.commit()
                    x = prod_to_update.first()
                    x.product_image = b64encode(b64decode(x.product_image)).decode('utf-8')
                    return x, 200

                except Exception as e:
                    if str(e)[1:23] == 'sqlite3.IntegrityError':
                        raise ConflictError()
                    else:
                        print(e)
                        raise InternalError()

    # Delete a cat with a given cat_id
    def delete(self, product_id):
        try:
            prod_to_del: query.Query = db.session.query(Product).filter(Product.product_id == product_id)
        except:
            raise InternalError()

        # Since the first() call is not made, the object is still a Query. The Count is thus checked.
        # The reason for maintaining the query object is that only they have a delete method.
        if prod_to_del.count() == 0:
            raise NotFoundError()
        else:
            prod_to_del.delete()
            db.session.commit()
            return make_response('', 200)

    def post(self, cat_id):
        args = product_req_parser.parse_args()
        args["product_image"] = b64encode(b64decode(args["product_image"]))

        if args["product_name"] is None:
            raise BadRequestError('PDT001', 'Product Name is required')
        elif args["product_price"] is None:
            raise BadRequestError('PDT002', 'Product Price is required')
        elif args["product_unit"] is None:
            raise BadRequestError('PDT003', 'Product Unit is required')
        elif args["product_stock"] is None:
            raise BadRequestError('PDT004', 'Product Stock is required')
        elif args["product_image"] is None:
            raise BadRequestError('PDT005', 'Product Image is required')
        else:
            try:
                db.session.add(Product(**args, category_id=cat_id))
                db.session.commit()
            except Exception as e:
                if str(e)[1:23] == 'sqlite3.IntegrityError':
                    raise ConflictError()
                else:
                    raise InternalError()

        return make_response('', 201)
