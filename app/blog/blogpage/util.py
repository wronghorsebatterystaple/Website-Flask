import bleach
import markdown
import re
from bs4 import BeautifulSoup
from functools import wraps

from flask import current_app, jsonify, redirect, request, url_for

import app.util as util
from app import db
from app.markdown_extensions.custom_extensions import CustomInlineExtensions
from app.models import *


def get_blogpage_id() -> int:
    """
    Gets blogpage id from `request.blueprint`.
    """

    return int(request.blueprint.split('.')[-1])


def get_post(post, post_sanitized_title, blogpage_id):
    """
    Gets post from URL, making sure it's valid and matches the whole URL.
    """

    if post is not None:
        return post
    return db.session.query(Post) \
            .filter_by(sanitized_title=post_sanitized_title, blogpage_id=blogpage_id) \
            .first()


def login_required_check_blogpage(content_type):
    """
    Enforces login to access private blogpages.
    Use before every view function potentially accessing private blogpages!!!
    """

    def inner_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            blogpage = db.session.get(Blogpage, get_blogpage_id())
            if blogpage is None:
                match request.method:
                    case util.ContentType.HTML:
                        return redirect(url_for(
                                f"main.index",
                                flash_msg=util.encode_uri_component("That blogpage doesn't exist :/"),
                                _external=True))
                    case util.ContentType.JSON:
                        return jsonify(
                                redir_url=url_for(f"{request.blueprint}.index", _external=True), 
                                flash_msg="That post doesn't exist :/")
                    case _:
                        return "app/blog/blogpage/util.py: `login_required_check_blogpage()` reached end of switch statement", 500

            if blogpage.is_login_required:
                result = util.custom_unauthorized(content_type)
                if result:
                    return result

            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


def requires_valid_post(content_type):
    def inner_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            blogpage_id = get_blogpage_id()
            # why does Flask view functions seem to turn `args` into `kwargs`? idk, but i'm not complaining
            post = get_post(kwargs.get("post", None), kwargs.get("post_sanitized_title"), blogpage_id)
            if post is None:
                return nonexistent_post(content_type)
            # also return `post` in addition since functions with these decorators probably need `post` anyway
            return func(post=post, *args, **kwargs)
        return wrapped
    return inner_decorator


def nonexistent_post(content_type):
    if content_type == util.ContentType.DEPENDS_ON_REQ_METHOD:
        content_type = util.ContentType.HTML if request.method == "GET" else util.ContentType.JSON

    match content_type:
        case util.ContentType.HTML:
            return redirect(url_for(
                    f"{request.blueprint}.index",
                    flash_msg=util.encode_uri_component("That post doesn't exist :/"),
                    _external=True))
        case util.ContentType.JSON:
            return jsonify(
                    redir_url=url_for(f"{request.blueprint}.index", _external=True), 
                    flash_msg="That post doesn't exist :/")
        case _:
            return "app/blog/blogpage/util.py: `nonexistent_post()` reached end of switch statement", 500


def not_a_redir_target(content_type):
    """
    If redirecting to this view function via the `next` parameter after logging in, instead redirect to simply the
    GET endpoint for the current post.

    Important: the view function this decorator wraps must have `post_sanitized_title` as its first parameter.
    """

    def inner_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            post = get_post(kwargs.get("post", None), kwargs.get("post_sanitized_title"), get_blogpage_id())
            if post is None:
                return nonexistent_post(content_type)
            if request.args.get("is_redir_after_login"):
                # here it's always `redirect()` aka HTML content type because this view function must've been called
                # by JS changing `window.location.href` after successful login + seeing `redir_url` JSON key from
                # `login()` view func. `window.location.href` change is always just the same as a `redirect()` via
                # GET an HTML page, as we typically do on loading a new page.
                return redirect(url_for("blog.post_by_id", post_id=post.id, _external=True))
            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


def render_post_titles_markdown(post):
    post.title = markdown.markdown(post.title, extensions=["extra", CustomInlineExtensions()])
    if post.subtitle:
        post.subtitle = markdown.markdown(post.subtitle, extensions=["extra", CustomInlineExtensions()])
    return post


def sanitize_untrusted_html(c) -> str:
    """
    Markdown sanitization for comments (XSS etc.).

    Notes:
        - Bleach is deprecated because html5lib is, but both seem to still be mostly active
    """

    # MathJax is processed client-side after this so no need to allow those tags
    c = bleach.clean(
            c,
            tags=current_app.config["POST_COMMENT_ALLOWED_TAGS"],
            attributes=current_app.config["POST_COMMENT_ALLOWED_ATTRIBUTES"])
    return c


def strip_markdown_from_html(html) -> str:
    return BeautifulSoup(html, "lxml").get_text()
