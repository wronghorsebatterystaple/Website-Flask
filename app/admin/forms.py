from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, MultipleFileField, PasswordField, RadioField, SelectField,
    SelectMultipleField, StringField, SubmitField, TextAreaField
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length

from app import db
from app.models import *
from config import Config


class LoginForm(FlaskForm):
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(max=Config.DB_CONFIGS["USER_PASSWORD_MAXLEN"])]
    )
    login_form_submit = SubmitField("Submit")


class ChooseActionForm(FlaskForm):
    action = RadioField(
        "Actions", choices=[
            ("create", "Create post"),
            ("edit", "Edit/delete post"),
            ("change_admin_password", "Change admin password")
        ],
        validators=[InputRequired()]
    )
    choose_action_form_submit = SubmitField("Submit")


class SearchBlogpostForm(FlaskForm):
    post = QuerySelectField(
        "Post", validators=[InputRequired()],
        query_factory=lambda: db.session.query(Post).order_by(Post.title), get_label="title"
    )
    search_blogpost_form_submit = SubmitField("Submit")
    back = SubmitField("Back", render_kw={"data-class": "back-btn", "type": "button"})


class BlogpostBaseForm(FlaskForm):
    blogpage_id = SelectField("Blog", coerce=int, validators=[InputRequired()])
    title = StringField("Title", validators=[InputRequired(), Length(max=Config.DB_CONFIGS["POST_TITLE_MAXLEN"])])
    subtitle = StringField("Subtitle", validators=[Length(max=Config.DB_CONFIGS["POST_SUBTITLE_MAXLEN"])])
    content = TextAreaField(
        "Content (Markdown, LaTeX supported)", validators=[Length(max=Config.DB_CONFIGS["POST_CONTENT_MAXLEN"])]
    )
    images = MultipleFileField(f"Upload images (supported formats: {', '.join(Config.IMAGE_UPLOAD_EXTS)})")
    cancel_image_uploads = SubmitField("Clear images to upload", render_kw={"type": "button"})


class CreateBlogpostForm(BlogpostBaseForm):
    create_blogpost_form_submit = SubmitField("Submit")
    back = SubmitField("Back", render_kw={"data-class": "back-btn", "type": "button"})


class EditBlogpostForm(BlogpostBaseForm):
    delete_images = SelectMultipleField("Delete images")
    cancel_delete_images = SubmitField("Clear images to delete", render_kw={"type": "button"})
    delete_unused_images = BooleanField("Delete unused images")
    update_updated_timestamp = BooleanField("Update updated timestamp")
    remove_updated_timestamp = BooleanField("Remove updated timestamp")
    edit_blogpost_form_submit = SubmitField("Submit")
    delete_post = SubmitField("Delete Post", render_kw={"type": "button"})
    back = SubmitField("Back", render_kw={"data-class": "back-btn", "type": "button"})


class ChangeAdminPasswordForm(FlaskForm):
    old_password = PasswordField(
        "Old password", validators=[InputRequired(), Length(max=Config.DB_CONFIGS["USER_PASSWORD_MAXLEN"])]
    )
    new_password_1 = PasswordField(
        "New password", validators=[InputRequired(), Length(max=Config.DB_CONFIGS["USER_PASSWORD_MAXLEN"])]
    )
    new_password_2 = PasswordField(
        "Repeat new password", validators=[InputRequired(), Length(max=Config.DB_CONFIGS["USER_PASSWORD_MAXLEN"])]
    )
    change_admin_password_submit = SubmitField("Submit")
    back = SubmitField("Back", render_kw={"data-class": "back-btn", "type": "button"})
