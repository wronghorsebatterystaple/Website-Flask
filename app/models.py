import re
from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.dialects.mysql as sa_mysql
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from config import Config


class Blogpage(db.Model):
    id: so.Mapped[int] = so.mapped_column(
            primary_key=True,
            nullable=False,
            autoincrement=False)    

    # basic attributes
    name: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["BLOGPAGE_NAME_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            nullable=False)

    subname: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["BLOGPAGE_SUBNAME_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            nullable=True,
            default=None,
            server_default=None)
    
    meta_description: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["BLOGPAGE_META_DESCRIPTION_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            nullable=True,
            default=None,
            server_default=None)

    color: so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["BLOGPAGE_COLOR_MAXLEN"]),
            nullable=False,
            default="black",
            server_default="black")

    ordering: so.Mapped[int] = so.mapped_column(
            unique=True,
            nullable=False,
            index=True)

    is_all_posts: so.Mapped[bool] = so.mapped_column(
            nullable=False,
            default=False,
            server_default=sa.false())

    is_login_required: so.Mapped[bool] = so.mapped_column(
            nullable=False,
            default=True,
            server_default=sa.true())

    is_published: so.Mapped[bool] = so.mapped_column(
            nullable=False,
            default=False,
            server_default=sa.false())

    is_writeable: so.Mapped[bool] = so.mapped_column(
            nullable=False,
            default=False,
            server_default=sa.false())

    # relationship: `Post`
    # using quotation marks for `"Post"` since the class isn't defined yet
    posts: so.WriteOnlyMapped["Post"] = so.relationship(
            back_populates="blogpage",
            cascade="all, delete-orphan",
            passive_deletes=True)

    # relationship: `Blogpage`
    publishing_sibling_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey("blogpage.id"), # these need to use lowercase SQL table name instead of Python class name
            unique=True,
            nullable=True,
            default=None,
            server_default=None)

    publishing_sibling: so.Mapped["Blogpage"] = so.relationship()


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(
            primary_key=True,
            nullable=False)

    # basic attributes
    title: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["POST_TITLE_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            nullable=False)

    sanitized_title: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["POST_TITLE_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            unique=True,
            nullable=False)

    subtitle: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["POST_SUBTITLE_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            nullable=True,
            default=None,
            server_default=None)

    timestamp: so.Mapped[datetime] = so.mapped_column(
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            server_default=sa.text("NOW()"), # should be same format as when SQLAlchemy casts Python `datetime` obj
            index=True)

    edited_timestamp: so.Mapped[datetime] = so.mapped_column(
            nullable=True,
            default=None,
            server_default=None)

    content: so.Mapped[sa_mysql.MEDIUMTEXT()] = so.mapped_column(
            sa_mysql.MEDIUMTEXT(charset="utf8mb4", collation="utf8mb4_0900_ai_ci"),
            nullable=True,
            default=None,
            server_default=None)

    is_published: so.Mapped[bool] = so.mapped_column(
            nullable=False,
            default=False,
            server_default=sa.false())

    # relationship: `Blogpage`
    blogpage_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(Blogpage.id, ondelete="CASCADE"),
            nullable=False)

    blogpage: so.Mapped[Blogpage] = so.relationship(
            back_populates="posts")

    # relationship: `Comment`
    comments: so.WriteOnlyMapped["Comment"] = so.relationship(
            back_populates="post",
            cascade="all, delete-orphan",
            passive_deletes=True)

    # util functions
    def sanitize_title(self):
        """
        Replaces whitespace with hyphens, uses all lowercase, and removes all non-alphanumeric and non-hypthen
        characters.
        """

        self.sanitized_title = ("-".join(self.title.split())).lower()
        self.sanitized_title = re.sub("[^A-Za-z0-9-]", "", self.sanitized_title)

    def check_titles(self) -> str:
        """
        Preconditions:
            - `db.session.add()`
        """

        # check that title still exists after sanitization
        if self.sanitized_title == "":
            return "Post must have alphanumeric characters in its title."
        # check that titles are unique
        if len(db.session.query(Post).filter_by(sanitized_title = self.sanitized_title).all()) != 1:
            return "There is already a post with that title or sanitized title."

        # standardize subtitles to None/NULL
        if self.subtitle == "":
            self.subtitle = None

        return None

    def add_timestamps(self, remove_edited_timestamp, update_edited_timestamp):
        if update_edited_timestamp:
            self.edited_timestamp = datetime.now(timezone.utc)
        if remove_edited_timestamp:
            self.edited_timestamp = None

        originally_published = self.is_published
        self.is_published = self.blogpage.is_published
        if not originally_published:
            # keep updating created time instead of edited time if not already published
            self.timestamp = datetime.now(timezone.utc)
            self.edited_timestamp = None

    def expand_image_markdown(self):
        self.content = re.sub(
                r"(!\[[\S\s]*?\])\(([\S\s]+?)\)",
                fr"\1({current_app.config['BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC']}/{self.blogpage_id}/images/{self.id}/\2)", 
                self.content)

    def collapse_image_markdown(self) -> str:
        return re.sub(
                fr"(!\[[\S\s]*?\])\({current_app.config['BLOGPAGE_ROUTES_TO_BLOGPAGE_STATIC']}/{self.blogpage_id}/images/{self.id}/([\S\s]+?)\)",
                r"\1(\2)",
                self.content)

    def get_comment_count(self) -> int:
        # god bless https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers
        query = sa.select(sa.func.count()).select_from(self.comments.select().subquery())
        return db.session.scalar(query)

    def get_unread_comment_count(self) -> int:
        query = sa.select(sa.func.count()).select_from(self.comments.select().filter_by(is_unread=True).subquery())
        return db.session.scalar(query)

    def __repr__(self):
        return f"<Post {self.id} with title \"{self.title}\" and subtitle \"{self.subtitle}\">"


