import os

from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

database_path = os.environ.get('DATABASE_URL')

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost:5432/recipe_sharing"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    migrate = Migrate(app, db)
    db.init_app(app)
    with app.app_context():
        db.create_all()


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


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


favorites = db.Table(
    "favorites",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id"), primary_key=True),
    db.Column("created_at", db.DateTime, nullable=False)
)


follows = db.Table(
    "follows",
    db.Column("following_user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("followed_user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("created_at", db.DateTime, nullable=False),
    info={'foreign_keys': ['follows.following_user_id', 'follows.followed_user_id']}
)


class User(BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.LargeBinary)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    # one-to-many relations
    recipes = db.relationship('Recipe', backref='users', lazy=True)

    # many-to-many relations
    favorites = db.relationship('Recipe', secondary=favorites, lazy='subquery', backref=db.backref('favorite', lazy=True))
    # follows = db.relationship('User', secondary=follows, lazy='subquery', backref=db.backref('follows', lazy=True))
    follows = db.relationship('User', secondary=follows, primaryjoin=(follows.c.following_user_id == id), secondaryjoin=(follows.c.followed_user_id == id), backref=db.backref('followers', lazy=True))



class Recipe(BaseModel):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    prepare_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    image = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    # one-to-many relations
    ingrediants = db.relationship('Ingrediant', backref='recipe_ingrediant', lazy=True)
    instructions = db.relationship('Instruction', backref='recipe_instruction', lazy=True)


class Ingrediant(BaseModel):
    __tablename__ = "ingrediants"

    # id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True, nullable=False)
    item_number = db.Column(db.Integer, nullable=False)
    item = db.Column(db.Text, nullable=False)

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }


class Instruction(BaseModel):
    __tablename__ = "instructions"

    # id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True, nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }


class Category(BaseModel):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False, unique=True)

    # one-to-many relations
    recipes = db.relationship('Recipe', backref='category', lazy=True)
