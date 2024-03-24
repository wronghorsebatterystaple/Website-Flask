from flask import render_template

from app.blog import bp

@bp.route("/")
def index():
    return render_template("blog/index.html")
