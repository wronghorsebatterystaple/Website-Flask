import image_titles
import markdown
from markdown_environments import *
from markdown.extensions.toc import TocExtension
from markdown_inline_extras.strikethrough import StrikethroughExtension

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.sql.functions as sa_func
from flask import current_app, get_template_attribute, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

import app.blog.blogpage.util as bp_util
import app.util as util
from app import db
from app.blog.blogpage import bp
from app.blog.blogpage.forms import *
from app.models import *
from app.util import ContentType


@bp.context_processor
def inject_blogpage_from_db():
    blogpage = db.session.query(Blogpage).filter_by(id=bp_util.get_blogpage_id()).first()
    return dict(blogpage=blogpage, blogpage_id=blogpage.id)


@bp.route("/", methods=["GET"])
@util.set_content_type(ContentType.HTML)
@bp_util.require_login_if_restricted_bp()
def index(**kwargs):
    page_num = request.args.get("page", 1, type=int) # should automatically redirect non-int to page 1
    blogpage_id = bp_util.get_blogpage_id()
    blogpage = db.session.get(Blogpage, blogpage_id)
    if blogpage is None:
        return "ok im actually impressed how did you do that"

    posts = None
    if blogpage.is_all_posts:
        posts = db.paginate(
                db.session.query(Post).join(Post.blogpage).filter_by(is_login_required=False, is_published=True)
                        .order_by(sa_func.coalesce(Post.edited_timestamp, Post.timestamp).desc()),
                page=page_num,
                per_page=current_app.config["POSTS_PER_PAGE"],
                error_out=False)
    else:
        posts = db.paginate(
                db.session.query(Post).filter_by(blogpage_id=blogpage_id) \
                        .order_by(sa_func.coalesce(Post.edited_timestamp, Post.timestamp).desc()),
                page=page_num,
                per_page=current_app.config["POSTS_PER_PAGE"],
                error_out=False)
    if posts is None:
        return "ok im actually impressed how did you do that"

    next_page_url = url_for(f"blog.{blogpage_id}.index", page=posts.next_num, _external=True) if posts.has_next \
            else None
    prev_page_url = url_for(f"blog.{blogpage_id}.index", page=posts.prev_num, _external=True) if posts.has_prev \
            else None

    return render_template(
            "blog/blogpage/index.html",
            posts=posts,
            total_pages=posts.pages,
            page_num=page_num,
            prev_page_url=prev_page_url,
            next_page_url=next_page_url)


# private posts, unlike blogpages, are still accessible by link (like YouTube's "unlisted")
# hence the lack of `@require_login_if_restricted_bp()`
@bp.route("/<string:post_sanitized_title>", methods=["GET"])
@util.set_content_type(ContentType.HTML)
@bp_util.require_valid_post()
def post(post, post_sanitized_title, **kwargs): # first param is from `require_valid_post` decorator
    # render Markdown for post
    content_md = None
    if post.content:
        def generate_anchors(value, separator):
            value = (separator.join(value.split())).lower()
            value = re.sub(f"[^A-Za-z0-9{separator}]", "", value)
            return value

        content_md = markdown.Markdown(extensions=[
            "extra",
            "image_titles",                     # images use `alt` text as `title` too
            CaptionedFigureExtension(
                html_class="md-captioned-figure", caption_html_class="md-captioned-figure__caption"
            ),
            CitedBlockquoteExtension(
                html_class="md-cited-blockquote", citation_html_class="md-cited-blockquote__citation"
            ),
            DivExtension(
                types={
                    "textbox": {"html_class": "md-textbox md-textbox-default last-child-no-mb"}
                }
            ),
            DropdownExtension(
                html_class="md-dropdown",
                summary_html_class="md-dropdown__summary last-child-no-mb",
                content_html_class="md-dropdown__content last-child-no-mb",
                types = {
                    "dropdown": {"html_class": "md-dropdown-default"}
                }
            ),
            StrikethroughExtension(),
            ThmsExtension(
                div_types={
                    "coro": {
                        "thm_type": "Corollary",
                        "html_class": "md-textbox md-textbox-coro last-child-no-mb",
                        "thm_counter_incr": "0,0,1"
                    },
                    "defn": {
                        "thm_type": "Definition",
                        "html_class": "md-textbox md-textbox-defn last-child-no-mb",
                        "thm_counter_incr": "0,0,1"
                    },
                    r"defn\\\*": {
                        "thm_type": "Definition",
                        "html_class": "md-textbox md-textbox-defn last-child-no-mb"
                    },
                    "ex": {
                        "thm_type": "Example",
                        "html_class": "md-div-ex"
                    },
                    r"notat\\\*": {
                        "thm_type": "Notation",
                        "html_class": "md-textbox md-textbox-notat last-child-no-mb"
                    },
                    "prop": {
                        "thm_type": "Proposition",
                        "html_class": "md-textbox md-textbox-prop last-child-no-mb",
                        "thm_counter_incr": "0,0,1"
                    },
                    "thm": {
                        "thm_type": "Theorem",
                        "html_class": "md-textbox md-textbox-thm last-child-no-mb",
                        "thm_counter_incr": "0,0,1"
                    },
                    r"thm\\\*": {
                        "thm_type": "Theorem",
                        "html_class": "md-textbox md-textbox-thm last-child-no-mb"
                    }
                },
                dropdown_html_class="md-dropdown",
                dropdown_summary_html_class="md-dropdown__summary last-child-no-mb",
                dropdown_content_html_class="md-dropdown__content last-child-no-mb",
                dropdown_types={
                    "exer": {
                        "thm_type": "Exercise",
                        "html_class": "md-dropdown-exer",
                        "thm_counter_incr": "0,0,1",
                        "use_punct_if_nothing_after": False
                    },
                    "pf": {
                        "thm_type": "Proof",
                        "html_class": "md-dropdown-pf",
                        "thm_name_overrides_thm_heading": True,
                        "use_punct_if_nothing_after": False
                    },
                    r"rmk\\\*": {
                        "thm_type": "Remark",
                        "html_class": "md-dropdown-rmk",
                        "thm_name_overrides_thm_heading": True,
                        "use_punct_if_nothing_after": False
                    }
                },
                thm_heading_html_class="md-thm-heading",
                thm_type_html_class="md-thm-heading__thm-type"
            ),
            TocExtension(
                    marker="", permalink="\uf470", permalink_class="header-link",
                    permalink_title="", slugify=generate_anchors, toc_depth=2)
        ])
        post.content = content_md.convert(post.content)

    add_comment_form = AddCommentForm()
    posts_in_curr_bp = db.session.query(Post).filter_by(blogpage_id=post.blogpage_id)
    curr_coalesced_timestamp = post.edited_timestamp if post.edited_timestamp is not None else post.timestamp
    prev_post = posts_in_curr_bp.filter(
            sa_func.coalesce(Post.edited_timestamp, Post.timestamp) < curr_coalesced_timestamp) \
                    .order_by(sa_func.coalesce(Post.edited_timestamp, Post.timestamp).desc()).first()
    next_post = posts_in_curr_bp.filter(
            sa_func.coalesce(Post.edited_timestamp, Post.timestamp) > curr_coalesced_timestamp) \
                    .order_by(sa_func.coalesce(Post.edited_timestamp, Post.timestamp)).first()
    return render_template(
            "blog/blogpage/post.html",
            post=post,
            prev_post=prev_post,
            next_post=next_post,
            toc_tokens=content_md.toc_tokens if content_md is not None else None,
            add_comment_form=add_comment_form)


