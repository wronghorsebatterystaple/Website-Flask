from app import app # import app variable from app package
from app import db
from app.models import Post, Comment, Image
import sqlalchemy as sa
from flask import render_template

@app.route("/")
def index():
    posts = db.session.query(Post).all()
    return render_template("index.html", posts=posts)
