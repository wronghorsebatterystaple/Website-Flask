import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    SERVER_NAME = "anonymousrand.xyz"
    ALLOWED_ORIGINS = [f"https://{SERVER_NAME}", f"https://blog.{SERVER_NAME}"]
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    csp_self = ["\'self\'", SERVER_NAME, f"*.{SERVER_NAME}"]
    CSP = {
        "default-src": csp_self,
        "font-src": csp_self + [
            "cdn.jsdelivr.net",
            "fonts.googleapis.com",
            "fonts.gstatic.com"
        ],
        "img-src": csp_self + [
            "data:"
        ],
        "script-src": csp_self + [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "code.jquery.com"
        ],
        "style-src": [
            "*",
            "\'unsafe-inline\'" # TODO
        ]
    }

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
    POSTS_PER_PAGE = 15

    # Scuffed configs
    LOGIN_REQUIRED_BLOG_IDS = ["-2", "-3", "-6", "-7"] # for displaying and Flask access control
    UNPUBLISHED_BLOG_IDS = ["-2", "-3", "-6", "-7"] # for published dates on blogs
    ALL_POSTS_BLOG_ID = "1"
    BLOG_ID_TO_PATH = {
        "1": "/all",
        "2": "/misc",
        "3": "/professor-google",
        "6": "/writers-block",
        "7": "/writers-unblock",
        "-2": "/misc-backrooms",
        "-3": "/professor-google-backrooms",
        "-6": "/writers-block-backrooms",
        "-7": "/writers-unblock-backrooms"
    }
    BLOG_ID_TO_TITLE = {
        "1": "All Posts",
        "2": "/misc/",
        "-2": "/misc/ - The Backrooms",
        "3": "Professor Google",
        "-3": "Professor Google - The Backrooms",
        "6": "Writer's Block",
        "-6": "Writer's Block - The Backrooms",
        "7": "Writer's Unblock",
        "-7": "Writer's Unblock - The Backrooms"
    }
    BLOG_ID_TO_TITLE_WRITEABLE = { # exclude All Posts
        "2": BLOG_ID_TO_TITLE["2"],
        "-2": BLOG_ID_TO_TITLE["-2"],
        "3": BLOG_ID_TO_TITLE["3"],
        "-3": BLOG_ID_TO_TITLE["-3"],
        "6": BLOG_ID_TO_TITLE["6"],
        "-6": BLOG_ID_TO_TITLE["-6"],
        "7": BLOG_ID_TO_TITLE["7"],
        "-7": BLOG_ID_TO_TITLE["-7"]
    }
    BLOG_ID_TO_SUBTITLE = {
        "3": "THE BLOG WHERE I TEACH MYSELF CS AND MATH",
        "6": "yes I stole this idea",
        "7": "creative writing and existential dumps from 3am"
    }
    BLOG_ID_TO_DESCRIPTION = {
        "1": "all posts by AnonymousRand.",
        "2": "all the posts that don't really belong anywhere else",
        "3": "intution, explanations, and details about computer science and math topics unlike any class you've taken.",
        "6": "the",
        "7": "creative writing dumps or random pieces of vent."
    }
    BLOG_ID_TO_COLOR_CLASS = {
        "2": "custom-blue",
        "3": "custom-green",
        "6": "custom-pink",
        "7": "custom-pink"
    }

    LOGIN_VIEW = "admin.login"
    LOGIN_REQUIRED_URLS = [ # for Flask access control on logout
        f"{SERVER_NAME}/admin",
        f"blog.{SERVER_NAME}/{BLOG_ID_TO_PATH['-2']}",
        f"blog.{SERVER_NAME}/{BLOG_ID_TO_PATH['-3']}",
        f"blog.{SERVER_NAME}/{BLOG_ID_TO_PATH['-6']}",
        f"blog.{SERVER_NAME}/{BLOG_ID_TO_PATH['-7']}"
    ]
    VERIFIED_AUTHOR = "originalposter" # lowercase and no spaces for easier comparison
