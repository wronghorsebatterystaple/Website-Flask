from functools import wraps
import urllib.parse as parse

from flask import current_app, jsonify, redirect, url_for
from flask_login import current_user


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


def custom_unauthorized(request):
    """
    Makes sure `current_user` is authenticated.

    If not authenticated:
        - GET requests (meaning page has not been loaded yet) redirect to login with absolute `next` URL
        - POST requests (meaning page is already loaded) show login modal again via Ajax/fetch response
    """

    if not current_user.is_authenticated:
        match request.method:
            case "GET":
                return redirect(url_for(current_app.config["LOGIN_VIEW"], next=encode_URI_component(request.url)))
            case "POST":
                return jsonify(relogin=True)
            case _:
                return "", 500
    return None


def custom_login_required(request):
    """
    Same functionality as custom_unauthorized(), but as a decorator.
    """

    def inner_decorator(func):
        @wraps(func) # this allows double decorator to work if this is the second decorator
        def wrapped(*args, **kwargs):
            result = custom_unauthorized(request)
            if result:
                return result
            return func(*args, **kwargs)
        return wrapped
    return inner_decorator
