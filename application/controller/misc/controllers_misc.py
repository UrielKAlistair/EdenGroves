from flask import render_template, current_app as app
from ..misc.helper_functions import session_user

@app.errorhandler(404)
def error_404(e):
    user=session_user()
    return render_template("common/404.html", user=user), 404
