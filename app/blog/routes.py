from app.blog import bp
from app.models import *
from app import db

import sqlalchemy as sa
from flask import render_template, abort

import markdown

@bp.route("/")
def index():
    posts = db.session.query(Post).all()
    return render_template("blog/index.html", posts=posts)

@bp.route("/<string:post_title_for_url>")
def post(post_title_for_url):
    post = db.session.query(Post).filter(Post.title_for_url == post_title_for_url).first()
    if post is None:
        abort(404)

    setattr(post, "content", markdown.markdown(post.content, extensions=["extra"]))
    return render_template("blog/post.html", post=post)
