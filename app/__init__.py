from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# declare extension instances outside so blueprints can still do `from app import db` etc.
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    # create app variable (Flask instance)
    app = Flask(__name__)
    app.config.from_object(config_class)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)

    # register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blog import bp as blog_bp
    from app.blog.admin import bp as blog_admin_bp
    blog_bp.register_blueprint(blog_admin_bp, url_prefix="/admin")
    app.register_blueprint(blog_bp, subdomain="blog")
    
    return app

from app import models # imports done at bottom to prevent circular imports
