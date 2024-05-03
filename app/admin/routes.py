import imghdr
import os
import shutil
import urllib.parse as ul
from werkzeug.utils import escape, secure_filename

from flask import current_app, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from wtforms.form import Form

from app import db, turnstile
from app.admin import bp
from app.admin.forms import *
from app.models import *
from app.forms import *
import app.util as util


def sanitize_filename(filename):
    filename = escape(secure_filename(filename))
    filename = filename.replace("(", "").replace(")", "") # for Markdown parsing
    return filename


def validate_image(image):
    header = image.read(512)
    image.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")


def upload_images(images, path_before_filename) -> str:
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

        path = os.path.join(path_before_filename, filename)
        os.makedirs(path_before_filename, exist_ok=True) # mkdir -p if not exist
        if not os.path.exists(path):
            image.save(path)
        else:
            return "Image already exists."

    return "success"


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        logout_user()

    if request.method == "GET":
        return render_template("admin/form-base.html", title="Login",
                prompt="Access the Secrets of the Universe", form=form, login_req=False)

    # Ajax: FormData
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)
        if not turnstile.verify():
            return jsonify(redirect_abs_url=url_for("main.bot_jail", _external=True))

        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check admin password
        if user is None or not user.check_password(request.form.get("password")):
            # display in submission errors section instead of flash
            return jsonify(submission_errors={"password":
                    ["No, the password is not \"solarwinds123\"."]})
        # No persistent cookies, so session expires on both browser close (if it isn't running in background)
        # and PERMANENT_SESSION_LIFETIME timeout (check README for cookie explanation)
        login_user(user, remember=False)
        session.permanent = False

        # assumes next is always within the same blueprint (request.url_root)!
        if request.args.get("next", "") != "":
            return jsonify(success=True, redirect_abs_url=request.args.get("next"),
                    flash_message="The universe is at your fingertips…")
        elif request.form.get("is_modal") == "yes":
            return jsonify(success=True, flash_message="The universe is at your fingertips…")
        return jsonify(success=True, redirect_abs_url=url_for("main.index", _external=True),
                flash_message="The universe is at your fingertips…")

    return "If you see this message, please panic."


@bp.route("/choose-action", methods=["GET", "POST"])
def choose_action():
    result = util.sign_in_if_not_admin(request)
    if result:
        return result

    form = ChooseActionForm()

    if request.method == "GET":
        return render_template("admin/form-base.html", title="Choose action",
                prompt="42", form=form, login_req=True)

    # Ajax: FormData
    elif request.method == "POST":
        if not current_user.is_authenticated:
            return jsonify(relogin=True)
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        action = request.form.get("action")
        redirect_abs_url = ""
        if action == "create":
            redirect_abs_url = url_for("admin.create_blogpost", _external=True)
        elif action == "edit":
            redirect_abs_url = url_for("admin.search_blogpost", _external=True)
        elif action == "change_admin_password":
            redirect_abs_url = url_for("admin.change_admin_password", _external=True)
        else:
            return jsonify(flash_message="Sneaky…")

        return jsonify(redirect_abs_url=redirect_abs_url)

    return "If you see this message, please panic."


@bp.route("/create-blogpost", methods=["GET", "POST"])
def create_blogpost():
    result = util.sign_in_if_not_admin(request)
    if result:
        return result

    form = CreateBlogpostForm()
    # set choices dynamically so we can access current_app context; also must do before POST handling so validation works?
    form.blog_id.choices = [(k, v) for k, v in current_app.config["BLOG_ID_TO_TITLE_WRITEABLE"].items()]

    if request.method == "GET":
        # automatically populate from query string if detected
        if request.args.get("blog_id") is not None \
                and request.args.get("blog_id") != current_app.config["ALL_POSTS_BLOG_ID"]:
            form.blog_id.data = request.args.get("blog_id")
        return render_template("admin/form-base.html", title="Create post",
                prompt="Create post", form=form, login_req=True)

    # Ajax: FormData
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post = Post(blog_id=int(request.form.get("blog_id")), title=request.form.get("title"),
                subtitle=request.form.get("subtitle"), content=request.form.get("content"))
        post.sanitize_title()
        post.expand_image_markdown()

        # check that title still exists after sanitization
        if post.sanitized_title == "":
            return jsonify(flash_message="Post must have alphanumeric characters in its title.")
        # check that title is unique (sanitized is unique => non-sanitized is unique)
        if not post.are_titles_unique():
            return jsonify(flash_message="There is already a post with that title or sanitized title.")

        # mark post as published and editable if creating on published blogpage
        if post.blog_id not in current_app.config["UNPUBLISHED_BLOG_IDS"]:
            post.published = True
        db.session.add(post)
        db.session.commit()

        # upload images if any
        try:
            res = upload_images(request.files.getlist("images"), os.path.join(current_app.root_path,
                    current_app.config["ROOT_TO_BLOGPAGE_STATIC"], post.blog_id, "images", str(post.id)))
            if not res == "success":
                return jsonify(flash_message=res)
        except Exception as e:
            return jsonify(flash_message=f"Image upload exception: {str(e)}")

        return jsonify(redirect_abs_url=url_for(f"blog.{post.blog_id}.post",
                post_sanitized_title=post.sanitized_title, _external=True),
                flash_message="Post created successfully!") # view completed post

    return "If you see this message, please panic."


@bp.route("/search-blogpost", methods=["GET", "POST"])
def search_blogpost():
    result = util.sign_in_if_not_admin(request)
    if result:
        return result

    form = SearchBlogpostForm()

    if request.method == "GET":
        return render_template("admin/form-base.html", title="Search Posts",
                prompt="Search posts", form=form, login_req=True)

    # Ajax: FormData
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post_id = request.form.get("post")
        if post_id is None:
            return jsonify(flash_message="You somehow managed to choose nothing, congratulations.")
        return jsonify(redirect_abs_url=url_for("admin.edit_blogpost", post_id=post_id, _external=True))

    return "If you see this message, please panic."


