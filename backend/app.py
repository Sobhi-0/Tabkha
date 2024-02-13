import datetime

from sqlalchemy import text

from database.models import (
    Category, Instruction, Ingrediant, Recipe, User, db, setup_db)
from flask import (Flask, flash, redirect, render_template,
                   request, session)
from flask_session import Session
from helpers import login_required, paginate_items, valid_email, valid_password
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(db_URI="", test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app = Flask(__name__, template_folder='../frontend/templates',
                static_folder='../frontend/static')

    # Enable template auto-reloading
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    if db_URI:
        setup_db(app, db_URI)
    else:
        setup_db(app)

    # with app.app_context():
    #     db_drop_and_create_all()

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
        recipes = Recipe.query.filter_by(
            user_id=session["user_id"]).order_by(Recipe.created_at.desc())

        # Paginating recipes
        paginated_recipes = paginate_items(
            selection=recipes, request=request, per_page=7)

        # return jsonify(paginated_recipes)
        return render_template('my-recipes.html', paginated_recipes=paginated_recipes)

    # Recipe details

    @app.route("/recipes", methods=["GET"])
    def recipes():
        # Paginating recipes
        recipes = Recipe.query.order_by(Recipe.created_at.desc())
        paginated_recipes = paginate_items(
            selection=recipes, request=request, per_page=7)

        return render_template('recipes.html', paginated_recipes=paginated_recipes)


    @app.route("/recipe/<int:recipe_id>", methods=["GET"])
    def recipe(recipe_id):
        recipe = Recipe.query.filter_by(id=recipe_id).first()

        # Ensure recipe exists
        if not recipe:
            flash("Recipe not found", "error")
            return render_template("home.html")

        # Check if the user added the recipe to favorites
        is_favorite = False
        if session.get("user_id"):
            user = User.query.filter_by(id=session["user_id"]).first()
            if recipe in user.favorites:
                is_favorite = True

        # Get the username of the recipe owner
        user = User.query.filter_by(id=recipe.user_id).first()

        # Get ingrediants and instructions for the recipe
        ingrediants_query = text(
            "SELECT * FROM ingrediants WHERE recipe_id = :recipe_id ORDER BY item_number")
        parameters = {"recipe_id": recipe_id}
        ingrediants_res = db.session.execute(ingrediants_query, parameters)
        ingrediants_rows = ingrediants_res.fetchall()
        ingrediants = [ingrediant for ingrediant in ingrediants_rows]

        instructions_query = text(
            "SELECT * FROM instructions WHERE recipe_id = :recipe_id ORDER BY step_number")
        parameters = {"recipe_id": recipe_id}
        instructions_res = db.session.execute(instructions_query, parameters)
        instructions_rows = instructions_res.fetchall()
        instructions = [instruction for instruction in instructions_rows]

        return render_template('recipe-details.html', recipe=recipe, ingredients=ingrediants, instructions=instructions, user=user, is_favorite=is_favorite)

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
                flash("Must fill all fields", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure prepare_time and cook_time are numbers
            if not prepare_time.isdigit() or not cook_time.isdigit():
                flash("Prepare time and cook time must be numbers", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure category is a number
            if not category_id.isdigit():
                flash("Category must be a number", "warning")

            # Ensure category exists
            if not Category.query.filter_by(id=category_id).first():
                flash("Category does not exist", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Create a new recipe
            recipe = Recipe(title=title, description=description, prepare_time=prepare_time, cook_time=cook_time,
                            category_id=category_id, user_id=session["user_id"], created_at=datetime.datetime.now())

            # Add ingrediants to the recipe
            for i, ingrediant in enumerate(ingrediants):
                recipe.ingrediants.append(Ingrediant(
                    item_number=i+1, item=ingrediant))

            # Add instructions to the recipe
            for i, instruction in enumerate(instructions):
                recipe.instructions.append(Instruction(
                    step_number=i+1, description=instruction))

            # Add recipe to the database session and commit the changes
            recipe.insert()

            flash("Recipe added successfully", "success")
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
                flash("You are not authorized to edit this recipe", "error")
                return redirect("/my-recipes")

            title = request.form.get("title")
            description = request.form.get("description")
            prepare_time = request.form.get("prepare_time")
            cook_time = request.form.get("cook_time")
            category_id = request.form.get("category_id")
            ingrediants = request.form.getlist("ingrediants[]")
            instructions = request.form.getlist("instructions[]")

            categories = Category.query.all()

            # Ensure all fields were submitted
            if not title or not description or not prepare_time or not cook_time or not category_id or not instructions or not ingrediants:
                flash("Must fill all fields", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure prepare_time and cook_time are numbers
            if not prepare_time.isdigit() or not cook_time.isdigit():
                flash("Prepare time and cook time must be numbers", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            # Ensure category is a number
            if not category_id.isdigit():
                flash("Category must be a number", "warning")

            # Ensure category exists
            if not Category.query.filter_by(id=category_id).first():
                flash("Category does not exist", "warning")
                return render_template("add-recipe.html", categories=categories, title=title, description=description, prepare_time=prepare_time, cook_time=cook_time, category_id=category_id, instructions=instructions, ingrediants=ingrediants)

            recipe = Recipe.query.filter_by(id=recipe_id).first()
            if session["user_id"] != recipe.user_id:
                flash("You are not authorized to edit this recipe", "error")
                return redirect("/my-recipes")

            recipe.title = title
            recipe.description = description
            recipe.prepare_time = prepare_time
            recipe.cook_time = cook_time
            recipe.category_id = category_id

            # Delete all ingrediants and instructions
            Ingrediant.query.filter_by(recipe_id=recipe_id).delete()
            Instruction.query.filter_by(recipe_id=recipe_id).delete()

            # Add ingrediants to the recipe
            for i, ingrediant in enumerate(ingrediants):
                recipe.ingrediants.append(Ingrediant(
                    item_number=i+1, item=ingrediant))

            # Add instructions to the recipe
            for i, instruction in enumerate(instructions):
                recipe.instructions.append(Instruction(
                    step_number=i+1, description=instruction))

            recipe.update()

            flash("Recipe updated!", "success")
            return redirect("/my-recipes")

        else:
            categories = Category.query.all()
            recipe = Recipe.query.filter_by(id=recipe_id).first()

            if session["user_id"] != recipe.user_id:
                flash("You are not authorized to edit this recipe", "error")
                return redirect("/my-recipes")

            # Get ingrediants and instructions for the recipe
            ingrediants_query = text(
                "SELECT * FROM ingrediants WHERE recipe_id = :recipe_id ORDER BY item_number")
            parameters = {"recipe_id": recipe_id}
            ingrediants_res = db.session.execute(ingrediants_query, parameters)
            ingrediants_rows = ingrediants_res.fetchall()
            ingrediants = [ingrediant for ingrediant in ingrediants_rows]

            instructions_query = text(
                "SELECT * FROM instructions WHERE recipe_id = :recipe_id ORDER BY step_number")
            parameters = {"recipe_id": recipe_id}
            instructions_res = db.session.execute(
                instructions_query, parameters)
            instructions_rows = instructions_res.fetchall()
            instructions = [instruction for instruction in instructions_rows]

            return render_template("/edit-recipe.html", recipe=recipe, categories=categories, ingrediants=ingrediants, instructions=instructions)

    @app.route("/recipe/<int:recipe_id>", methods=["DELETE"])
    @login_required
    def delete_recipe(recipe_id):
        # Paginating recipes
        recipes = Recipe.query.filter_by(
            user_id=session["user_id"]).order_by(Recipe.created_at.desc())
        paginated_recipes = paginate_items(
            selection=recipes, request=request, per_page=7)

        recipe = Recipe.query.filter_by(id=recipe_id).first()

        if not recipe:
            flash("Recipe doesn't exist", "error")
            return render_template("my-recipes.html", paginated_recipes=paginated_recipes)

        if session["user_id"] != recipe.user_id:
            flash("You are not authorized to delete this recipe", "error")
            return render_template("my-recipes.html", paginated_recipes=paginated_recipes)

        recipe.delete()

        flash("Recipe deleted!", "success")
        return render_template("my-recipes.html", paginated_recipes=paginated_recipes)

    # Search for recipes

    @app.route("/search", methods=["GET"])
    def search():
        search_query = request.args.get("q")
        recipes = Recipe.query.filter(Recipe.title.ilike(
            f"%{search_query}%")).order_by(Recipe.created_at.desc())
        count = len(recipes.all())
        # Paginating recipes
        paginated_recipes = paginate_items(
            selection=recipes, request=request, per_page=7)

        return render_template("search.html", search_query=search_query, paginated_recipes=paginated_recipes, count=count)

    # Add recipe to favorites

    @app.route("/favorite/<int:recipe_id>", methods=["POST"])
    @login_required
    def favorite(recipe_id):
        recipe = Recipe.query.filter_by(id=recipe_id).first()

        if not recipe:
            flash("Recipe not found", "error")
            return redirect("/")

        user = User.query.filter_by(id=session["user_id"]).first()
        user.favorites.append(recipe)
        user.update()

        flash("Recipe added to favorites!", "success")
        return redirect("/")

    # Remove recipe from favorites

    @app.route("/unfavorite/<int:recipe_id>", methods=["POST"])
    @login_required
    def unfavorite(recipe_id):
        recipe = Recipe.query.filter_by(id=recipe_id).first()

        if not recipe:
            flash("Recipe not found", "error")
            return redirect("/")

        user = User.query.filter_by(id=session["user_id"]).first()

        if recipe not in user.favorites:
            flash("Recipe not in favorites", "error")
            return redirect("/")

        user.favorites.remove(recipe)
        user.update()

        flash("Recipe removed from favorites!", "success")
        # return render_template("favorites.html",)
        return redirect("/")

    # View user's favorites

    @app.route("/my-favorites", methods=["GET"])
    @login_required
    def my_favorites():
        user = User.query.filter_by(id=session["user_id"]).first()
        recipes = user.favorites

        return render_template("my-favorites.html", recipes=recipes)

    @app.route("/profile", methods=["GET"])
    @login_required
    def profile():
        user = User.query.filter_by(id=session["user_id"]).first()

        if not user:
            flash("User not found", "error")
            return redirect("/")

        return render_template("profile.html", user=user)

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
                flash("Enter email", "warning")
                return render_template("login.html")

            # Ensure password was submitted
            elif not password:
                flash("Enter password", "warning")
                return render_template("login.html")

            # Query database for username
            user = User.query.filter_by(username=username).first()

            # Ensure username exists and password is correct
            if user is None or not check_password_hash(user.password_hash, password):
                flash("Invalid username and/or password", "error")
                return render_template("login.html")

            # Remember which user has logged in
            session["user_id"] = user.id

            # Redirect user to home page
            flash(f"Welcome back, {user.first_name}!", "info")
            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")

    @app.route("/change-password", methods=["POST"])
    @login_required
    def change_password():
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Ensure all fields were submitted
        if not old_password or not new_password or not confirm_password:
            flash("Must fill all fields", "warning")
            return redirect("/profile")

        # Ensure old password is correct
        user = User.query.filter_by(id=session["user_id"]).first()
        if not check_password_hash(user.password_hash, old_password):
            flash("Old password is incorrect", "error")
            return redirect("/profile")

        # Ensure new password meets constraints
        if not valid_password(new_password):
            flash("Password does not meet constraints", "error")
            return redirect("/profile")

        # Ensure new password and confirm password match
        if new_password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect("/profile")

        user.password_hash = generate_password_hash(new_password)
        user.update()

        flash("Password changed successfully", "success")
        return redirect("/profile")

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
            if not firstname or not lastname or not email or not username or not password1 or not password2:
                flash("Must fill all fields", "warning")
                return render_template("register.html")

            # Ensure valid email and password
            if not valid_email(email):
                flash("Email not valid", "error")
                return render_template("register.html", firstname=firstname, lastname=lastname, username=username)

            if not valid_password(password1):
                flash("Password does not meet constraints", "error")
                return render_template("register.html", firstname=firstname, lastname=lastname, username=username, email=email)

            if password1 != password2:
                flash("Passwords do not match", "error")
                return render_template("register.html", firstname=firstname, lastname=lastname, username=username, email=email)

            # Ensure username is unique
            exist_user = User.query.filter_by(username=username).first()
            if exist_user:
                flash("Username already exists", "error")
                return render_template("register.html", firstname=firstname, lastname=lastname, email=email)

            # Ensure email is unique
            exist_email = User.query.filter_by(email=email).first()
            if exist_email:
                flash("Email already exists", "error")
                return render_template("register.html", firstname=firstname, lastname=lastname, username=username)

            new_user = User(first_name=firstname, last_name=lastname, username=username, email=email,
                            password_hash=generate_password_hash(password1), created_at=datetime.datetime.now())
            new_user.insert()

            flash("Account created successfully", "success")
            return render_template("login.html")

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
        # Recipes to be displayed on the home page
        recipes = Recipe.query.order_by(Recipe.id.desc()).limit(5).all()

        return render_template("home.html", recipes=recipes)

    return app


APP = create_app()
