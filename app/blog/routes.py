import sqlalchemy as sa
from sqlalchemy import desc
from flask import flash, redirect, render_template, request, url_for

from app.blog import bp
from app.blog.forms import *
from app import db
from app.models import *
from app.util.turnstile_check import has_failed_turnstile

import markdown

@bp.route("/")
def index():
    posts = db.session.query(Post).order_by(desc(Post.timestamp))
    return render_template("blog/index.html", posts=posts)

@bp.route("/<string:post_sanitized_title>")
def post(post_sanitized_title):
    form = AddCommentForm()

    post = db.session.query(Post).filter(Post.sanitized_title == post_sanitized_title).first()
    if post is None:
        flash("The post doesn't exist.")
        return redirect(url_for("blog.index"))

    # process POST requests (after making sure post that is being commented on still exists)
    if form.validate_on_submit():
        if has_failed_turnstile():
            return redirect(url_for("main.bot_jail"))

        comment = Comment(author_name=form.name.data, content=form.content.data,
                post=post) # SQLAlchemy automatically generate post_id ForeignKey from post relationship()
        db.session.add(comment)
        db.session.commit()
        flash("Comment added successfully!")
        return redirect(request.url)

    # process GET requests otherwise
    setattr(post, "content", markdown.markdown(post.content, extensions=["extra"]))
    comments = db.sessoin.query(Comment).filter
    return render_template("blog/post.html", post=post)
