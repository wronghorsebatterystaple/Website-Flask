import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    SERVER_NAME = "anonymousrand.xyz"
    CORS_ORIGINS = [f"https://{SERVER_NAME}", f"https://blog.{SERVER_NAME}"]
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Flask cookies
    SESSION_COOKIE_DOMAIN = f".{SERVER_NAME}"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = False
    PERMANENT_SESSION_LIFETIME = 3

    # Flask-WTF
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = False # allows cross-site Ajax POST (Flask-CORS whitelisting not enough)

    # Custom errors
    CUSTOM_ERRORS = {
        "REFRESH_CSRF": (499, "CSRF token expired because the session expired.")
    }

    # Paths
    ROOT_TO_BLOGPAGE_STATIC = "blog/static/blog/blogpage"
    BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC = "../static/blog/blogpage"

    # Other "conventional" configs
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    IMAGE_EXTENSIONS = [".jpg", ".png", ".gif"]
    POSTS_PER_PAGE = 10

    # Scuffed configs
    MAIN_PAGE_URL_FULL = f"https://{SERVER_NAME}"
    LOGIN_VIEW = "admin.login"
    LOGIN_REQUIRED_URLS = [ # for Flask access control
        f"{SERVER_NAME}/admin",
        f"blog.{SERVER_NAME}/the-backrooms"
    ]
    VERIFIED_AUTHOR = "verifiedoriginalposter" # lowercase and no spaces for easier comparison

    PRIVATE_BLOG_IDS = [0] # for displaying and Flask access control
    UNPUBLISHED_BLOG_IDS = [0] # for published dates on blogs
    ALL_POSTS_BLOG_ID = 1
    BLOG_ID_TO_TITLE = {
        0: "The Backrooms",
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
        3: "THE BLOG WHERE I TEACH MYSELF CS AND MATH",
        6: "yes I stole this idea",
        7: "creative writing and existential dumps from 3am"
    }
    BLOG_ID_TO_DESCRIPTION = {
        1: "all posts made by AnonymousRand.",
        3: "intution, explanations, and details about computer science and math topics unlike any class you've taken.",
        6: "the",
        7: "creative writing dumps or random pieces of vent from my journal."
    }
    BLOG_ID_TO_COLOR_CLASS = {
        3: "customgreen",
        6: "custompink",
        7: "custompink"
    }
