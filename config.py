import os
from dotenv import load_dotenv

class Config(object):
    # basics
    SERVER_NAME = "anonymousrand.xyz"
    ALLOWED_ORIGINS = [f"https://{SERVER_NAME}", f"https://blog.{SERVER_NAME}"]
    SECRET_KEY = os.environ.get("SECRET_KEY")
    _csp_self = ["\'self\'", SERVER_NAME, f"blog.{SERVER_NAME}"]
    _csp_default_src = _csp_self
    CSP = {
        "default-src": _csp_default_src,
        "connect-src": _csp_default_src + [
            "data:",                        # DarkReader
            "cdnjs.cloudflare.com"          # Highlight.js
        ],
        "font-src": _csp_default_src + [
            "cdn.jsdelivr.net",             # MathJax
            "fonts.googleapis.com",
            "fonts.gstatic.com"
        ],
        "img-src": _csp_default_src + [
            "data:"                         # Bootstrap, DarkReader
        ],
        "script-src": _csp_default_src + [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "code.jquery.com",
        ],
        "style-src": _csp_default_src + [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "code.jquery.com",
            "fonts.googleapis.com",
            "\'unsafe-inline\'"             # a lot of things apparently
        ],
        "base-uri": _csp_default_src,
        "frame-ancestors": _csp_default_src
    }

    # cookies
    PERMANENT_SESSION_LIFETIME = 604800 # one week
    SESSION_COOKIE_DOMAIN = f".{SERVER_NAME}"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = False

    # Flask-WTF
    WTF_CSRF_SSL_STRICT = False # allows cross-site Ajax POST (Flask-CORS whitelisting not enough)
    WTF_CSRF_TIME_LIMIT = None  # CSRF token lasts until session expires

    # Flask-SQLAlchemy/database
    DB_CONFIGS = {
        "BLOGPAGE_NAME_MAXLEN": 50,
        "BLOGPAGE_SUBNAME_MAXLEN": 100,
        "BLOGPAGE_URL_PATH_MAXLEN": 50,
        "BLOGPAGE_META_DESCRIPTION_MAXLEN": 500,
        "BLOGPAGE_COLOR_MAXLEN": 100,
        "POST_TITLE_MAXLEN": 150,
        "POST_SUBTITLE_MAXLEN": 150,
        # can't enforce this db-side because it's MEDIUMTEXT so just don't be more than 2^24 - 1 Okayge
        "POST_CONTENT_MAXLEN": 100000,
        "COMMENT_AUTHOR_MAXLEN": 100,
        "COMMENT_CONTENT_MAXLEN": 5000,
        "USER_USERNAME_MAXLEN": 25,
        "USER_EMAIL_MAXLEN": 512,
        "USER_PASSWORD_MAXLEN": 50,
        "USER_PASSWORD_HASH_MAXLEN": 256
    }
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Jinja (must be explicitly configured in `app/__init__.py`)
    JINJA_LSTRIP_BLOCKS = True
    JINJA_TRIM_BLOCKS = True

    # other "conventional" configs
    CUSTOM_ERRORS = {
        "REFRESH_CSRF": (499, "CSRF Error")
    }
    POST_COMMENT_ALLOWED_TAGS = {
        "abbr", "acronym", "b", "blockquote", "br", "center", "code", "details", "div", "em", "h1", "h2", "h3", "i",
        "li", "p", "pre", "ol", "small", "span", "strong", "sub", "summary", "sup", "table", "tbody", "td", "th",
        "thead", "tr", "ul"
    }
    POST_COMMENT_ALLOWED_ATTRIBUTES = [
        "class", "colspan", "data-align-bottom", "data-align-center", "data-align-right", "data-align-top",
        "data-col-width", "height", "rowspan", "title", "width"
    ]
    IMAGE_UPLOAD_EXTENSIONS = [".gif", ".jpeg", ".jpg", ".png", ".svg", ".xcf"]
    IMAGE_UPLOAD_EXTENSIONS_CAN_VALIDATE = [".gif", ".jpeg", ".jpg", ".png"]
    IMAGE_UPLOAD_EXTENSIONS_CAN_DELETE_UNUSED = [".gif", ".jpeg", ".jpg", ".png", ".svg"]
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024 # 100 MB
    LOGIN_VIEW = "admin.login"
    AFTER_LOGOUT_VIEW = "main.index"
    POSTS_PER_PAGE = 20
    VERIFIED_AUTHOR = "AnonymousRand"

    # scuffed configs; SYNC!
    BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC = "../static/blogpage"
    ROOT_TO_BLOGPAGE_STATIC = "blog/static/blogpage"
    # this is not in db as it's only used for initializing blueprints, during which db is not yet accessible
    BLOGPAGE_ID_TO_URL_PREFIX = {
         "1": "/all",
         "2": "/misc",
        "-2": "/misc-backrooms",
         "3": "/professor-google",
        "-3": "/professor-google-backrooms",
         "4": "/typewriter-monkey-does-ctfs",
        "-4": "/typewriter-monkey-does-ctfs-backrooms",
         "5": "/the-fake-news-network",
        "-5": "/the-fake-news-network-backrooms",
         "6": "/writers-block",
        "-6": "/writers-block-backrooms",
         "7": "/writers-unblock",
        "-7": "/writers-unblock-backrooms"
    }
