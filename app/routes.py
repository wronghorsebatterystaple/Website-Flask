from flask import jsonify, render_template, url_for
from flask_wtf.csrf import generate_csrf
import sqlalchemy as sa

from app import db
from app.forms import *
from app.models import *
from config import Config


## For login modal
def inject_login_form():
    return dict(login_form=LoginForm())


## For navbar
def inject_blogpages_from_db():
    blogpages_all_query = db.session.query(Blogpage)
    blogpages_all = blogpages_all_query.order_by(Blogpage.ordering).all()
    login_required_blogpages = blogpages_all_query.filter_by(login_required=True).all()
    return dict(blogpages_all=blogpages_all, login_required_blogpages=login_required_blogpages)


## Regenerate CSRF token on token (tied to session) expire
## then let Ajax take it from there with custom error handler
## (non-auth action: resend request; auth action: show login modal for re-login)
def handle_csrf_error(e):
    csrf_token = generate_csrf()
    # don't use custom HTTPException since we can't `raise` here
    code = Config.CUSTOM_ERRORS["REFRESH_CSRF"][0]
    # return new token in Ajax response since csrf_token() in Jinja doesn't seem to update until page reload
    # so instead we pass the error description in as the new csrf_token in JS
    # shouldn't be a security issue since CSRF token sent in POST anyways
    # (most scuffed CSRF refresh in history)
    return jsonify(new_csrf_token=csrf_token), code
