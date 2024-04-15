from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

from app.db_config import db_config


class LoginForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired(),
            Length(max=db_config["MAXLEN_USER_PASSWORD"])])
    submit = SubmitField("Submit")
