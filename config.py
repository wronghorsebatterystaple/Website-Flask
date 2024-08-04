import os
from dotenv import load_dotenv

class Config(object):
    ## Basics
    SERVER_NAME = "anonymousrand.xyz"
    ALLOWED_ORIGINS = [f"https://{SERVER_NAME}", f"https://blog.{SERVER_NAME}"]
    SECRET_KEY = os.environ.get("SECRET_KEY")
    _CSP_SELF = ["\'self\'", SERVER_NAME, f"blog.{SERVER_NAME}"]
    _CSP_DEFAULT_SRC = _CSP_SELF
    CSP = {
        "default-src": _CSP_DEFAULT_SRC,
        "connect-src": _CSP_DEFAULT_SRC + [
            "data:",                        # DarkReader
            "cdnjs.cloudflare.com"          # Highlight.js
        ],
        "font-src": _CSP_DEFAULT_SRC + [
            "cdn.jsdelivr.net",
            "fonts.googleapis.com",
            "fonts.gstatic.com"
        ],
        "img-src": _CSP_DEFAULT_SRC + [
            "data:"                         # Bootstrap, DarkReader
        ],
        "script-src": _CSP_DEFAULT_SRC + [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "code.jquery.com",
        ],
        "style-src": _CSP_DEFAULT_SRC + [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "code.jquery.com",
            "fonts.googleapis.com",
            "\'unsafe-inline\'"             # MathJax >:(
        ],
        "base-uri": _CSP_DEFAULT_SRC,
        "frame-ancestors": _CSP_DEFAULT_SRC
    }

    ## Cookies
    PERMANENT_SESSION_LIFETIME = 86400
    SESSION_COOKIE_DOMAIN = f".{SERVER_NAME}"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = False

    ## Flask-WTF
    WTF_CSRF_SSL_STRICT = False # allows cross-site Ajax POST (Flask-CORS whitelisting not enough)
    WTF_CSRF_TIME_LIMIT = None # CSRF token lasts until session expires

    ## Flask-SQLAlchemy/database
    DB_CONFIGS = {
        "BLOGPAGE_URL_PATH_LENMAX": 50,
        "BLOGPAGE_TITLE_LENMAX": 50,
        "BLOGPAGE_SUBTITLE_LENMAX": 100,
        "BLOGPAGE_META_DESCRIPTION_LENMAX": 500,
        "BLOGPAGE_COLOR_HTML_CLASS_LENMAX": 100,
        "POST_TITLE_LENMAX": 150,
        "POST_SUBTITLE_LENMAX": 150,
        # can't enforce this db-side because it's MEDIUMTEXT so just don't be more than 2^24 - 1 Okayge
        "POST_CONTENT_LENMAX": 100000,
        "COMMENT_AUTHOR_LENMAX": 100,
        "COMMENT_CONTENT_LENMAX": 5000,
        "USER_USERNAME_LENMAX": 25,
        "USER_EMAIL_LENMAX": 512,
        "USER_PASSWORD_LENMAX": 50,
        "USER_PASSWORD_HASH_LENMAX": 256
    }
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    ## Other "conventional" configs
    POST_COMMENT_ALLOWED_TAGS = {
        "abbr", "acronym", "b", "blockquote", "br", "center", "code", "details", "div", "em", "h1", "h2", "h3", "i",
        "li", "p", "pre", "ol", "small", "span", "strong", "sub", "summary", "sup", "table", "tbody", "td", "th",
        "thead", "tr", "ul"
    }
    POST_COMMENT_ALLOWED_ATTRIBUTES = [
        "class", "colspan", "data-align-bottom", "data-align-center", "data-align-right", "data-align-top",
        "data-col-width", "height", "rowspan", "title", "width"
    ]
    CUSTOM_ERRORS = {
        "REFRESH_CSRF": (499, "CSRF Error")
    }
    IMAGE_UPLOAD_EXTENSIONS = [".gif", ".jpeg", ".jpg", ".png", ".svg", ".xcf"]
    IMAGE_UPLOAD_EXTENSIONS_CAN_VALIDATE = [".gif", ".jpeg", ".jpg", ".png"]
    IMAGE_UPLOAD_EXTENSIONS_CAN_DELETE_UNUSED = [".gif", ".jpeg", ".jpg", ".png", ".svg"]
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    LOGIN_VIEW = "admin.login"
    POSTS_PER_PAGE = 20

    ## Scuffed configs
    BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC = "../static/blog/blogpage"
    ROOT_TO_BLOGPAGE_STATIC = "blog/static/blog/blogpage"
    ALL_POSTS_BLOGPAGE_ID = 1
    BLOGPAGE_ID_TO_PATH = { # SYNC: with db (for initializing blueprints)
        "1": "/all",
        "2": "/misc",
        "3": "/professor-google",
        "5": "/the-fake-news-network",
        "6": "/writers-block",
        "7": "/writers-unblock",
        "-2": "/misc-backrooms",
        "-3": "/professor-google-backrooms",
        "-5": "/the-fake-news-network-backrooms",
        "-6": "/writers-block-backrooms",
        "-7": "/writers-unblock-backrooms"
    }
    LOGIN_REQUIRED_URLS = [ # for Flask access control on logout
        f"{SERVER_NAME}/admin",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-2']}",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-3']}",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-5']}",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-6']}",
        f"blog.{SERVER_NAME}{BLOGPAGE_ID_TO_PATH['-7']}"
    ]
    VERIFIED_AUTHOR = "AnonymousRand"