class Comment(db.Model):
    id: so.Mapped[int] = so.mapped_column(
            primary_key=True)

    # basic attributes
    author: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["COMMENT_AUTHOR_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            nullable=False)

    timestamp: so.Mapped[datetime] = so.mapped_column(
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            server_default=sa.text("NOW()"),
            index=True)

    content: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["COMMENT_CONTENT_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            nullable=False)

    is_unread: so.Mapped[bool] = so.mapped_column(
            nullable=False,
            default=True,
            server_default=sa.true())

    # relationship: `Post`
    post_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(Post.id, ondelete="CASCADE"),
            nullable=False)

    post: so.Mapped[Post] = so.relationship(
            back_populates="comments")

    # nested set; quite the beautiful data structure
    depth: so.Mapped[int] = so.mapped_column(nullable=False)
    left: so.Mapped[int] = so.mapped_column(
            nullable=False,
            index=True)
    right: so.Mapped[int] = so.mapped_column(
            nullable=False,
            index=True)

    # util functions
    def insert_comment(self, post, parent) -> bool:
        if parent is None:
            # add child with left = max of right for that post + 1
            max_right_query = post.comments.select().order_by(sa.desc(Comment.right)).limit(1)
            max_right_comment = db.session.scalars(max_right_query).first()
            max_right = 0
            if max_right_comment is not None:
                max_right = max_right_comment.right
            self.left = max_right + 1
            self.right = max_right + 2
            self.depth = 0
            return True
        elif post.id != parent.post_id:
            # make sure people aren't tampering with the packet and screwing up the db relationships
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
        # sanity check
        if self.post_id != post.id:
            return False

        descendants = self.get_descendants(post)
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

    def get_descendants(self, post) -> list:
        comments_query = post.comments.select().filter(sa.and_(
                Comment.left > self.left, Comment.right < self.right))
        return db.session.scalars(comments_query).all()

    def __repr__(self):
        return f"<Comment {self.id} for post {self.post_id} written by \"{self.author}\""


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(
            primary_key=True,
            nullable=False)

    # basic attributes
    email: so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["USER_EMAIL_MAXLEN"]),
            unique=True,
            nullable=False)

    username: so.Mapped[sa_mysql.VARCHAR()] = so.mapped_column(
            sa_mysql.VARCHAR(
                    Config.DB_CONFIGS["USER_USERNAME_MAXLEN"],
                    charset="utf8mb4",
                    collation="utf8mb4_0900_ai_ci"),
            unique=True,
            nullable=False)

    password_hash: so.Mapped[str] = so.mapped_column(
            sa.String(Config.DB_CONFIGS["USER_PASSWORD_HASH_MAXLEN"]),
            nullable=False)

    # util functions
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# required for Flask-Login
@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))
