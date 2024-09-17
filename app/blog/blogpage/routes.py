import markdown
import markdown_grid_tables

import sqlalchemy as sa
from flask import current_app, get_template_attribute, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

import app.blog.blogpage.util as blogpage_util
import app.util as util
from app import db, turnstile
from app.blog.blogpage import bp
from app.blog.blogpage.forms import *
from app.markdown_extensions.custom_extensions import CustomBlockExtensions, CustomInlineExtensions
from app.models import *


@bp.context_processor
def inject_blogpage_from_db():
    blogpage = db.session.query(Blogpage).filter_by(id=blogpage_util.get_blogpage_id()).first()
    return dict(blogpage=blogpage, blogpage_id=blogpage.id)


@bp.route("/", methods=["GET"])
@blogpage_util.login_required_check_blogpage(content_type=util.ContentType.HTML)
def index():
    page_num = request.args.get("page", 1, type=int) # should automatically redirect non-int to page 1
    if page_num <= 0:                                # prevent funny query string shenanigans
        return "", 418

    blogpage_id = blogpage_util.get_blogpage_id()
    blogpage = db.session.get(Blogpage, blogpage_id)
    if blogpage is None:
        return redirect(url_for("blog.index", flash_msg="That blogpage doesn't exist :/", _external=True))
    posts = None
    is_all_posts = False

    if blogpage.id == current_app.config["ALL_POSTS_BLOGPAGE_ID"]:
        is_all_posts = True
        posts = db.paginate(
                db.session.query(Post).join(Post.blogpage).filter_by(login_required=False)
                        .order_by(sa.desc(Post.timestamp)),
                page=page_num,
                per_page=current_app.config["POSTS_PER_PAGE"],
                error_out=False)
    else:
        is_all_posts = False
        posts = db.paginate(
                db.session.query(Post).join(Post.blogpage).filter_by(id=blogpage_id)
                        .order_by(sa.desc(Post.timestamp)),
                page=page_num,
                per_page=current_app.config["POSTS_PER_PAGE"],
                error_out=False)
    if posts is None or (posts.pages > 0 and page_num > posts.pages): # prevent funny query string shenanigans, 2.0
        return "", 418

    next_page_url = url_for(f"blog.{blogpage_id}.index", page=posts.next_num, _external=True) if posts.has_next \
            else None
    prev_page_url = url_for(f"blog.{blogpage_id}.index", page=posts.prev_num, _external=True) if posts.has_prev \
            else None

    # generate corresponding unpublished blogpage ID for "Create Post" button
    unpublished_blogpage_id = blogpage_id
    if not blogpage.unpublished:
        blogpage_temp = db.session.get(Blogpage, -blogpage_id)
        if blogpage_temp is not None and blogpage_temp.unpublished:
            unpublished_blogpage_id = -blogpage_id

    return render_template(
            "blog/blogpage/index.html",
            is_all_posts=is_all_posts,
            posts=posts,
            unpublished_blogpage_id=unpublished_blogpage_id,
            total_pages=posts.pages,
            page_num=page_num,
            prev_page_url=prev_page_url,
            next_page_url=next_page_url)


@bp.route("/<string:post_sanitized_title>", methods=["GET"])
@blogpage_util.login_required_check_blogpage(content_type=util.ContentType.HTML)
def post(post_sanitized_title):
    blogpage_id = blogpage_util.get_blogpage_id()

    # get post from url, making sure it's valid and matches the whole url
    post = blogpage_util.get_post_from_url(post_sanitized_title, blogpage_id)
    if post is None:
        return blogpage_util.post_nonexistent_response(util.ContentType.HTML)

    # render Markdown for post
    post.title = markdown.markdown(post.title, extensions=["extra", CustomInlineExtensions()])
    post.title = blogpage_util.additional_markdown_processing(post.title)
    if post.subtitle:
        post.subtitle = markdown.markdown(post.subtitle, extensions=["extra", CustomInlineExtensions()])
        post.subtitle = blogpage_util.additional_markdown_processing(post.subtitle)
    if post.content:
        post.content = markdown.markdown(
                post.content,
                extensions=["extra", "markdown_grid_tables", CustomInlineExtensions(), CustomBlockExtensions()])
        post.content = blogpage_util.additional_markdown_processing(post.content)

    # strip Markdown for title here instead of on the frontend with JQuery `.text()` because this is only part of
    # the title, and I can't put `<span>`s or anything in `<title>` to selectively only change part of it in JS
    # only Jinja can selectively put stuff in `<title>`, so I use bs4 here to do `.text()` and send that to Jinja
    post_title_no_markdown = blogpage_util.strip_markdown_from_html(post.title)
    add_comment_form = AddCommentForm()
    return render_template(
            "blog/blogpage/post.html",
            post=post,
            post_title_no_markdown=post_title_no_markdown,
            add_comment_form=add_comment_form)


