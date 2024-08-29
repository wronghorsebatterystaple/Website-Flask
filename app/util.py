import urllib.parse as parse
from enum import Enum
from functools import wraps

from flask import current_app, jsonify, redirect, request, url_for
from flask_login import current_user


class ContentType(Enum):
    """
    Choices:
        - `HTML`: `text/html`
        - `JSON`: `application/json`
        - `DEPENDS_ON_REQ_METHOD`: `text/html` if GET, otherwise `application/json`
    """

    HTML = 0
    JSON = 1
    DEPENDS_ON_REQ_METHOD = 2


def custom_unauthorized(content_type, do_relogin=True):
    """
    Makes sure `current_user` is authenticated.
    If not authenticated:
        - `Content-Type: text/html` responses redirect to login page with absolute `next` URL
        - `Content-Type: application/json` responses return `relogin` Ajax response

    Usage:
        ```
        result = util.custom_unauthorized(...)
        if result:
            return result
        ```

    Params:
        - `content_type`: specifies the `Content-Type` of the expected server response from the view function
        - `do_relogin`: should be `False` iff the view function handles POST requests that are not manual (triggered
          by a user action). This prevents users from seeing login modal pop up out of nowhere when an automated,
          hard-to-detect action happens.
    """

    if not current_user.is_authenticated:
        if content_type == ContentType.DEPENDS_ON_REQ_METHOD:
            content_type = ContentType.HTML if request.method == "GET" else ContentType.JSON

        match content_type:
            case ContentType.HTML:
                return redirect(url_for(current_app.config["LOGIN_VIEW"], next=encode_uri_component(request.url)))
            case ContentType.JSON:
                if do_relogin:
                    return jsonify(relogin=True)
                else:
                    return jsonify()
            case _:
                return "app/util.py: `custom_unauthorized()` reached end of switch statement", 500
    return None


def custom_login_required(content_type, do_relogin=True):
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
            result = custom_unauthorized(content_type, do_relogin)
            if result:
                return result
            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


def redir_depending_on_req_method(redir_endpoint, flash_msg=None):
    match request.method:
        case "GET":
            redir_url = None
            if flash_msg:
                redir_url = url_for(redir_endpoint, flash_msg=flash_msg, _external=True)
            else:
                redir_url = url_for(redir_endpoint, _external=True)
            return redirect(redir_url)
        case "POST":
            redir_url = url_for(redir_endpoint, _external=True)
            if flash_msg:
                return jsonify(redir_url=redir_url, flash_msg=flash_msg)
            else:
                return jsonify(redir_url=redir_url)
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
