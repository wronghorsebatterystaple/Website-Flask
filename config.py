import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    SERVER_NAME = "anonymousrand.xyz"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Flask-login
    REMEMBER_COOKIE_DOMAIN = f".{SERVER_NAME}"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = 3600
