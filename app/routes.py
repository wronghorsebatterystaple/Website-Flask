from flask import jsonify, render_template, url_for
from flask_wtf.csrf import generate_csrf

from app.forms import *
from config import Config


def inject_login_form():
    return dict(login_form=LoginForm())


def handle_csrf_error(e):
    csrf_token = generate_csrf()
    # don't use custom HTTPException since we can't `raise` here
    (code, description) = Config.CUSTOM_ERRORS["REFRESH_CSRF"]
    return description, code
#
#
#def catchall_refresh_csrf_error(e):
#    return jsonify(flash_message="Ajax should've caught this...")
#
#
#def catchall_refresh_login_error(e):
#    return jsonify(flash_message="Ajax should've caught this...")
