from flask import Blueprint

## `static_url_path` used to avoid conflicts with root-level `static` folder, since this blueprint is registered
## at the "root" URL with no URL prefixes/subdomains
bp = Blueprint(
        "main",
        __name__,
        template_folder="templates",
        static_folder="static/main/",
        static_url_path="/static/main")

from app.main import routes
