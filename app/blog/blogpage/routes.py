import markdown
import re
import shutil

from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user
import sqlalchemy as sa
from sqlalchemy import desc

from app import db, turnstile
from app.blog.blogpage import bp
from app.blog.blogpage.forms import *
from app.models import *
import app.util as util
from markdownext.myextensions import MyExtensions


def get_blog_id(blueprint_name) -> int:
    return int(blueprint_name.split('.')[-1])


@bp.route("/")
def index():
    blog_id = get_blog_id(request.blueprint)
    
    # require login to access private blogs
    if blog_id in current_app.config["PRIVATE_BLOG_IDS"] and not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    # not the neatest way to do this probably
    if blog_id == current_app.config["ALL_POSTS_BLOG_ID"]:
        posts = db.session.query(Post).filter(Post.blog_id \
                .notin_(current_app.config["PRIVATE_BLOG_IDS"])).order_by(desc(Post.timestamp))
        return render_template("blog/blogpage/all_posts.html",
                blog_id=blog_id, title=current_app.config["BLOG_ID_TO_TITLE"][blog_id],
                posts=posts)

    posts = db.session.query(Post).filter_by(blog_id=blog_id) \
            .order_by(desc(Post.timestamp))
    return render_template("blog/blogpage/index.html",
            blog_id=blog_id, title=current_app.config["BLOG_ID_TO_TITLE"][blog_id],
            subtitle=current_app.config["BLOG_ID_TO_SUBTITLE"].get(blog_id, ""),
            posts=posts)


@bp.route("/<string:post_sanitized_title>", methods=["GET", "POST"])
def post(post_sanitized_title):
    blog_id = get_blog_id(request.blueprint)

    # require login to access private blogs
    if blog_id in current_app.config["PRIVATE_BLOG_IDS"] and not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    add_comment_form = AddCommentForm()
    reply_comment_button = ReplyCommentButton()
    delete_comment_button = DeleteCommentButton()
    post = db.session.query(Post).filter(Post.sanitized_title == post_sanitized_title).first()
    if post is None:
        return redirect(url_for(f"{request.blueprint}.index",
                flash=util.encode_URI_component("The post doesn't exist.")))

    if request.method == "GET":
        post.content = markdown.markdown(post.content, extensions=["extra", MyExtensions()])
    #    # custom Markdown \lf{}\elf to give stuff inside LaTeX font
    #    post.content = re.sub(r"\\lf{([\S\s]*?)}\\elf", r'<span class="font-latex">\1</span>', post.content)

        comments_query = post.comments.select().order_by(desc(Comment.timestamp))
        comments = db.session.scalars(comments_query).all()
        for comment in comments:
            comment.content = markdown.markdown(comment.content, extensions=["extra", MyExtensions()])

        return render_template("blog/blogpage/post.html",
                blog_id=blog_id, blog_title=current_app.config["BLOG_ID_TO_TITLE"][blog_id],
                post=post, comments=comments, add_comment_form=add_comment_form,
                reply_comment_button = reply_comment_button,
                delete_comment_button = delete_comment_button,
                get_descendants_list=Comment.get_descendants_list)

    # Ajax: FormData
    elif request.method == "POST":
        if not turnstile.verify():
            return jsonify(redirect_uri=url_for("main.bot_jail"))

        # handle comment deletion (after confirmation button)
        if "delete" in request.form:
            if not current_user.is_authenticated: # since we can't use @login_required here
                return jsonify(flash_message="Nice try.")

            comment = db.session.get(Comment, request.form["id"])
            if comment is None:
                return jsonify(success=True, flash_message=f"That comment is already gone...")

            descendants = comment.get_descendants_list(post)
            if not comment.remove_comment(post):
                return jsonify(redirect_uri=url_for(f"{request.blueprint}.index"),
                        flash_message="Sanity check is not supposed to fail...")
            for descendant in descendants:
                db.session.delete(descendant)
            db.session.delete(comment)
            db.session.commit()
            return jsonify(success=True, flash_message="1984 established!")

        # handle comment addition otherwise
        if not add_comment_form.validate():
            return jsonify(submission_errors=add_comment_form.errors)
        # make sure non-admin users can't masquerade as verified author
        if request.form["author"].lower() == current_app.config["VERIFIED_AUTHOR"].lower() \
                and not current_user.is_authenticated:
            return jsonify(submission_errors={"author": ["You are not the verified original poster."]})

        comment = Comment(author=request.form["author"], content=request.form["content"],
                post=post) # SQLAlchemy automatically generates post_id ForeignKey from post relationship()
        if not comment.insert_comment(post, db.session.get(Comment, request.form["parent"])):
            return jsonify(redirect_uri=url_for(f"{request.blueprint}.index"),
                    flash_message="Sanity check is not supposed to fail...")
        db.session.add(comment)
        db.session.commit()
        return jsonify(success=True, flash_message="Comment added successfully!")

    return "If you see this message, please panic."
