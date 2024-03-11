from flask import render_template, url_for

from app.main import bp

@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/bot-jail")
def bot_jail():
    img_filepath = url_for("main.static", filename="amogus.webp")
    return render_template("main/bot-jail.html", img_filepath=img_filepath)
