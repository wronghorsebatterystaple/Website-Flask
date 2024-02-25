from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy() # declare outside so blueprints can still do `from app import db` etc.
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    # register blueprints
    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp, subdomain="blog")

    return app

from app import models # imports done at bottom to prevent circular imports
