from werkzeug.exceptions import HTTPException
from config import Config


# case CSRFError when not logged in: regenerate CSRF token and resend form Ajax
class RefreshCSRFError(HTTPException):
    (code, description) = Config.CUSTOM_ERRORS["REFRESH_CSRF"]


# case CSRFError when logged in: show login modal
class RefreshLoginError(HTTPException):
    (code, description) = Config.CUSTOM_ERRORS["REFRESH_LOGIN"]
