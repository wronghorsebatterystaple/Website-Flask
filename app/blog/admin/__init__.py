from flask import Blueprint

bp = Blueprint("admin", __name__)

from app.blog.admin import routes

