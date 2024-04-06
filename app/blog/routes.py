from flask import current_app, redirect, url_for

from app.blog import bp

@bp.route("/")
def index():
    return redirect(url_for(f"blog.{current_app.config['ALL_POSTS_BLOG_ID']}.index"))
