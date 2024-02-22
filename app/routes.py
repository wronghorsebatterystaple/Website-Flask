from app import app # import app variable from app package
from app import db
from app.models import Post, Comment, Image
import sqlalchemy as sa
from flask import render_template, abort

@app.route("/")
def index():
    posts = db.session.query(Post).all()
    return render_template("index.html", posts=posts)

@app.route("/<string:post_title_for_url>")
def post(post_title_for_url):
    post = db.session.query(Post).filter(Post.title_for_url == post_title_for_url).first()
    if post is None:
        abort(404)
    return render_template("post.html", post=post)
