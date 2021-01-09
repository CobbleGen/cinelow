from .. import db, app
from .dbhandler import User
from flask_login import current_user
import secrets
from PIL import Image
import os


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