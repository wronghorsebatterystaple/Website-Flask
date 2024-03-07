from app.blog.admin import bp
from app.blog.admin.forms import *
from app import db
from app.models import User

import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user

@bp.route("/", methods=["GET", "POST"])
def index():
    # make sure logged-in admin doesn't try to log in again
    if current_user.is_authenticated:
        logout_user()

    password_form = PasswordForm()
    # process POST requests (form submitted)
    if password_form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check admin password
        if user is None or not user.check_password(password_form.password.data):
            flash("Invalid password lol")
            return redirect(url_for("blog.admin.index"))
        login_user(user)
        return f"Logged in!"

    # process GET requests otherwise (page being loaded)
    return render_template("blog/admin/form-base.html",
        prompt="Access the Secrets of the Universe", form=password_form)

