from flask import render_template

from app.main import bp


@bp.route("/", methods=["GET"])
def index():
    return render_template("main/index.html")


@bp.route("/bot-jail", methods=["GET"])
def bot_jail():
    return render_template("main/bot_jail.html")
