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
            return "File name was reduced to atoms by sanitization."

        file_ext = os.path.splitext(filename)[1]
        invalid = \
                file_ext not in current_app.config["IMAGE_UPLOAD_EXTENSIONS"] \
                or (file_ext in current_app.config["IMAGE_UPLOAD_EXTENSIONS_CAN_VALIDATE"] \
                and file_ext != validate_image(image.stream)) # imghdr can't check SVG; trustable since admin-only?
        if invalid:
            return "Invalid image. If it's another heic or webp im gonna lose my mind i swear to god i hate heic and webp theyre so annoying i hat"

        path = os.path.join(path_before_filename, filename)
        os.makedirs(path_before_filename, exist_ok=True)      # mkdir -p if not exist
        image.save(path)                                      # replaces image if it's already there

    return "success"


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        logout_user()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Login",
                prompt="Access the Secrets of the Universe", form=form)

    # Ajax: FormData
    elif request.method == "POST":
        if not turnstile.verify():
            return jsonify(redirect_url_abs=url_for("main.bot_jail", _external=True))
        if not form.validate():
            return jsonify(submission_errors=form.errors)

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
            return jsonify(success=True, redirect_url_abs=request.args.get("next"), # keeping the URL encoded works
                    flash_message="The universe is at your fingertips…")
        elif request.form.get("is_modal") == "yes":
            return jsonify(success=True, flash_message="The universe is at your fingertips…")
        return jsonify(success=True, redirect_url_abs=url_for("main.index", _external=True),
                flash_message="The universe is at your fingertips…")

    return "If you see this message, please panic."


@bp.route("/choose-action", methods=["GET", "POST"])
@util.custom_login_required(request)
def choose_action():
    form = ChooseActionForm()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Choose action",
                prompt="42", form=form)

    # Ajax: FormData
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        action = request.form.get("action")
        redirect_url_abs = ""
        if action == "create":
            redirect_url_abs = url_for("admin.create_blogpost", _external=True)
        elif action == "edit":
            redirect_url_abs = url_for("admin.search_blogpost", _external=True)
        elif action == "change_admin_password":
            redirect_url_abs = url_for("admin.change_admin_password", _external=True)
        else:
            return jsonify(flash_message="Sneaky…")

        return jsonify(redirect_url_abs=redirect_url_abs)

    return "If you see this message, please panic."


@bp.route("/create-blogpost", methods=["GET", "POST"])
@util.custom_login_required(request)
def create_blogpost():
    # must create form outside of POST handling or else validate() throws 500 for some reason?
    form = CreateBlogpostForm()
    all_blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    form.blogpage_id.choices = [(blogpage.id, blogpage.title) for blogpage in all_blogpages if blogpage.writeable]

    if request.method == "GET":
        try:
            blogpage_id = int(request.args.get("blogpage_id", default=None))
        except Exception:
            return jsonify(redirect_url_abs=url_for("blog.index",
                    flash=util.encode_URI_component("Good try."),
                    _external=True))

        # automatically populate blogpage form field from query string if detected
        if blogpage_id is not None and blogpage_id != current_app.config["ALL_POSTS_BLOGPAGE_ID"]:
            form.blogpage_id.data = blogpage_id # don't need decoding URL here; will use first option if invalid

        return render_template("admin/form_base.html", title="Create post",
                prompt="Create post", form=form)

    # Ajax: FormData
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post = Post(blogpage_id=request.form.get("blogpage_id"), title=request.form.get("title"),
                subtitle=request.form.get("subtitle"), content=request.form.get("content"))
        if post.subtitle == "": # standardize to None/NULL
            post.subtitle = None
        post.sanitize_title()
        db.session.add(post)
        db.session.flush() # must do this before expand_image_markdown so post gets automatically assigned an id
                           # must also do this to auto populate blogpage relationship from foreign key to use later
                           # must also do add() before are_titles_unique(), as specified by are_titles_unique()

        # check that title still exists after sanitization
        if post.sanitized_title == "":
            return jsonify(flash_message="Post must have alphanumeric characters in its title.")
        # check that titles are unique
        if not post.are_titles_unique():
            return jsonify(flash_message="There is already a post with that title or sanitized title.")

        # mark post as published and editable if creating on published blogpage
        if not post.blogpage.unpublished:
            post.published = True
        else:
            post.published = False

        post.expand_image_markdown()
        db.session.commit()

        # upload images if any
        try:
            images_path = os.path.join(current_app.root_path,
                    current_app.config["ROOT_TO_BLOGPAGE_STATIC"],
                    str(post.blogpage_id), "images", str(post.id))
            res = upload_images(request.files.getlist("images"), images_path)
            if not res == "success":
                return jsonify(flash_message=res)
        except Exception as e:
            return jsonify(flash_message=f"File upload exception: {str(e)}")

        return jsonify(redirect_url_abs=url_for(f"blog.{post.blogpage_id}.post",
                post_sanitized_title=post.sanitized_title, _external=True),
                flash_message="Post created successfully!") # view completed post

    return "If you see this message, please panic."


@bp.route("/search-blogpost", methods=["GET", "POST"])
@util.custom_login_required(request)
def search_blogpost():
    form = SearchBlogpostForm()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Search Posts",
                prompt="Search posts", form=form)

    # Ajax: FormData
    elif request.method == "POST":
        if not form.validate():
            return jsonify(submission_errors=form.errors)

        post_id = request.form.get("post")
        if post_id is None:
            return jsonify(flash_message="You somehow managed to choose nothing, congratulations.")
        return jsonify(redirect_url_abs=url_for("admin.edit_blogpost", post_id=post_id, _external=True))

    return "If you see this message, please panic."


