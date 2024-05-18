from flask import Flask, jsonify, redirect, url_for
from config import Config

from flask_cors import CORS
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_turnstile import Turnstile
from flask_wtf.csrf import CSRFProtect, CSRFError

from app.forms import *
from app.util import *

import secrets


# declare extension instances outside so blueprints can still do `from app import db` etc.
cors = CORS(origins=Config.ALLOWED_ORIGINS, supports_credentials=True)
csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = Config.LOGIN_VIEW
login_manager.session_protection = "strong" # deletes session cookie on IP/UA change
talisman = Talisman()
turnstile = Turnstile()

def create_app(config_class=Config):
    # create app variable (Flask instance)
    app = Flask(__name__)
    app.config.from_object(config_class)

    # register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.blog import bp as blog_bp
    from app.blog.blogpage import bp as blog_blogpage_bp
    # "name" param must match blog_id in "Post" db table
    # This makes the endpoints "blog.0.index", "blog.1.index" etc.
    for k, v in config_class.BLOG_ID_TO_PATH.items():
        blog_bp.register_blueprint(blog_blogpage_bp, url_prefix=v, name=k)
    app.register_blueprint(blog_bp, subdomain="blog")

    # register global routes and stuff
    @app.context_processor
    def inject_login_form():
        return dict(login_form=LoginForm())

    # Regenerate CSRF token on token (tied to session) expire
    # then let Ajax take it from there with custom error fail() handler
    # (non-auth action: resend request; auth action: show login modal for re-login)
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        csrf_token = generate_csrf()
        # don't use custom HTTPException since we can't `raise` here
        (code, description) = Config.CUSTOM_ERRORS["REFRESH_CSRF"]
        # return new token as description since csrf_token() in Jinja
        # doesn't seem to update until page reload; so instead we pass
        # the error description in as the new csrf_token in JS
        # shouldn't be a security issue since CSRF token sent in POST anyways
        # (most scuffed CSRF refresh in history)
        return csrf_token, code

    # init extensions after all that
    cors.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    login_manager.init_app(app)
    talisman.init_app(app, content_security_policy=config_class.CSP,
            content_security_policy_nonce_in=["script-src", "script-src-attr", "script-src-elem"])
    turnstile.init_app(app)

    return app


from app import models # imports done at bottom to prevent circular imports
