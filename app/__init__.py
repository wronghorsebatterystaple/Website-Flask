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

from app.util import *


# declare extension instances outside so blueprints can still do `from app import db` etc.
cors = CORS(origins=Config.ALLOWED_ORIGINS, supports_credentials=True)
csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = Config.LOGIN_VIEW
#login_manager.session_protection = "strong" # deletes session cookie on IP/UA change
talisman = Talisman()
turnstile = Turnstile()

from app.routes import * # here to prevent circular imports

def create_app():
    # create app variable (Flask instance)
    app = Flask(__name__)
    app.config.from_object(Config)

    # register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.blog import bp as blog_bp
    from app.blog.blogpage import bp as blog_blogpage_bp
    # "name" param must match blogpage_id in "Post" db table
    # This makes the endpoints "blog.0.index", "blog.1.index" etc.
    for k, v in Config.BLOGPAGE_ID_TO_PATH.items():
        blog_bp.register_blueprint(blog_blogpage_bp, url_prefix=v, name=k)
    app.register_blueprint(blog_bp, subdomain="blog")

    # register global routes and stuff
    app.context_processor(inject_login_form)
    app.context_processor(inject_blogpages_from_db)
    app.register_error_handler(CSRFError, handle_csrf_error)

    # init extensions after all that
    cors.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    login_manager.init_app(app)
    talisman.init_app(app, content_security_policy=Config.CSP,
            content_security_policy_nonce_in=["script-src", "script-src-attr", "script-src-elem"],
    turnstile.init_app(app)

    return app


from app import models # prevent circular imports
