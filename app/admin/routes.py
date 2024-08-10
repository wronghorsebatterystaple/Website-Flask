import os
import shutil

import sqlalchemy as sa
from flask import current_app, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from wtforms.form import Form

import app.admin.util as admin_util
import app.util as util
from app import db, turnstile
from app.admin import bp
from app.admin.forms import *
from app.forms import *
from app.models import *


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        logout_user()

    if request.method == "GET":
        return render_template(
                "admin/form_base.html",
                title="Login",
                prompt="Access the Secrets of the Universe",
                form=form)
    elif request.method == "POST":
        if not turnstile.verify():
            return jsonify(redirect_url=url_for("bot_jail", _external=True))
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check admin password
        if user is None or not user.check_password(request.form.get("password")):
            # display in submission errors section instead of flash
            return jsonify(submission_errors={
                "password": ["No, the password is not \"solarwinds123\"."]
            })

        # no persistent cookies, so session expires on both browser close (if it isn't running in background)
        # and PERMANENT_SESSION_LIFETIME timeout (check README for cookie explanation)
        login_user(user, remember=False)
        session.permanent = False

        if request.form.get("is_modal") == "yes":
            return jsonify(success=True, flash_message="The universe is at your fingertips…")

        next_url = request.args.get("next", url_for("admin.choose_action", _external=True))
        return jsonify(success=True, redirect_url=next_url, flash_message="The universe is at your fingertips…")

    return "If you see this message, please panic."


@bp.route("/choose-action", methods=["GET", "POST"])
@util.custom_login_required(content_type=util.ContentType.DEPENDS_ON_REQUEST_METHOD)
def choose_action():
    form = ChooseActionForm()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Choose action", prompt="42", form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        action = request.form.get("action")
        redirect_url = ""
        match action:
            case "create":
                redirect_url = url_for("admin.create_blogpost", _external=True)
            case "edit":
                redirect_url = url_for("admin.search_blogpost", _external=True)
            case "change_admin_password":
                redirect_url = url_for("admin.change_admin_password", _external=True)
            case _:
                return jsonify(flash_message="haker :3")

        return jsonify(redirect_url=redirect_url)

    return "If you see this message, please panic."


