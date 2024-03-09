from flask_wtf import FlaskForm
from wtforms import PasswordField, RadioField, StringField, SubmitField
from wtforms.validators import InputRequired, Length
from wtforms_sqlalchemy.fields import QuerySelectField

from app import db
from app import db_config
from app.models import Post

class PasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_USER_PASSWORD"])])
    submit = SubmitField("Submit")


class ChooseActionForm(FlaskForm):
    action = RadioField("Actions", choices=[("create", "Create"), ("edit", "Edit/Delete"),
            ("change_admin_password", "Change Admin Password")], validators=[InputRequired()])
    submit = SubmitField("Submit")


class CreateBlogpostForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_POST_TITLE"])])
    subtitle = StringField("Subtitle", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_POST_SUBTITLE"])])
    content = StringField("Content (Markdown supported)", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_POST_CONTENT"])])
    submit = SubmitField("Submit")


class SearchBlogpostForm(FlaskForm):
    post = QuerySelectField("Post", validators=[InputRequired()],
            query_factory=lambda: db.session.query(Post), get_label="title")
    submit = SubmitField("Submit")


class EditBlogpostForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_POST_TITLE"])])
    subtitle = StringField("Subtitle", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_POST_SUBTITLE"])])
    content = StringField("Content (Markdown supported)", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_POST_CONTENT"])])
    submit = SubmitField("Submit")
    delete = SubmitField("Delete Post")


class ChangeAdminPasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_USER_PASSWORD"])])
    new_password_1 = PasswordField("New password", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_USER_PASSWORD"])])
    new_password_2 = PasswordField("Repeat new password", validators=[InputRequired(),
            Length(max=db_config.config["MAXLEN_USER_PASSWORD"])])
    submit = SubmitField("Submit")
