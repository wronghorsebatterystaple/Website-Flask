import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    SERVER_NAME = "anonymousrand.xyz"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Flask-Login
    SESSION_COOKIE_DOMAIN = f".{SERVER_NAME}"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600
    REMEMBER_COOKIE_DOMAIN = f".{SERVER_NAME}"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # Flask-WTF
    WTF_CSRF_TIME_LIMIT = None

    # Image uploads
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    IMAGE_EXTENSIONS = [".jpg", ".png", ".gif"]

    # Paths
    ROOT_TO_BLOGPAGE_STATIC = "blog/static/blog/blogpage"
    BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC = "../static/blog/blogpage"

    # Mappings for blogpage blueprints
    ALL_POSTS_BLOG_ID = 0;
    BLOG_ID_TO_TITLE = {
        0: "All Posts",
        2: "Professor Google",
        5: "Writer's Block",
        6: "Writer's Unblock"
    }
    BLOG_ID_TO_SUBTITLE = {
        2: "THE BLOG WHERE I TEACH MYSELF",
        5: "YES I STOLE THIS IDEA",
        6: "CREATIVE WRITING DUMPS FROM 3AM"
    }
