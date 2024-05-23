from flask_wtf import FlaskForm
from wtforms import BooleanField, MultipleFileField, PasswordField, RadioField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length

from app import db
from app.models import Post
from config import Config


class LoginForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired(),
            Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])])
    submit = SubmitField("Submit")


class ChooseActionForm(FlaskForm):
    action = RadioField("Actions", choices=[("create", "Create post"), ("edit", "Edit/delete post"),
            ("change_admin_password", "Change admin password")], validators=[InputRequired()])
    submit = SubmitField("Submit")


class CreateBlogpostForm(FlaskForm):
    blog_id = SelectField("Blog", validators=[InputRequired()])
    title = StringField("Title", validators=[InputRequired(),
            Length(max=Config.DB_CONFIGS["MAXLEN_POST_TITLE"])])
    subtitle = StringField("Subtitle", validators=[Length(max=Config.DB_CONFIGS["MAXLEN_POST_SUBTITLE"])])
    content = TextAreaField("Content (Markdown, LaTeX supported (remember to escape backslashes))",
            validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_POST_CONTENT"])])
    images = MultipleFileField("Upload images")
    submit = SubmitField("Submit")
    back = SubmitField("Back", render_kw={"data-back-btn": ""})


class SearchBlogpostForm(FlaskForm):
    post = QuerySelectField("Post", validators=[InputRequired()],
            query_factory=lambda: db.session.query(Post), get_label="title")
    submit = SubmitField("Submit")
    back = SubmitField("Back", render_kw={"data-back-btn": ""})


class EditBlogpostForm(FlaskForm):
    blog_id = SelectField("Blog", validators=[InputRequired()])
    title = StringField("Title", validators=[InputRequired(),
            Length(max=Config.DB_CONFIGS["MAXLEN_POST_TITLE"])])
    subtitle = StringField("Subtitle", validators=[Length(max=Config.DB_CONFIGS["MAXLEN_POST_SUBTITLE"])])
    content = TextAreaField("Content (Markdown, LaTeX supported (remember to escape backslashes))",
            validators=[InputRequired(), Length(max=Config.DB_CONFIGS["MAXLEN_POST_CONTENT"])])
    SUPPORTED_IMAGE_FORMATS = ", ".join(Config.IMAGE_EXTENSIONS).replace(".", "")
    images = MultipleFileField(f"Upload images (supported formats: {SUPPORTED_IMAGE_FORMATS})")
    cancel_images = SubmitField("Clear images to upload", render_kw={"id": "cancel-images-btn"})
    delete_images = SelectMultipleField("Delete images")
    dont_add_edited_timestamp = BooleanField("Don't add edited timestamp")
    remove_edited_timestamps = BooleanField("Remove all edited timestamps")
    submit = SubmitField("Submit")
    delete = SubmitField("Delete Post", render_kw={"data-confirm-submit": ""})
    back = SubmitField("Back", render_kw={"data-back-btn": ""})


class ChangeAdminPasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[InputRequired(),
            Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])])
    new_password_1 = PasswordField("New password", validators=[InputRequired(),
            Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])])
    new_password_2 = PasswordField("Repeat new password", validators=[InputRequired(),
            Length(max=Config.DB_CONFIGS["MAXLEN_USER_PASSWORD"])])
    submit = SubmitField("Submit")
    back = SubmitField("Back", render_kw={"data-back-btn": ""})
