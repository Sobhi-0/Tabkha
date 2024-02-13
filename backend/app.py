import datetime

from database.models import (Category, Ingrediant, Instruction, Recipe, User,
                             db, db_drop_and_create_all, setup_db)
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

    # for testing purposes
    app.config['SQLALCHEMY_ECHO'] = True

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
        recipes = Recipe.query.filter_by(user_id=session["user_id"]).order_by(Recipe.created_at.desc())
        
        # Paginating recipes
        paginated_recipes = paginate_items(selection=recipes, request=request, per_page=7)

        # return jsonify(paginated_recipes)
        return render_template('my-recipes.html', paginated_recipes=paginated_recipes)


    @app.route("/add-recipe", methods=["GET", "POST"])
    @login_required
    def add_recipe():
        if request.method == "POST":
            title = request.form.get("title")
            description = request.form.get("description")
            prepare_time = request.form.get("prepare_time")
            cook_time = request.form.get("cook_time")
            category_id = request.form.get("category_id")

            instructions = request.form.getlist("instructions[]")
            ingrediants = request.form.getlist("ingrediants[]")

            categories = Category.query.all()

            # Ensure all fields were submitted
            if not title or not description or not prepare_time or not cook_time or not category_id or not instructions or not ingrediants:
                flash(f"Must fill all fields", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure prepare_time and cook_time are numbers
            if not prepare_time.isdigit() or not cook_time.isdigit():
                flash(f"Prepare time and cook time must be numbers", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure category is a number
            if not category_id.isdigit():
                flash(f"Category must be a number", "warning")

            # Ensure category exists
            if not Category.query.filter_by(id=category_id).first():
                flash(f"Category does not exist", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Create a new recipe
            recipe = Recipe(title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, user_id=session["user_id"], created_at=datetime.datetime.now())

            for index, ingrediant in enumerate(ingrediants, start=1):
                ingrediant = Ingrediant(item_number=index, item=ingrediant)
                recipe.ingrediants.append(ingrediant)

            for index, instruction in enumerate(instructions, start=1):
                instruction = Instruction(step_number=index, description=instruction)
                recipe.instructions.append(instruction)

            # Add recipe to the database session and commit the changes
            recipe.insert()

            flash(f"Recipe added successfully", "success")
            return redirect("/my-recipes")

        else:
            categories = Category.query.all()
            return render_template("add-recipe.html", categories=categories)


    @app.route("/edit-recipe/<int:recipe_id>", methods=["GET", "POST"])
    @login_required
    def edit_recipe(recipe_id):
        if request.method == "POST":
            recipe = Recipe.query.filter_by(id=recipe_id).first()
            if session["user_id"] != recipe.user_id:
                flash(f"You are not authorized to edit this recipe", "error")
                return redirect("/my-recipes")

            title = request.form.get("title")
            description = request.form.get("description")
            prepare_time = request.form.get("prepare_time")
            cook_time = request.form.get("cook_time")
            category_id = request.form.get("category_id")

            ingrediants = request.form.getlist("ingrediants[]")
            instructions = request.form.getlist("instructions[]")

            # print("ingrediants", ingrediants)

            categories = Category.query.all()
            
            # Ensure all fields were submitted
            if not title or not description or not prepare_time or not cook_time or not category_id or not instructions or not ingrediants:
                flash(f"Must fill all fields", "warning")
                return render_template("edit-recipe.html", recipe=recipe ,categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure prepare_time and cook_time are numbers
            if not prepare_time.isdigit() or not cook_time.isdigit():
                flash(f"Prepare time and cook time must be numbers", "warning")
                return render_template("edit-recipe.html", recipe=recipe, categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure category is a number
            if not category_id.isdigit():
                flash(f"Category must be a number", "warning")

            # Ensure category exists
            if not Category.query.filter_by(id=category_id).first():
                flash(f"Category does not exist", "warning")
                return render_template("edit-recipe.html", recipe=recipe, categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            recipe.title = title
            recipe.description = description
            recipe.prepare_time = prepare_time
            recipe.cook_time = cook_time
            recipe.category_id = category_id

            # delete all ingrediants and instructions
            for i in recipe.ingrediants:
                # i.delete()
                db.session.delete(i)

            for i in recipe.instructions:
                # i.delete()
                db.session.delete(i)

            # add new ingrediants and instructions
            for index, ingrediant in enumerate(ingrediants, start=1):
                ingrediant = Ingrediant(recipe_id=recipe_id, item_number=index, item=ingrediant)
                # recipe.ingrediants.append(ingrediant)
                db.session.add(ingrediant)

            for index, instruction in enumerate(instructions, start=1):
                instruction = Instruction(recipe_id=recipe_id, step_number=index, description=instruction)
                # recipe.instructions.append(instruction)
                db.session.add(instruction)

            recipe.update()

            flash(f"Recipe updated!", "success")
            return redirect("/my-recipes")

        else:
            recipe = Recipe.query.filter_by(id=recipe_id).first()
            if session["user_id"] != recipe.user_id:
                flash(f"You are not authorized to edit this recipe", "error")
                return redirect("/my-recipes")

            categories = Category.query.all()
            ingrediants = Ingrediant.query.filter(Ingrediant.recipe_id == recipe_id).all()
            instructions = Instruction.query.filter_by(recipe_id=recipe_id).all()
            print("HERE ==>", ingrediants)
                
            return render_template("/edit-recipe.html", recipe=recipe, categories=categories, instructions=instructions, ingrediants=ingrediants)


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

        return render_template("home.html", recipes=recipes)
        


    return app



app = create_app()
