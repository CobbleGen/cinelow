from .. import db, app
from .dbhandler import User, MovieUserScores
from flask_login import current_user
from sqlalchemy.sql import func
import secrets
from PIL import Image
import os


def createUser(uname, email, password):
    new = User(username=uname, email=email, password=password)
    db.session.add(new)
    db.session.commit()

def getUserById(uid):
    user = User.query.filter_by(id=uid).first()
    return user

def getUserByEmail(umail):
    user = User.query.filter(func.lower(User.email) == func.lower(umail)).first()
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

def get_user_scores(user_id):
    query = db.session.query(
    MovieUserScores,
    func.rank()\
        .over(
            order_by=MovieUserScores.score.desc(),
            partition_by=MovieUserScores.user_id,
        )\
        .label('rank')
    ).filter(MovieUserScores.votes >= 5)
    # now filter
    query = query.filter(MovieUserScores.user_id == user_id)
    query = query.order_by(MovieUserScores.user_id, 'rank')
    movies = query.all()
    return movies

def get_user_total_votes(user_id):
    votes = db.session.query(func.sum(MovieUserScores.votes)).filter(MovieUserScores.user_id == user_id).first()[0]
    if votes:
        return votes/2
    return 0