@bp.route("/edit-blogpost", methods=["GET", "POST"])
def edit_blogpost():
    result = util.sign_in_if_not_admin(request)
    if result:
        return result

    post = db.session.get(Post, request.args.get("post_id"))
    if post is None:
        return jsonify(redirect_abs_url=url_for("admin.search_blogpost", _external=True),
                flash_message="That post no longer exists. Did you hit the back button? Regret your choice, did you?")
    
    images_path = os.path.join(current_app.root_path,
            current_app.config["ROOT_TO_BLOGPAGE_STATIC"],
            post.blog_id, "images", str(post.id))
    form = EditBlogpostForm(obj=post) # pre-populate fields
    form.blog_id.choices = [(k, v) for k, v in \
            current_app.config["BLOG_ID_TO_TITLE_WRITEABLE"].items()]
    if os.path.exists(images_path) and os.path.isdir(images_path):
        form.delete_images.choices = [(f, f) for f in os.listdir(images_path) \
                if os.path.isfile(os.path.join(images_path, f))]
    form.content.data = post.collapse_image_markdown()

    if request.method == "GET":
        return render_template("admin/form-base.html", title=f"Edit Post: {post.title}",
                prompt=f"Edit post: {post.title}", form=form, login_req=True)

    # Ajax: FormData
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        # handle post deletion (after confirmation button)
        if "delete" in request.form:
            db.session.delete(post)
            db.session.commit()
            try:
                if os.path.exists(images_path) and os.path.isdir(images_path):
                    shutil.rmtree(images_path)
            except Exception as e:
                return jsonify(flash_message=f"Directory delete exception: {str(e)}")
            return jsonify(redirect_abs_url=url_for(f"blog.{post.blog_id}.index", _external=True),
                    flash_message="Post deleted successfully!")

        # handle post editing otherwise
        old_blog_id = post.blog_id
        old_sanitized_title = post.sanitized_title

        post_temp = Post()
        post_temp.title = request.form.get("title")
        post_temp.sanitize_title()
        # check that title still exists after sanitization
        if post.sanitized_title == "":
            return jsonify(flash_message="Post must have alphanumeric characters in its title.")
        # check that sanitized title is unique if changed; temp for unique check to work
        if post_temp.sanitized_title != old_sanitized_title:
            if not post_temp.are_titles_unique():
                return jsonify(flash_message="There is already a post with that title or sanitized title.")

        post.blog_id = request.form.get("blog_id")
        post.title = post_temp.title
        post.sanitized_title = post_temp.sanitized_title
        post.subtitle = request.form.get("subtitle")
        post.content = request.form.get("content")
        # update edited time if editing a published post
        if post.published:
            post.edited_timestamp = datetime.now(timezone.utc)
        else:
            # mark post as published and editable if not published and moving to published blogpage
            if request.form.get("blog_id") not in current_app.config["UNPUBLISHED_BLOG_IDS"]:
                post.published = True
            # keep updating created time instead of updated time if not published
            post.timestamp = datetime.now(timezone.utc)
        post.expand_image_markdown()

        # upload images if any
        try:
            res = upload_images(request.files.getlist("images"), images_path)
            if not res == "success":
                return jsonify(flash_message=res)
        except Exception as e:
            return jsonify(flash_message=f"Image upload exception: {str(e)}")

        # delete images if any
        try:
            for image in request.form.getlist("delete_images"):
                filepath = os.path.join(images_path, image)
                if os.path.exists(filepath):
                    os.remove(filepath)
            if os.path.exists(images_path) and len(os.listdir(images_path)) == 0 and os.path.isdir(images_path):
                shutil.rmtree(images_path)
        except Exception as e:
            return jsonify(flash_message=f"Image delete exception: {str(e)}")
        
        # move images if moving blogpost
        if post.blog_id != old_blog_id:
            if os.path.exists(images_path):
                try:
                    shutil.move(images_path, os.path.join(current_app.root_path,
                            current_app.config["ROOT_TO_BLOGPAGE_STATIC"],
                            post.blog_id, "images", str(post.id)))
                except Exception as e:
                    return jsonify(flash_message=f"Image move exception: {str(e)}")
            post.update_image_markdown_blog_id(old_blog_id) # shouldn't be needed but just in case?
        db.session.commit()

        return jsonify(redirect_abs_url=url_for(f"blog.{post.blog_id}.post",
                post_sanitized_title=post.sanitized_title, _external=True),
                flash_message="Post edited successfully!") # view edited post

    return "If you see this message, please panic."
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
def change_admin_password():
    result = util.sign_in_if_not_admin(request)
    if result:
        return result

    form = ChangeAdminPasswordForm()

    if request.method == "GET":
        return render_template("admin/form-base.html", title="Change Admin Password",
                prompt="Do not make it password123456", form=form, login_req=True)

    # Ajax: FormData
    elif request.method == "POST":
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
        logout_user()
        return jsonify(redirect_abs_url=url_for("main.index", _external=True),
                flash_message="Your password has been changed!")

    return "If you see this message, please panic."


@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()

    from_url = request.args.get("from_url")
    for url in current_app.config["LOGIN_REQUIRED_URLS"]:
        if from_url.startswith(url):
            return jsonify(redirect_abs_url=url_for("main.index", _external=True), 
                    flash_message="Mischief managed.")

    return jsonify(flash_message="Mischief managed.")
