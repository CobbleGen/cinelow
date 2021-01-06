from flask import Flask
import flask_sqlalchemy
from flask_login import LoginManager

app = Flask(__name__)
from my_server.config import Config
app.config.from_object(Config)
db = flask_sqlalchemy.SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

from my_server import errors
from my_server.main.routes import main
from my_server.users.routes import users
from my_server.people_movies.routes import people_movies