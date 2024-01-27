from flask import redirect, abort, session
from ...model.db import db
from ...model.models import User

def session_user():
    try:
        if session['user']:
            return db.session.query(User).filter(User.user_id == session['user']).first()
    except KeyError:
        return None


# The following functions are decorators that are used to permit a user any further only if they are logged in,
# are an admin, or a god, respectively.

def only_logged_in(func):
    def wrapper(*args, **kwargs):
        user = session_user()
        if user is None:
            return redirect('/login?not_logged_in=True')
        else:
            return func(*args, **kwargs)

    wrapper.__name__ = func.__name__  # if the wrapper is not renamed, the name "wrapper" is used by flask when it
    # binds to an url; when multiple functions use this wrapper, there will be a name conflict.
    return wrapper


def only_admins(func):
    def wrapper(*args, **kwargs):
        user = session_user()
        if user is None:
            return redirect('/login?not_logged_in=True')
        elif user.user_type == 'Admin' or user.user_type == 'God':
            return func(*args, **kwargs)
        else:
            abort(404, description="Resource not found")

    wrapper.__name__ = func.__name__
    return wrapper


def only_gods(func):
    def wrapper(*args, **kwargs):
        user = session_user()
        if user is None:
            return redirect('/login?not_logged_in=True')
        elif user.user_type == 'God':
            return func(*args, **kwargs)
        else:
            abort(404, description="Resource not found")

    wrapper.__name__ = func.__name__
    return wrapper
