from flask import render_template, url_for

from app.forms import *

def inject_login_form():
    return dict(login_form=LoginForm())
