from flask import Flask
from config import Config

from flask_cors import CORS
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager
from flask_paranoid import Paranoid
from flask_sqlalchemy import SQLAlchemy
from flask_turnstile import Turnstile
from flask_wtf.csrf import CSRFProtect, CSRFError

from app.routes import *


# declare extension instances outside so blueprints can still do `from app import db` etc.
cors = CORS(origins=Config.CORS_ORIGINS, supports_credentials=True)
csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = Config.LOGIN_VIEW
paranoid = Paranoid()
paranoid.redirect_view = Config.LOGIN_VIEW
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
    blog_bp.register_blueprint(blog_blogpage_bp, url_prefix="/the-backrooms", name="0")
    blog_bp.register_blueprint(blog_blogpage_bp, url_prefix="/all", name="1")
    blog_bp.register_blueprint(blog_blogpage_bp, url_prefix="/professor-google", name="3")
    blog_bp.register_blueprint(blog_blogpage_bp, url_prefix="/writers-block", name="6")
    blog_bp.register_blueprint(blog_blogpage_bp, url_prefix="/writers-unblock", name="7")
    app.register_blueprint(blog_bp, subdomain="blog")

    # register global routes and stuff
    app.context_processor(inject_login_form)
    app.register_error_handler(CSRFError, handle_csrf_error)

    # init extensions after all that
    cors.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    login_manager.init_app(app)
    paranoid.init_app(app)
    turnstile.init_app(app)

    return app


from app import models # imports done at bottom to prevent circular imports
