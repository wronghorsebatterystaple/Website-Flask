from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

from app.db_config import db_config

class AddCommentForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_COMMENT_AUTHOR_NAME"])])
    content = TextAreaField("Comment (markdown supported)", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_COMMENT_CONTENT"])])
    submit = SubmitField("Submit")
