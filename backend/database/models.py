import os

from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

database_path = os.environ.get('DATABASE_URL')

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    migrate = Migrate(app, db)
    db.init_app(app)
    with app.app_context():
        db.create_all()


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    # This makes this class abstract and not mapped to a database table.
    __abstract__ = True

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.LargeBinary)
    password_hash = db.Column(db.String, nullable=False)

    # Establish a many-to-many relationship between models
    favorite_recipes = db.relationship('Recipe', secondary='favorite_recipes', back_populates='favorited_by')
    favorite_recipes = db.relationship('Follower', secondary='followers', back_populates='followers')

# new_recipe = Recipe(title="Recipe Title", description="Recipe Description")
# instruction1 = Instruction(step_number=1, description="Step 1 Description", recipe=new_recipe)
# instruction2 = Instruction(step_number=2, description="Step 2 Description", recipe=new_recipe)
class Recipe(BaseModel):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    prepare_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    image = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Establish a many-to-many relationship between models
    instructions = db.relationship('Instruction', backref='recipe', lazy=True)
    categories = db.relationship('Category', secondary='recipe_categories', backref='recipes')
    favorited_by = db.relationship('User', secondary='favorite_recipes', back_populates='favorite_recipes')


class Instruction(BaseModel):
    __tablename__ = "instructions"

    id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

class Category(BaseModel):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

# to manage the many-to-many relationship
recipe_categories = db.Table(
    'recipe_categories',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
)


class FavoriteRecipe(BaseModel):
    __tablename__ = "favorite_recipes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)


class Follower(BaseModel):
    __tablename__ = "followers"

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
