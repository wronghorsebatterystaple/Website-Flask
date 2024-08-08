"""
Use this blueprint instead of `blog.blogpage` for things that are not on a per-blogpage basis.
"""

from flask import Blueprint

blueprint_name = "blog"
bp = Blueprint(blueprint_name, __name__, template_folder="templates/", static_folder="static/")

from . import routes
