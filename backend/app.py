import datetime
from functools import wraps

from database.models import (Category, Instruction, Recipe, User, db,
                             db_drop_and_create_all, setup_db)
from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def create_app(db_URI="", test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

    if db_URI:
        setup_db(app, db_URI)
    else:
        setup_db(app)  

    # with app.app_context():
    #     db_drop_and_create_all()

    # print("lol1")
    # Create users and add them to the session
    # user1 = User(first_name="John", last_name="Doe", email="john@example.com", password_hash="hashed_password1", created_at=datetime.datetime.now())
    # user2 = User(first_name="Jane", last_name="Smith", email="jane@example.com", password_hash="hashed_password2", created_at=datetime.datetime.now())

    # Create recipes and add them to the session
    # recipe1 = Recipe(title="Recipe 1", description="Description 1", prepare_time=30, cook_time=60, user_id=1, created_at=datetime.datetime.now())
    # recipe2 = Recipe(title="Recipe 2", description="Description 2", prepare_time=20, cook_time=45, user_id=2, created_at=datetime.datetime.now())

    # Create instructions and add them to the session
    # instruction1 = Instruction(step_number=1, description="Step 1 for Recipe 1", recipe_id=1)
    # instruction2 = Instruction(step_number=2, description="Step 2 for Recipe 1", recipe_id=1)
    # instruction3 = Instruction(step_number=1, description="Step 1 for Recipe 2", recipe_id=2)

    # # Create categories and add them to the session
    # category1 = Category(category="Category 1")
    # category2 = Category(category="Category 2")

    # Add data to the database session and commit the changes
    # with app.app_context():
    #     instruction1.insert()
    #     instruction2.insert()
    #     instruction3.insert()
    #     category1.insert()
    #     category2.insert()


    # configure session to use filesystem (instead of signed cookies)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)


    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


    @app.route('/health')
    def health():
        return "Up and Running!"

    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""

        # Forget any user_id
        session.clear()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            # Ensure username was submitted
            if not username:
                flash(f"Enter email", "warning")
                return render_template("login.html")

            # Ensure password was submitted
            elif not password:
                flash(f"Enter password", "warning")
                return render_template("login.html")

            # Query database for username
            user = User.query.filter_by(username=username).first()

            # Ensure username exists and password is correct
            print(check_password_hash(password, user.password_hash))
            if user is None or not check_password_hash(user.password_hash, password):
                flash(f"Invalid username and/or password", "error")
                return render_template("login.html")

            # Remember which user has logged in
            session["user_id"] = user.id

            # Redirect user to home page
            flash(f"Welcome {user.first_name}!", "info")
            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")

    
    @app.route("/logout")
    def logout():
        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

    
    @app.route("/")
    def index():
        recipes = Recipe.query.order_by(Recipe.id.desc()).limit(5).all()

        dict = {}

        # for i in recipes:


        print("HERE ==>\n", recipes)

        return render_template("home.html", recipes=recipes)
        


    return app



app = create_app()
