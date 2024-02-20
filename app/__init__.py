from flask import Flask

app = Flask(__name__)

from app import routes # imports done at bottom to prevent circular imports
