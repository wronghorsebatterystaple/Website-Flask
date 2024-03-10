import sqlalchemy as sa
from sqlalchemy import desc
from flask import render_template, abort

from app.blog import bp
from app import db
from app.models import *

import markdown

@bp.route("/")
def index():
    posts = db.session.query(Post).order_by(desc(Post.timestamp))
    return render_template("blog/index.html", posts=posts)

@bp.route("/<string:post_sanitized_title>")
def post(post_sanitized_title):
    post = db.session.query(Post).filter(Post.sanitized_title == post_sanitized_title).first()
    if post is None:
        abort(404)

    setattr(post, "content", markdown.markdown(post.content, extensions=["extra"]))
    return render_template("blog/post.html", post=post)
