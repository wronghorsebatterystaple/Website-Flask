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

    # Configs for blogpage blueprints
    HIDDEN_BLOG_IDS = [0]
    ALL_POSTS_BLOG_ID = 1
    BLOG_ID_TO_TITLE = {
        0: "The Backrooms",
        1: "All Posts",
        3: "Professor Google",
        6: "Writer's Block",
        7: "Writer's Unblock"
    }
    BLOG_ID_TO_TITLE_PUBLIC = { # exclude The Backrooms
        1: "All Posts",
        3: "Professor Google",
        6: "Writer's Block",
        7: "Writer's Unblock"
    }
    BLOG_ID_TO_TITLE_WRITEABLE = { # exclude All Posts
        0: "The Backrooms",
        3: "Professor Google",
        6: "Writer's Block",
        7: "Writer's Unblock"
    }
    BLOG_ID_TO_SUBTITLE = {
        0: "yes I know this is technically public",
        3: "THE BLOG WHERE I TEACH MYSELF CS AND MATH",
        6: "yes I stole this idea",
        7: "creative writing dumps from 3am"
    }
    BLOG_ID_TO_COLOR_CLASS = {
        3: "customgreen",
        6: "custompink",
        7: "custompink"
    }

    # Other
    VERIFIED_AUTHOR = "Verified Original Poster"
