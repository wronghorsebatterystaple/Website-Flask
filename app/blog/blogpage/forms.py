from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

from config import Config


class AddCommentForm(FlaskForm):
    author = StringField(
            "Name",
            validators=[InputRequired(), Length(max=Config.DB_CONFIGS["COMMENT_AUTHOR_LENMAX"])])

    parent = HiddenField(
            default=None)

    content = TextAreaField(
            "Comment",
            validators=[InputRequired(), Length(max=Config.DB_CONFIGS["COMMENT_CONTENT_LENMAX"])],
            render_kw={"data-comment-formatting-tooltip": ""})

    add_comment_form_submit = SubmitField(

            "Submit")


class ReplyCommentButton(FlaskForm):
    reply_comment_button_submit = SubmitField(
            "Reply")


class DeleteCommentButton(FlaskForm):
    delete = SubmitField(
            "Delete",
            render_kw={"data-confirm-submit": ""})
