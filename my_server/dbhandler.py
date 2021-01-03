from my_server import db, login_manager, app
from flask_login import UserMixin, current_user
from PIL import Image
import secrets
import os

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable = False)
    score = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f'Movie: {self.name}'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable = False, unique=True)
    email = db.Column(db.String(100), nullable = False, unique=True)
    password = db.Column(db.String(20), nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default='default.jpg')

    def __repr__(self):
        return f'User: {self.username}'

def resetDB():
    db.drop_all()
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Start of own functions

def usernameExists(uname):
    missing = User.query.filter_by(username=uname).first()
    return missing is not None

def emailExists(umail):
    missing = User.query.filter_by(email=umail).first()
    return missing is not None

def createUser(uname, email, password):
    new = User(username=uname, email=email, password=password)
    db.session.add(new)
    db.session.commit()

def getUserByEmail(umail):
    user = User.query.filter_by(email=umail).first()
    return user

def getUserByUname(uname):
    user = User.query.filter_by(username=uname).first()
    return user

def commitDB():
    db.session.commit()

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_name)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    current_user.image_file = picture_name
    