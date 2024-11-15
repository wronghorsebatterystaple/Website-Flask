import os
import shutil
import tldextract

import sqlalchemy as sa
from flask import current_app, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from wtforms.form import Form

import app.admin.util as admin_util
import app.util as util
from app import db
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
        # and on `PERMANENT_SESSION_LIFETIME` timeout (check readme for cookie explanation)
        login_user(user, remember=False)
        session.permanent = False

        # if modal login, we are done
        if request.form.get("is_modal") == "true":
            return jsonify(success=True, flash_msg="The universe is at your fingertips…")

        # if not modal login, then try to redirect back to previous page
        next_url = util.decode_uri_component(
                request.args.get("next", url_for("admin.choose_action", _external=True)))
        next_url_extracted = tldextract.extract(next_url)
        # make sure we can only redirect within the same domain
        if f"{next_url_extracted.domain}.{next_url_extracted.suffix}" == current_app.config["SERVER_NAME"]:
            # when we do the redir back after logging in, we need to let our server know that it is a post-login
            # redir, so if we were trying to redir back to an API endpoint or something instead of a typical
            # webpage, we can handle it properly
            #
            # the `is_redir_after_login` key takes the following path:
            #     `login()` view func (here) adds to response JSON ->
            #     `doAjaxResponseBase()` handles response JSON and adds to params of url being redirected to ->
            #     view func of url being redirected to handles this
            return jsonify(success=True, redir_url=next_url, is_redir_after_login=True)

        return jsonify(success=True, redir_url=url_for("admin.choose_action", flash_msg="haker :3", _external=True))

    return "If you see this message, please panic.", 500


@bp.route("/choose-action", methods=["GET", "POST"])
@util.set_content_type(util.ContentType.DEPENDS_ON_REQ_METHOD)
@util.requires_login()
def choose_action(**kwargs):
    form = ChooseActionForm()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Choose action", prompt="42", form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        action = request.form.get("action")
        redir_url = ""
        match action:
            case "create":
                redir_url = url_for("admin.create_blogpost", _external=True)
            case "edit":
                redir_url = url_for("admin.search_blogpost", _external=True)
            case "change_admin_password":
                redir_url = url_for("admin.change_admin_password", _external=True)
            case _:
                return jsonify(flash_msg="haker :3")

        return jsonify(redir_url=redir_url)

    return "If you see this message, please panic.", 500


@bp.route("/create-blogpost", methods=["GET", "POST"])
@util.set_content_type(util.ContentType.DEPENDS_ON_REQ_METHOD)
@util.requires_login()
def create_blogpost(**kwargs):
    form = CreateBlogpostForm()
    blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    form.blogpage_id.choices = [(blogpage.id, blogpage.name) for blogpage in blogpages if blogpage.is_writeable]

    if request.method == "GET":
        # automatically populate blogpage form field from query string if detected
        # don't need URL decode here, and uses first option if invalid
        blogpage_id = request.args.get("blogpage_id", None)
        if blogpage_id is not None:
            try:
                blogpage_id = int(blogpage_id)
                blogpage = db.session.get(Blogpage, blogpage_id)
                if blogpage and blogpage.is_writeable:
                    form.blogpage_id.data = int(blogpage_id)
            except Exception:
                pass
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
        err = post.check_and_try_flushing(True)
        if err:
            return jsonify(flash_msg=err)
        post.add_timestamps(False, False)
        post.expand_image_markdown()

        # upload images if any
        images_path = admin_util.get_images_path(post)
        err = admin_util.upload_images(request.files.getlist("images"), images_path)
        if err:
            return jsonify(flash_msg=err)

        db.session.commit()                             # commit at very end when success is guaranteed
        return jsonify(
                redir_url=url_for(
                        f"blog.{post.blogpage_id}.post", post_sanitized_title=post.sanitized_title, _external=True),
                flash_msg="Post created successfully!") # view completed post

    return "If you see this message, please panic.", 500


@bp.route("/search-blogpost", methods=["GET", "POST"])
@util.set_content_type(util.ContentType.DEPENDS_ON_REQ_METHOD)
@util.requires_login()
def search_blogpost(**kwargs):
    form = SearchBlogpostForm()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Search Posts", prompt="Search posts", form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post_id = request.form.get("post")
        if post_id is None:
            return jsonify(flash_msg="You somehow managed to choose nothing, congratulations.")
        return jsonify(redir_url=url_for("admin.edit_blogpost", post_id=post_id, _external=True))

    return "If you see this message, please panic.", 500


