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
from app.util import ContentType


def requires_login_if_restricted_bp():
    """
    Enforces login to access private blogpages.
    Use before every view function potentially accessing private blogpages!!!
    """

    def inner_decorator(func):
        @wraps(func)
        def wrapped(content_type: ContentType, *args, **kwargs):
            blogpage = db.session.get(Blogpage, get_blogpage_id())
            if blogpage is None:
                match content_type:
                    case ContentType.HTML:
                        return redirect(url_for(
                                f"main.index",
                                flash_msg=util.encode_uri_component("That blogpage doesn't exist :/"),
                                _external=True))
                    case ContentType.JSON:
                        return jsonify(
                                redir_url=url_for(f"{request.blueprint}.index", _external=True), 
                                flash_msg="That post doesn't exist :/")
                    case _:
                        return "app/blog/blogpage/util.py: `requires_login_if_restricted_bp()` reached end of switch statement", 500

            if blogpage.is_login_required:
                result = util.custom_unauthorized(content_type)
                if result:
                    return result

            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


def requires_valid_post():
    """
    Makes sure URL points to a post that exists, and if so, fetches the post from the db and passes it to its inner
    function as a parameter for later use.
    """

    def inner_decorator(func):
        @wraps(func)
        def wrapped(content_type: ContentType, *args, **kwargs):
            blogpage_id = get_blogpage_id()
            # why does Flask view functions seem to turn `args` into `kwargs`? idk, but i'm not complaining
            post = get_post(kwargs.get("post"), kwargs.get("post_sanitized_title"), blogpage_id)
            if post is None:
                return nonexistent_post(content_type)
            # also return `post` in addition since functions with these decorators probably need `post` anyway
            return func(post=post, *args, **kwargs)
        return wrapped
    return inner_decorator


def redirs_to_post_after_login():
    """
    If redirecting to this view function via the `next` parameter after logging in, instead redirect to simply the
    GET endpoint for the current post.

    Important: the view function this decorator wraps must have `post_sanitized_title` as its first parameter.
    """

    def inner_decorator(func):
        @wraps(func)
        def wrapped(content_type: ContentType, *args, **kwargs):
            post = get_post(kwargs.get("post"), kwargs.get("post_sanitized_title"), get_blogpage_id())
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


@util.resolve_content_type()
def nonexistent_post(content_type: ContentType):
    match content_type:
        case ContentType.HTML:
            return redirect(url_for(
                    f"{request.blueprint}.index",
                    flash_msg=util.encode_uri_component("That post doesn't exist :/"),
                    _external=True))
        case ContentType.JSON:
            return jsonify(
                    redir_url=url_for(f"{request.blueprint}.index", _external=True), 
                    flash_msg="That post doesn't exist :/")
        case _:
            return "app/blog/blogpage/util.py: `nonexistent_post()` reached end of switch statement", 500


def get_blogpage_id() -> int:
    """
    Gets blogpage id from `request.blueprint`.
    """

    return int(request.blueprint.split('.')[-1])


def get_post(post: Post, post_sanitized_title: str, blogpage_id: int) -> Post:
    """
    Gets post from URL, making sure it's valid and matches the whole URL.
    """

    if post is not None:
        return post
    return db.session.query(Post).filter_by(sanitized_title=post_sanitized_title, blogpage_id=blogpage_id).first()


def render_post_titles_markdown(post: Post) -> Post:
    post.title = markdown.markdown(post.title, extensions=["extra", CustomInlineExtensions()])
    if post.subtitle:
        post.subtitle = markdown.markdown(post.subtitle, extensions=["extra", CustomInlineExtensions()])
    return post


def sanitize_untrusted_html(s: str) -> str:
    """
    Markdown sanitization for comments (XSS etc.).

    Notes:
        - Bleach is deprecated because html5lib is, but both seem to still be mostly active
    """

    s = bleach.clean(
            s,
            tags=current_app.config["POST_COMMENT_ALLOWED_TAGS"],
            attributes=current_app.config["POST_COMMENT_ALLOWED_ATTRIBUTES"])
    return s


def strip_markdown_from_html(html: str) -> str:
    return BeautifulSoup(html, "lxml").get_text()
