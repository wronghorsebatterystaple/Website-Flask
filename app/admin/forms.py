from flask_wtf import FlaskForm
from wtforms import BooleanField, MultipleFileField, PasswordField, RadioField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length

from app import db
from app.models import Post
from config import Config


class LoginForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])]
    )
    login_form_submit = SubmitField(
        "Submit"
    )


class ChooseActionForm(FlaskForm):
    action = RadioField(
        "Actions",
        choices=[
            ("create", "Create post"),
            ("edit", "Edit/delete post"),
            ("change_admin_password", "Change admin password")
        ],
        validators=[InputRequired()]
    )
    choose_action_form_submit = SubmitField(
        "Submit"
    )


class CreateBlogpostForm(FlaskForm):
    blogpage_id = SelectField(
        "Blog",
        coerce=int,
        validators=[InputRequired()]
    )
    title = StringField(
        "Title",
        validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_POST_TITLE"])]
    )
    subtitle = StringField(
        "Subtitle",
        validators=[Length(max=Config.DB_CONFIGS["MAXLEN_POST_SUBTITLE"])]
    )
    content = TextAreaField(
        "Content",
        validators=[Length(max=Config.DB_CONFIGS["MAXLEN_POST_CONTENT"])]
    )
    images = MultipleFileField(
        f"Upload images (supported formats: {', '.join(Config.IMAGE_UPLOAD_EXTENSIONS)})"
    )
    create_blogpost_form_submit = SubmitField(
        "Submit"
    )
    back = SubmitField(
        "Back",
        render_kw={"data-back-btn": ""}
    )


class SearchBlogpostForm(FlaskForm):
    post = QuerySelectField("Post",
        validators=[InputRequired()],
        query_factory=lambda: db.session.query(Post).order_by(Post.title),
        get_label="title")
    search_blogpost_form_submit = SubmitField(
        "Submit"
    )
    back = SubmitField(
        "Back",
        render_kw={"data-back-btn": ""}
    )


class EditBlogpostForm(FlaskForm):
    blogpage_id = SelectField(
        "Blog",
        validators=[InputRequired()]
    )
    title = StringField(
        "Title",
        validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_POST_TITLE"])]
    )
    subtitle = StringField(
        "Subtitle",
        validators=[Length(max=Config.DB_CONFIGS["MAXLEN_POST_SUBTITLE"])]
    )
    content = TextAreaField(
        "Content",
        validators=[Length(max=Config.DB_CONFIGS["MAXLEN_POST_CONTENT"])]
    )
    images = MultipleFileField(
        f"Upload images (supported formats: {', '.join(Config.IMAGE_UPLOAD_EXTENSIONS)})"
    )
    cancel_image_uploads = SubmitField(
        "Clear images to upload",
        render_kw={"id": "cancel-image-uploads-btn", "data-no-submit": ""}
    )
    delete_images = SelectMultipleField(
        "Delete images"
    )
    cancel_delete_images = SubmitField(
        "Clear images to delete",
        render_kw={"id": "cancel-delete-images-btn", "data-no-submit": ""}
    )
    delete_unused_images = BooleanField(
        "Delete unused images"
    )
    update_edited_timestamp = BooleanField(
        "Update edited timestamp"
    )
    remove_edited_timestamp = BooleanField(
        "Remove edited timestamp"
    )
    edit_blogpost_form_submit = SubmitField(
        "Submit"
    )
    delete = SubmitField(
        "Delete Post",
        render_kw={"data-confirm-submit": ""}
    )
    back = SubmitField(
        "Back",
        render_kw={"data-back-btn": ""}
    )


class ChangeAdminPasswordForm(FlaskForm):
    old_password = PasswordField(
        "Old password",
        validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])]
    )
    new_password_1 = PasswordField(
        "New password",
        validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])]
    )
    new_password_2 = PasswordField(
        "Repeat new password",
        validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])]
    )
    change_admin_password_submit = SubmitField(
        "Submit"
    )
    back = SubmitField(
        "Back",
        render_kw={"data-back-btn": ""}
    )
