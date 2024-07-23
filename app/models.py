from datetime import datetime, timezone
import re
from typing import Optional

from flask import current_app
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.types import Text
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login_manager
from config import Config


class Blogpage(db.Model):
    id: \
        so.Mapped[int] = so.mapped_column(
            primary_key=True,
            autoincrement=False
        )    
    ordering: \
        so.Mapped[int] = so.mapped_column(
            sa.Integer(),
            unique=True,
            index=True
        )
    url_path: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_BLOGPAGE_URL_PATH"])
        )
    title: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_BLOGPAGE_TITLE"])
        )
    subtitle: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_BLOGPAGE_SUBTITLE"]),
            nullable=True,
            default=None
        )
    meta_description: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_BLOGPAGE_META_DESCRIPTION"]),
            nullable=True,
            default=None
        )
    html_color_class: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_BLOGPAGE_COLOR_HTML_CLASS"]),
            nullable=True,
            default=None
        )

    login_required: so.Mapped[bool] = so.mapped_column(
        sa.Boolean,
        default=True
    )
    unpublished: \
        so.Mapped[bool] = so.mapped_column(
            sa.Boolean,
            default=True
        )
    writeable: \
        so.Mapped[bool] = so.mapped_column(
            sa.Boolean,
            default=False
        )

    posts: \
        so.WriteOnlyMapped["Post"] = so.relationship(
            back_populates="blogpage",
            cascade="all, delete, delete-orphan",
            passive_deletes=True
        )


class Post(db.Model):
    id: \
        so.Mapped[int] = so.mapped_column(
            primary_key=True
        )
    blogpage_id: \
        so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(Blogpage.id, ondelete="CASCADE")
        )
    published: \
        so.Mapped[bool] = so.mapped_column(
            default=False
        )
    timestamp: \
        so.Mapped[datetime] = so.mapped_column(
            index=True,
            default=lambda: datetime.now(timezone.utc)
        )
    edited_timestamp: \
        so.Mapped[datetime] = so.mapped_column(
            nullable=True,
            default=None
        )
    title: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_POST_TITLE"])
        )
    sanitized_title: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_POST_TITLE"])
        )
    subtitle: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_POST_SUBTITLE"]),
            nullable=True,
            default=None
        )
    content: \
        so.Mapped[Text()] = so.mapped_column(
            Text(Config.DB_CONFIGS["MAXLEN_POST_CONTENT"]),
            nullable=True
        )

    blogpage: \
        so.Mapped[Blogpage] = so.relationship(
            back_populates="posts"
        )

    comments: \
        so.WriteOnlyMapped["Comment"] = so.relationship(
            back_populates="post",
            cascade="all, delete, delete-orphan",
            passive_deletes=True
        )

    def sanitize_title(self):
        self.sanitized_title = ("-".join(self.title.split())).lower()
        self.sanitized_title = re.sub("[^A-Za-z0-9-]", "", self.sanitized_title)

    # must be done after add() and flush()!!! Hence why `unique=True` not enforced for title and sanitized title
    def are_titles_unique(self) -> bool:
        return len(db.session.query(Post).filter_by(sanitized_title = self.sanitized_title).all()) == 1

    def expand_image_markdown(self):
        self.content = re.sub(r"(!\[[\S\s]*?\])\(([\S\s]+?)\)",
                fr"\1({current_app.config['BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC']}/{self.blogpage_id}/images/{self.id}/\2)", self.content)

    def collapse_image_markdown(self) -> str:
        return re.sub(fr"(!\[[\S\s]*?\])\({current_app.config['BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC']}/{self.blogpage_id}/images/{self.id}/([\S\s]+?)\)",
                r"\1(\2)", self.content)

    # god bless Miguel Grinberg https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers
    def get_comment_count(self) -> int:
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            self.comments.select().subquery()))

    def __repr__(self):
        return f"<Post {self.id} with title \"{self.title}\" and subtitle \"{self.subtitle}\">"


class Comment(db.Model):
    id: \
        so.Mapped[int] = so.mapped_column(
            primary_key=True
        )
    post_id: \
        so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(Post.id, ondelete="CASCADE")
        )
    timestamp: \
        so.Mapped[datetime] = so.mapped_column(
            index=True,
            default=lambda: datetime.now(timezone.utc)
        )
    author: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_COMMENT_AUTHOR"])
        )
    content: \
        so.Mapped[Text()] = so.mapped_column(
            Text(Config.DB_CONFIGS["MAXLEN_COMMENT_CONTENT"])
        )

    post: \
        so.Mapped[Post] = so.relationship(
            back_populates="comments"
        )

        # nested set; quite the beautiful data structure
    left: \
        so.Mapped[int] = so.mapped_column(
            sa.Integer,
            index=True
        )
    right: \
        so.Mapped[int] = so.mapped_column(
            sa.Integer,
            index=True
        )
    depth: \
        so.Mapped[int] = so.mapped_column(
            sa.Integer
        )

    def insert_comment(self, post, parent) -> bool:
        if parent is None: # add child with left = max of right for that post + 1
            max_right_query = post.comments.select().order_by(sa.desc(Comment.right)).limit(1)
            max_right_comment = db.session.scalars(max_right_query).first()
            max_right = 0
            if max_right_comment is not None:
                max_right = max_right_comment.right
            self.left = max_right + 1
            self.right = max_right + 2
            self.depth = 0
            return True

        if self.post_id != parent.post_id or self.post_id != post.id: # sanity check
            return False

        self.left = parent.right
        self.right = parent.right + 1
        self.depth = parent.depth + 1

        comments_to_update_query = post.comments.select().filter(Comment.right >= parent.right)
        comments_to_update = db.session.scalars(comments_to_update_query).all()
        for comment in comments_to_update:
            if comment.left >= parent.right:
                comment.left += 2
            comment.right += 2
        return True

    def remove_comment(self, post) -> bool:
        if self.post_id != post.id: # sanity check
            return False

        descendants = self.get_descendants_list(post)
        for descendant in descendants:
            if not descendant.remove_comment(post):
                return False

        comments_to_update_query = post.comments.select().filter(Comment.right > self.right)
        comments_to_update = db.session.scalars(comments_to_update_query).all()
        for comment in comments_to_update:
            if comment.left > self.right:
                comment.left -= 2
            comment.right -= 2
        return True

    def get_descendants_list(self, post) -> list:
        comments_query = post.comments.select().filter(sa.and_(
                Comment.left > self.left, Comment.right < self.right))
        return db.session.scalars(comments_query).all()

    def __repr(self):
        return f"<Comment {self.id} for post {self.post_id} written by \"{self.author}\""


class User(UserMixin, db.Model):
    id: \
        so.Mapped[int] = so.mapped_column(
            primary_key=True
        )
    username: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_USER_USERNAME"]),
            unique=True
        )
    email: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_USER_EMAIL"]),
            unique=True
        )
    password_hash: \
        so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["MAXLEN_USER_PASSWORD_HASH"])
        )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id):
	return db.session.get(User, int(id))
