from app.blog.admin import bp
from app.blog.admin.forms import *
from app import db
from app.models import User

import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit

@bp.route("/", methods=["GET", "POST"])
def index():
    # make sure logged-in admin doesn't try to log in again
    if current_user.is_authenticated:
        logout_user()

    form = PasswordForm()

    # process POST requests (form submitted)
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check admin password
        if user is None or not user.check_password(form.password.data):
            flash("Invalid password lol")
            return redirect(request.url)
        login_user(user)
        
        # allow redirects from @login_required
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "": # ensure redirects are only local for security
            next_page = url_for("blog.admin.choose_action")
        return redirect(next_page)

    # process GET requests otherwise (page being loaded)
    return render_template("blog/admin/form-base.html",
            prompt="Access the Secrets of the Universe", form=form)


@bp.route("/choose-action", methods=["GET", "POST"])
@login_required
def choose_action():
    form = ChooseActionForm()
    # process POST requests
    if form.validate_on_submit():
        action = form.action.data
        if action == "create":
            pass
        elif action == "edit":
            pass
        elif action == "delete":
            pass
        elif action == "change_admin_password":
            pass
        return action

    # process GET requests otherwise
    return render_template("blog/admin/form-base.html", prompt="42", form=form)
