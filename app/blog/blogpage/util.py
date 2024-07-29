from functools import wraps

from flask import redirect, url_for

from app import db
from app.models import *
from app.util import *


# Requires login to access private blogpages
def login_required_check_blogpage(request):
    def inner_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            blogpage = db.session.get(Blogpage, get_blogpage_id(request.blueprint))
            if blogpage is None:
                return redirect(url_for(f"main.index",
                        flash_message=encode_URI_component("That blogpage doesn't exist."),
                        _external=True))

            if blogpage.login_required:
                result = custom_unauthorized(request)
                if result:
                    return result

            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


# Gets blogpage id from request.blueprint
def get_blogpage_id(blueprint_name) -> int:
    return int(blueprint_name.split('.')[-1])
