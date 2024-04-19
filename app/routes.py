from flask import render_template, url_for

from app.forms import *

def inject_login_form():
    return dict(login_form=LoginForm())

def handle_csrf_error(e):
    return "Has it been a year already?"
