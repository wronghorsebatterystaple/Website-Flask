import urllib.parse as parse
from enum import Enum
from functools import wraps

from flask import current_app, jsonify, redirect, request, url_for
from flask_login import current_user


class ContentType(Enum):
    ## String values are not used; just a reference
    HTML = "text/html"
    JSON = "application/json"
    DEPENDS_ON_REQUEST_METHOD = "text/html if GET, otherwise application/json"


def custom_unauthorized(content_type):
    """
    Makes sure `current_user` is authenticated.
    If not authenticated:
        - `Content-Type: text/html` responses redirect to login with absolute `next` URL
        - `Content-Type: application/json` responses show login modal again via base Ajax response

    Usage:
        ```
        result = util.custom_unauthorized(request)
        if result:
            return result
        ```
    """

    if not current_user.is_authenticated:
        if content_type == ContentType.DEPENDS_ON_REQUEST_METHOD:
            content_type = ContentType.HTML if request.method == "GET" else ContentType.JSON

        match content_type:
            case ContentType.HTML:
                return redirect(url_for(current_app.config["LOGIN_VIEW"], next=encode_URI_component(request.url)))
            case ContentType.JSON:
                return jsonify(relogin=True)
            case _:
                return "app/util.py: custom_unauthorized() reached end of switch statement, gg", 500
    return None


def custom_login_required(content_type):
    """
    Same functionality as custom_unauthorized(), but as a decorator.

    Usage:
        ```
        @bp.route(...)
        @util.custom_login_required(request)
        def view_func():
            pass
        ```
    """

    def inner_decorator(func):
        @wraps(func) # this allows double decorator to work if this is the second decorator
        def wrapped(*args, **kwargs):
            result = custom_unauthorized(content_type)
            if result:
                return result
            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


def encode_URI_component(s: str) -> str:
    """
    Mimics JavaScript's encodeURIComponent().
    """

    return parse.quote(s, safe="~!*()'")


def decode_URI_component(s: str) -> str:
    """
    Mimics JavaScript's decodeURIComponent().
    """

    return parse.unquote(s)
