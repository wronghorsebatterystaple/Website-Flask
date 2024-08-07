import markdown
import markdown_grid_tables

import sqlalchemy as sa
from flask import current_app, jsonify, redirect, render_template, request, url_for
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
    blogpage = db.session.query(Blogpage).filter_by(id=blogpage_util.get_blogpage_id(request.blueprint)).first()
    return dict(blogpage=blogpage, blogpage_id=blogpage.id)


@bp.route("/", methods=["GET"])
def index():
    blogpage_id = blogpage_util.get_blogpage_id(request.blueprint)
    blogpage = db.session.get(Blogpage, blogpage_id)
    if blogpage is None:
        return redirect(url_for(
                f"main.index",
                flash_message=util.encode_URI_component("That blogpage doesn't exist :/"),
                _external=True))
    
    # require login to access private blogs
    if blogpage.login_required:
        result = util.custom_unauthorized(request)
        if result:
            return result

    page_num = request.args.get("page", 1, type=int) # should automatically redirect non-int to page 1
    if page_num <= 0:                                # prevent funny query string shenanigans
        return "", 204
    posts = None
    all_posts = False

    if blogpage.id == current_app.config["ALL_POSTS_BLOGPAGE_ID"]:
        all_posts = True
        posts = db.paginate(db.session.query(Post).join(Post.blogpage).filter_by(login_required=False)
                .order_by(
                        sa.desc(Post.timestamp)),
                        page=page_num,
                        per_page=current_app.config["POSTS_PER_PAGE"],
                        error_out=False)
    else:
        all_posts = False
        posts = db.paginate(db.session.query(Post).join(Post.blogpage).filter_by(id=blogpage_id)
                .order_by(
                        sa.desc(Post.timestamp)),
                        page=page_num,
                        per_page=current_app.config["POSTS_PER_PAGE"],
                        error_out=False)
    if posts is None or (posts.pages > 0 and page_num > posts.pages): # prevent funny query string shenanigans, 2.0
        return "", 204

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
            next_page_url=next_page_url,
            page_num=page_num,
            all_posts=all_posts,
            posts=posts,
            prev_page_url=prev_page_url,
            total_pages=posts.pages,
            unpublished_blogpage_id=unpublished_blogpage_id)


@bp.route("/<string:post_sanitized_title>", methods=["GET"])
@blogpage_util.login_required_check_blogpage(request)
def post(post_sanitized_title):
    blogpage_id = blogpage_util.get_blogpage_id(request.blueprint)

    # get post from URL, making sure it's valid and matches the whole URL
    post = blogpage_util.get_post_from_URL(post_sanitized_title, blogpage_id)
    if post is None:
        return redirect(url_for(
                f"{request.blueprint}.index",
                flash_message=util.encode_URI_component("That post doesn't exist."),
                _external=True))

    # render Markdown for post content
    post.content = markdown.markdown(
            post.content,
            extensions=["extra", "markdown_grid_tables", CustomInlineExtensions(), CustomBlockExtensions()])
    post.content = blogpage_util.additional_markdown_processing(post.content)

    # render Markdown for comment content
    comments_query = post.comments.select().order_by(sa.desc(Comment.timestamp))
    comments = db.session.scalars(comments_query).all()
    for comment in comments:
        if comment.author == current_app.config["VERIFIED_AUTHOR"]:
            comment.content = markdown.markdown(
                    comment.content,
                    extensions=["extra", "markdown_grid_tables", CustomInlineExtensions(), CustomBlockExtensions()])
            comment.content = blogpage_util.additional_markdown_processing(comment.content)
        else:
            # no custom block Markdown because there are ways to 500 the page that I don't wanna fix
            comment.content = markdown.markdown(
                    comment.content,
                    extensions=["extra", "markdown_grid_tables", CustomInlineExtensions()])
            comment.content = blogpage_util.additional_markdown_processing(comment.content)
            comment.content = blogpage_util.sanitize_untrusted_html(comment.content)


    add_comment_form = AddCommentForm()
    reply_comment_button = ReplyCommentButton()
    delete_comment_button = DeleteCommentButton()
    return render_template(
            "blog/blogpage/post.html",
            add_comment_form=add_comment_form,
            comments=comments,
            delete_comment_button=delete_comment_button,
            post=post,
            reply_comment_button=reply_comment_button)


