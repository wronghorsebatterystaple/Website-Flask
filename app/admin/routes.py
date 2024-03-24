import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from wtforms.form import Form
from flask import current_app, flash, jsonify, redirect, render_template, request, url_for

from app.admin import bp
from app.admin.forms import *
from app import db
from app.models import *
from app.util.uri_util import encode_uri_component
from app.util.turnstile_check import has_failed_turnstile

import imghdr
import os
import urllib.parse as ul
from werkzeug.utils import escape, secure_filename


def sanitize_filename(filename):
    filename = escape(secure_filename(filename))
    filename = filename.replace("(", "").replace(")", "")
    return filename


def validate_image(image):
    header = image.read(512)
    image.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")


def upload_images(images, post_id: int) -> str:
    for image in images:
        if image.filename == "": # this happens when no image is submitted
            continue

        filename = sanitize_filename(image.filename)
        if filename == "":
            return "Image name was reduced to atoms by sanitization."

        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config["IMAGE_EXTENSIONS"] \
                or file_ext != validate_image(image.stream):
            return "Invalid image."

        path_before_filename = os.path.join(current_app.root_path,
                "blog/static/blog/images", str(post_id))
        path = os.path.join(path_before_filename, filename)
        os.makedirs(path_before_filename, exist_ok=True) # mkdir -p if not exist
        if not os.path.exists(path):
            image.save(path)
        else:
            return "Image name already exists."

    return "success"


@bp.route("/login", methods=["GET", "POST"])
def login():
    # make sure logged-in admin doesn't try to log in again
    if current_user.is_authenticated:
        logout_user()

    form = PasswordForm()

    # process POST requests (with Ajax: FormData)
    if request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)
        if has_failed_turnstile():
            return jsonify(redirect_uri=url_for("main.bot_jail"))

        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check admin password
        if user is None or not user.check_password(request.form.get("password")):
            return jsonify(flash_message="Invalid password lol")
        login_user(user, remember=True)
        
        # allow redirects from @login_required
        next_page = request.args.get("next")
        if next_page is None or ul.urlsplit(next_page).netloc != "": # ensure redirects are only local for security
            next_page = url_for("admin.choose_action")
        return jsonify(redirect_uri=next_page)

    # process GET requests otherwise (page being loaded)
    return render_template("admin/form-base.html", title="Assistant Professor Bing",
            prompt="Access the Secrets of the Universe", form=form)


@bp.route("/choose-action", methods=["GET", "POST"])
@login_required
def choose_action():
    form = ChooseActionForm()

    # process POST requests (with Ajax: FormData)
    if request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        action = request.form.get("action")
        redirect_uri = ""

        if action == "create":
            redirect_uri = url_for("admin.create_blogpost")
        elif action == "edit":
            redirect_uri = url_for("admin.search_blogpost")
        elif action == "change_admin_password":
            redirect_uri = url_for("admin.change_admin_password")
        else:
            return jsonify(flash_message="How did you do that?")

        return jsonify(redirect_uri=redirect_uri)

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Sleeping TA Yandex", prompt="42", form=form)


@bp.route("/create-blogpost", methods=["GET", "POST"])
@login_required
def create_blogpost():
    form = CreateBlogpostForm()

    # process POST requests (with Ajax: FormData)
    if request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        new_post = Post(title=request.form.get("title"), subtitle=request.form.get("subtitle"), content=request.form.get("content"))
        new_post.sanitize_title()
        new_post.expand_image_markdown()

        # check that title still exists after sanitization
        if new_post.sanitized_title == "":
            return jsonify(flash_message="Post must have alphanumeric characters in its title.")
        # check that title is unique (sanitized is unique => non-sanitized is unique)
        if not new_post.are_titles_unique():
            return jsonify(flash_message="There is already a post with that title or sanitized title.")

        db.session.add(new_post)
        db.session.commit()

        # upload images if any
        res = upload_images(request.files.getlist("images"), new_post.id)
        if not res == "success":
            return jsonify(flash_message=res)

        return jsonify(redirect_uri=url_for("blog.post",
                post_sanitized_title=new_post.sanitized_title),
                flash_message="Post created successfully") # view completed post

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Create post",
            prompt="Create post", form=form)


@bp.route("/search-blogpost", methods=["GET", "POST"])
@login_required
def search_blogpost():
    form = SearchBlogpostForm()

    # process POST requests (with Ajax: FormData)
    if request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post_id = request.form.get("post")
        if post_id is None:
            return jsonify(flash_message="You somehow managed to choose nothing, congratulations.")
        return jsonify(redirect_uri=url_for("admin.edit_blogpost", post_id=post_id))
        
    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Search Posts",
            prompt="Search posts", form=form)


@bp.route("/edit-blogpost", methods=["GET", "POST"])
@login_required
def edit_blogpost():
    post = db.session.get(Post, request.args.get("post_id"))
    if post is None:
        return jsonify(redirect_uri=url_for("admin.search_blogpost"),
                flash_message="That post no longer exists. Did you hit the back button? Regret your choice, did you?")
    
    form = EditBlogpostForm(obj=post) # pre-populate fields
    form.content.data = post.collapse_image_markdown()

    # process POST requests (with Ajax: FormData)
    if request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        # handle post deletion (after confirmation button)
        if "delete" in request.form:
            db.session.delete(post)
            db.session.commit()
            return jsonify(redirect_uri=url_for("blog.index"),
                    flash_message="Post deleted successfully!")

        # handle post editing otherwise
        old_title = post.title
        post.title = request.form.get("title")
        post.subtitle = request.form.get("subtitle")
        post.content = request.form.get("content")
        post.sanitize_title()

        # check that title still exists after sanitization
        if post.sanitized_title == "":
            return jsonify(flash_message="Post must have alphanumeric characters in its title.")
        # check that title is unique if changed
        if post.title != old_title:
            if not post.are_titles_unique():
                return jsonify(flash_message="There is already a post with that title or sanitized title.")

        post.expand_image_markdown()
        post.edited_timestamp = datetime.now(timezone.utc) # updated edited time
        db.session.commit()

        # upload images if any
        res = upload_images(request.files.getlist("images"), post.id)
        if not res == "success":
            return jsonify(flash_message=res)

        return jsonify(redirect_uri=url_for("blog.post", post_sanitized_title=post.sanitized_title),
                flash_message="Post edited successfully!") # view edited post

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Edit Post",
            prompt=f"Edit post: {post.title}", form=form)
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
@login_required
def change_admin_password():
    form = ChangeAdminPasswordForm()

    # process POST requests (with Ajax: FormData)
    if request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check given password
        if user is None or not user.check_password(request.form.get("old_password")):
            return jsonify(flash_message="Old password is not correct.")

        # check new passwords are identical
        if request.form.get("new_password_1") != request.form.get("new_password_2"):
            return jsonify(flash_message="New passwords do not match.")
        
        user.set_password(request.form.get("new_password_1"))
        db.session.commit()
        return jsonify(redirect_uri=url_for("admin.login"),
                flash=True, flash_message="Your password has been changed!")

    # process GET requests otherwise
    return render_template("admin/form-base.html", title="Change Admin Password",
            prompt="Do not make it password123456", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index", flash=encode_uri_component("Mischief managed.")))
