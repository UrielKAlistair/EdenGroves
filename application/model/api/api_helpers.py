from flask_restful import Api
from flask import current_app as app
from werkzeug.exceptions import HTTPException
from flask import make_response
from json import dumps

api = Api(app)


# Defining Errors the API may throw
class NotFoundError(HTTPException):
    def __init__(self):
        self.response = make_response('', 404)


class ConflictError(HTTPException):
    def __init__(self):
        self.response = make_response('', 409)


class InternalError(HTTPException):
    def __init__(self):
        self.response = make_response('', 500)


class BadRequestError(HTTPException):
    def __init__(self, error_code, error_message):
        msg = {
            "error_code": error_code,
            "error_message": error_message
        }
        self.response = make_response(dumps(msg), 400)
