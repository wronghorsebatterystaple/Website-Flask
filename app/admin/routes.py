import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from wtforms.form import Form
from flask import flash, redirect, render_template, request, url_for

from app.admin import bp
from app.admin.forms import *
from app import db
from app.models import *
#from app import turnstile
from app.util.turnstile_check import has_failed_turnstile

from urllib.parse import urlsplit

@bp.route("/login", methods=["GET", "POST"])
def login():
    # make sure logged-in admin doesn't try to log in again
    if current_user.is_authenticated:
        logout_user()

    form = PasswordForm()

    # process POST requests (form submitted)
    if form.validate_on_submit():
        if has_failed_turnstile():
            return redirect(url_for("main.bot_jail"))

        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check admin password
        if user is None or not user.check_password(form.password.data):
            flash("Invalid password lol")
            return redirect(request.url)
        login_user(user, remember=True)
        
        # allow redirects from @login_required
        next_page = request.args.get("next")
        if next_page is None or urlsplit(next_page).netloc != "": # ensure redirects are only local for security
            next_page = url_for("admin.choose_action")
        return redirect(next_page)

    # process GET requests otherwise (page being loaded)
    return render_template("admin/form-base.html", title="Assistant Professor Bing",
            prompt="Access the Secrets of the Universe", form=form)


@bp.route("/choose-action", methods=["GET", "POST"])
@login_required
def choose_action():
    form = ChooseActionForm()

    # process POST requests
    if form.validate_on_submit():
        action = form.action.data
        if action == "create":
            return redirect(url_for("admin.create_blogpost"))
        elif action == "edit":
            return redirect(url_for("admin.search_blogpost"))
        elif action == "change_admin_password":
            return redirect(url_for("admin.change_admin_password"))
        return action

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Sleeping TA Yandex", prompt="42", form=form)


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
            flash("Post must have alphanumeric characters in its title.")
            return redirect(request.url)

        # check that title is unique (sanitized is unique => non-sanitized is unique)
        if db.session.query(Post).filter_by(sanitized_title=new_post.sanitized_title).first() is not None:
            flash("There is already a post with that title or sanitized title.")
            return redirect(request.url) # can also use Ajax to avoid clearing all fields with reload
        
        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully!")
        return redirect(url_for("blog.post", post_sanitized_title=new_post.sanitized_title)) # view completed post

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Create post", prompt="Create post", form=form)


@bp.route("/search-blogpost", methods=["GET", "POST"])
@login_required
def search_blogpost():
    form = SearchBlogpostForm()

    # process POST requests
    if form.validate_on_submit():
        post = form.post.data
        if post is None:
            flash("You somehow managed to choose nothing, congratulations.")
            return redirect(request.url)
        post = post.id
        return redirect(url_for("admin.edit_blogpost", post_id=post))
        
    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Search Posts", prompt="Search posts", form=form)


@bp.route("/edit-blogpost", methods=["GET", "POST"])
@login_required
def edit_blogpost():
    post = db.session.get(Post, request.args.get("post_id"))
    if post is None:
        flash("That post no longer exists. Did you hit the back button? Regret your choice, did you?")
        return redirect(url_for("admin.search_blogpost"))
    
    form = EditBlogpostForm(obj=post) # pre-populate fields

    # process POST requests
    if form.validate_on_submit():
        # handle form deletion (after confirmation button)
        if form.delete.data:
            db.session.delete(post)
            db.session.commit()
            flash("Post deleted successfully!")
            return redirect(url_for("blog.index"))

        # check that title is unique if changed
        if form.title.data != post.title:
            post_temp = Post(title=form.title.data, subtitle=form.subtitle.data, content=form.content.data)
            post_temp.sanitize_title() # need post_temp for this--populate_obj() seems to already add to db
            if db.session.query(Post).filter_by(sanitized_title=post_temp.sanitized_title).first() is not None:
                flash("There is already a post with that title or sanitized title.")
                return redirect(request.url)

        form.populate_obj(post)
        post.sanitize_title()
        # check that title still exists after sanitization
        if post.sanitized_title == "":
            flash("Post must have alphanumeric characters in its title.")
            return redirect(request.url)
        
        post.edited_timestamp = datetime.now(timezone.utc) # updated edited time
        db.session.commit()
        flash("Post edited successfully!")
        return redirect(url_for("blog.post", post_sanitized_title=post.sanitized_title)) # view edited post

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Edit Post",
            prompt=f"Edit post: {post.title}", form=form)
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
@login_required
def change_admin_password():
    form = ChangeAdminPasswordForm()

    # process POST requests
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check given password
        if user is None or not user.check_password(form.old_password.data):
            flash("Old password is not correct.")
            return redirect(request.url)

        # check new passwords are identical
        if form.new_password_1.data != form.new_password_2.data:
            flash("New passwords do not match.")
            return redirect(request.url)
        
        user.set_password(form.new_password_1.data)
        db.session.commit()
        flash("Your password has been changed!")
        return redirect(url_for("admin.login"))

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Change Admin Password",
            prompt="Do not make it password123456", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f"You have been logged out.")
    return redirect(url_for("main.index"))
