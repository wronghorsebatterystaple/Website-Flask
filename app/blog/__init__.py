from flask import Blueprint

bp = Blueprint("blog", __name__, template_folder="templates", static_folder="static")

from app.blog import routes
