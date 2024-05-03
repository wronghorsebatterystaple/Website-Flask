from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

from app.db_config import db_config


class LoginForm(FlaskForm):
    is_modal = HiddenField("Is Modal", default="no")
    password = PasswordField("Password", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_USER_PASSWORD"])])
    submit = SubmitField("Submit")
