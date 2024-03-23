import sqlalchemy as sa
from sqlalchemy import desc
from flask_login import current_user
from flask import jsonify, redirect, render_template, request, url_for

from app.blog import bp
from app.blog.forms import *
from app import db
from app.models import *
from app.util.uri_util import encode_uri_component, url_with_flash
from app.util.turnstile_check import has_failed_turnstile

import markdown
import re


@bp.route("/")
def index():
    create_blogpost_button = CreateBlogpostButton()
    posts = db.session.query(Post).order_by(desc(Post.timestamp))
    return render_template("blog/index.html", posts=posts, create_blogpost_button=create_blogpost_button)


@bp.route("/<string:post_sanitized_title>", methods=["GET", "POST"])
def post(post_sanitized_title):
    add_comment_form = AddCommentForm()
    reply_comment_button = ReplyCommentButton()
    edit_blogpost_button = EditBlogpostButton()
    post = db.session.query(Post).filter(Post.sanitized_title == post_sanitized_title).first()
    if post is None:
        return redirect(url_for("blog.index", flash=encode_uri_component("The post doesn't exist.")))

    # process POST requests (adding comments) (with Ajax: FormData)
    if request.method == "POST":
        if not add_comment_form.validate():
            return jsonify(submission_errors=add_comment_form.errors)
        if has_failed_turnstile():
            return jsonify(redirect_uri=url_for("main.bot_jail"))

        comment = Comment(author=request.form["author"], content=request.form["content"],
                post=post) # SQLAlchemy automatically generates post_id ForeignKey from post relationship()
        if not comment.insert_comment(post, db.session.get(Comment, request.form["parent"])):
            return jsonify(redirect_uri=url_for("blog.index"),
                    flash_message="Sanity check is not supposed to fail...")
        db.session.add(comment)
        db.session.commit()
        return jsonify(success=True, flash_message="Comment added successfully!")

    # process GET requests otherwise
    post.content = markdown.markdown(post.content, extensions=["extra"])

    comments_query = post.comments.select().order_by(desc(Comment.timestamp))
    comments = db.session.scalars(comments_query).all()
    for comment in comments:
        comment.content = markdown.markdown(comment.content, extensions=["extra"])

    return render_template("blog/post.html", post=post,
            get_descendants_list=Comment.get_descendants_list,
            comments=comments, add_comment_form=add_comment_form,
            reply_comment_button = reply_comment_button,
            edit_blogpost_button=edit_blogpost_button)


@bp.route("/create-blogpost-button", methods=["POST"])
def create_blogpost_button():
    return redirect(url_for("admin.create_blogpost"))


@bp.route("/edit-blogpost-button", methods=["POST"])
def edit_blogpost_button():
    return redirect(url_for("admin.edit_blogpost", post_id=request.args.get("post_id")))
