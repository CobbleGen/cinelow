from flask import Flask
import flask_sqlalchemy
from flask_login import LoginManager

app = Flask(__name__)
from my_server.config import Config
app.config.from_object(Config)
db = flask_sqlalchemy.SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
from my_server import routes, errors

