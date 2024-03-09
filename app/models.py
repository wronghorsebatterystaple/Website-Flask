from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app import db
from app import db_config
from app import login_manager

import re

class Comment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
            index=True, default=lambda: datetime.now(timezone.utc))
    author_name: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_COMMENT_AUTHOR_NAME"]))
    content: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_COMMENT_CONTENT"]))

    def __repr(self):
        return f"<Comment {comment.id} written by \"{self.author_name}\", last modified on {self.timestamp}>"


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
            index=True, default=lambda: datetime.now(timezone.utc))
    title: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_TITLE"]),
            unique=True)
    sanitized_title: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_TITLE"]),
            unique=True)
    subtitle: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_SUBTITLE"]))
    content: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_CONTENT"]))
    comment_ids: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Comment.id))

    def sanitize_title(self):
        self.sanitized_title = ("-".join(self.title.split())).lower()
        self.sanitized_title = re.sub("[^A-Za-z0-9-]", "", self.sanitized_title) # sanitize all non [A-Za-z0-9-] in titles

    def __repr__(self):
        return f"<Post {self.id} with title \"{self.title}\" and subtitle \"{self.subtitle}\">"



class Image(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    post_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Post.id))
    img_pos: so.Mapped[int] = so.mapped_column(index=True)

    def __repr__(self):
        return f"<Image {self.id} for post {self.post_id} at position {self.img_pos}>"


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_USER_USERNAME"]),
            unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_USER_EMAIL"]),
            unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_USER_PASSWORD_HASH"]))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id):
	return db.session.get(User, int(id))
