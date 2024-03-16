import sqlalchemy as sa
from sqlalchemy import desc
from flask_login import current_user
from flask import flash, get_flashed_messages, redirect, render_template, request, url_for

from app.blog import bp
from app.blog.forms import *
from app import db
from app.models import *
from app.util.turnstile_check import has_failed_turnstile

import markdown

@bp.route("/", methods=["GET", "POST"])
def index():
    create_blogpost_button = CreateBlogpostButton()
    # process POST requests (create blogpost button):
    if create_blogpost_button.validate_on_submit():
        if has_failed_turnstile():
            return redirect(url_for("main.bot_jail"))

        return redirect(url_for("admin.create_blogpost"))

    # process GET requests otherwise
    posts = db.session.query(Post).order_by(desc(Post.timestamp))
    return render_template("blog/index.html", posts=posts, create_blogpost_button=create_blogpost_button)

@bp.route("/<string:post_sanitized_title>", methods=["GET", "POST"])
def post(post_sanitized_title):
    add_comment_form = AddCommentForm()
    edit_blogpost_button = EditBlogpostButton()
    post = db.session.query(Post).filter(Post.sanitized_title == post_sanitized_title).first()
    if post is None:
        flash("The post doesn't exist.")
        return redirect(url_for("blog.index"))

    # process POST requests (adding comments; after making sure that post still exists)
    if add_comment_form.validate_on_submit():
        if has_failed_turnstile():
            return redirect(url_for("main.bot_jail"))

        comment = Comment(author=add_comment_form.author.data, content=add_comment_form.content.data,
                post=post) # SQLAlchemy automatically generates post_id ForeignKey from post relationship()
        if not comment.insert_comment(post, db.session.get(Comment, 52)):
            flash("Attempted addition of comment under the wrong post")
            return redirect(request.url)
        db.session.add(comment)
        db.session.commit()
        flash("Comment added successfully!")
        return redirect(request.url)

    # process POST requests (editing/deleting blogposts)
    if edit_blogpost_button.validate_on_submit():
        if has_failed_turnstile():
            return redirect(url_for("main.bot_jail"))

        return redirect(url_for("admin.edit_blogpost", post_id=post.id))

    # process GET requests otherwise
    post.content = markdown.markdown(post.content, extensions=["extra"])
    
    comments_query = post.comments.select().order_by(desc(Comment.timestamp))
    comments = db.session.scalars(comments_query).all()
    for comment in comments:
        comment.content = markdown.markdown(comment.content, extensions=["extra"])

    return render_template("blog/post.html", post=post,
            get_descendants_list=Comment.get_descendants_list,
            comments=comments, add_comment_form=add_comment_form,
            edit_blogpost_button=edit_blogpost_button)

