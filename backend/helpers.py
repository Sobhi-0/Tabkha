import re
from functools import wraps

from email_validator import EmailNotValidError, validate_email
from flask import g, redirect, request, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def valid_email(email):
    try:
        valid = validate_email(email)
        email = valid.email
        return True
    except EmailNotValidError as e:
        return False


def valid_password(password):
    password_regex = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()-_=+])[a-zA-Z0-9!@#$%^&*()-_=+]{8,20}$"
    if re.match(password_regex, password):
        return True
    return False
