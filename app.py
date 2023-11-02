from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session


def create_app(db_URI="", test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # # configure session to use filesystem (instead of signed cookies)
    # app.config["SESSION_PERMANENT"] = False
    # app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    @app.route('/health')
    def health():
        return "Up and Running!"


    return app



app = create_app()