@bp.route("/edit-blogpost", methods=["GET", "POST"])
@util.set_content_type(util.ContentType.DEPENDS_ON_REQ_METHOD)
@util.requires_login()
def edit_blogpost(**kwargs):
    try:
        post_id = int(request.args.get("post_id"))
    except Exception:
        return util.redir_depending_on_req_method("admin.search_blogpost", flash_msg="haker :3")

    post = db.session.get(Post, post_id)
    if post is None:
        return util.redir_depending_on_req_method(
                "admin.search_blogpost",
                flash_msg="That post no longer exists. Did you hit the back button? Regret it, do you?")
    
    form = EditBlogpostForm(obj=post) # pre-populate fields by name; again form must be created outside
    blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    form.blogpage_id.choices = [(blogpage.id, blogpage.name) for blogpage in blogpages if blogpage.is_writeable]
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
                prompt="Edit post",
                form=form)
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        # handle post deletion
        if "delete_post" in request.form:
            db.session.delete(post)
            db.session.commit()
            try:
                if os.path.exists(images_path) and os.path.isdir(images_path):
                    shutil.rmtree(images_path)
            except Exception as e:
                return jsonify(flash_msg=f"Directory delete exception: {str(e)}")
            return jsonify(
                    redir_url=url_for(f"blog.{post.blogpage_id}.index", _external=True),
                    flash_msg="Post deleted successfully!")

        # handle post editing otherwise
        old_blogpage_id = post.blogpage_id
        post.blogpage_id = request.form.get("blogpage_id")
        post.title = request.form.get("title")
        post.subtitle = request.form.get("subtitle")
        post.content = request.form.get("content")
        
        post.sanitize_title()
        err = post.check_and_try_flushing(False)
        if err:
            return jsonify(flash_msg=err)
        post.add_timestamps(
                request.form.get("remove_edited_timestamp"), request.form.get("update_edited_timestamp"))
        post.expand_image_markdown()

        # upload images if any
        err = admin_util.upload_images(request.files.getlist("images"), images_path)
        if err:
            return jsonify(flash_msg=err)
        
        # delete images if any
        try:
            for image in request.form.getlist("delete_images"):
                filepath = os.path.join(images_path, image)
                if os.path.exists(filepath):
                    os.remove(filepath)

            # delete image directory if now empty
            admin_util.delete_dir_if_empty(images_path)
        except Exception as e:
            return jsonify(flash_msg=f"Image delete exception: {str(e)}")

        # delete unused images if applicable; we assume any image whose filename is not in the Markdown is unused
        if request.form.get("delete_unused_images") and os.path.exists(images_path):
            try:
                images = os.listdir(images_path)
                for image in images:
                    file_ext = os.path.splitext(image)[1]
                    if file_ext in current_app.config["IMAGE_UPLOAD_EXTS_CAN_DELETE_UNUSED"] \
                            and image not in post.content:
                        os.remove(os.path.join(images_path, image))

                admin_util.delete_dir_if_empty(images_path)
            except Exception as e:
                return jsonify(flash_msg=f"Image delete unused exception: {str(e)}")
        
        # move images if moving blogpost
        if post.blogpage_id != old_blogpage_id:
            if os.path.exists(images_path):
                try:
                    new_images_path = admin_util.get_images_path(post)
                    shutil.move(images_path, new_images_path)
                except Exception as e:
                    return jsonify(flash_msg=f"Image move exception: {str(e)}")

        db.session.commit()
        return jsonify(
                redir_url=url_for(
                        f"blog.{post.blogpage_id}.post", post_sanitized_title=post.sanitized_title, _external=True),
                flash_msg="Post edited successfully!") # view edited post

    return "If you see this message, please panic.", 500
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
@util.set_content_type(util.ContentType.DEPENDS_ON_REQ_METHOD)
@util.requires_login()
def change_admin_password(**kwargs):
    form = ChangeAdminPasswordForm()

    if request.method == "GET":
        return render_template(
                "admin/form_base.html",
                title="Change admin password",
                prompt="Don't make it \"solarwinds123\" or else my incorrect password message won't wo",
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
        return jsonify(redir_url=url_for("main.index", _external=True), flash_msg="Your password has been changed! Here's some randomart: ඞ") # this works!?

    return "If you see this message, please panic.", 500


@bp.route("/session-status", methods=["GET"])
def session_status():
    resp = make_response(jsonify(logged_in=current_user.is_authenticated))
    resp.headers["Cache-Control"] = "no-cache, no-store"
    return resp


###################################################################################################
# POST Endpoints
###################################################################################################


@bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return jsonify(
            redir_url=url_for(current_app.config["AFTER_LOGOUT_VIEW"], _external=True),
            flash_msg="Mischief managed.")
