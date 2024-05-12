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


@bp.route("/add-comment", methods=["POST"])
def endpoint_add_comment():
    if not turnstile.verify():
        return jsonify(redirect_abs_url=url_for("main.bot_jail", _external=True))

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
        return jsonify(redirect_abs_url=url_for(f"{request.blueprint}.index", _external=True),
                flash_message="Sanity check is not supposed to fail…")
    db.session.add(comment)
    db.session.commit()

    return jsonify(success=True, flash_message="Comment added successfully!")


@bp.route("/delete-comment", methods=["POST"])
def endpoint_delete_comment():
    result = util.custom_unauthorized(request)
    if result:
        return result

    comment = db.session.get(Comment, request.form["comment_id"])
    if comment is None:
        return jsonify(success=True, flash_message=f"That comment doesn't exist.")

    post = db.session.query(Post).get(request.form["post_id"])
    descendants = comment.get_descendants_list(post)
    if not comment.remove_comment(post):
        return jsonify(redirect_abs_url=url_for(f"{request.blueprint}.index", _external=True),
                flash_message="Sanity check is not supposed to fail…")
    for descendant in descendants:
        db.session.delete(descendant)
    db.session.delete(comment)
    db.session.commit()

    return jsonify(success=True, flash_message="1984 established!")
