import sqlalchemy as sa
from flask import current_app, jsonify, redirect, request, url_for
from flask_login import current_user

import app.util as util
from app import db
from app.blog import bp
from app.models import *


@bp.route("/", methods=["GET"])
def index():
    query_string = ""
    # preserve query string
    if request.query_string.decode() != "":
        query_string = "?" + request.query_string.decode()

    return redirect(
            url_for(f"blog.{current_app.config['ALL_POSTS_BLOGPAGE_ID']}.index", _external=True) + query_string)


## For more permanent links that don't change if a post changes title/moves between blogs
## MySQL also does not change id on delete
@bp.route("/<int:post_id>", methods=["GET"])
def post_by_id(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return redirect(url_for(
                f"blog.index",
                flash_message=util.encode_URI_component("That post doesn't exist."),
                _external=True))

    return redirect(url_for(
            f"blog.{post.blogpage_id}.post", post_sanitized_title=post.sanitized_title, _external=True))


###################################################################################################
# POST Endpoints
###################################################################################################


@bp.route("/get-posts-with-unread-comments", methods=["POST"])
@util.custom_login_required(request)
def get_posts_with_unread_comments():
    posts_with_unread_comments = {}
    posts = db.session.query(Post).all()
    for post in posts:
        comment_unread_count = post.get_comment_unread_count()
        if comment_unread_count > 0:
            posts_with_unread_comments[post.title] = {
                "unread_count": comment_unread_count,
                "url": url_for("blog.post_by_id", post_id=post.id, _external=True)
            }

    return jsonify(posts_with_unread_comments)
