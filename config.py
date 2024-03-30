import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    SERVER_NAME = "anonymousrand.xyz"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Flask-Login
    REMEMBER_COOKIE_DOMAIN = f".{SERVER_NAME}"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = 3600
    PERMANENT_SESSION_LIFETIME = 3600

    # Image uploads
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    IMAGE_EXTENSIONS = [".jpg", ".png", ".gif"]

    # Relative path to blogpages' static directory from root_path
    BLOGPAGE_STATIC_FROM_ROOT = "blog/static/blog/blogpage"
    # Relative path to blogpages' static directory from blogpage's routes.py
    BLOGPAGE_STATIC_FROM_ROUTES = "../static/blog/blogpage"

    # Mappings for blogpage blueprints
    BLOG_ID_TO_TITLE = {
        0: "Professor Google",
        1: "Writer's Block",
        2: "Writer's Unblock"
    }
    BLOG_ID_TO_SUBTITLE = {
        0: "THE BLOG WHERE I TEACH MYSELF",
        1: "YES I STOLE THIS IDEA",
        2: "CREATIVE WRITING DUMPS FROM 3AM"
    }
