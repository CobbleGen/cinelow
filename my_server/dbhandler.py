from my_server import db, login_manager, app
from flask_login import UserMixin, current_user
from sqlalchemy.orm import relationship
import requests
import json
from PIL import Image
import secrets
import os

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable = False, unique=True)
    email = db.Column(db.String(100), nullable = False, unique=True)
    password = db.Column(db.String(20), nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default='default.jpg')

    def __repr__(self):
        return f'User: {self.username}'

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable = False)
    categories = relationship("Association", back_populates="movie")

    def __repr__(self):
        return f'Movie: {self.name}'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    movies = relationship("Association", back_populates="category")

class Association(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    score = db.Column(db.Integer)
    votes = db.Column(db.Integer)
    category = relationship("Category", back_populates="movies")
    movie = relationship("Movie", back_populates="categories")

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
    

def add_movie(id):
    respons = requests.get('http://api.themoviedb.org/3/movie/' + str(id) + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        return None
    movie = json.loads(respons.text)
    genres = movie['genres']
    categories = []
    for genre in genres:
        cate = Category.query.filter_by(id=genre['id']).first()
        if cate is None:
            cate = add_category(genre['id'], genre['name'])
        categories.append(cate)
    m = Movie(id = movie['id'], name = movie['original_title'])
    a = Association(score=700, votes=0)
    a.movie = m
    for category in categories:
        category.movies.append(a)
    db.session.add(m)
    db.session.add(a)
    db.session.commit()
    

def add_category(id, name):
    new = Category(id = id, name = name)
    db.session.add(new)
    db.session.commit()
    return new