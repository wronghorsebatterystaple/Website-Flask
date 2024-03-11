from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.types import Text
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.db_config import db_config
from app import login_manager

import re

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
            index=True, default=lambda: datetime.now(timezone.utc))
    edited_timestamp: so.Mapped[datetime] = so.mapped_column(nullable=True, default=None)
    title: so.Mapped[str] = so.mapped_column(sa.String(db_config["MAXLEN_POST_TITLE"]),
            unique=True)
    sanitized_title: so.Mapped[str] = so.mapped_column(sa.String(db_config["MAXLEN_POST_TITLE"]),
            unique=True)
    subtitle: so.Mapped[str] = so.mapped_column(sa.String(db_config["MAXLEN_POST_SUBTITLE"]))
    content: so.Mapped[Text()] = so.mapped_column(Text(db_config["MAXLEN_POST_CONTENT"]))

    images: so.WriteOnlyMapped["Image"] = so.relationship(back_populates="post",
            cascade="all, delete, delete-orphan", passive_deletes=True)
    comments: so.WriteOnlyMapped["Comment"] = so.relationship(back_populates="post",
            cascade="all, delete, delete-orphan", passive_deletes=True)

    def sanitize_title(self):
        self.sanitized_title = ("-".join(self.title.split())).lower()
        self.sanitized_title = re.sub("[^A-Za-z0-9-]", "", self.sanitized_title) # sanitize all non [A-Za-z0-9-] in titles

    def __repr__(self):
        return f"<Post {self.id} with title \"{self.title}\" and subtitle \"{self.subtitle}\">"


class Comment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    post_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Post.id, ondelete="CASCADE"))
    timestamp: so.Mapped[datetime] = so.mapped_column(
            index=True, default=lambda: datetime.now(timezone.utc))
    edited_timestamp: so.Mapped[datetime] = so.mapped_column(nullable=True)
    author: so.Mapped[str] = so.mapped_column(sa.String(db_config["MAXLEN_COMMENT_AUTHOR"]))
    content: so.Mapped[Text()] = so.mapped_column(Text(db_config["MAXLEN_COMMENT_CONTENT"]))

    post: so.Mapped[Post] = so.relationship(back_populates="comments")

    def __repr(self):
        return f"<Comment {self.id} for post {self.post_id} written by \"{self.author}\""


class Image(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    post_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Post.id, ondelete="CASCADE"))
    img_pos: so.Mapped[int] = so.mapped_column(index=True)

    post: so.Mapped[Post] = so.relationship(back_populates="images")

    def __repr__(self):
        return f"<Image {self.id} for post {self.post_id} at position {self.img_pos}>"


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(db_config["MAXLEN_USER_USERNAME"]),
            unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(db_config["MAXLEN_USER_EMAIL"]),
            unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(db_config["MAXLEN_USER_PASSWORD_HASH"]))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id):
	return db.session.get(User, int(id))