@bp.route("/<string:post_sanitized_title>/get-comments", methods=["GET"])
@util.set_content_type(ContentType.HTML)
@bp_util.require_valid_post()
@bp_util.redir_to_post_after_login()
def get_comments(post, post_sanitized_title, **kwargs):
    # get comments from db and render Markdown
    comments_query = post.comments.select().order_by(Comment.timestamp.desc())
    comments = db.session.scalars(comments_query).all()

    for comment in comments:
        if comment.author == current_app.config["VERIFIED_AUTHOR"]:
            comment.content = markdown.markdown(
                    comment.content,
                    extensions=["extra", "image_titles", StrikethroughExtension()])
        else:
            # no custom block Markdown for non-admin because there are prob ways to 500 the page that I don't wanna fix
            # (and besides it loads faster)
            comment.content = markdown.markdown(comment.content, extensions=["extra"])
            comment.content = bp_util.sanitize_untrusted_html(comment.content)
 
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
@util.set_content_type(ContentType.JSON)
@bp_util.require_valid_post()
@bp_util.redir_to_post_after_login()
def get_comment_count(post, post_sanitized_title, **kwargs):
    return jsonify(count=post.get_comment_count())


@bp.route("/<string:post_sanitized_title>/get-comment-unread-count", methods=["GET"])
@util.set_content_type(ContentType.JSON)
@util.require_login()
@bp_util.require_valid_post()
@bp_util.redir_to_post_after_login()
def get_unread_comment_count(post, post_sanitized_title, **kwargs):
    return jsonify(count=post.get_unread_comment_count())


###################################################################################################
# POST Endpoints
###################################################################################################


@bp.route("/<string:post_sanitized_title>/add-comment", methods=["POST"])
@util.set_content_type(ContentType.JSON)
@bp_util.require_login_if_restricted_bp()
@bp_util.require_valid_post()
@bp_util.redir_to_post_after_login()
def add_comment(post, post_sanitized_title, **kwargs):
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

    # add comment
    comment = Comment(
            author=author,
            content=request.form.get("content"),
            post=post,
            is_unread=not is_verified_author) # make sure I my own comments aren't unread when I add them, cause duh
    with db.session.no_autoflush:             # otherwise there's a warning
        if not comment.insert_comment(post, db.session.get(Comment, request.form.get("parent"))):
            return jsonify(flash_msg="haker :3")
    db.session.add(comment)
    db.session.commit()

    return jsonify(success=True, flash_msg="Comment added successfully!")


@bp.route("/<string:post_sanitized_title>/delete-comment", methods=["POST"])
@util.set_content_type(ContentType.JSON)
@util.require_login()
@bp_util.require_valid_post()
@bp_util.redir_to_post_after_login()
def delete_comment(post, post_sanitized_title, **kwargs):
    comment = db.session.get(Comment, request.args.get("comment_id"))
    if comment is None:
        return jsonify(success=True, flash_msg=f"That comment doesn't exist :/")

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
@util.set_content_type(ContentType.JSON)
@util.require_login()
@bp_util.require_valid_post()
@bp_util.redir_to_post_after_login()
def mark_comments_as_read(post, post_sanitized_title, **kwargs):
    # mark comments under current post as read
    unread_comments_query = post.comments.select().filter_by(is_unread=True)
    unread_comments = db.session.scalars(unread_comments_query).all()
    for comment in unread_comments:
        comment.is_unread=False
    db.session.commit()
    return jsonify(success=True)
