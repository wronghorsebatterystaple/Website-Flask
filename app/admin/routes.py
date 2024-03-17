import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from wtforms.form import Form
from flask import flash, jsonify, redirect, render_template, request, url_for

from app.admin import bp
from app.admin.forms import *
from app import db
from app.models import *
from app.util.turnstile_check import has_failed_turnstile

from urllib.parse import urlsplit

@bp.route("/login", methods=["GET", "POST"])
def login():
    # make sure logged-in admin doesn't try to log in again
    if current_user.is_authenticated:
        logout_user()

    form = PasswordForm()

    # process POST requests (with Ajax)
    if form.validate_on_submit():
        if has_failed_turnstile():
            return jsonify(redirect=True, redirect_url=url_for("main.bot_jail"))

        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check admin password
        if user is None or not user.check_password(form.password.data):
            return jsonify(redirect=False, flash="Invalid password lol")
            # return redirect(request.url)
        login_user(user, remember=True)
        
        # allow redirects from @login_required
        next_page = request.args.get("next")
        if next_page is None or urlsplit(next_page).netloc != "": # ensure redirects are only local for security
            next_page = url_for("admin.choose_action")
        return jsonify(redirect=True, redirect_url=next_page)

    # process GET requests otherwise (page being loaded)
    return render_template("admin/form-base.html", title="Assistant Professor Bing",
            prompt="Access the Secrets of the Universe", form=form)


@bp.route("/choose-action", methods=["GET", "POST"])
@login_required
def choose_action():
    form = ChooseActionForm()

    # process POST requests (with Ajax)
    if form.validate_on_submit():
        action = form.action.data
        redirect_url = ""

        if action == "create":
            redirect_url = url_for("admin.create_blogpost")
        elif action == "edit":
            redirect_url = url_for("admin.search_blogpost")
        elif action == "change_admin_password":
            redirect_url = url_for("admin.change_admin_password")
        else:
            return jsonify(redirect=False, flash="How did you do that?")

        return jsonify(redirect=True, redirect_url=redirect_url)

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Sleeping TA Yandex", prompt="42", form=form)


@bp.route("/create-blogpost", methods=["GET", "POST"])
@login_required
def create_blogpost():
    form = CreateBlogpostForm()

    # process POST requests (with Ajax)
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, subtitle=form.subtitle.data, content=form.content.data)
        new_post.sanitize_title()

        # check that title still exists after sanitization
        if new_post.sanitized_title == "":
            return jsonify(redirect=False,
                    flash="Post must have alphanumeric characters in its title.")

        # check that title is unique (sanitized is unique => non-sanitized is unique)
        if not new_post.are_titles_unique():
            return jsonify(redirect=False,
                    flash="There is already a post with that title or sanitized title.")
        
        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully!")
        return jsonify(redirect=True,
                redirect_url=url_for("blog.post",
                post_sanitized_title=new_post.sanitized_title)) # view completed post

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Create post",
            prompt="Create post", form=form)


@bp.route("/search-blogpost", methods=["GET", "POST"])
@login_required
def search_blogpost():
    form = SearchBlogpostForm()

    # process POST requests (with Ajax)
    if form.validate_on_submit():
        post = form.post.data
        if post is None:
            return jsonify(redirect=False,
                    flash="You somehow managed to choose nothing, congratulations.")
        return jsonify(redirect=True, redirect_url=url_for("admin.edit_blogpost", post_id=post.id))
        
    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Search Posts",
            prompt="Search posts", form=form)


@bp.route("/edit-blogpost", methods=["GET", "POST"])
@login_required
def edit_blogpost():
    post = db.session.get(Post, request.args.get("post_id"))
    if post is None:
        flash("That post no longer exists. Did you hit the back button? Regret your choice, did you?")
        return jsonify(redirect=True, redirect_url=url_for("admin.search_blogpost"))
    
    form = EditBlogpostForm(obj=post) # pre-populate fields

    import json
    # process POST requests (with Ajax)
    if form.validate_on_submit():
        # handle form deletion (after confirmation button)
        if "delete" in request.get_json():
            db.session.delete(post)
            db.session.commit()
            flash("Post deleted successfully!")
            return jsonify(redirect=True, redirect_url=url_for("blog.index"))

        # check that title is unique if changed
        if form.title.data != post.title:
            post_temp = Post(title=form.title.data, subtitle=form.subtitle.data, content=form.content.data)
            post_temp.sanitize_title() # need post_temp for this--populate_obj() seems to already add to db
            if not post_temp.are_titles_unique():
                return jsonify(redirect=False,
                        flash="There is already a post with that title or sanitized title.")

        form.populate_obj(post)
        post.sanitize_title()
        # check that title still exists after sanitization
        if post.sanitized_title == "":
            return jsonify(redirect=False,
                    flash="Post must have alphanumeric characters in its title.")
        
        post.edited_timestamp = datetime.now(timezone.utc) # updated edited time
        db.session.commit()
        flash("Post edited successfully!")
        return jsonify(redirect=True,
                redirect_url=url_for("blog.post",
                post_sanitized_title=post.sanitized_title)) # view edited post

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Edit Post",
            prompt=f"Edit post: {post.title}", form=form)
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
@login_required
def change_admin_password():
    form = ChangeAdminPasswordForm()

    # process POST requests (with Ajax)
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check given password
        if user is None or not user.check_password(form.old_password.data):
            return jsonify(redirect=False, flash="Old password is not correct.")

        # check new passwords are identical
        if form.new_password_1.data != form.new_password_2.data:
            return jsonify(redirect=False, flash="New passwords do not match.")
        
        user.set_password(form.new_password_1.data)
        db.session.commit()
        flash("Your password has been changed!")
        return jsonify(redirect=True, redirect_url=url_for("admin.login"))

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Change Admin Password",
            prompt="Do not make it password123456", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f"You have been logged out.")
    return redirect(url_for("main.index"))
