from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

from app.db_config import db_config


class AddCommentForm(FlaskForm):
    author = StringField("Name", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_COMMENT_AUTHOR"])])
    parent = HiddenField(default=None)
    content = TextAreaField("Comment (Markdown, LaTeX supported (remember to escape backslashes))", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_COMMENT_CONTENT"])])
    submit = SubmitField("Submit")


class ReplyCommentButton(FlaskForm):
    submit = SubmitField("Reply")


class DeleteCommentButton(FlaskForm):
    id = HiddenField(default=None)
    delete = SubmitField("Delete", render_kw={"onclick": "return confirm('Abuse of power check');"})
