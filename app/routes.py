from flask import jsonify, render_template, url_for
from flask_wtf.csrf import generate_csrf

from app.forms import *
from config import Config


def inject_login_form():
    return dict(login_form=LoginForm())


# Regenerate CSRF token on token (tied to session) expire
# then let Ajax take it from there with custom error fail() handler
# (non-auth action: resend request; auth action: show login modal for re-login)
def handle_csrf_error(e):
    csrf_token = generate_csrf()
    # don't use custom HTTPException since we can't `raise` here
    (code, description) = Config.CUSTOM_ERRORS["REFRESH_CSRF"]
    # return new token as description since csrf_token() in Jinja
    # doesn't seem to update until page reload; so instead we pass
    # the error description in as the new csrf_token in JS
    # shouldn't be a security issue since CSRF token sent in POST anyways
    # (most scuffed CSRF refresh in history)
    return csrf_token, code
