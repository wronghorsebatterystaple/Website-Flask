import sqlalchemy as sa
from flask import jsonify, redirect, render_template, url_for
from flask_wtf.csrf import generate_csrf

from app import db
from app.forms import *
from app.models import *
from config import Config


def inject_forms():
    return dict(login_form=LoginForm())


# for navbar
def inject_blogpages():
    blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    return dict(blogpages=blogpages)


def handle_general_http_error(e):
    return redirect(f"https://http.cat/{e.code}")


def handle_csrf_error(e):
    """
    Regenerates CSRF token on token (tied to session) expire, then let Ajax take it from there with standard
    `fetchWrapper()`.
    """

    csrf_token = generate_csrf()
    code = Config.CUSTOM_ERRORS["REFRESH_CSRF"][0]
    # return new token in Ajax response since csrf_token() in Jinja doesn't update asynchronously,
    # so instead we pass the error description in as the new csrf_token in JS.
    # Shouldn't be a security issue since CSRF token sent in POST anyways.
    # (most scuffed CSRF refresh in history)
    return jsonify(new_csrf_token=csrf_token), code
