from flask_restful import Resource, marshal_with, fields, reqparse
from flask_sqlalchemy import query
from flask import make_response
from ...model.models import Category
from ...model.db import db
from .api_helpers import NotFoundError, InternalError, BadRequestError, ConflictError

cat_json = {"category_id": fields.Integer,
            "category_name": fields.String}

cat_req_parser = reqparse.RequestParser()
cat_req_parser.add_argument("category_name", type=str, required=True)


class CategoryApi(Resource):

    # Get details about a cat with a given cat_id
    @marshal_with(cat_json)
    def get(self, cat_id):
        try:
            cat_info = db.session.query(Category).filter(Category.category_id == cat_id).first()
        except:
            raise InternalError()

        # Since the first() call is made, an empty Query results in a None object.
        if cat_info is None:
            raise NotFoundError()
        else:
            return cat_info, 200

    # Update the details of a cat with a given cat_id
    @marshal_with(cat_json)
    def put(self, cat_id):
        args = cat_req_parser.parse_args()
        cn = args['category_name']

        if cn is None:
            raise BadRequestError('CAT001', 'Category Name is required')
        else:
            try:
                cat_to_update: query.Query = db.session.query(Category).filter(Category.category_id == cat_id)
            except:
                raise InternalError()

            if cat_to_update.count() == 0:
                raise NotFoundError()
            else:

                try:
                    cat_to_update.update({"category_name": cn})
                    db.session.commit()
                    return cat_to_update.first(), 200

                except Exception as e:
                    if str(e)[1:23] == 'sqlite3.IntegrityError':
                        raise ConflictError()
                    else:
                        raise InternalError()

    # Delete a cat with a given cat_id
    def delete(self, cat_id):
        try:
            cat_to_del: query.Query = db.session.query(Category).filter(Category.category_id == cat_id)
        except:
            raise InternalError()

        # Since the first() call is not made, the object is still a Query. The Count is thus checked.
        # The reason for maintaining the query object is that only they have a delete method.
        if cat_to_del.count() == 0:
            raise NotFoundError()
        else:
            cat_to_del.delete()
            db.session.commit()
            return make_response('', 200)

    def post(self):
        args = cat_req_parser.parse_args()
        cn = args.get("category_name", None)

        if cn is None:
            raise BadRequestError('CAT001', 'Category Name is required')
        else:
            try:
                db.session.add(Category(cn))
                db.session.commit()
            except Exception as e:
                if str(e)[1:23] == 'sqlite3.IntegrityError':
                    raise ConflictError()
                else:
                    raise InternalError()

        return make_response('', 201)
