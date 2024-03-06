from flask_wtf import FlaskForm
from wtforms import PasswordField, RadioField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app import db_config

class PasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_PASSWORD"])])
    submit = SubmitField("Submit")


class SelectActionForm(FlaskForm):
    action = RadioField("Actions", choices=[("create", "Create"), ("edit", "Edit"), ("delete", "Delete"),
            ("change_admin_password", "Change Admin Password")], validators=[DataRequired()])
    submit = SubmitField("Submit")


class CreateBlogpostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_POST_TITLE"])])
    subtitle = StringField("Subtitle", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_POST_SUBTITLE"])])
    content = StringField("Content (Markdown supported)", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_POST_CONTENT"])])
    submit = SubmitField("Submit")


class SearchBlogpostForm(FlaskForm):
    searched_title = StringField("Title of form", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_POST_TITLE"])])


class EditBlogpostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_POST_TITLE"])])
    subtitle = StringField("Subtitle", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_POST_SUBTITLE"])])
    content = StringField("Content (Markdown supported)", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_POST_CONTENT"])])
    submit = SubmitField("Submit")


class ChangeAdminPasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_PASSWORD"])])
    new_password_1 = PasswordField("New password", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_PASSWORD"])])
    new_password_2 = PasswordField("Repeat new password", validators=[DataRequired(),
            Length(max=db_config.config["MAXLEN_PASSWORD"])])
    submit = SubmitField("Submit")
