import datetime

from database.models import (Category, Instruction, Recipe, User, db,
                             db_drop_and_create_all, setup_db)
from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_session import Session
from helpers import login_required, paginate_items, valid_email, valid_password
from werkzeug.security import check_password_hash, generate_password_hash


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
    # recipe1 = Recipe(title="Recipe-289", description="Description4 1", prepare_time=30, cook_time=60, category_id=1, user_id=1, created_at=datetime.datetime.now())
    # recipe2 = Recipe(title="Recipe 2", description="Description 2", prepare_time=20, cook_time=45, user_id=2, created_at=datetime.datetime.now())

    # Create instructions and add them to the session
    # instruction1 = Instruction(step_number=1, description="Step 1 for Recipe 1", recipe_id=4)
    # instruction2 = Instruction(step_number=2, description="Step 2 for Recipe 1", recipe_id=4)
    # instruction3 = Instruction(step_number=1, description="Step 1 for Recipe 2", recipe_id=2)

    # # Create categories and add them to the session
    # category1 = Category(category="Category 1")
    # category2 = Category(category="Category 2")

    # Add data to the database session and commit the changes
    # with app.app_context():
    #     recipe1.insert()
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


    @app.route("/health")
    def health():
        return "Up and Running!"


    @app.route("/my-recipes")
    @login_required
    def my_recipes():
        user_id = session["user_id"]
        recipes = Recipe.query.filter_by(user_id=user_id).order_by(Recipe.created_at.desc())
        
        # Paginating recipes
        paginated_recipes = paginate_items(selection=recipes, request=request, per_page=7)

        # return jsonify(paginated_recipes)
        return render_template('my-recipes.html', paginated_recipes=paginated_recipes)


    
    @app.route("/login", methods=["GET", "POST"])
    def login():
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
            if user is None or not check_password_hash(user.password_hash, password):
                flash(f"Invalid username and/or password", "error")
                return render_template("login.html")

            # Remember which user has logged in
            session["user_id"] = user.id

            # Redirect user to home page
            flash(f"Welcome back, {user.first_name}!", "info")
            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")

    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")
            username = request.form.get("username")
            email = request.form.get("email")
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")

            # Ensure all fields were submitted
            if  not firstname or not lastname or not email or not username or not password1 or not password2:
                flash(f"Must fill all fields", "warning")
                return render_template("register.html")

            if password1 != password2:
                flash("Passwords do not match", "error")
                return render_template("register.html")

            if not valid_email(email):
                flash("Email not valid", "error")
                return render_template("register.html")

            if not valid_password(password1):
                flash("Password does not meet constraints", "error")
                return render_template("register.html")

            new_user = User(first_name=firstname, last_name=lastname, username=username, email=email, password_hash=generate_password_hash(password1), created_at=datetime.datetime.now())
            new_user.insert()

            flash("Account created successfully", "success")
            return redirect("/login")

        else:
            return render_template("register.html")

    
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


        # print("HERE ==>\n", recipes)

        return render_template("home.html", recipes=recipes)
        


    return app



app = create_app()
