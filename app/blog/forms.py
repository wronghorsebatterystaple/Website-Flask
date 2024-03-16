from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

from app.db_config import db_config

class AddCommentForm(FlaskForm):
    author = StringField("Name", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_COMMENT_AUTHOR"])])
    content = TextAreaField("Comment (Markdown, LaTeX supported)", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_COMMENT_CONTENT"])])
    submit = SubmitField("Submit")


class CreateBlogpostButton(FlaskForm):
    submit = SubmitField("Create post")


class EditBlogpostButton(FlaskForm):
    submit = SubmitField("Edit/delete post")