###################################################################################################
# POST Endpoints
###################################################################################################


@bp.route("/<string:post_sanitized_title>/add-comment", methods=["POST"])
@blogpage_util.login_required_check_blogpage(request)
def add_comment(post_sanitized_title):
    # captcha
    if not turnstile.verify():
        return jsonify(redirect_url_abs=url_for("main.bot_jail", _external=True))

    # validate form submission
    add_comment_form = AddCommentForm()
    # let admin user leave author field blank to fill in their name by default
    author = request.form["author"]
    if current_user.is_authenticated and not author:
        author = current_app.config["VERIFIED_AUTHOR"];
        add_comment_form.author.raw_data[0] = author # to avoid this being interpreted as a validation error
    if not add_comment_form.validate():
        return jsonify(submission_errors=add_comment_form.errors)

    # make sure non-admin users can't masquerade as verified author
    is_verified_author = author.strip() == current_app.config["VERIFIED_AUTHOR"]
    if is_verified_author and not current_user.is_authenticated:
        return jsonify(submission_errors={
            "author": ["$8 isn't going to buy you a verified checkmark here."]
        })

    # get post from URL, making sure it's valid and matches the whole URL
    post = blogpage_util.get_post_from_URL(post_sanitized_title, blogpage_util.get_blogpage_id(request.blueprint))
    if post is None:
        return redirect(url_for(
                f"{request.blueprint}.index",
                flash_message=util.encode_URI_component("That post doesn't exist."),
                _external=True))

    # add comment
    comment = Comment(
            author=author,
            content=request.form["content"],
            post=post,
            unread=not is_verified_author) # make sure I my own comments aren't unread when I add them, cause duh
    with db.session.no_autoflush: # otherwise there's a warning
        if not comment.insert_comment(post, db.session.get(Comment, request.form["parent"])):
            return jsonify(flash_message="haker :3")
    db.session.add(comment)
    db.session.commit()

    return jsonify(flash_message="Comment added successfully!", success=True)


@bp.route("/<string:post_sanitized_title>/delete-comment", methods=["POST"])
@util.custom_login_required(request)
def delete_comment(post_sanitized_title):
    # check comment existence
    comment = db.session.get(Comment, request.args.get("comment_id"))
    if comment is None:
        return jsonify(flash_message=f"That comment doesn't exist.", success=True)

    # get post from URL, making sure it's valid and matches the whole URL
    post = blogpage_util.get_post_from_URL(post_sanitized_title, blogpage_util.get_blogpage_id(request.blueprint))
    if post is None:
        return redirect(url_for(
                f"{request.blueprint}.index",
                flash_message=util.encode_URI_component("That post doesn't exist."),
                _external=True))

    # delete comment
    descendants = comment.get_descendants(post)
    if not comment.remove_comment(post):
        return jsonify(flash_message="haker :3")
    for descendant in descendants:
        db.session.delete(descendant)
    db.session.delete(comment)
    db.session.commit()

    return jsonify(flash_message="1984 established!", success=True)


@bp.route("/<string:post_sanitized_title>/mark-comments-as-read", methods=["POST"])
@util.custom_login_required(request)
def mark_comments_as_read(post_sanitized_title):
    # get post from URL, making sure it's valid and matches the whole URL
    post = blogpage_util.get_post_from_URL(post_sanitized_title, blogpage_util.get_blogpage_id(request.blueprint))
    if post is None:
        return redirect(url_for(
                f"{request.blueprint}.index",
                flash_message=util.encode_URI_component("That post doesn't exist."),
                _external=True))

    # mark comments under current post as read
    comments_unread_query = post.comments.select().filter_by(unread=True)
    comments_unread = db.session.scalars(comments_unread_query).all()
    for comment in comments_unread:
        comment.unread=False
    db.session.commit()

    return jsonify() # since we're expecting Ajax for everything
