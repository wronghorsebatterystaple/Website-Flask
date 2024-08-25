from flask import Blueprint


# `static_url_path` used to avoid conflicts with root-level `static` folder, since this blueprint is registered
# at the "root" URL with no URL prefixes/subdomains
blueprint_name = "main"
bp = Blueprint(
        blueprint_name,
        __name__,
        template_folder="templates/",
        static_folder="static/",
        static_url_path=f"/{blueprint_name}/static/")


from . import routes
