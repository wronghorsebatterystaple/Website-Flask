import sqlalchemy as sa
from flask import jsonify, render_template, url_for
from flask_wtf.csrf import generate_csrf

from app import db
from app.forms import *
from app.models import *
from config import Config


## For login modal
def inject_login_form():
    return dict(login_form=LoginForm())


## For navbar
def inject_blogpages_from_db():
    blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    return dict(blogpages=blogpages)


def bot_jail():
    return render_template("bot_jail.html")


def handle_csrf_error(e):
    """
    Regenerates CSRF token on token (tied to session) expire, then let Ajax take it from there with standard
    `fetchWrapper()`.
    """

    csrf_token = generate_csrf()
    # don't use custom HTTPException since we can't `raise` here
    code = Config.CUSTOM_ERRORS["REFRESH_CSRF"][0]
    # return new token in Ajax response since csrf_token() in Jinja doesn't seem to update until page reload
    # so instead we pass the error description in as the new csrf_token in JS
    # shouldn't be a security issue since CSRF token sent in POST anyways
    # (most scuffed CSRF refresh in history)
    return jsonify(new_csrf_token=csrf_token), code
