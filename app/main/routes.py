from flask import render_template

from app.main import bp


@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/bot-jail")
def bot_jail():
    return render_template("main/bot-jail.html")
