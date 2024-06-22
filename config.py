import os
from dotenv import load_dotenv

class Config(object):
    # Basics
    SERVER_NAME = "anonymousrand.xyz"
    ALLOWED_ORIGINS = [f"https://{SERVER_NAME}", f"https://blog.{SERVER_NAME}"]
    SECRET_KEY = os.environ.get("SECRET_KEY")
    csp_self = ["\'self\'", SERVER_NAME, f"blog.{SERVER_NAME}"]
    csp_default_src = csp_self
    CSP = {
        "default-src": csp_default_src,
        "connect-src": csp_default_src + [
            "data:",                        # DarkReader
            "cdnjs.cloudflare.com"          # Highlight.js
        ],
        "font-src": csp_default_src + [
            "cdn.jsdelivr.net",
            "fonts.googleapis.com",
            "fonts.gstatic.com"
        ],
        "img-src": csp_default_src + [
            "data:"                         # Bootstrap, DarkReader
        ],
        "script-src": csp_default_src + [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "code.jquery.com",
        ],
        "style-src": csp_default_src + [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "code.jquery.com",
            "fonts.googleapis.com",
            "\'unsafe-inline\'"             # MathJax >:(
        ],
        "base-uri": csp_default_src,
        "frame-ancestors": csp_default_src
    }

    # Flask cookies
    PERMANENT_SESSION_LIFETIME = 86400
    SESSION_COOKIE_DOMAIN = f".{SERVER_NAME}"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = False

    # Flask-WTF
    WTF_CSRF_SSL_STRICT = False # allows cross-site Ajax POST (Flask-CORS whitelisting not enough)
    WTF_CSRF_TIME_LIMIT = None # CSRF token lasts until session expires

    # Database
    DB_CONFIGS = {
        "MAXLEN_BLOGPAGE_URL_PATH": 50,
        "MAXLEN_BLOGPAGE_TITLE": 50,
        "MAXLEN_BLOGPAGE_SUBTITLE": 100,
        "MAXLEN_BLOGPAGE_META_DESCRIPTION": 500,
        "MAXLEN_BLOGPAGE_COLOR_HTML_CLASS": 100,
        "MAXLEN_POST_TITLE": 150,
        "MAXLEN_POST_SUBTITLE": 150,
        "MAXLEN_POST_CONTENT": 100000,
        "MAXLEN_COMMENT_AUTHOR": 100,
        "MAXLEN_COMMENT_CONTENT": 5000,
        "MAXLEN_USER_USERNAME": 25,
        "MAXLEN_USER_EMAIL": 512,
        "MAXLEN_USER_PASSWORD": 50,
        "MAXLEN_USER_PASSWORD_HASH": 256
    }
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Custom errors
    CUSTOM_ERRORS = {
        "REFRESH_CSRF": (499, "CSRF Error")
    }

    # Other "conventional" configs
    IMAGE_EXTENSIONS = [".gif", ".jpg", ".png"]
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    LOGIN_VIEW = "admin.login"
    POSTS_PER_PAGE = 20

    # Scuffed configs
    # Paths
    BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC = "../static/blog/blogpage"
    ROOT_TO_BLOGPAGE_STATIC = "blog/static/blog/blogpage"

    ALL_POSTS_BLOGPAGE_ID = 1
    BLOGPAGE_ID_TO_PATH = { # KEEP UPDATED WITH DB (for initializing blueprints) and use string keys because negatives
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
    LOGIN_REQUIRED_URLS = [ # for Flask access control on logout
        f"{SERVER_NAME}/admin",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-2']}",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-3']}",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-6']}",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-7']}"
    ]
    VERIFIED_AUTHOR = "originalposter" # lowercase and no spaces for easier comparison
