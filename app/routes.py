from flask import current_app, jsonify, render_template, url_for
from flask_wtf.csrf import CSRFError, generate_csrf

from app.forms import *

def inject_login_form():
    return dict(login_form=LoginForm())

def handle_csrf_error(e):
    csrf_token = generate_csrf()
    # make sure all things that can generate CSRF errors have appropriate Ajax set up!
    # don't know how to do it any other way :/
    return jsonify(refresh_login=True)
