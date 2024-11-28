from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

from config import Config


class AddCommentForm(FlaskForm):
    parent = HiddenField(default=None)

    author = StringField("Name",validators=[InputRequired(), Length(max=Config.DB_CONFIGS["COMMENT_AUTHOR_MAXLEN"])])

    content = TextAreaField(
            "Comment", validators=[InputRequired(), Length(max=Config.DB_CONFIGS["COMMENT_CONTENT_MAXLEN"])])

    add_comment_form_submit = SubmitField("Submit")


class ReplyCommentBtn(FlaskForm):
    reply_comment = SubmitField("Reply")


class DeleteCommentBtn(FlaskForm):
    delete_comment = SubmitField("Delete")
