from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user
import sqlalchemy as sa

from app import db, turnstile
from app.blog import bp
from app.blog.forms import *
from app.models import *
import app.util as util


@bp.route("/")
def index():
    return redirect(url_for(f"blog.{current_app.config['ALL_POSTS_BLOG_ID']}.index"))


# For more permanent links that don't change if a post changes title/moves between blogs
# MySQL also does not change id on delete
@bp.route("/<int:post_id>")
def post_by_id(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return redirect(url_for(f"blog.index",
                flash=util.encode_URI_component("That post doesn't exist.")))

    return redirect(url_for(f"blog.{post.blogpage_id}.post", post_sanitized_title=post.sanitized_title))


@bp.route("/add-comment", methods=["POST"])
def add_comment():
    if not turnstile.verify():
        return jsonify(redirect_url_abs=url_for("main.bot_jail", _external=True))

    add_comment_form = AddCommentForm()
    if not add_comment_form.validate():
        return jsonify(submission_errors=add_comment_form.errors)
    # make sure non-admin users can't masquerade as verified author
    if request.form["author"].lower().replace(" ", "") == current_app.config["VERIFIED_AUTHOR"] \
            and not current_user.is_authenticated:
        return jsonify(submission_errors={"author": ["$8 isn't going to buy you a verified checkmark here."]})

    post = db.session.query(Post).get(request.form["post_id"])
    comment = Comment(author=request.form["author"], content=request.form["content"],
            post=post) # SQLAlchemy automatically generates post_id ForeignKey from post relationship()
    if not comment.insert_comment(post, db.session.get(Comment, request.form["parent"])):
        return jsonify(flash_message="Sneaky…")
    db.session.add(comment)
    db.session.commit()

    return jsonify(success=True, flash_message="Comment added successfully!")


@bp.route("/delete-comment", methods=["POST"])
@util.custom_login_required(request)
def delete_comment():
    comment = db.session.get(Comment, request.form["comment_id"])
    if comment is None:
        return jsonify(success=True, flash_message=f"That comment doesn't exist.")

    post = db.session.query(Post).get(request.form["post_id"])
    descendants = comment.get_descendants_list(post)
    if not comment.remove_comment(post):
        return jsonify(flash_message="Sneaky…")
    for descendant in descendants:
        db.session.delete(descendant)
    db.session.delete(comment)
    db.session.commit()

    return jsonify(success=True, flash_message="1984 established!")
