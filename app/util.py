from functools import wraps
import urllib.parse as parse

from flask import current_app, jsonify, redirect, url_for
from flask_login import current_user


# Mimics JavaScript's encodeURIComponent(), from StackOverflow
def encode_URI_component(s: str) -> str:
    return parse.quote(s, safe="~!*()'")


# Mimics JavaScript's decodeURIComponent()
def decode_URI_component(s: str) -> str:
    return parse.unquote(s)


# GET requests to banned pages (meaning page has not been loaded yet) redirects to login with absolute `next` URL
# POST requests on banned pages (meaning page is already loaded) shows login modal again via Ajax/fetch response
def custom_unauthorized(request):
    if not current_user.is_authenticated:
        if request.method == "GET":
            return redirect(url_for(current_app.config["LOGIN_VIEW"], next=encode_URI_component(request.url)))
        elif request.method == "POST":
            return jsonify(relogin=True)
    return None


# Same thing as custom_unauthorized() but as a decorator
def custom_login_required(request):
    def inner_decorator(func):
        @wraps(func) # this allows double decorator to work if this is the second decorator
        def wrapped(*args, **kwargs):
            result = custom_unauthorized(request)
            if result:
                return result
            return func(*args, **kwargs)
        return wrapped
    return inner_decorator
