import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    SERVER_NAME = "anonymousrand.xyz"
    ALLOWED_ORIGINS = [f"https://{SERVER_NAME}", f"https://blog.{SERVER_NAME}"]
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Flask cookies
    SESSION_COOKIE_DOMAIN = f".{SERVER_NAME}"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = False
    PERMANENT_SESSION_LIFETIME = 86400

    # Flask-WTF
    WTF_CSRF_TIME_LIMIT = None # CSRF token lasts until session expires
    WTF_CSRF_SSL_STRICT = False # allows cross-site Ajax POST (Flask-CORS whitelisting not enough)

    # Custom errors
    CUSTOM_ERRORS = {
        "REFRESH_CSRF": (499, "CSRF Error")
    }

    # Paths
    ROOT_TO_BLOGPAGE_STATIC = "blog/static/blog/blogpage"
    BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC = "../static/blog/blogpage"

    # Other "conventional" configs
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    IMAGE_EXTENSIONS = [".jpg", ".png", ".gif"]
    POSTS_PER_PAGE = 10

    # Scuffed configs
    LOGIN_VIEW = "admin.login"
    LOGIN_REQUIRED_URLS = [ # for Flask access control on logout
        f"{SERVER_NAME}/admin",
        f"blog.{SERVER_NAME}/professor-google-backrooms",
        f"blog.{SERVER_NAME}/writers-block-backrooms",
        f"blog.{SERVER_NAME}/writers-unblock-backrooms",
    ]
    VERIFIED_AUTHOR = "verifiedoriginalposter" # lowercase and no spaces for easier comparison

    PRIVATE_BLOG_IDS = ["-3", "-6", "-7"] # for displaying and Flask access control
    UNPUBLISHED_BLOG_IDS = ["-3", "-6", "-7"] # for published dates on blogs
    ALL_POSTS_BLOG_ID = "1"
    BLOG_ID_TO_URL = {
        "1": "/all",
        "3": "/professor-google",
        "-3": "/professor-google-backrooms",
        "6": "/writers-block",
        "-6": "/writers-block-backrooms",
        "7": "/writers-unblock",
        "-7": "/writers-unblock-backrooms"
    }
    BLOG_ID_TO_TITLE = {
        "1": "All Posts",
        "3": "Professor Google",
        "-3": "Professor Google - The Backrooms",
        "6": "Writer's Block",
        "-6": "Writer's Block - The Backrooms",
        "7": "Writer's Unblock",
        "-7": "Writer's Unblock - The Backrooms"
    }
    BLOG_ID_TO_TITLE_WRITEABLE = { # exclude All Posts
        "3": "Professor Google",
        "-3": "Professor Google - The Backrooms",
        "6": "Writer's Block",
        "-6": "Writer's Block - The Backrooms",
        "7": "Writer's Unblock",
        "-7": "Writer's Unblock - The Backrooms"
    }
    BLOG_ID_TO_SUBTITLE = {
        "3": "THE BLOG WHERE I TEACH MYSELF CS AND MATH",
        "6": "yes I stole this idea",
        "7": "creative writing and existential dumps from 3am"
    }
    BLOG_ID_TO_DESCRIPTION = {
        "1": "all posts by AnonymousRand.",
        "3": "intution, explanations, and details about computer science and math topics unlike any class you've taken.",
        "6": "the",
        "7": "creative writing dumps or random pieces of vent."
    }
    BLOG_ID_TO_COLOR_CLASS = {
        "3": "custom-green-deep",
        "6": "custom-pink",
        "7": "custom-pink"
    }
