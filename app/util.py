import urllib.parse as parse
from enum import Enum
from functools import wraps

from flask import current_app, jsonify, redirect, request, url_for
from flask_login import current_user


class ContentType(Enum):
    HTML = "text/html"
    JSON = "application/json"
    DEPENDS_ON_REQ_METHOD = "`text/html` if GET, else `application/json`"


def custom_unauthorized(content_type, redir_to_parent_endpt=False):
    """
    Makes sure `current_user` is authenticated. If not, redirect to login page with *aboluste* `next` URL, which
    allows it to go from `blog.anonymousrand.xyz` to `anonymousrand.xyz/admin`, for instance, unlike the built-in
    `unauthorized()` function.

    Usage:
        ```
        result = util.custom_unauthorized(...)
        if result:
            return result
        ```

    Params:
        - `content_type`: specifies the `Content-Type` of the expected server response from the view function
        - `redir_to_parent_endpt`: set to `True` if the current view function doesn't return something you want to
          redirect back to on logging in (e.g. API call)
    """

    if not current_user.is_authenticated:
        login_url = url_for(
                current_app.config["LOGIN_VIEW"],
                next=request.url[:request.url.rfind("/")] if redir_to_parent_endpt
                        else encode_uri_component(request.url),
                flash_msg=encode_uri_component(
                        "Your session has expired, or you were being sneaky…please log in again ^^"),
                _external=True)

        if content_type == ContentType.DEPENDS_ON_REQ_METHOD:
            content_type = ContentType.HTML if request.method == "GET" else ContentType.JSON
        match content_type:
            case ContentType.HTML:
                return redirect(login_url)
            case ContentType.JSON:
                return jsonify(redir_url=login_url)
            case _:
                return "app/util.py: `custom_unauthorized()` reached end of switch statement", 500
    return None


def custom_login_required(content_type, redir_to_parent_endpt=False):
    """
    Same functionality as custom_unauthorized(), but as a decorator.

    Usage:
        ```
        @bp.route(...)
        @util.custom_login_required(...)
        def view_func():
            pass
        ```
    """

    def inner_decorator(func):
        @wraps(func) # this allows double decorator to work if this is the second decorator
        def wrapped(*args, **kwargs):
            result = custom_unauthorized(content_type, redir_to_parent_endpt)
            if result:
                return result
            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


def redir_depending_on_req_method(redir_endpt, flash_msg=None):
    match request.method:
        case "GET":
            redir_url = ""
            if flash_msg:
                redir_url = url_for(redir_endpt, flash_msg=flash_msg, _external=True)
            else:
                redir_url = url_for(redir_endpt, _external=True)
            return redirect(redir_url)
        case "POST":
            args = {"redir_url": url_for(redir_endpt, _external=True)}
            if flash_msg:
                args["flash_msg"] = flash_msg
            return jsonify(**args)
        case _:
            return "app/util.py: `redir_depending_on_req_method()` reached end of switch statement", 500


def encode_uri_component(s: str) -> str:
    """
    Mimics JavaScript's encodeURIComponent().
    """

    return parse.quote(s, safe="~!*()'")


def decode_uri_component(s: str) -> str:
    """
    Mimics JavaScript's decodeURIComponent().
    """

    return parse.unquote(s)
