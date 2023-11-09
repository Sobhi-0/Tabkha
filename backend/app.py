import datetime

from database.models import (Category, Instruction, Recipe, User, db,
                             db_drop_and_create_all, setup_db)
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session)
from flask_session import Session
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


    @app.route('/health')
    def health():
        return "Up and Running!"

    
    @app.route("/")
    def index():
        recipes = Recipe.query.order_by(Recipe.id.desc()).limit(5).all()

        dict = {}

        # for i in recipes:


        print("HERE ==>\n", recipes)

        return render_template("home.html", recipes=recipes)
        


    return app



app = create_app()
