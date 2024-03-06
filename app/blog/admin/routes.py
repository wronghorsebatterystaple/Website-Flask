from app.blog.admin import bp
from app.blog.admin.forms import *
from app import db

from flask import render_template

@bp.route("/", methods=["GET", "POST"])
def index():
    password_form = PasswordForm()
    if password_form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
        form.username.data, form.remember_me.data))
        return f"Submitted password is {password_form.password.data}"
    return render_template("blog/admin/form-base.html",
        title="Access the Secrets of the Universe", form=password_form)