@bp.route("/create-blogpost", methods=["GET", "POST"])
@util.custom_login_required(content_type=util.ContentType.DEPENDS_ON_REQUEST_METHOD)
def create_blogpost():
    form = CreateBlogpostForm()
    blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    form.blogpage_id.choices = [(blogpage.id, blogpage.name) for blogpage in blogpages if blogpage.writeable]

    if request.method == "GET":
        try:
            blogpage_id = int(request.args.get("blogpage_id", default=None))
        except Exception:
            return jsonify(redirect_url=url_for(
                    "blog.index",
                    flash_message=util.encode_URI_component("haker :3"),
                    _external=True))

        # automatically populate blogpage form field from query string if detected
        if blogpage_id is not None and blogpage_id != current_app.config["ALL_POSTS_BLOGPAGE_ID"]:
            form.blogpage_id.data = blogpage_id # don't need decoding URL here; will use first option if invalid

        return render_template("admin/form_base.html", title="Create post", prompt="Create post", form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post = Post(
                blogpage_id=request.form.get("blogpage_id"),
                title=request.form.get("title"),
                subtitle=request.form.get("subtitle"),
                content=request.form.get("content"))
        
        post.sanitize_title()
        db.session.add(post)
        res = post.check_titles()
        if res is not None:
            return jsonify(flash_message=res)
        post.add_timestamps(False, True)
        post.expand_image_markdown()

        # upload images if any
        images_path = admin_util.get_images_path(post)
        res = admin_util.upload_images(request.files.getlist("images"), images_path)
        if res is not None:
            return jsonify(flash_message=res)

        db.session.commit()                                 # commit at very end when success is guaranteed
        return jsonify(
                redirect_url=url_for(
                        f"blog.{post.blogpage_id}.post",
                        post_sanitized_title=post.sanitized_title,
                        _external=True),
                flash_message="Post created successfully!") # view completed post

    return "If you see this message, please panic."


@bp.route("/search-blogpost", methods=["GET", "POST"])
@util.custom_login_required(content_type=util.ContentType.DEPENDS_ON_REQUEST_METHOD)
def search_blogpost():
    form = SearchBlogpostForm()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Search Posts", prompt="Search posts", form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post_id = request.form.get("post")
        if post_id is None:
            return jsonify(flash_message="You somehow managed to choose nothing, congratulations.")
        return jsonify(redirect_url=url_for("admin.edit_blogpost", post_id=post_id, _external=True))

    return "If you see this message, please panic."


@bp.route("/edit-blogpost", methods=["GET", "POST"])
@util.custom_login_required(content_type=util.ContentType.DEPENDS_ON_REQUEST_METHOD)
def edit_blogpost():
    try:
        post_id = int(request.args.get("post_id"))
    except Exception:
        return jsonify(redirect_url=url_for("admin.search_blogpost", _external=True), flash_message="haker :3")

    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify(
                redirect_url=url_for("admin.search_blogpost", _external=True),
                flash_message="That post no longer exists. Did you hit the back button? Regret it, do you?")
    
    form = EditBlogpostForm(obj=post) # pre-populate fields by name; again form must be created outside
    blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    form.blogpage_id.choices = [(blogpage.id, blogpage.name) for blogpage in blogpages if blogpage.writeable]
    form.content.data = post.collapse_image_markdown()
    
    images_path = admin_util.get_images_path(post)
    if os.path.exists(images_path) and os.path.isdir(images_path):
        images_choices = [(f, f) for f in os.listdir(images_path)
                         if os.path.isfile(os.path.join(images_path, f)) and not f.startswith(".")]
        images_choices.sort(key=lambda t: t[0])
        form.delete_images.choices = images_choices

    if request.method == "GET":
        return render_template(
                "admin/form_base.html",
                title=f"Edit Post: {post.title}",
                prompt=f"Edit post: {post.title}",
                form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        # handle post deletion
        if "delete" in request.form:
            db.session.delete(post)
            db.session.commit()
            try:
                if os.path.exists(images_path) and os.path.isdir(images_path):
                    shutil.rmtree(images_path)
            except Exception as e:
                return jsonify(flash_message=f"Directory delete exception: {str(e)}")
            return jsonify(
                    redirect_url=url_for(f"blog.{post.blogpage_id}.index", _external=True),
                    flash_message="Post deleted successfully!")

        # handle post editing otherwise
        old_blogpage_id = post.blogpage_id
        post.blogpage_id = request.form.get("blogpage_id")
        post.title = request.form.get("title")
        post.subtitle = request.form.get("subtitle")
        post.content = request.form.get("content")
        
        post.sanitize_title()
        res = post.check_titles()
        if res is not None:
            return jsonify(flash_message=res)
        post.add_timestamps(
                request.form.get("remove_edited_timestamp"),
                request.form.get("update_edited_timestamp"))
        post.expand_image_markdown()

        # upload images if any
        res = admin_util.upload_images(request.files.getlist("images"), images_path)
        if res is not None:
            return jsonify(flash_message=res)
        
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

        # delete unused images if applicable; we assume any image whose filename is not in the Markdown is unused
        if request.form.get("delete_unused_images") and os.path.exists(images_path):
            try:
                images = os.listdir(images_path)
                for image in images:
                    file_ext = os.path.splitext(image)[1]
                    if file_ext in current_app.config["IMAGE_UPLOAD_EXTENSIONS_CAN_DELETE_UNUSED"] \
                            and image not in post.content:
                        os.remove(os.path.join(images_path, image))

                if len(os.listdir(images_path)) == 0 and os.path.isdir(images_path):
                    shutil.rmtree(images_path)
            except Exception as e:
                return jsonify(flash_message=f"Image delete unused exception: {str(e)}")
        
        # move images if moving blogpost
        if post.blogpage_id != old_blogpage_id:
            if os.path.exists(images_path):
                try:
                    new_images_path = admin_util.get_images_path(post)
                    shutil.move(images_path, new_images_path)
                except Exception as e:
                    return jsonify(flash_message=f"Image move exception: {str(e)}")

        db.session.commit()
        return jsonify(
                redirect_url=url_for(
                        f"blog.{post.blogpage_id}.post",
                        post_sanitized_title=post.sanitized_title,
                        _external=True),
                flash_message="Post edited successfully!") # view edited post

    return "If you see this message, please panic."
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
@util.custom_login_required(content_type=util.ContentType.DEPENDS_ON_REQUEST_METHOD)
def change_admin_password():
    form = ChangeAdminPasswordForm()

    if request.method == "GET":
        return render_template(
                "admin/form_base.html",
                title="Change admin password",
                prompt="Don't make it \"solarwinds123\" or else my incorrect password message won't wor",
                form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        user = db.session.scalar(sa.select(User).where(User.username == "admin"))
        # check old password
        if user is None or not user.check_password(request.form.get("old_password")):
            return jsonify(submission_errors={
                "old_password": ["Incorrect password, uh oh."]
            })
        # check new passwords are identical
        if request.form.get("new_password_1") != request.form.get("new_password_2"):
            return jsonify(submission_errors={
                "new_password_1": ["Passwords do not match."],
                "new_password_2": ["Passwords do not match."]
            })
        
        user.set_password(request.form.get("new_password_1"))
        db.session.commit()
        logout_user()
        return jsonify(
                redirect_url=url_for("main.index", _external=True),
                flash_message="Your password has been changed!")

    return "If you see this message, please panic."


###################################################################################################
# POST Endpoints
###################################################################################################


@bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()

    previous = util.decode_URI_component(request.args.get("previous"))
    for url in current_app.config["LOGIN_REQUIRED_URLS"]:
        if previous.startswith(url):
            return jsonify(
                    redirect_url=url_for("main.index", _external=True),
                    flash_message="Mischief managed.")

    return jsonify(flash_message="Mischief managed.")
