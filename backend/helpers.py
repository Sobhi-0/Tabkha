import re
import os
from functools import wraps
from uuid import uuid4

from werkzeug.utils import secure_filename
from email_validator import EmailNotValidError, validate_email
from flask import redirect, request, session, url_for


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
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
    password_regex = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()-_=+])[a-zA-Z0-9!@#$%^&*()-_=+]{8,20}$"
    if re.match(password_regex, password):
        return True
    return False


def paginate_items(selection, request, per_page):
    # Takes the page number (if not provided takes 1 as a default)
    page = request.args.get("page", 1, type=int)

    paginated_recipes = selection.paginate(per_page=per_page, page=page, error_out=False)

    return paginated_recipes


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Define a function to generate a unique filename
def generate_unique_filename(filename):
    secure_name = secure_filename(filename)
    # Get the file extension
    _, extension = os.path.splitext(secure_name)
    # Generate a unique identifier (UUID) and combine it with the file extension
    unique_filename = str(uuid4()) + extension
    return unique_filename
