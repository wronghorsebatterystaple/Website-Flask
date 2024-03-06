from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
import re

from app import db_config

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
    title: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_TITLE"]), unique=True)
    title_for_url: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_TITLE"]), unique=True)
    subtitle: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_SUBTITLE"]))
    content: so.Mapped[str] = so.mapped_column(sa.String(db_config.config["MAXLEN_POST_CONTENT"]))
    comment_ids: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Comment.id))

    def __repr__(self):
        return f"<Post {self.id} with title \"{self.title}\" and subtitle \"{self.subtitle}\">"

    def gen_title_for_url(self):
        self.title_for_url = ("-".join(self.title.split())).lower()
        self.title_for_url = re.sub("[^A-Za-z0-9-]", "", self.title_for_url) # sanitize all non [A-Za-z0-9-] in titles


class Image(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    post_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Post.id))
    img_pos: so.Mapped[int] = so.mapped_column(index=True)

    def __repr__(self):
        return f"<Image {self.id} for post {self.post_id} at position {self.img_pos}>"
