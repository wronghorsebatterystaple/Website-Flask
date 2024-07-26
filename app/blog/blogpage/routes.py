import bleach
import markdown
import markdown_grid_tables
import re
import shutil

from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user
import sqlalchemy as sa

from app import db
from app.blog.blogpage import bp
from app.blog.forms import *
from app.models import *
import app.util as util
from app.markdown_extensions.myextensions import MyBlockExtensions, MyInlineExtensions


@bp.context_processor
def inject_blogpage_from_db():
    blogpage = db.session.query(Blogpage).filter(Blogpage.id==get_blogpage_id(request.blueprint)).first()
    return dict(blogpage=blogpage, blogpage_id=blogpage.id)


@bp.route("/")
def index():
    blogpage_id = get_blogpage_id(request.blueprint)
    blogpage = db.session.get(Blogpage, blogpage_id)
    if blogpage is None:
        return redirect(url_for(f"main.index",
            flash=util.encode_URI_component("That blogpage doesn't exist :/"),
                _external=True))
    
    # require login to access private blogs
    if blogpage.login_required:
        result = util.custom_unauthorized(request)
        if result:
            return result

    page = request.args.get("page", 1, type=int) # should automatically redirect non-int to page 1
    if page <= 0: # prevent funny query string shenanigans
        return "", 204
    posts = None
    all_posts = False

    if blogpage.id == current_app.config["ALL_POSTS_BLOGPAGE_ID"]:
        all_posts = True
        posts = db.paginate(db.session.query(Post).join(Post.blogpage).filter(Blogpage.login_required==False)
                .order_by(sa.desc(Post.timestamp)), page=page,
                per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    else:
        all_posts = False
        posts = db.paginate(db.session.query(Post).join(Post.blogpage).filter(Blogpage.id==blogpage_id)
                .order_by(sa.desc(Post.timestamp)), page=page,
                per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)

    if posts is None or (page > posts.pages and posts.pages > 0): # prevent funny query string shenanigans, 2.0
        return "", 204
    next_page_url = url_for(f"blog.{blogpage_id}.index", page=posts.next_num, _external=True) \
            if posts.has_next else None
    prev_page_url = url_for(f"blog.{blogpage_id}.index", page=posts.prev_num, _external=True) \
            if posts.has_prev else None

    unpublished_blogpage_id = blogpage_id
    if not blogpage.unpublished:
        blogpage_temp = db.session.get(Blogpage, -blogpage_id)
        if blogpage_temp is not None and blogpage_temp.unpublished:
            unpublished_blogpage_id = -blogpage_id

    return render_template("blog/blogpage/index.html",
            unpublished_blogpage_id=unpublished_blogpage_id, page=page, total_pages=posts.pages,
            all_posts=all_posts, posts=posts, next_page_url=next_page_url,
            prev_page_url=prev_page_url, get_comment_count=Post.get_comment_count)


@bp.route("/<string:post_sanitized_title>")
def post(post_sanitized_title):
    blogpage_id = get_blogpage_id(request.blueprint)
    blogpage = db.session.get(Blogpage, blogpage_id)
    if blogpage is None:
        return redirect(url_for(f"main.index",
                flash=util.encode_URI_component("That blogpage doesn't exist."),
                _external=True))

    # require login to access private blogs
    if blogpage.login_required:
        result = util.custom_unauthorized(request)
        if result:
            return result

    add_comment_form = AddCommentForm()
    reply_comment_button = ReplyCommentButton()
    delete_comment_button = DeleteCommentButton()
    post = db.session.query(Post).filter(Post.sanitized_title == post_sanitized_title).first()
    if post is None:
        return redirect(url_for(f"{request.blueprint}.index",
                flash=util.encode_URI_component("That post doesn't exist."),
                _external=True))

    post.content = markdown.markdown(post.content, extensions=["extra", "markdown_grid_tables",
            MyInlineExtensions(), MyBlockExtensions()])
    post.content = additional_markdown_processing(post.content)

    comments_query = post.comments.select().order_by(sa.desc(Comment.timestamp))
    comments = db.session.scalars(comments_query).all()
    for comment in comments: # no custom block Markdown because there ways to 500 the page that I don't wanna fix
        comment.content = markdown.markdown(comment.content, extensions=["extra", "markdown_grid_tables",
                MyInlineExtensions()])
        comment.content = additional_markdown_processing(comment.content)
        comment.content = sanitize_comment_html(comment.content)

    return render_template("blog/blogpage/post.html",
            post=post, comments=comments, add_comment_form=add_comment_form,
            reply_comment_button = reply_comment_button, delete_comment_button = delete_comment_button,
            get_comment_count=Post.get_comment_count, get_descendants_list=Comment.get_descendants_list)


###################################################################################################
# Helper functions
###################################################################################################


# Gets blog id from request.blueprint
def get_blogpage_id(blueprint_name) -> int:
    return int(blueprint_name.split('.')[-1])


# Markdown tweaks round 2
# Changes:
#   Remove extra `<p>` tags generated by 3rd-party extension `markdown_grid_tables` around `<pre>` tags that mess up table spacing and don't seem to be JQuery-parsable
def additional_markdown_processing(s) -> str:
    s = s.replace("</pre></p>", "</pre>")
    # using regex to not take chances here with attributes and stuff
    s = re.sub(r"<p><pre([\S\s]*?)>", r"<pre\1>", s)

    return s


# Markdown sanitization for comments (XSS etc.)
# Bleach is deprecated because html5lib is, but both seem to still be mostly active
def sanitize_comment_html(c) -> str:
    # MathJax should be processed client-side after this so no need to allow those tags
    c = bleach.clean(c,
            tags={"abbr", "acronym", "b", "blockquote", "br", "center", "code", "details", "div", "em",
                "h1", "h2", "h3", "i", "li", "p", "pre", "ol", "small", "span", "strong", "sub", "summary",
                "sup", "table", "tbody", "td", "th", "thead", "tr", "ul"},
            attributes=["class", "colspan", "data-align-bottom", "data-align-center", "data-align-right",
                "data-align-top", "data-col-width", "height", "rowspan", "title", "width"])
    return c
