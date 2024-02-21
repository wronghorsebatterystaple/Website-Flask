from app import app # import app variable from app package
from flask import render_template

@app.route("/")
def index():
    return render_template("index.html")
