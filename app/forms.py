from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

from config import Config


class LoginForm(FlaskForm):
    is_modal = HiddenField(
            default="no")

    password = PasswordField(
            "Password",
            validators=[InputRequired(), Length(max=Config.DB_CONFIGS["USER_PASSWORD_MAXLEN"])])

    login_form_submit = SubmitField(
            "Submit")
