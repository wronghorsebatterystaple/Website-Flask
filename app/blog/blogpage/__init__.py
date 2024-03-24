from flask import Blueprint

bp = Blueprint("blogpage", __name__)

from app.blog.blogpage import routes