@bp.route("/edit-blogpost", methods=["GET", "POST"])
@util.custom_login_required(request)
def edit_blogpost():
    try:
        post_id = int(request.args.get("post_id"))
    except Exception:
        return jsonify(redirect_url_abs=url_for("admin.search_blogpost", _external=True),
                flash_message="Good try.")

    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify(redirect_url_abs=url_for("admin.search_blogpost", _external=True),
                flash_message="That post no longer exists. Did you hit the back button? Regret it, do you?")

    images_path = os.path.join(current_app.root_path,
            current_app.config["ROOT_TO_BLOGPAGE_STATIC"],
            str(post.blogpage_id), "images", str(post.id))

    form = EditBlogpostForm(obj=post) # pre-populate fields by name; again form must be created outside
    all_blogpages = db.session.query(Blogpage).order_by(Blogpage.ordering).all()
    form.blogpage_id.choices = [(blogpage.id, blogpage.title) for blogpage in all_blogpages if blogpage.writeable]
    form.content.data = post.collapse_image_markdown()
    if os.path.exists(images_path) and os.path.isdir(images_path):
        images_choices = [(f, f) for f in os.listdir(images_path) \
                if os.path.isfile(os.path.join(images_path, f))]
        images_choices.sort(key=lambda t: t[0])
        form.delete_images.choices = images_choices

    if request.method == "GET":
        return render_template("admin/form_base.html", title=f"Edit Post: {post.title}",
                prompt=f"Edit post: {post.title}", form=form)

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
            return jsonify(redirect_url_abs=url_for(f"blog.{post.blogpage_id}.index", _external=True),
                    flash_message="Post deleted successfully!")

        # handle post editing otherwise
        old_blogpage_id = post.blogpage_id
        post.blogpage_id = request.form.get("blogpage_id")
        post.title = request.form.get("title")
        post.sanitize_title()
        db.session.flush()

        if post.sanitized_title == "":
            return jsonify(flash_message="Post must have alphanumeric characters in its title.")
        if not post.are_titles_unique():
            return jsonify(flash_message="There is already a post with that title or sanitized title.")

        post.subtitle = request.form.get("subtitle")
        if post.subtitle == "":
            post.subtitle = None
        post.content = request.form.get("content")

        # update edited time if editing a published post
        if post.published:
            if request.form.get("remove_edited_timestamps"):
                post.edited_timestamp = None
            elif request.form.get("dont_update_edited_timestamp"):
                pass
            else:
                post.edited_timestamp = datetime.now(timezone.utc)
            # unpublish if moving back to backrooms
            if post.blogpage.unpublished:
                post.published = False
                post.edited_timestamp = None
        else:
            # mark post as published and editable if not published and moving to published blogpage
            if not post.blogpage.unpublished:
                post.published = True
            # keep updating created time instead of updated time if not published
            post.timestamp = datetime.now(timezone.utc)
        post.expand_image_markdown() # must be done after post.blogpage_id is finalized for image markdown updating!

        # delete images if any
        try:
            for image in request.form.getlist("delete_images"):
                filepath = os.path.join(images_path, image)
                if os.path.exists(filepath):
                    os.remove(filepath)
            if os.path.exists(images_path) and len(os.listdir(images_path)) == 0 and os.path.isdir(images_path):
                shutil.rmtree(images_path)
        except Exception as e:
            return jsonify(flash_message=f"File delete exception: {str(e)}")

        # delete unused images if that is checked; do this after deleting normally
        # but before uploading to make sure newly-uploaded images aren't immediately scrapped
        if request.form.get("delete_unused_images"):
            try:
                if os.path.exists(images_path):
                    images = os.listdir(images_path)
                    # todo check without extension?
                    for image in images:
                        file_ext = os.path.splitext(image)[1]
                        if file_ext in current_app.config["IMAGE_UPLOAD_EXTENSIONS_CAN_DELETE_UNUSED"] \
                                and image not in post.content:
                            os.remove(os.path.join(images_path, image))

                    if len(os.listdir(images_path)) == 0 and os.path.isdir(images_path):
                        shutil.rmtree(images_path)
            except Exception as e:
                return jsonify(flash_message=f"File delete unused exception: {str(e)}")
        
        # upload images if any
        try:
            res = upload_images(request.files.getlist("images"), images_path)
            if not res == "success":
                return jsonify(flash_message=res)
        except Exception as e:
            return jsonify(flash_message=f"File upload exception: {str(e)}")

        # move images if moving blogpost
        if post.blogpage_id != old_blogpage_id:
            if os.path.exists(images_path):
                try:
                    shutil.move(images_path, os.path.join(os.path.split(images_path)[0], str(post.id)))
                except Exception as e:
                    return jsonify(flash_message=f"File move exception: {str(e)}")
        db.session.commit()

        return jsonify(redirect_url_abs=url_for(f"blog.{post.blogpage_id}.post",
                post_sanitized_title=post.sanitized_title, _external=True),
                flash_message="Post edited successfully!") # view edited post

    return "If you see this message, please panic."
        

@bp.route("/change-admin-password", methods=["GET", "POST"])
@util.custom_login_required(request)
def change_admin_password():
    form = ChangeAdminPasswordForm()

    if request.method == "GET":
        return render_template("admin/form_base.html", title="Change Admin Password",
                prompt="Do not make it password123456", form=form)

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
        return jsonify(redirect_url_abs=url_for("main.index", _external=True),
                flash_message="Your password has been changed!")

    return "If you see this message, please panic."


@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()

    previous = util.decode_URI_component(request.args.get("previous"))
    for url in current_app.config["LOGIN_REQUIRED_URLS"]:
        if previous.startswith(url):
            return jsonify(redirect_url_abs=url_for("main.index", _external=True), 
                    flash_message="Mischief managed.")

    return jsonify(flash_message="Mischief managed.")