@bp.route("/<string:post_sanitized_title>/get-comments", methods=["GET"])
@blogpage_util.login_required_check_blogpage(content_type=util.ContentType.JSON)
def get_comments(post_sanitized_title):
    post = blogpage_util.get_post_from_url(post_sanitized_title, blogpage_util.get_blogpage_id())
    if post is None:
        return blogpage_util.post_nonexistent_response(util.ContentType.JSON)

    # get comments from db and render Markdown
    comments_query = post.comments.select().order_by(sa.desc(Comment.timestamp))
    comments = db.session.scalars(comments_query).all()

    for comment in comments:
        if comment.author == current_app.config["VERIFIED_AUTHOR"]:
            comment.content = markdown.markdown(
                    comment.content,
                    extensions=["extra", "markdown_grid_tables", CustomInlineExtensions(), CustomBlockExtensions()])
            comment.content = blogpage_util.additional_markdown_processing(comment.content)
        else:
            # no custom block Markdown for non-admin because there are ways to 500 the page that I don't wanna fix
            comment.content = markdown.markdown(
                    comment.content,
                    extensions=["extra", "markdown_grid_tables", CustomInlineExtensions()])
            comment.content = blogpage_util.additional_markdown_processing(comment.content)
            comment.content = blogpage_util.sanitize_untrusted_html(comment.content)
 
    add_comment_form = AddCommentForm()
    reply_comment_btn = ReplyCommentBtn()
    delete_comment_btn = DeleteCommentBtn()
    return jsonify(html=render_template(
            "blog/blogpage/post_comments.html",
            post=post,
            comments=comments,
            add_comment_form=add_comment_form,
            delete_comment_btn=delete_comment_btn,
            reply_comment_btn=reply_comment_btn))


@bp.route("/<string:post_sanitized_title>/get-comment-count", methods=["GET"])
@blogpage_util.login_required_check_blogpage(content_type=util.ContentType.JSON)
def get_comment_count(post_sanitized_title):
    post = blogpage_util.get_post_from_url(post_sanitized_title, blogpage_util.get_blogpage_id())
    if post is None:
        return blogpage_util.post_nonexistent_response(util.ContentType.JSON)
    return jsonify(count=post.get_comment_count())


@bp.route("/<string:post_sanitized_title>/get-comment-unread-count", methods=["GET"])
@blogpage_util.login_required_check_blogpage(content_type=util.ContentType.JSON)
def get_comment_unread_count(post_sanitized_title):
    post = blogpage_util.get_post_from_url(post_sanitized_title, blogpage_util.get_blogpage_id())
    if post is None:
        return blogpage_util.post_nonexistent_response(util.ContentType.JSON)
    return jsonify(count=post.get_comment_unread_count())


###################################################################################################
# POST Endpoints
###################################################################################################


@bp.route("/<string:post_sanitized_title>/add-comment", methods=["POST"])
@blogpage_util.login_required_check_blogpage(content_type=util.ContentType.JSON)
def add_comment(post_sanitized_title):
    # captcha
    if not turnstile.verify():
        return jsonify(redir_url=url_for("bot_jail", _external=True))

    # validate form submission
    add_comment_form = AddCommentForm()
    if not add_comment_form.validate():
        return jsonify(submission_errors=add_comment_form.errors)

    # make sure non-admin users can't masquerade as verified author
    author = request.form.get("author")
    is_verified_author = author.strip() == current_app.config["VERIFIED_AUTHOR"]
    if is_verified_author and not current_user.is_authenticated:
        return jsonify(submission_errors={
            "author": ["$8 isn't going to buy you a verified checkmark here."]
        })

    # get post from url, making sure it's valid and matches the whole url
    post = blogpage_util.get_post_from_url(post_sanitized_title, blogpage_util.get_blogpage_id())
    if post is None:
        return blogpage_util.post_nonexistent_response(util.ContentType.JSON)

    # add comment
    comment = Comment(
            author=author,
            content=request.form.get("content"),
            post=post,
            unread=not is_verified_author) # make sure I my own comments aren't unread when I add them, cause duh
    with db.session.no_autoflush: # otherwise there's a warning
        if not comment.insert_comment(post, db.session.get(Comment, request.form.get("parent"))):
            return jsonify(flash_msg="haker :3")
    db.session.add(comment)
    db.session.commit()

    return jsonify(success=True, flash_msg="Comment added successfully!")


@bp.route("/<string:post_sanitized_title>/delete-comment", methods=["POST"])
@util.custom_login_required(content_type=util.ContentType.JSON)
def delete_comment(post_sanitized_title):
    # check comment existence
    comment = db.session.get(Comment, request.args.get("comment_id"))
    if comment is None:
        return jsonify(success=True, flash_msg=f"That comment doesn't exist :/")

    # get post from url, making sure it's valid and matches the whole url
    post = blogpage_util.get_post_from_url(post_sanitized_title, blogpage_util.get_blogpage_id())
    if post is None:
        return blogpage_util.post_nonexistent_response(util.ContentType.JSON)

    # delete comment
    descendants = comment.get_descendants(post)
    if not comment.remove_comment(post):
        return jsonify(flash_msg="haker :3")
    for descendant in descendants:
        db.session.delete(descendant)
    db.session.delete(comment)
    db.session.commit()

    return jsonify(success=True, flash_msg="literally 1984")


@bp.route("/<string:post_sanitized_title>/mark-comments-as-read", methods=["POST"])
@util.custom_login_required(content_type=util.ContentType.JSON, do_relogin=False)
def mark_comments_as_read(post_sanitized_title):
    # get post from url, making sure it's valid and matches the whole url
    post = blogpage_util.get_post_from_url(post_sanitized_title, blogpage_util.get_blogpage_id())
    if post is None:
        return blogpage_util.post_nonexistent_response(util.ContentType.JSON)

    # mark comments under current post as read
    comments_unread_query = post.comments.select().filter_by(unread=True)
    comments_unread = db.session.scalars(comments_unread_query).all()
    for comment in comments_unread:
        comment.unread=False
    db.session.commit()

    return jsonify(success=True)
