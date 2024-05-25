from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

from app.db_config import db_config


class AddCommentForm(FlaskForm):
    post_id = HiddenField(default=None)
    author = StringField("Name", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_COMMENT_AUTHOR"])])
    parent = HiddenField(default=None)
    content = TextAreaField("Comment",
            validators=[InputRequired(), Length(max=db_config["MAXLEN_COMMENT_CONTENT"])])
    submit = SubmitField("Submit")


class ReplyCommentButton(FlaskForm):
    submit = SubmitField("Reply")


class DeleteCommentButton(FlaskForm):
    comment_id = HiddenField(default=None)
    post_id = HiddenField(default=None)
    delete = SubmitField("Delete", render_kw={"data-confirm-submit": ""})
