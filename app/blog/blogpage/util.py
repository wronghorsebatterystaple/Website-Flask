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


def get_post_from_url(post_sanitized_title, blogpage_id):
    """
    Gets post from URL, making sure it's valid and matches the whole URL.
    """

    return db.session.query(Post) \
            .filter_by(sanitized_title=post_sanitized_title, blogpage_id=blogpage_id) \
            .first()


def login_required_check_blogpage(content_type, redir_to_parent_endpt=False):
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
                result = util.custom_unauthorized(content_type, redir_to_parent_endpt)
                if result:
                    return result

            return func(*args, **kwargs)
        return wrapped
    return inner_decorator


def nonexistent_post_response(content_type):
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
            return "app/blog/blogpage/util.py: `return_nonexistent_post()` reached end of switch statement", 500


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
