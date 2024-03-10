from app.blog.admin import bp
from app.blog.admin.forms import *
from app import db
from app.models import *

import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request

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
            return redirect(url_for("blog.admin.create_blogpost"))
        elif action == "edit":
            return redirect(url_for("blog.admin.search_blogpost"))
        elif action == "change_admin_password":
            return redirect(url_for("blog.admin.change_admin_password"))
        return action

    # process GET requests otherwise
    return render_template("blog/admin/form-base.html", prompt="42", form=form)


@bp.route("/create-blogpost", methods=["GET", "POST"])
@login_required
def create_blogpost():
    form = CreateBlogpostForm()
    # process POST requests
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, subtitle=form.subtitle.data, content=form.content.data)
        new_post.sanitize_title()
        # check that title still exists after sanitization
        if new_post.sanitized_title == "":
            flash("Post must have alphanumeric characters in its title")
            return redirect(request.url) # can also use Ajax to avoid clearing all fields with reload
        # check that title is unique
        if db.session.query(Post).filter_by(title=form.title.data).first() is not None \
                or db.session.query(Post).filter_by(sanitized_title=new_post.sanitized_title).first() is not None:
            flash("There is already a post with that title or sanitized title")
            return redirect(request.url)

        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully!")
        return redirect(url_for("blog.post", post_sanitized_title=new_post.sanitized_title)) # view completed post

    # process GET requests otherwise
    return render_template("blog/admin/form-base.html", prompt="Create post", form=form)


@bp.route("/search-blogpost", methods=["GET", "POST"])
@login_required
def search_blogpost():
    form = SearchBlogpostForm()
    # process POST requests
    if form.validate_on_submit():
        post = form.post.data
        if post == None:
            flash("You somehow managed to choose nothing, congratulations.")
            return redirect(request.url)
        post = post.id
        return redirect(url_for("blog.admin.edit_blogpost", post=post))
        
    # process GET requests otherwise
    return render_template("blog/admin/form-base.html", prompt="Find a post", form=form)


@bp.route("/edit-blogpost", methods=["GET", "POST"])
@login_required
def edit_blogpost():
    form = EditBlogpostForm()
    # process POST requests
    if form.validate_on_submit():
        if form.delete.data:
            pass
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
@login_required
def change_admin_password():
    pass
